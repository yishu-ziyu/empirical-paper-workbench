from protocols import GenerateTitleOutput
from state import EconPaperState


def call_llm(prompt: str) -> str:
    """调 LLM 生成标题。

    走 ``llm.call_llm``（运行时 MiniMax；pytest 为占位）。
    测试通过 ``monkeypatch.setattr(nodes.generate_title, "call_llm", ...)``
    替换为 fake，故必须是模块级函数。
    """
    from llm.call_llm import call_llm as unified_call

    return unified_call(prompt, node_type="title")


def _clean_title(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return "未命名论文"
    first = text.splitlines()[0].strip().strip("\"'`“”‘’").strip()
    if first.lower().startswith("title:"):
        first = first[6:].strip()
    if first.startswith("\\title{") and first.endswith("}"):
        first = first[7:-1].strip()
    first = first.strip("*").strip()
    return first[:80] or "未命名论文"


def generate_title(state: EconPaperState) -> GenerateTitleOutput:
    """调 LLM 生成 ``\\title{...}``，写入 state.title_chapter。"""
    datasets = state.get("uploaded_datasets", [])
    data_summary = f"数据集 {len(datasets)} 个"
    if datasets:
        ds = datasets[0]
        cols = ds.get("columns")
        if cols:
            data_summary += f"，列：{cols}"

    rd = state.get("research_direction")
    if isinstance(rd, dict) and rd.get("question"):
        data_summary += (
            f"。研究问题：{rd.get('question')}。"
            f"方法：{rd.get('method') or ''}"
        )

    estimate = state.get("estimate") or {}
    has_estimate = (
        isinstance(estimate, dict)
        and estimate.get("produced_by") == "estimate"
        and bool(estimate.get("status"))
    )
    if has_estimate:
        data_summary += (
            f"。估计已完成，方法 {estimate.get('method') or ''}，"
            f"关注变量 {estimate.get('treatment') or ''}。"
            "标题可以写研究问题与估计方向，不要点名估计里没有的发现。"
        )
    else:
        data_summary += (
            "。估计尚未完成。标题只写研究问题与方法方向，"
            "不要点名任何发现、显著性或系数。"
        )

    prompt = (
        "根据以下信息生成一个经济学论文标题。"
        "只输出标题本身，不要 LaTeX，不要引号，不要解释。"
        f"中文，30 字以内。{data_summary}"
    )
    title = _clean_title(call_llm(prompt))

    chapter = {
        "type": "title",
        "title": title,
        "content": f"\\title{{{title}}}",
        "status": "done",
    }
    return {"title_chapter": chapter}
