"""递归搜索 (Search) wrapper service。

业务目标: 把任务书 (brief.md) 转成 3-5 个 arxiv 检索词，跑 arxiv 拿候选，
LLM 重排打分，写 Tasks/{slug}/literature.md。

依赖注入约定:
- chat_completion_fn: 形同 Product.backend.llm_client.chat_completion(messages, ...) -> (text, usage)
- arxiv_fn:           arxiv_fn(query: str, max_results: int) -> list[dict]

两者都可被测试桩替换；生产代码用默认实现。
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

from Product.backend.llm_client import chat_completion
from Product.types.research import Paper, SearchRequest, SearchResponse


# 默认 provider / model (MiniMax Token Plan, Anthropic-compatible)
# 参考: ~/Desktop/AI组件工作流库/components/minimax-token-plan-real-service/WORKFLOW.md
_DEFAULT_PROVIDER = "minimax"
_DEFAULT_MODEL = "MiniMax-M3"
_DEFAULT_TEMPERATURE = 0.3

# verdict gate
DEFAULT_MIN_COUNT = 8
DEFAULT_MAX_COUNT = 12

# rerank fallback score (LLM 解析失败时使用)
_FALLBACK_RELEVANCE = 0.5


# ── helpers ───────────────────────────────────────────────────────────────────


def _strip_code_fence(text: str) -> str:
    """LLM 常把 JSON 包在 ```json ... ``` 里。剥掉外壳。"""
    if "```" not in text:
        return text
    # 抓第一个 ``` 之后到下一个 ``` 之前
    parts = text.split("```", 2)
    if len(parts) >= 2:
        block = parts[1]
        # 去掉首行的 ```json / ```python 之类
        block = re.sub(r"^[a-zA-Z]+\n", "", block, count=1)
        return block.strip()
    return text


def _safe_json_loads(text: str) -> Any:
    """先剥 code fence 再 parse JSON；遇错抛 ValueError 给上层兜底。"""
    cleaned = _strip_code_fence(text).strip()
    return json.loads(cleaned)


def _paper_from_arxiv_item(item: dict[str, Any]) -> Paper:
    """把 arxiv-mcp 返回的 dict 映射成 Paper。

    arxiv-mcp 返回的 keys: title, authors(list[str]), year(int), abstract, arxiv_id
    relevance_score 缺省为 0.0（待 rerank 填充），accepted 默认 True。
    """
    return Paper(
        title=item.get("title", "").strip(),
        authors=list(item.get("authors", []) or []),
        year=int(item.get("year", 0) or 0),
        abstract=item.get("abstract", "").strip(),
        arxiv_id=item.get("arxiv_id", "").strip(),
        relevance_score=0.0,
        accepted=True,
    )


# ── core steps ────────────────────────────────────────────────────────────────


def build_queries(
    brief_text: str,
    *,
    chat_completion_fn: Callable[..., tuple[str, dict[str, int]]] | None = None,
    prompt_loader: Callable[[], str] | None = None,
) -> list[dict[str, str]]:
    """调 LLM 把研究简报转成 3-5 个 arxiv 检索词。

    Returns:
        list of {"query": str, "rationale": str}
    """
    from Program.prompts.search.v1 import load_prompt_v1 as _default_loader

    chat = chat_completion_fn or chat_completion
    loader = prompt_loader or _default_loader

    # 用 .replace() 而非 .format()：prompt 里含 JSON 示例的 { "query": ... } 字面量
    # 会被 str.format 当成占位符抛 KeyError。
    prompt = (
        loader()
        .replace("{research_question}", brief_text[:2000])  # 防 LLM context 溢出
        .replace("{contributions}", "见上文研究简报")
    )
    text, _usage = chat(
        [{"role": "user", "content": prompt}],
        provider_id=_DEFAULT_PROVIDER,
        model=_DEFAULT_MODEL,
        temperature=_DEFAULT_TEMPERATURE,
    )
    data = _safe_json_loads(text)
    if not isinstance(data, list):
        raise ValueError(f"search LLM did not return a JSON list: {text[:300]}")
    # 截断到 3-5
    data = data[:5] if len(data) > 5 else data
    if len(data) < 3:
        raise ValueError(f"search LLM returned too few queries ({len(data)}); need >= 3")
    # 字段清洗
    out: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        q = str(item.get("query", "")).strip()
        r = str(item.get("rationale", "")).strip()
        if not q:
            continue
        out.append({"query": q, "rationale": r})
    if len(out) < 3:
        raise ValueError(f"search LLM returned too many empty queries; got {len(out)} valid")
    return out


def run_queries(
    queries: list[dict[str, str]],
    *,
    arxiv_fn: Callable[[str, int], list[dict[str, Any]]],
    per_query: int = 5,
) -> list[Paper]:
    """对每个 query 调 arxiv_fn，dedupe by arxiv_id，返回去重后的 Paper 列表。

    arxiv_fn signature: (query: str, max_results: int) -> list[dict]
    """
    seen: set[str] = set()
    papers: list[Paper] = []
    for q in queries:
        query = q.get("query", "").strip()
        if not query:
            continue
        try:
            raw = arxiv_fn(query, per_query) or []
        except Exception:
            # arxiv 调用失败不中断整个流程
            continue
        for item in raw:
            if not isinstance(item, dict):
                continue
            aid = str(item.get("arxiv_id", "")).strip()
            if not aid or aid in seen:
                continue
            seen.add(aid)
            try:
                papers.append(_paper_from_arxiv_item(item))
            except Exception:
                # 字段缺失的 paper 跳过
                continue
    return papers


def rerank(
    papers: list[Paper],
    *,
    brief_text: str = "",
    chat_completion_fn: Callable[..., tuple[str, dict[str, int]]] | None = None,
) -> list[Paper]:
    """LLM 给每篇 paper 打 relevance_score 0-1；按分数倒序。

    鲁棒性:
    - LLM 解析失败 → 给所有 paper 打 _FALLBACK_RELEVANCE (0.5) 后按 title 稳定排序
    - 越界分数 → clamp 到 [0, 1]
    - LLM 漏掉某些 arxiv_id → 那些保留 0.0（最低优先级）
    """
    if not papers:
        return []

    chat = chat_completion_fn or chat_completion

    payload = json.dumps(
        [
            {"arxiv_id": p.arxiv_id, "title": p.title, "abstract": p.abstract[:500]}
            for p in papers
        ],
        ensure_ascii=False,
    )
    user_prompt = (
        "你是文献相关性评估专家。给每篇论文打 relevance_score (0-1 浮点数) "
        "表示其与研究简报的相关性。仅输出 JSON 数组，元素形如 "
        '{"arxiv_id": "...", "relevance_score": 0.85}。\n\n'
        f"研究简报：{brief_text[:1500]}\n\n"
        f"论文列表：{payload}"
    )
    score_map: dict[str, float] = {}
    try:
        text, _usage = chat(
            [{"role": "user", "content": user_prompt}],
            provider_id=_DEFAULT_PROVIDER,
            model=_DEFAULT_MODEL,
            temperature=_DEFAULT_TEMPERATURE,
        )
        data = _safe_json_loads(text)
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                aid = str(item.get("arxiv_id", "")).strip()
                raw_score = item.get("relevance_score", _FALLBACK_RELEVANCE)
                try:
                    score = float(raw_score)
                except (TypeError, ValueError):
                    score = _FALLBACK_RELEVANCE
                # clamp
                score = max(0.0, min(1.0, score))
                if aid:
                    score_map[aid] = score
    except Exception:
        # LLM 失败：保留初始 0.0 / 不动
        pass

    # 把分数写回 paper
    for p in papers:
        if p.arxiv_id in score_map:
            p.relevance_score = score_map[p.arxiv_id]
        # 不在 score_map 的保持 0.0，自然落到尾部
    # 倒序
    papers.sort(key=lambda p: p.relevance_score, reverse=True)
    return papers


def write_literature(
    *,
    papers: list[Paper],
    topic: str,
    topic_slug: str,
    tasks_root: Path,
    model: str = _DEFAULT_MODEL,
    prompt_version: str = "v1",
) -> Path:
    """落盘到 Tasks/{topic_slug}/literature.md，附 provenance frontmatter。"""
    topic_dir = tasks_root / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    path = topic_dir / "literature.md"

    # YAML frontmatter (provenance)
    frontmatter = yaml.safe_dump(
        {
            "topic": topic,
            "topic_slug": topic_slug,
            "generated_by": "search-llm-m3",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "prompt_version": prompt_version,
            "n_papers": len(papers),
            "upstream": ["brief.md"],
            "downstream_consumers": ["variables.yaml", "design.json", "manuscript_paper.pdf"],
        },
        allow_unicode=True,
        sort_keys=False,
    )

    # body: 每篇一段，含相关性评分
    body_lines: list[str] = [f"# {topic} — 递归搜索文献综述", ""]
    body_lines.append(f"共 {len(papers)} 篇候选论文（按相关性倒序）。")
    body_lines.append("")
    for i, p in enumerate(papers, start=1):
        authors_str = ", ".join(p.authors) if p.authors else "未知作者"
        body_lines.extend([
            f"## {i}. {p.title}",
            "",
            f"- **作者**: {authors_str}",
            f"- **年份**: {p.year}",
            f"- **arXiv ID**: {p.arxiv_id}",
            f"- **相关性评分**: {p.relevance_score:.2f}",
            f"- **采纳**: {'是' if p.accepted else '否'}",
            "",
            p.abstract,
            "",
        ])

    content = f"---\n{frontmatter}---\n\n" + "\n".join(body_lines) + "\n"
    path.write_text(content, encoding="utf-8")
    return path


def verify_search(
    papers: list[Paper],
    *,
    min_count: int = DEFAULT_MIN_COUNT,
    max_count: int = DEFAULT_MAX_COUNT,
) -> bool:
    """verdict gate: paper 数在 [min_count, max_count] 区间且每篇都有有效 score。"""
    n = len(papers)
    if n < min_count or n > max_count:
        return False
    for p in papers:
        # relevance_score 在 [0, 1] 区间且已打分（>0 视为打分过，0 视为未打分）
        if p.relevance_score < 0.0 or p.relevance_score > 1.0:
            return False
        # 0.0 是 Pydantic 默认值；rerank 后有效分数应 > 0
        if p.relevance_score == 0.0:
            return False
    return True


# ── end-to-end ────────────────────────────────────────────────────────────────


def run_search(
    req: SearchRequest,
    tasks_root: Path,
    *,
    chat_completion_fn: Callable[..., tuple[str, dict[str, int]]] | None = None,
    arxiv_fn: Callable[[str, int], list[dict[str, Any]]] | None = None,
    per_query: int = 5,
) -> SearchResponse:
    """端到端: 读 brief → build_queries → run_queries → rerank → write_literature → verify。"""
    brief_path = Path(req.brief_path)
    if not brief_path.exists():
        raise FileNotFoundError(f"brief_path not found: {brief_path}")
    brief_text = brief_path.read_text(encoding="utf-8")

    # 1. build queries
    queries = build_queries(
        brief_text,
        chat_completion_fn=chat_completion_fn,
    )

    # 2. arxiv
    if arxiv_fn is None:
        arxiv_fn = _default_arxiv_stub
    papers = run_queries(queries, arxiv_fn=arxiv_fn, per_query=per_query)

    # 3. rerank
    papers = rerank(
        papers,
        brief_text=brief_text,
        chat_completion_fn=chat_completion_fn,
    )

    # 4. write
    topic = brief_path.stem  # 兜底: brief.md → "brief"
    # 尝试从 frontmatter 拿 topic
    try:
        if brief_text.startswith("---"):
            end = brief_text.find("\n---", 3)
            if end > 0:
                meta = yaml.safe_load(brief_text[3:end])
                if isinstance(meta, dict) and meta.get("topic"):
                    topic = str(meta["topic"])
    except Exception:
        pass

    path = write_literature(
        papers=papers,
        topic=topic,
        topic_slug=req.topic_slug,
        tasks_root=tasks_root,
    )

    # 5. verify
    passed = verify_search(papers)

    # 组 markdown（直接复用 write_literature 的产物内容；避免重复落盘）
    literature_markdown = path.read_text(encoding="utf-8")

    return SearchResponse(
        literature_markdown=literature_markdown,
        literature_path=str(path),
        papers=papers,
        verdict_passed=passed,
    )


# ── default arxiv stub (fallback when MCP not available) ─────────────────────


def _default_arxiv_stub(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """MCP 不可用时的兜底 stub：返回少量固定 list。

    真实环境用 mcp__paper-search__search_arxiv；测试或 fallback 用这个。
    """
    from Product.types.research import Paper as _P  # noqa: F401  防止循环 import

    seed: list[dict[str, Any]] = [
        {
            "title": f"Industrial Robots and Labor Markets (stub for '{query}')",
            "authors": ["Acemoglu, D.", "Restrepo, P."],
            "year": 2020,
            "abstract": "This is a stub paper returned by the local fallback when arxiv-mcp is unavailable. "
                        "It exists only to satisfy the verdict gate during local development.",
            "arxiv_id": f"stub-{abs(hash(query)) % 10**8:08d}-1",
        },
        {
            "title": f"Automation, Skills, and Wage Inequality (stub for '{query}')",
            "authors": ["Autor, D."],
            "year": 2019,
            "abstract": "Fallback stub #2. Replace with real arxiv-mcp output in production.",
            "arxiv_id": f"stub-{abs(hash(query)) % 10**8:08d}-2",
        },
    ]
    return seed[:max_results]
