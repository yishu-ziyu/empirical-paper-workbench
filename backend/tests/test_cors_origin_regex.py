"""CORS_ORIGIN_REGEX is not a production default for every localhost port."""

from config import _LOCAL_ORIGIN_REGEX, _cors_origin_regex


def test_cors_origin_regex_none_when_debug_false(monkeypatch):
    monkeypatch.delenv("CORS_ORIGIN_REGEX", raising=False)
    monkeypatch.setenv("DEBUG", "false")
    assert _cors_origin_regex() is None


def test_cors_origin_regex_localhost_when_debug_true(monkeypatch):
    monkeypatch.delenv("CORS_ORIGIN_REGEX", raising=False)
    monkeypatch.setenv("DEBUG", "true")
    assert _cors_origin_regex() == _LOCAL_ORIGIN_REGEX


def test_cors_origin_regex_explicit_env(monkeypatch):
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("CORS_ORIGIN_REGEX", r"^https://app.example$")
    assert _cors_origin_regex() == r"^https://app.example$"
