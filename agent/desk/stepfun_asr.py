"""阶跃星辰 ASR。接法对齐 AI组件工作流库 + Kairos SpeechASRRouter。"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
from pathlib import Path

from ..llm.ssot import load_ssot

DEFAULT_ASR_URL = "https://api.stepfun.com/step_plan/v1/audio/asr/sse"
DEFAULT_ASR_MODEL = "stepaudio-2.5-asr"


def _asr_config() -> tuple[str, str, str]:
    load_ssot()
    key = (
        os.environ.get("STEP_API_KEY")
        or os.environ.get("STEPFUN_API_KEY")
        or ""
    ).strip()
    base = (
        os.environ.get("STEPFUN_ASR_BASE")
        or os.environ.get("STEPFUN_STEP_PLAN_BASE")
        or "https://api.stepfun.com/step_plan/v1"
    ).rstrip("/")
    model = os.environ.get("STEPFUN_ASR_MODEL") or DEFAULT_ASR_MODEL
    url = f"{base}/audio/asr/sse" if not base.endswith("/audio/asr/sse") else base
    return key, url, model


def asr_available() -> bool:
    key, _, _ = _asr_config()
    return bool(key)


def audio_to_pcm16_16k(raw: bytes, suffix: str = ".webm") -> bytes:
    if not raw:
        raise RuntimeError("empty audio")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"in{suffix}"
        src.write_bytes(raw)
        proc = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(src),
                "-f",
                "s16le",
                "-acodec",
                "pcm_s16le",
                "-ac",
                "1",
                "-ar",
                "16000",
                "pipe:1",
            ],
            check=False,
            capture_output=True,
        )
    if proc.returncode != 0 or not proc.stdout:
        detail = (proc.stderr or b"").decode("utf-8", errors="replace")[:200]
        raise RuntimeError(f"ffmpeg failed: {detail}")
    return proc.stdout


def parse_asr_sse(raw: str) -> str:
    text = ""
    for block in raw.replace("\r\n", "\n").split("\n\n"):
        payload_lines = []
        for line in block.split("\n"):
            if line.startswith("data:"):
                payload_lines.append(line[5:].lstrip())
        if not payload_lines:
            continue
        try:
            obj = json.loads("\n".join(payload_lines))
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if obj.get("type") == "error":
            raise RuntimeError(str(obj.get("message") or "asr error"))
        if obj.get("type") == "transcript.text.done":
            piece = str(obj.get("text") or "").strip()
            if piece:
                return piece
        if isinstance(obj.get("text"), str) and obj["text"].strip():
            text = obj["text"].strip()
    if text:
        return text
    raise RuntimeError("asr empty")


def transcribe_pcm16(pcm: bytes, language: str = "zh") -> str:
    import urllib.error
    import urllib.request

    key, url, model = _asr_config()
    if not key:
        raise RuntimeError("STEP_API_KEY missing")
    body = json.dumps(
        {
            "audio": {
                "data": base64.b64encode(pcm).decode("ascii"),
                "input": {
                    "transcription": {
                        "language": language,
                        "model": model,
                        "enable_itn": True,
                        "enable_timestamp": False,
                    },
                    "format": {
                        "type": "pcm",
                        "codec": "pcm_s16le",
                        "rate": 16000,
                        "bits": 16,
                        "channel": 1,
                    },
                },
            }
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:240]
        raise RuntimeError(f"asr HTTP {exc.code}: {detail}") from exc
    return parse_asr_sse(raw)


def transcribe_upload(raw: bytes, filename: str = "clip.webm", language: str = "zh") -> str:
    suffix = Path(filename).suffix or ".webm"
    pcm = audio_to_pcm16_16k(raw, suffix=suffix)
    return transcribe_pcm16(pcm, language=language)
