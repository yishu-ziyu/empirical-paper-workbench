from protocols import GenerateTitleOutput
from state import EconPaperState


def call_llm(prompt: str) -> str:
    """调 LLM 生成标题。

    生产环境接 langchain-anthropic；开发阶段返回占位标题。
    测试通过 ``monkeypatch.setattr(nodes.generate_title, "call_llm", ...)``
    替换为 fake，故必须是模块级函数。
    """
    return "Placeholder Title from LLM"


def generate_title(state: EconPaperState) -> GenerateTitleOutput:
    """调 LLM 生成 ``\\title{...}``，写入 state.title_chapter。"""
    datasets = state.get("uploaded_datasets", [])
    data_summary = f"数据集 {len(datasets)} 个"
    if datasets:
        ds = datasets[0]
        cols = ds.get("columns")
        if cols:
            data_summary += f"，列：{cols}"

    prompt = f"根据以下数据生成一个经济学论文标题（中文，30 字以内）：{data_summary}"
    title = call_llm(prompt)

    chapter = {
        "type": "title",
        "title": title,
        "content": f"\\title{{{title}}}",
        "status": "done",
    }
    return {"title_chapter": chapter}
