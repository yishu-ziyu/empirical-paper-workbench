"""MiniMax t2a。接法对齐 AI组件工作流库 minimax-voice-clone-pipeline。"""
from __future__ import annotations

import json
import os

from llm.ssot import load_ssot

DEFAULT_VOICE_ID = "shangqiuzi_v3_20260717"
DEFAULT_MODEL = "speech-2.8-hd"
DEFAULT_T2A_URL = "https://api.minimaxi.com/v1/t2a_v2"


def _tts_config() -> tuple[str, str, str, str]:
    load_ssot()
    key = (os.environ.get("MINIMAX_API_KEY") or os.environ.get("MINIMAX_TOKEN_PLAN_KEY") or "").strip()
    base = (os.environ.get("MINIMAX_OPENAI_BASE_URL") or "https://api.minimaxi.com/v1").rstrip("/")
    url = DEFAULT_T2A_URL
    if base.endswith("/v1"):
        url = f"{base[:-3]}/v1/t2a_v2"
    voice = os.environ.get("MINIMAX_TTS_VOICE_ID") or DEFAULT_VOICE_ID
    model = os.environ.get("MINIMAX_TTS_MODEL") or DEFAULT_MODEL
    return key, url, voice, model


def tts_available() -> bool:
    key, _, _, _ = _tts_config()
    return bool(key)


def synthesize(text: str) -> bytes:
    import urllib.error
    import urllib.request

    cleaned = (text or "").strip()
    if not cleaned:
        raise RuntimeError("empty text")
    key, url, voice, model = _tts_config()
    if not key:
        raise RuntimeError("MINIMAX_API_KEY missing")
    payload = {
        "model": model,
        "text": cleaned[:500],
        "stream": False,
        "voice_setting": {"voice_id": voice, "speed": 0.96, "vol": 1.0, "pitch": 0},
        "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1},
        "output_format": "hex",
        "language_boost": "Chinese",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:240]
        raise RuntimeError(f"tts HTTP {exc.code}: {detail}") from exc
    status = (body.get("base_resp") or {}).get("status_code")
    if status not in (None, 0):
        raise RuntimeError(f"tts status {status}")
    hex_audio = ((body.get("data") or {}).get("audio") or "")
    if not isinstance(hex_audio, str) or len(hex_audio) < 20:
        raise RuntimeError("tts empty audio")
    return bytes.fromhex(hex_audio)
