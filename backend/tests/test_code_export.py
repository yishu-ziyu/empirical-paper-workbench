"""T-09 / GS-E5 tests for GET /sessions/{id}/code-export and POST /translate-code.

契约：
1. GET /sessions/{id}/code-export?format=py → 返回 .py 文件
2. GET /sessions/{id}/code-export?format=do → 返回 .do 文件（Stata）
3. GET /sessions/{id}/code-export?format=R → 返回 .R 文件
4. GET /sessions/{id}/code-export?format=m → 返回 .m 文件（EViews）
5. Content-Disposition: attachment; filename="analysis.<ext>"
6. 未知 session_id → 404
7. 不支持的 format → 400
8. session 无 code_translations 且无真实方向列 / 未写章 → 404（不编造 y ~ treat）
   有 outcome+treatment 或已 generate 时 GET 可先跑 translate_code
9. POST /sessions/{id}/translate-code → 200 + 写入 code_translations
"""
from __future__ import annotations

# Importing the code_export router triggers its self-registration on main.app.
import routers.code_export  # noqa: F401
from facade import facade

from conftest import make_write_ready_state


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


def test_export_empty_translations_without_direction_returns_404(client):
    """No translations and no real direction columns: 404, do not invent y ~ treat."""
    sid = _seed_session_without_translations()
    try:
        resp = client.get(f"/sessions/{sid}/code-export", params={"format": "py"})
        assert resp.status_code == 404
        assert "y ~ treat" not in resp.text
        state = facade.get_state(sid)
        assert not (state.get("code_translations") or [])
    finally:
        facade.drop_session(sid)


def test_export_question_only_direction_does_not_autofill(client):
    """A question without outcome+treatment is not a real spec."""
    import uuid

    sid = f"test-hollow-direction-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        {"research_direction": {"question": "something about crime", "method": "did"}},
    )
    try:
        resp = client.get(f"/sessions/{sid}/code-export", params={"format": "do"})
        assert resp.status_code == 404
        state = facade.get_state(sid)
        assert not (state.get("code_translations") or [])
        assert "y ~ treat" not in (resp.text or "")
    finally:
        facade.drop_session(sid)


def test_get_do_and_R_without_prior_post(client):
    """Named outcome+treatment: GET do|R fills translations on first download."""
    import uuid

    sid = f"test-lazy-translate-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/user.csv",
            "research_direction": {
                "question": "post on l_homicide",
                "dv": "l_homicide",
                "iv": "post",
                "controls": ["l_prison"],
                "method": "did",
                "id_col": "sid",
                "time_col": "year",
            },
            "body_chapters": [
                {"type": "results", "content": "no python fences in this chapter"}
            ],
        },
    )
    try:
        do = client.get(f"/sessions/{sid}/code-export", params={"format": "do"})
        assert do.status_code == 200, do.text
        assert "xtreg" in do.text
        assert "reghdfe" in do.text
        assert "l_homicide" in do.text
        assert "analysis.do" in do.headers.get("content-disposition", "")
        assert "y ~ treat" not in do.text
        assert "无 Python 代码可翻译" not in do.text

        r_resp = client.get(f"/sessions/{sid}/code-export", params={"format": "R"})
        assert r_resp.status_code == 200, r_resp.text
        assert "feols" in r_resp.text
        assert "felm" in r_resp.text
        assert "l_homicide" in r_resp.text
        assert "analysis.R" in r_resp.headers.get("content-disposition", "")
        assert "无 Python 代码可翻译" not in r_resp.text
    finally:
        facade.drop_session(sid)


def test_post_translate_code_fills_export(client):
    """POST /translate-code writes code_translations; GET do|R return text."""
    import uuid

    sid = f"test-translate-hook-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/user.csv",
            "research_direction": {
                "question": "post on l_homicide",
                "dv": "l_homicide",
                "iv": "post",
                "controls": ["l_prison"],
                "method": "did",
                "id_col": "sid",
                "time_col": "year",
            },
            "body_chapters": [
                {"type": "results", "content": "no python fences in this chapter"}
            ],
        },
    )
    try:
        posted = client.post(f"/sessions/{sid}/translate-code")
        assert posted.status_code == 200, posted.text
        body = posted.json()
        assert body["ok"] is True
        langs = {t["lang"] for t in body["code_translations"]}
        assert langs == {"py", "stata", "r", "eviews"}

        do = client.get(f"/sessions/{sid}/code-export", params={"format": "do"})
        assert do.status_code == 200, do.text
        assert "xtreg" in do.text
        assert "reghdfe" in do.text
        assert "l_homicide" in do.text
        assert "analysis.do" in do.headers.get("content-disposition", "")
        assert "无 Python 代码可翻译" not in do.text

        r_resp = client.get(f"/sessions/{sid}/code-export", params={"format": "R"})
        assert r_resp.status_code == 200, r_resp.text
        assert "feols" in r_resp.text
        assert "felm" in r_resp.text
        assert "l_homicide" in r_resp.text
        assert "analysis.R" in r_resp.headers.get("content-disposition", "")
        assert "无 Python 代码可翻译" not in r_resp.text
    finally:
        facade.drop_session(sid)


