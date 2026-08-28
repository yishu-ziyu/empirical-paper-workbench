"""T-09 RED tests for translate_code 节点.

契约：
1. translate_code(state) 从 body_chapters 提取 Python 代码块（```python）
2. 从 cleaning_report.audit.final_python 读取清洗 audit 脚本（若存在）
3. 翻译成 3 种格式：Stata (.do) / R (.R) / EViews (.m)
4. 返回 {"code_translations": [{"lang", "code", "filename"}, ...]}
5. 翻译器内置关键词映射（pandas/statsmodels 常用操作）
6. 未知 Python 代码不报错（降级保留为注释）
7. 空 state（无 body_chapters / cleaning_report）返回 4 条空翻译（py/do/R/m）
"""
from __future__ import annotations

from cleaning.audit import AuditStep
from nodes.translate_code import translate_code

from conftest import make_state


# ---------------------------------------------------------------------------
# 辅助：构造测试 state
# ---------------------------------------------------------------------------
def _state_with_chapters_python() -> dict:
    """构造一个 body_chapters 中带 Python 代码块的 state。"""
    body_chapters = [
        {
            "type": "results",
            "title": "结果",
            "content": (
                "# 结果章节\n\n"
                "下面是基准回归代码：\n\n"
                "```python\n"
                "import pandas as pd\n"
                "import statsmodels.api as sm\n"
                "df = pd.read_csv('data.csv')\n"
                "X = df[['educ', 'experience']]\n"
                "y = df['wage']\n"
                "X = sm.add_constant(X)\n"
                "model = sm.OLS(y, X).fit()\n"
                "print(model.summary())\n"
                "```\n"
            ),
            "status": "approved",
        }
    ]
    return make_state(body_chapters=body_chapters)


_UPLOAD_CLEANING_NAMES = (
    "profiling",
    "merge",
    "missing",
    "outliers",
    "transform",
    "filter",
    "balance",
)


def _upload_cleaning_report(tmp_path, csv_name: str = "course-panel.csv") -> tuple[dict, str]:
    """Seed cleaning_report the way POST /upload's AuditStep writes it.

    clean.py is ``df = pd.read_csv(DATA_PATH)`` plus step comments — not a
    regression script, and not the older dropna fixture.
    """
    csv_path = tmp_path / csv_name
    csv_path.write_text(
        "id,year,income,age\n1,2010,100,30\n2,2011,110,31\n",
        encoding="utf-8",
    )
    prior = [
        {"name": name, "status": "success", "report": {}}
        for name in _UPLOAD_CLEANING_NAMES
    ]
    _, audit_report = AuditStep().run(
        [{"path": str(csv_path)}],
        {"workspace": str(tmp_path), "steps": prior},
    )
    return (
        {
            "steps": prior
            + [{"name": "audit", "status": "success", "report": audit_report}]
        },
        str(csv_path),
    )


def _column_guessed_id_year() -> list[dict]:
    """set_direction CSV-guess degradations for columns named id and year."""
    return [
        {
            "node": "set_direction",
            "reason": "column_guessed",
            "field": "id_col",
            "value": "id",
            "visible": True,
        },
        {
            "node": "set_direction",
            "reason": "column_guessed",
            "field": "time_col",
            "value": "year",
            "visible": True,
        },
    ]


def _state_with_cleaning_audit(tmp_path) -> dict:
    """构造一个带 cleaning_report.steps[7] (audit) 的 state（clean.py 文件存在）。"""
    clean_py = tmp_path / "clean.py"
    clean_py.write_text(
        'import pandas as pd\n'
        'df = pd.read_csv("raw.csv")\n'
        'df = df.dropna()\n'
        'df.describe()\n',
        encoding="utf-8",
    )
    return make_state(
        cleaning_report={
            "steps": [
                {"name": "profiling", "status": "success", "report": {}},
                {"name": "merge", "status": "success", "report": {}},
                {"name": "missing", "status": "success", "report": {}},
                {"name": "outliers", "status": "success", "report": {}},
                {"name": "transform", "status": "success", "report": {}},
                {"name": "filter", "status": "success", "report": {}},
                {"name": "balance", "status": "success", "report": {}},
                {
                    "name": "audit",
                    "status": "success",
                    "report": {
                        "clean_py": str(clean_py),
                        "clean_do": str(tmp_path / "clean.do"),
                    },
                },
            ]
        }
    )


