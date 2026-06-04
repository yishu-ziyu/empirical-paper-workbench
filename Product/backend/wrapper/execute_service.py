"""L5-execution: 执行实验 (Execution) wrapper service。

行为契约（spec §6.1 row 5）：
- load_inputs: 读 brief/variables/design 三个文件
- write_section: 落盘 Manuscripts/{topic}/sections/section_{N}.md
- render_paper: 拼接 9 节生成 Manuscripts/{topic}/paper.pdf（weasyprint）
- write_results: 落盘 Results/{topic}/results.json 含 provenance
- run_execute_stream: SSE 风格 generator，yield ExecuteEvent
  序列：start → progress×N → section_done×9 → paper_ready → done
  异常时 yield error 事件后停止
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator, Optional

import yaml
from weasyprint import CSS, HTML

from Product.backend.llm_client import chat_completion
from Product.types.research import ExecuteEvent, ExecuteRequest, Variable

# 9 节执行实验的固定顺序
SECTION_NAMES: tuple[str, ...] = (
    "section_intro",
    "section_lit",
    "section_institution",
    "section_data",
    "section_strategy",
    "section_results",
    "section_robust",
    "section_conclusion",
    "section_refs",
)

# 9 节对应的标题（用于 paper.pdf 拼装时的章节标题）
SECTION_TITLES: dict[str, str] = {
    "section_intro": "1. 引言",
    "section_lit": "2. 文献综述",
    "section_institution": "3. 制度背景",
    "section_data": "4. 数据",
    "section_strategy": "5. 实证策略",
    "section_results": "6. 主结果",
    "section_robust": "7. 稳健性检验",
    "section_conclusion": "8. 结论",
    "section_refs": "9. 参考文献",
}


# ============== 行为 1: load_inputs ==============


def load_inputs(
    brief_path: Path,
    variables_path: Path,
    design_path: Path,
) -> tuple[str, list[Variable], dict]:
    """读 brief / variables / design 三个文件。

    Returns:
        (brief_text, variables, design_dict)
    """
    brief_text = Path(brief_path).read_text(encoding="utf-8")

    variables_payload = yaml.safe_load(Path(variables_path).read_text(encoding="utf-8"))
    if not isinstance(variables_payload, dict) or "variables" not in variables_payload:
        raise ValueError(f"variables file must contain 'variables' key: {variables_path}")
    raw_vars = variables_payload["variables"]
    variables = [Variable(**v) for v in raw_vars]

    design_dict = json.loads(Path(design_path).read_text(encoding="utf-8"))
    if not isinstance(design_dict, dict):
        raise ValueError(f"design file must be JSON object: {design_path}")

    return brief_text, variables, design_dict


# ============== 行为 2: write_section ==============


def write_section(
    section_index: int,
    content: str,
    topic_slug: str,
    manuscripts_root: Path,
) -> Path:
    """写一节 markdown 到 Manuscripts/{topic}/sections/section_{N}.md。"""
    sections_dir = Path(manuscripts_root) / topic_slug / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)
    path = sections_dir / f"section_{section_index}.md"
    path.write_text(content, encoding="utf-8")
    return path


# ============== 行为 3: render_paper ==============


def render_paper(
    topic_slug: str,
    sections_root: Path,
    manuscripts_root: Path,
) -> Path:
    """拼接 9 节 markdown 渲染成 paper.pdf 落到 Manuscripts/{topic}/paper.pdf。"""
    topic_dir = Path(manuscripts_root) / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    paper_path = topic_dir / "paper.pdf"

    # 拼接所有 section 文件 + 章节标题
    parts: list[str] = [
        f"<html><head><meta charset='utf-8'><title>{topic_slug}</title></head><body>",
        f"<h1 style='text-align:center'>{topic_slug}</h1>",
    ]
    sections_dir = Path(sections_root)
    for idx, sec_name in enumerate(SECTION_NAMES, start=1):
        sec_path = sections_dir / f"section_{idx}.md"
        if sec_path.exists():
            sec_md = sec_path.read_text(encoding="utf-8")
            title = SECTION_TITLES[sec_name]
            parts.append(f"<h2>{title}</h2>")
            # 极简 markdown → HTML：标题/段落
            parts.append(_md_to_html(sec_md))
    parts.append("</body></html>")
    html_doc = "\n".join(parts)

    # 用 weasyprint 渲染
    HTML(string=html_doc).write_pdf(
        str(paper_path),
        stylesheets=[CSS(string="body{font-family: serif; max-width: 800px; margin: 2em auto; line-height: 1.6; padding: 0 1em;} h1,h2{color:#222;}")],
    )
    return paper_path


def _md_to_html(md: str) -> str:
    """极简 markdown → HTML（仅支持 # 标题 + 段落），避免额外依赖。"""
    lines = md.splitlines()
    out: list[str] = []
    in_para = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_para:
                out.append("</p>")
                in_para = False
            continue
        if stripped.startswith("# "):
            if in_para:
                out.append("</p>")
                in_para = False
            out.append(f"<h3>{_escape(stripped[2:].strip())}</h3>")
        elif stripped.startswith("## "):
            if in_para:
                out.append("</p>")
                in_para = False
            out.append(f"<h4>{_escape(stripped[3:].strip())}</h4>")
        else:
            if not in_para:
                out.append("<p>")
                in_para = True
            out.append(_escape(stripped) + " ")
    if in_para:
        out.append("</p>")
    return "\n".join(out)


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ============== 行为 4: write_results ==============


