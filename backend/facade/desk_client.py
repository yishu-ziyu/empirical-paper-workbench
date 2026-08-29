"""Desk 能力客户端（facade 收敛 Task 1 / Task 5）。

职责一句话：**封装 agent.desk 的各路助手（问题收敛讨论 / 设计对话 / 语音识别 / 语音合成），
供 AgentFacade 对外复用，并统一把"agent 模块缺失"投影成 HTTP 503。**
"""
from __future__ import annotations

from typing import Optional

from fastapi import HTTPException


def discuss_desk(notes: str, turns: Optional[list[dict]] = None) -> dict:
    """空桌讨论：把乱想法收敛成研究问题；LLM 通道失败时启发式降级。"""
    try:
        from agent.desk.socratic import discuss
    except Exception as exc:  # pragma: no cover - agent 模块缺失
        raise HTTPException(
            status_code=503, detail=f"desk discuss unavailable: {exc}"
        ) from exc
    return discuss(notes, turns or [])


def design_chat_desk(notes: str, turns: list[dict], columns: list) -> dict:
    """设计对话：把念头聊成研究设定卡（dv/iv/controls/method 逐轮抽齐）。

    异常直接向上抛（调用方 desk.py 把 HTTPException 透传、其他异常转 502），
    与既有路由的降级语义保持一致。
    """
    from agent.desk.design_chat import design_chat as _design_chat

    return _design_chat(notes, turns, columns)


def transcribe_desk(raw: bytes, filename: str = "clip.webm") -> dict:
    """语音转写：STT 通道返回 {text, source}；agent 模块缺失时 503。"""
    try:
        from agent.desk.stepfun_asr import transcribe_upload
    except Exception as exc:  # pragma: no cover - agent 模块缺失
        raise HTTPException(
            status_code=503, detail=f"desk asr unavailable: {exc}"
        ) from exc
    text = transcribe_upload(raw, filename=filename)
    return {"text": text, "source": "stepfun"}


def speak_desk(text: str) -> bytes:
    """语音合成：TTS 通道返回音频字节；agent 模块缺失时 503。"""
    try:
        from agent.desk.minimax_tts import synthesize
    except Exception as exc:  # pragma: no cover - agent 模块缺失
        raise HTTPException(
            status_code=503, detail=f"desk tts unavailable: {exc}"
        ) from exc
    return synthesize(text)