# ---------------------------------------------------------------------------
# 基本契约
# ---------------------------------------------------------------------------
def test_translate_code_returns_code_translations_key():
    """返回 dict 必须含 code_translations 键。"""
    result = translate_code({})
    assert "code_translations" in result
    assert isinstance(result["code_translations"], list)


def test_translate_code_empty_state_returns_four_langs():
    """空 state 仍返回 4 条翻译（py / do / R / m）。"""
    result = translate_code({})
    translations = result["code_translations"]
    assert len(translations) == 4
    langs = {t["lang"] for t in translations}
    assert langs == {"py", "stata", "r", "eviews"}


def test_translate_code_each_entry_has_required_fields():
    """每条翻译必须有 lang / code / filename 三字段。"""
    result = translate_code({})
    for t in result["code_translations"]:
        assert "lang" in t
        assert "code" in t
        assert "filename" in t


def test_translate_code_filename_extensions():
    """每种语言对应正确的文件扩展名。"""
    result = translate_code({})
    by_lang = {t["lang"]: t["filename"] for t in result["code_translations"]}
    assert by_lang["py"].endswith(".py")
    assert by_lang["stata"].endswith(".do")
    assert by_lang["r"].endswith(".R")
    assert by_lang["eviews"].endswith(".m")


# ---------------------------------------------------------------------------
# Python 代码收集
# ---------------------------------------------------------------------------
def test_translate_code_collects_python_from_chapters():
    """从 body_chapters[].content 里提取 ```python 代码块。"""
    state = _state_with_chapters_python()
    result = translate_code(state)
    py_entry = next(t for t in result["code_translations"] if t["lang"] == "py")
    # Python 代码应原样保留
    assert "import pandas as pd" in py_entry["code"]
    assert "sm.OLS(y, X).fit()" in py_entry["code"]


def test_translate_code_collects_python_from_audit_file(tmp_path):
    """从 cleaning_report.steps[7].report.clean_py 读取 clean.py。"""
    state = _state_with_cleaning_audit(tmp_path)
    result = translate_code(state)
    py_entry = next(t for t in result["code_translations"] if t["lang"] == "py")
    assert "import pandas as pd" in py_entry["code"]
    assert "df = pd.read_csv" in py_entry["code"]


def test_translate_code_merges_chapter_and_audit_python(tmp_path):
    """body_chapters 里的 Python + audit 里的 Python 都进入 py 翻译。"""
    chapters_state = _state_with_chapters_python()
    audit_state = _state_with_cleaning_audit(tmp_path)
    state = make_state(
        body_chapters=chapters_state["body_chapters"],
        cleaning_report=audit_state["cleaning_report"],
    )
    result = translate_code(state)
    py_entry = next(t for t in result["code_translations"] if t["lang"] == "py")
    # 两段代码都应出现
    assert "sm.OLS" in py_entry["code"]  # 来自 body_chapters
    assert "df = df.dropna()" in py_entry["code"]  # 来自 audit


# ---------------------------------------------------------------------------
# 翻译：Stata (.do)
# ---------------------------------------------------------------------------
def test_translate_to_stata_import_pandas():
    """pandas import 在 Stata 里翻成 import delimited。"""
    state = _state_with_chapters_python()
    result = translate_code(state)
    stata_entry = next(t for t in result["code_translations"] if t["lang"] == "stata")
    code = stata_entry["code"]
    # Stata 用 import delimited
    assert "import delimited" in code


def test_translate_to_stata_ols_becomes_regress():
    """sm.OLS(...).fit() 翻成 regress。"""
    state = _state_with_chapters_python()
    result = translate_code(state)
    stata_entry = next(t for t in result["code_translations"] if t["lang"] == "stata")
    code = stata_entry["code"]
    assert "regress" in code.lower()