def write_results(
    stats: dict,
    topic: str,
    topic_slug: str,
    results_root: Path,
    model: str = "MiniMax-M3",
    prompt_version: str = "v1",
) -> Path:
    """落盘 Results/{topic}/results.json 含 provenance + stats + generated_at。"""
    topic_dir = Path(results_root) / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    path = topic_dir / "results.json"

    payload = {
        "topic": topic,
        "topic_slug": topic_slug,
        **stats,
        "provenance": {
            "model": model,
            "prompt_version": prompt_version,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


# ============== 行为 5: run_execute_stream ==============


# 默认 prompt loader 工厂：直接 import 已有的 loaders
# 优先 v4 → v3 → v2 → v1 (向后兼容未升级的节, 2026-06-04 L7 调优)
def _default_prompt_loader(section_name: str) -> Callable[[], str]:
    """根据 section_name 返回最新的 prompt loader（v4 → v3 → v2 → v1 fallback）。"""
    for ver in ("v4", "v3", "v2", "v1"):
        try:
            module = __import__(
                f"Program.prompts.execution.{section_name}.{ver}",
                fromlist=[f"load_prompt_{ver}"],
            )
            return getattr(module, f"load_prompt_{ver}")
        except ModuleNotFoundError:
            continue
    raise ModuleNotFoundError(
        f"No prompt loader found for section {section_name} (tried v1-v4)"
    )


def run_execute_stream(
    req: ExecuteRequest,
    manuscripts_root: Path,
    results_root: Path,
    tasks_root: Path,
    prompt_loader: Optional[Callable[[str], Callable[[], str]]] = None,
    chat_completion_fn: Optional[Callable] = None,
) -> Iterator[ExecuteEvent]:
    """SSE 风格 generator：按 spec 顺序 yield ExecuteEvent。

    序列：start → progress×9 → section_done×9 → paper_ready → done
    任意一步异常时 yield error 事件并停止。
    """
    if prompt_loader is None:
        prompt_loader = _default_prompt_loader
    # 注：chat_completion_fn 在循环内通过模块名动态查找，
    # 这样测试可以用 patch('Product.backend.wrapper.execute_service.chat_completion') 替换。
    if chat_completion_fn is None:
        import Product.backend.wrapper.execute_service as _self_module
        chat_completion_fn = lambda messages, **kw: _self_module.chat_completion(
            messages, **kw
        )

    # 1. start
    yield ExecuteEvent(
        event="start",
        stage="loading",
        message="加载输入文件 (brief / variables / design)",
    )

    try:
        # 2. 加载输入
        brief_text, variables, design_dict = load_inputs(
            Path(req.brief_path),
            Path(req.variables_path),
            Path(req.design_path),
        )

        # 3. 9 节写作循环
        sections_dir = Path(manuscripts_root) / req.topic_slug / "sections"
        for idx, sec_name in enumerate(SECTION_NAMES, start=1):
            yield ExecuteEvent(
                event="progress",
                stage=f"section_{idx}",
                message=f"writing section {idx}/9: {sec_name}",
                section_index=idx,
            )
            loader = prompt_loader(sec_name)
            prompt = loader() + "\n\n" + brief_text[:500]
            text, _usage = chat_completion_fn(
                messages=[{"role": "user", "content": prompt}],
                provider_id="minimax",
                model="MiniMax-M3",
                temperature=0.3,
            )
            write_section(
                section_index=idx,
                content=text,
                topic_slug=req.topic_slug,
                manuscripts_root=manuscripts_root,
            )
            yield ExecuteEvent(
                event="section_done",
                stage=f"section_{idx}",
                message=f"section {idx}/9 done: {sec_name}",
                section_index=idx,
                # 推理链可视化（D2）：注入 prompt + 原始 LLM 输出 + 落盘后的最终内容
                prompt=prompt,
                raw_output=text,
                parsed_output=text,
            )

        # 4. 渲染 paper.pdf
        paper_path = render_paper(
            topic_slug=req.topic_slug,
            sections_root=sections_dir,
            manuscripts_root=manuscripts_root,
        )
        yield ExecuteEvent(
            event="paper_ready",
            stage="rendering",
            message="paper.pdf 已落盘",
            paper_pdf_path=str(paper_path),
        )

        # 5. 落盘 results.json（用 design 的 method + stub 提取的 stats 占位）
        stats = {
            "method": design_dict.get("method") or design_dict.get("recommended", ""),
            "n_variables": len(variables),
            "n_sections": 9,
            "topic_slug": req.topic_slug,
        }
        topic_title = design_dict.get("topic", req.topic_slug)
        results_path = write_results(
            stats=stats,
            topic=topic_title,
            topic_slug=req.topic_slug,
            results_root=results_root,
        )
        yield ExecuteEvent(
            event="done",
            stage="complete",
            message="execution 完成",
            results_json_path=str(results_path),
        )

    except Exception as exc:
        yield ExecuteEvent(
            event="error",
            stage="execution",
            message=str(exc),
        )
