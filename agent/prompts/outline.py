"""Outline 生成 prompt 模板 (T-06)。

把研究方向 dict 渲染成给 LLM 的 prompt。节点层调 ``call_llm(prompt)``，
测试通过 monkeypatch ``nodes.generate_outline.call_llm`` 替换，故此模块
保持纯函数、无副作用。
"""
from __future__ import annotations

from typing import Any


def build_outline_prompt(rd: Any) -> str:
    """把研究方向 dict 渲染为 outline 生成 prompt。

    ``rd`` 期望是 {question, dv, iv, controls, method, template}；若为空或
    非字典，字段降级为空串，保证 prompt 构造不抛异常。
    """
    if not isinstance(rd, dict):
        rd = {}

    question = rd.get("question", "")
    dv = rd.get("dv", "")
    iv = rd.get("iv", "")
    controls = rd.get("controls", "")
    method = rd.get("method", "")
    template = rd.get("template", "")

    return (
        f"研究问题：{question}\n"
        f"因变量：{dv}\n"
        f"自变量：{iv}\n"
        f"控制变量：{controls}\n"
        f"计量方法：{method}\n"
        f"论文模板：{template}\n\n"
        "请为以下经济学论文生成 6 章大纲："
        "引言 / 文献综述 / 数据描述 / 方法 / 结果 / 结论。"
        "每章给出标题与 2-3 条要点。"
    )