def test_translate_to_stata_describe_becomes_summarize():
    """df.describe() 翻成 summarize。"""
    state = make_state(
        body_chapters=[
            {
                "type": "data_desc",
                "title": "数据描述",
                "content": "```python\ndf.describe()\n```",
            }
        ]
    )
    result = translate_code(state)
    stata_entry = next(t for t in result["code_translations"] if t["lang"] == "stata")
    assert "summarize" in stata_entry["code"].lower()


def test_translate_to_stata_corr_becomes_correlate():
    """df.corr() 翻成 correlate。"""
    state = make_state(
        body_chapters=[
            {
                "type": "data_desc",
                "title": "数据描述",
                "content": "```python\ndf.corr()\n```",
            }
        ]
    )
    result = translate_code(state)
    stata_entry = next(t for t in result["code_translations"] if t["lang"] == "stata")
    assert "correlate" in stata_entry["code"].lower()


# ---------------------------------------------------------------------------
# 翻译：R (.R)
# ---------------------------------------------------------------------------
def test_translate_to_r_read_csv():
    """pd.read_csv 翻成 read.csv。"""
    state = _state_with_chapters_python()
    result = translate_code(state)
    r_entry = next(t for t in result["code_translations"] if t["lang"] == "r")
    assert "read.csv" in r_entry["code"]


def test_translate_to_r_ols_becomes_lm():
    """sm.OLS(...).fit() 翻成 lm(...)。"""
    state = _state_with_chapters_python()
    result = translate_code(state)
    r_entry = next(t for t in result["code_translations"] if t["lang"] == "r")
    assert "lm(" in r_entry["code"] or "lm (" in r_entry["code"]


def test_translate_to_r_describe_becomes_summary():
    """df.describe() 翻成 summary(df)。"""
    state = make_state(
        body_chapters=[
            {
                "type": "data_desc",
                "title": "数据描述",
                "content": "```python\ndf.describe()\n```",
            }
        ]
    )
    result = translate_code(state)
    r_entry = next(t for t in result["code_translations"] if t["lang"] == "r")
    assert "summary" in r_entry["code"].lower()


# ---------------------------------------------------------------------------
# 翻译：EViews (.m)
# ---------------------------------------------------------------------------
def test_translate_to_eviews_regression():
    """OLS 翻成 ls（EViews 最小二乘命令）。"""
    state = _state_with_chapters_python()
    result = translate_code(state)
    eviews_entry = next(t for t in result["code_translations"] if t["lang"] == "eviews")
    # EViews 用 ls 命令做最小二乘
    assert "ls" in eviews_entry["code"].lower()


def test_translate_to_eviews_import():
    """read_csv 翻成 EViews import。"""
    state = _state_with_chapters_python()
    result = translate_code(state)
    eviews_entry = next(t for t in result["code_translations"] if t["lang"] == "eviews")
    assert "import" in eviews_entry["code"].lower() or "load" in eviews_entry["code"].lower()


# ---------------------------------------------------------------------------
# 鲁棒性
# ---------------------------------------------------------------------------
def test_translate_code_unknown_python_does_not_crash():
    """未知 Python 代码不应崩溃（降级为注释保留）。"""
    state = make_state(
        body_chapters=[
            {
                "type": "results",
                "title": "结果",
                "content": (
                    "```python\n"
                    "import torch\n"
                    "model = torch.nn.Linear(10, 1)\n"
                    "# 这不是经济学代码\n"
                    "```\n"
                ),
            }
        ]
    )
    # 不应抛异常
    result = translate_code(state)
    assert "code_translations" in result
    # 4 种语言都有
    assert len(result["code_translations"]) == 4


