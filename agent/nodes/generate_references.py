"""ADR-0009: 参考文献列表生成节点。

在 export_docx 前生成 References 章节，
按学术规范格式化（APA 风格，中英文兼容）。
"""
from __future__ import annotations

from typing import Any, List

from protocols import ReferencesOutput
from state import EconPaperState


def _format_apa(entry: Any) -> str:
    """APA 格式化单条参考文献。

    - 作者 > 3 用 et al.；
    - DOI 拼成 https://doi.org/{doi}；
    - 中文作者原样输出。
    """
    if not isinstance(entry, dict):
        return "Unknown (n.d.)."

    authors = entry.get("authors") or []
    if len(authors) > 3:
        author_str = f"{authors[0]} et al."
    elif authors:
        author_str = ", ".join(str(a) for a in authors)
    else:
        author_str = "Unknown"

    year = entry.get("year", "n.d.")
    title = entry.get("title", "") or ""
    doi = entry.get("doi")

    ref = f"{author_str} ({year}). {title}."
    if doi:
        ref += f" https://doi.org/{doi}"
    return ref


def generate_references(state: EconPaperState) -> ReferencesOutput:
    """生成参考文献列表。

    1. 读 citation_graph（build_citation_graph 节点产出）
    2. 按 (year, title) 升序排序后分配连续引用编号 [1], [2], ...
    3. APA 格式化每条
    4. 返回 references_list

    排序与 build_citation_graph 一致；此处再次排序是防御性措施，
    确保即使 citation_graph.entries 未排序也能产出有序列表。
    """
    graph = state.get("citation_graph") or {}
    raw_entries: List[Any] = graph.get("entries", []) if isinstance(graph, dict) else []

    if not raw_entries:
        return {"references_list": []}

    # 防御性排序：与 build_citation_graph 同样的 (year, title) 升序
    entries = sorted(
        raw_entries,
        key=lambda e: (
            (e.get("year", 0) or 0) if isinstance(e, dict) else 0,
            (e.get("title", "") or "") if isinstance(e, dict) else "",
        ),
    )

    references: List[dict] = []
    for i, entry in enumerate(entries, start=1):
        ref_text = _format_apa(entry)
        references.append(
            {
                "index": i,
                "text": ref_text,
                "doi": entry.get("doi") if isinstance(entry, dict) else None,
                "entry": entry,
            }
        )

    return {"references_list": references}
