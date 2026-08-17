from desk.minimax_tts import _tts_config
from desk.stepfun_asr import parse_asr_sse


def test_parse_asr_sse_done_event():
    raw = (
        "event: transcript\n"
        'data: {"type":"transcript.text.delta","text":"导"}\n'
        "\n"
        'data: {"type":"transcript.text.done","text":"导师让我用 CHARLS 做点养老的"}\n'
        "\n"
    )
    assert parse_asr_sse(raw) == "导师让我用 CHARLS 做点养老的"


def test_parse_asr_sse_error():
    try:
        parse_asr_sse('data: {"type":"error","message":"bad audio"}\n\n')
    except RuntimeError as exc:
        assert "bad audio" in str(exc)
    else:
        raise AssertionError("expected error")


def test_tts_config_reads_minimax_host(monkeypatch):
    monkeypatch.setenv("MINIMAX_API_KEY", "sk-test")
    monkeypatch.setenv("MINIMAX_OPENAI_BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setenv("MINIMAX_TTS_VOICE_ID", "shangqiuzi_v3_20260717")
    key, url, voice, model = _tts_config()
    assert key == "sk-test"
    assert url.endswith("/v1/t2a_v2")
    assert voice == "shangqiuzi_v3_20260717"
    assert model