def test_translate_code_direction_without_python_fences_emits_panel_scripts():
    """Named panel direction, no ```python fences: usable xtreg/reghdfe + feols/felm."""
    result = translate_code(
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
                {"type": "results", "content": "散文结果章，没有代码块。"}
            ],
        }
    )
    by_lang = {t["lang"]: t["code"] for t in result["code_translations"]}
    assert "xtreg" in by_lang["stata"]
    assert "reghdfe" in by_lang["stata"]
    assert "l_homicide" in by_lang["stata"]
    assert "post" in by_lang["stata"]
    assert "sid" in by_lang["stata"]
    assert "feols" in by_lang["r"]
    assert "felm" in by_lang["r"]
    assert "l_homicide" in by_lang["r"]
    assert "C(sid)" in by_lang["py"]
    assert "C(year)" in by_lang["py"]
    assert 'smf.ols("l_homicide ~ post + l_prison", data=df)' not in by_lang["py"]
    assert "TWFE" in by_lang["py"]
    assert "TWFE" in by_lang["stata"]
    assert "TWFE" in by_lang["r"]
    assert "MISMATCH" in by_lang["eviews"]
    assert "无 Python 代码可翻译" not in by_lang["stata"]
    assert "无 Python 代码" not in by_lang["py"]
    assert "y ~ treat" not in by_lang["stata"]


def test_translate_code_ols_guessed_id_year_emits_regress_not_xtreg(tmp_path):
    """OLS stays pooled OLS when set_direction guessed CSV id+year."""
    cleaning_report, csv_path = _upload_cleaning_report(tmp_path)
    result = translate_code(
        make_state(
            csv_path=csv_path,
            cleaning_report=cleaning_report,
            research_direction={
                "question": "age on income",
                "dv": "income",
                "iv": "age",
                "method": "OLS",
                "id_col": "id",
                "time_col": "year",
                "id": "id",
                "year": "year",
            },
            degradations=_column_guessed_id_year(),
        )
    )
    by_lang = {t["lang"]: t["code"] for t in result["code_translations"]}
    stata = by_lang["stata"]
    r_code = by_lang["r"]
    assert "import delimited" in stata
    assert "regress income age" in stata
    assert "xtreg" not in stata
    assert "reghdfe" not in stata
    assert "Cleaning steps applied" not in stata
    assert "read.csv" in r_code
    assert "lm(" in r_code
    assert "feols" not in r_code
    assert "felm" not in r_code
    assert "无 Python 代码可翻译" not in stata
    assert "无 Python 代码" not in by_lang["py"]
    assert 'smf.ols("income ~ age"' in by_lang["py"]


def test_translate_code_empty_state_does_not_invent_y_treat():
    """Empty state keeps placeholder langs; does not fabricate y ~ treat."""
    result = translate_code({})
    by_lang = {t["lang"]: t["code"] for t in result["code_translations"]}
    assert "无 Python 代码可翻译" in by_lang["stata"]
    assert "y ~ treat" not in by_lang["stata"]
    assert "y ~ treat" not in by_lang["r"]
    assert "y ~ treat" not in by_lang["py"]


def test_translate_code_chapter_without_code_block():
    """章节内容里没有 Python 代码块时不报错。"""
    state = make_state(
        body_chapters=[
            {
                "type": "intro",
                "title": "引言",
                "content": "这是普通文本，没有代码块。",
            }
        ]
    )
    result = translate_code(state)
    assert len(result["code_translations"]) == 4


def test_translate_code_handles_missing_chapters_key():
    """state 里没有 body_chapters 键时不报错。"""
    result = translate_code({"cleaning_report": {}})
    assert len(result["code_translations"]) == 4


def test_translate_code_handles_missing_cleaning_report():
    """state 里没有 cleaning_report 键时不报错。"""
    result = translate_code({"body_chapters": []})
    assert len(result["code_translations"]) == 4


def test_translate_code_audit_file_missing(tmp_path):
    """cleaning_report.steps[7].report.clean_py 路径不存在时不报错。"""
    state = make_state(
        cleaning_report={
            "steps": [
                {"name": "profiling", "status": "success", "report": {}},
                {"name": "merge", "status": "success", "report": {}},
                {"name": "missing", "status": "success", "report": {}},
                {"name": "outliers", "status": "success", "report": {}},
                {"name": "transform", "status": "success", "report": {}},
                {"name": "filter", "status": "success", "report": {}},
                {"name": "balance", "status": "success", "report": {}},
                {
                    "name": "audit",
                    "status": "success",
                    "report": {
                        "clean_py": str(tmp_path / "nonexistent.py"),
                    },
                },
            ]
        }
    )
    result = translate_code(state)
    assert len(result["code_translations"]) == 4
