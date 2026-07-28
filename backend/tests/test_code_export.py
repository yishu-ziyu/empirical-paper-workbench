"""T-09 RED tests for GET /sessions/{id}/code-export?format=py|do|R|m.

契约：
1. GET /sessions/{id}/code-export?format=py → 返回 .py 文件
2. GET /sessions/{id}/code-export?format=do → 返回 .do 文件（Stata）
3. GET /sessions/{id}/code-export?format=R → 返回 .R 文件
4. GET /sessions/{id}/code-export?format=m → 返回 .m 文件（EViews）
5. Content-Disposition: attachment; filename="analysis.<ext>"
6. 未知 session_id → 404
7. 不支持的 format → 400
8. session 无 code_translations → 404（提示先跑翻译）
"""
from __future__ import annotations

# Importing the code_export router triggers its self-registration on main.app.
import routers.code_export  # noqa: F401
from facade import facade


def _seed_session_with_translations() -> str:
    """Seed a session with code_translations for all 4 langs."""
    import uuid

    sid = f"test-code-export-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        {
            "code_translations": [
                {
                    "lang": "py",
                    "code": "import pandas as pd\ndf = pd.read_csv('data.csv')\n",
                    "filename": "analysis.py",
                },
                {
                    "lang": "stata",
                    "code": "import delimited \"data.csv\", clear\n",
                    "filename": "analysis.do",
                },
                {
                    "lang": "r",
                    "code": "df <- read.csv('data.csv')\n",
                    "filename": "analysis.R",
                },
                {
                    "lang": "eviews",
                    "code": "import data.csv\n",
                    "filename": "analysis.m",
                },
            ]
        },
    )
    return sid


def _seed_session_without_translations() -> str:
    """Seed a session that has no code_translations."""
    import uuid

    sid = f"test-no-translations-{uuid.uuid4()}"
    facade.seed_state(sid, {})
    return sid


# ---------------------------------------------------------------------------
# 4 种格式下载
# ---------------------------------------------------------------------------
def test_export_py_format(client):
    """GET ?format=py 返回 Python 代码。"""
    sid = _seed_session_with_translations()
    resp = client.get(f"/sessions/{sid}/code-export", params={"format": "py"})
    assert resp.status_code == 200, resp.text
    assert "import pandas" in resp.text
    assert "analysis.py" in resp.headers.get("content-disposition", "")


def test_export_do_format(client):
    """GET ?format=do 返回 Stata 代码。"""
    sid = _seed_session_with_translations()
    resp = client.get(f"/sessions/{sid}/code-export", params={"format": "do"})
    assert resp.status_code == 200, resp.text
    assert "import delimited" in resp.text
    assert "analysis.do" in resp.headers.get("content-disposition", "")


def test_export_R_format(client):
    """GET ?format=R 返回 R 代码。"""
    sid = _seed_session_with_translations()
    resp = client.get(f"/sessions/{sid}/code-export", params={"format": "R"})
    assert resp.status_code == 200, resp.text
    assert "read.csv" in resp.text
    assert "analysis.R" in resp.headers.get("content-disposition", "")


def test_export_m_format(client):
    """GET ?format=m 返回 EViews 代码。"""
    sid = _seed_session_with_translations()
    resp = client.get(f"/sessions/{sid}/code-export", params={"format": "m"})
    assert resp.status_code == 200, resp.text
    assert "import" in resp.text.lower()
    assert "analysis.m" in resp.headers.get("content-disposition", "")


# ---------------------------------------------------------------------------
# Content-Disposition
# ---------------------------------------------------------------------------
def test_export_attachment_header(client):
    """响应带 Content-Disposition: attachment。"""
    sid = _seed_session_with_translations()
    resp = client.get(f"/sessions/{sid}/code-export", params={"format": "py"})
    assert resp.status_code == 200
    cd = resp.headers.get("content-disposition", "")
    assert "attachment" in cd.lower()


# ---------------------------------------------------------------------------
# 错误处理
# ---------------------------------------------------------------------------
def test_export_unknown_session_returns_404(client):
    """未知 session_id 返回 404。"""
    resp = client.get(
        "/sessions/no-such-session/code-export",
        params={"format": "py"},
    )
    assert resp.status_code == 404


def test_export_unsupported_format_returns_400(client):
    """不支持的 format 返回 400。"""
    sid = _seed_session_with_translations()
    resp = client.get(
        f"/sessions/{sid}/code-export",
        params={"format": "julia"},
    )
    assert resp.status_code == 400


def test_export_no_translations_returns_404(client):
    """session 无 code_translations 时返回 404 + 提示。"""
    sid = _seed_session_without_translations()
    resp = client.get(f"/sessions/{sid}/code-export", params={"format": "py"})
    assert resp.status_code == 404


def test_export_default_format_is_py(client):
    """未指定 format 时默认 py。"""
    sid = _seed_session_with_translations()
    resp = client.get(f"/sessions/{sid}/code-export")
    assert resp.status_code == 200
    assert "import pandas" in resp.text
