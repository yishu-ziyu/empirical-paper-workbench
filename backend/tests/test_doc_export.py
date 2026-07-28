r"""T-10 RED tests for GET /sessions/{id}/doc-export (doc_export router).

契约（任务规格 §T-10）：
- GET /sessions/{id}/doc-export?format=tex|pdf|docx&template=<name>
- format=tex  → 200, body 含 \title{...}, Content-Type: application/x-tex
- format=pdf  → 200, Content-Type: application/pdf（latexmk 不可用 → 503）
- format=docx → 200, docx Content-Type（pandoc 不可用 → 503）
- 未知 format → 400
- session 不存在 → 404
- template 默认 cn_journal
"""
from __future__ import annotations

from pathlib import Path

import pytest

import routers.doc_export  # noqa: F401 — import to trigger _self_register()
from facade import facade


def _inject_session(session_id: str = "doc-export-session") -> str:
    """把一个带 title + 内容章节的 session 直接塞进 facade。"""
    facade.seed_state(
        session_id,
        {
            "title_chapter": {
                "type": "title",
                "title": "教育回报率研究",
                "content": "\\title{教育回报率研究}",
                "status": "generated",
                "versions": ["\\title{教育回报率研究}"],
            },
            "body_chapters": [
                {
                    "type": "intro",
                    "title": "引言",
                    "content": "教育回报是经典议题。",
                    "status": "approved",
                    "versions": ["教育回报是经典议题。"],
                },
            ],
        },
    )
    return session_id


@pytest.fixture
def doc_session():
    sid = _inject_session()
    yield sid
    facade.drop_session(sid)


# ---------------------------------------------------------------------------
# format=tex
# ---------------------------------------------------------------------------
def test_doc_export_tex_returns_latex(doc_session, client):
    """format=tex → 200，body 含 \\title{...}。"""
    resp = client.get(
        f"/sessions/{doc_session}/doc-export",
        params={"format": "tex"},
    )
    assert resp.status_code == 200, resp.text
    assert "\\title{" in resp.text
    assert "教育回报率研究" in resp.text


def test_doc_export_tex_content_type(doc_session, client):
    """format=tex → Content-Type 含 x-tex。"""
    resp = client.get(
        f"/sessions/{doc_session}/doc-export",
        params={"format": "tex"},
    )
    assert resp.status_code == 200
    ctype = resp.headers.get("content-type", "")
    assert "x-tex" in ctype, f"unexpected content-type: {ctype!r}"


# ---------------------------------------------------------------------------
# format=pdf
# ---------------------------------------------------------------------------
def test_doc_export_pdf_returns_file(doc_session, client, monkeypatch, tmp_path):
    """format=pdf，export_docx 返回 pdf_path → 200，Content-Type pdf。"""
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    def fake_export(state):
        return {
            "latex_source": "\\documentclass{article}\\begin{document}\\end{document}",
            "pdf_path": str(pdf),
            "docx_path": None,
            "degraded": False,
        }

    monkeypatch.setattr("facade.export_docx_node", fake_export)
    resp = client.get(
        f"/sessions/{doc_session}/doc-export",
        params={"format": "pdf"},
    )
    assert resp.status_code == 200, resp.text
    assert "pdf" in resp.headers.get("content-type", "").lower()


def test_doc_export_pdf_unavailable_returns_503(doc_session, client, monkeypatch):
    """format=pdf，pdf_path=None（latexmk 不可用）→ 503。"""
    def fake_export(state):
        return {
            "latex_source": "x",
            "pdf_path": None,
            "docx_path": None,
            "degraded": True,
        }

    monkeypatch.setattr("facade.export_docx_node", fake_export)
    resp = client.get(
        f"/sessions/{doc_session}/doc-export",
        params={"format": "pdf"},
    )
    assert resp.status_code == 503


# ---------------------------------------------------------------------------
# format=docx
# ---------------------------------------------------------------------------
def test_doc_export_docx_returns_file(doc_session, client, monkeypatch, tmp_path):
    """format=docx，export_docx 返回 docx_path → 200，docx Content-Type。"""
    docx = tmp_path / "paper.docx"
    docx.write_bytes(b"PK fake docx")

    def fake_export(state):
        return {
            "latex_source": "x",
            "pdf_path": None,
            "docx_path": str(docx),
            "degraded": False,
        }

    monkeypatch.setattr("facade.export_docx_node", fake_export)
    resp = client.get(
        f"/sessions/{doc_session}/doc-export",
        params={"format": "docx"},
    )
    assert resp.status_code == 200, resp.text
    ctype = resp.headers.get("content-type", "").lower()
    assert "wordprocessingml" in ctype or "octet-stream" in ctype or "docx" in ctype


def test_doc_export_docx_unavailable_returns_503(doc_session, client, monkeypatch):
    """format=docx，docx_path=None → 503。"""
    monkeypatch.setattr(
        "facade.export_docx_node",
        lambda state: {
            "latex_source": "x",
            "pdf_path": None,
            "docx_path": None,
            "degraded": True,
        },
    )
    resp = client.get(
        f"/sessions/{doc_session}/doc-export",
        params={"format": "docx"},
    )
    assert resp.status_code == 503


# ---------------------------------------------------------------------------
# 错误处理
# ---------------------------------------------------------------------------
def test_doc_export_unknown_format_returns_400(doc_session, client, monkeypatch):
    """未知 format → 400。"""
    monkeypatch.setattr(
        "facade.export_docx_node",
        lambda state: {
            "latex_source": "x",
            "pdf_path": None,
            "docx_path": None,
            "degraded": True,
        },
    )
    resp = client.get(
        f"/sessions/{doc_session}/doc-export",
        params={"format": "xyz"},
    )
    assert resp.status_code == 400


def test_doc_export_session_not_found_returns_404(client):
    """session 不存在 → 404。"""
    resp = client.get(
        "/sessions/nonexistent-session/doc-export",
        params={"format": "tex"},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# template 参数
# ---------------------------------------------------------------------------
def test_doc_export_passes_template_to_state(doc_session, client, monkeypatch):
    """template 查询参数写入 state.export_template 传给 export_docx。"""
    captured = {}

    def fake_export(state):
        captured["export_template"] = state.get("export_template")
        return {
            "latex_source": "\\title{T}",
            "pdf_path": None,
            "docx_path": None,
            "degraded": True,
        }

    monkeypatch.setattr("facade.export_docx_node", fake_export)
    resp = client.get(
        f"/sessions/{doc_session}/doc-export",
        params={"format": "tex", "template": "master_thesis"},
    )
    assert resp.status_code == 200
    assert captured["export_template"] == "master_thesis"


def test_doc_export_default_template_is_cn_journal(doc_session, client, monkeypatch):
    """未传 template 时默认 cn_journal。"""
    captured = {}

    def fake_export(state):
        captured["export_template"] = state.get("export_template")
        return {
            "latex_source": "\\title{T}",
            "pdf_path": None,
            "docx_path": None,
            "degraded": True,
        }

    monkeypatch.setattr("facade.export_docx_node", fake_export)
    resp = client.get(
        f"/sessions/{doc_session}/doc-export",
        params={"format": "tex"},
    )
    assert resp.status_code == 200
    assert captured["export_template"] == "cn_journal"