def test_after_generate_get_do_and_R_return_takeable_files(client):
    """After generate, GET do|R is 200 with runnable Stata/R, not empty stubs."""
    import uuid

    sid = f"test-after-generate-{uuid.uuid4()}"
    facade.seed_state(sid, make_write_ready_state())
    try:
        gen = client.post(
            f"/sessions/{sid}/generate-chapter",
            json={"chapter": {"type": "intro", "title": "引言"}},
        )
        assert gen.status_code == 200, gen.text

        do = client.get(f"/sessions/{sid}/code-export", params={"format": "do"})
        assert do.status_code == 200, do.text
        assert "analysis.do" in do.headers.get("content-disposition", "")
        assert "import delimited" in do.text
        assert "regress " in do.text
        assert "income" in do.text
        assert "age" in do.text
        assert "y ~ treat" not in do.text
        assert "无 Python 代码可翻译" not in do.text
        assert "无 Python 代码" not in do.text

        r_resp = client.get(f"/sessions/{sid}/code-export", params={"format": "R"})
        assert r_resp.status_code == 200, r_resp.text
        assert "analysis.R" in r_resp.headers.get("content-disposition", "")
        assert "read.csv" in r_resp.text
        assert "lm(" in r_resp.text
        assert "income" in r_resp.text
        assert "age" in r_resp.text
        assert "无 Python 代码可翻译" not in r_resp.text
    finally:
        facade.drop_session(sid)


def test_get_does_not_return_empty_stub_files(client):
    """Persisted placeholder translations are not served as 200 downloads."""
    import uuid

    sid = f"test-stub-not-served-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        {
            "code_translations": [
                {
                    "lang": "stata",
                    "code": "* Auto-generated Stata script (econpaper T-09)\n* 无 Python 代码可翻译\n",
                    "filename": "analysis.do",
                },
                {
                    "lang": "r",
                    "code": "# Auto-generated R script (econpaper T-09)\n# 无 Python 代码可翻译\n",
                    "filename": "analysis.R",
                },
            ]
        },
    )
    try:
        do = client.get(f"/sessions/{sid}/code-export", params={"format": "do"})
        assert do.status_code == 404, do.text
        assert "无 Python 代码可翻译" not in do.text
        r_resp = client.get(f"/sessions/{sid}/code-export", params={"format": "R"})
        assert r_resp.status_code == 404, r_resp.text
    finally:
        facade.drop_session(sid)


def test_get_replaces_stubs_when_direction_names_columns(client):
    """Stubs + a real spec → GET rebuilds takeable Stata/R."""
    import uuid

    sid = f"test-replace-stubs-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/user.csv",
            "research_direction": {"dv": "income", "iv": "age", "method": "ols"},
            "code_translations": [
                {
                    "lang": "stata",
                    "code": "* 无 Python 代码可翻译\n",
                    "filename": "analysis.do",
                },
                {
                    "lang": "r",
                    "code": "# 无 Python 代码可翻译\n",
                    "filename": "analysis.R",
                },
            ],
        },
    )
    try:
        do = client.get(f"/sessions/{sid}/code-export", params={"format": "do"})
        assert do.status_code == 200, do.text
        assert "regress " in do.text
        assert "income" in do.text
        assert "无 Python 代码可翻译" not in do.text
        r_resp = client.get(f"/sessions/{sid}/code-export", params={"format": "R"})
        assert r_resp.status_code == 200, r_resp.text
        assert "lm(" in r_resp.text
        assert "无 Python 代码可翻译" not in r_resp.text
    finally:
        facade.drop_session(sid)


def test_openapi_lists_post_translate_code(client):
    """Published app contract includes POST /sessions/{id}/translate-code."""
    spec = client.app.openapi()
    path = spec["paths"].get("/sessions/{session_id}/translate-code") or {}
    assert "post" in path


def test_export_default_format_is_py(client):
    """未指定 format 时默认 py。"""
    sid = _seed_session_with_translations()
    resp = client.get(f"/sessions/{sid}/code-export")
    assert resp.status_code == 200
    assert "import pandas" in resp.text
