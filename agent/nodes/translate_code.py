"""translate_code 节点 (T-09).

6 章全部生成 / 审批通过后，graph 经条件边进入此节点。本节点：

1. 收集 Python 代码片段：
   - 从 ``state['body_chapters'][].content`` 提取 triple-backtick python 代码块
   - 从 ``state['cleaning_report']['steps'][7]['report']['clean_py']`` 读取 clean.py
2. 翻译成 Stata (.do) / R (.R) / EViews (.m) 三种格式（外加原 Python .py）。
3. 返回 ``{"code_translations": [{"lang", "code", "filename"}, ...]}``。

stata-code 上游包（``stata_code``）经检查是 Stata *执行*桥（subprocess
runner），不是 Python→Stata 翻译器——其公开 API 只有 ``run / execute /
run_console`` 等，无 translate 函数。故本节点用内置关键词映射翻译器，
覆盖常见 pandas / statsmodels 操作（read_csv / describe / corr / OLS /
dropna / groupby / plot / head）。未知 Python 代码降级为注释保留，不报错。

HITL 简化策略：state-driven，不调 interrupt()。本节点不在 graph 主循环里
单独触发 HITL；翻译完成后直接返回，由 graph 集成阶段决定后续边。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from protocols import TranslateCodeOutput
from state import EconPaperState


# ---------------------------------------------------------------------------
# Python 代码收集
# ---------------------------------------------------------------------------
_PYTHON_FENCE_RE = re.compile(
    r"```python\s*\n(.*?)```",
    re.DOTALL,
)


def _collect_python_from_chapters(body_chapters: list) -> str:
    """从 body_chapters[].content 提取所有 ```python``` 代码块，拼接返回。"""
    if not body_chapters:
        return ""
    snippets: list[str] = []
    for ch in body_chapters:
        if not isinstance(ch, dict):
            continue
        content = ch.get("content") or ""
        if not isinstance(content, str):
            continue
        for m in _PYTHON_FENCE_RE.finditer(content):
            snippets.append(m.group(1).strip())
    return "\n\n".join(snippets)


def _collect_python_from_audit(cleaning_report: Any) -> str:
    """从 cleaning_report.steps[7].report.clean_py 读 clean.py（若存在）。"""
    if not isinstance(cleaning_report, dict):
        return ""
    steps = cleaning_report.get("steps")
    if not isinstance(steps, list) or len(steps) < 8:
        return ""
    audit_step = steps[7]
    if not isinstance(audit_step, dict) or audit_step.get("name") != "audit":
        return ""
    report = audit_step.get("report")
    if not isinstance(report, dict):
        return ""
    py_path = report.get("clean_py")
    if not py_path:
        return ""
    try:
        return Path(py_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _collect_python(state: EconPaperState) -> str:
    """合并 body_chapters + audit 两处 Python 代码。"""
    body_chapters = state.get("body_chapters") or []
    cleaning_report = state.get("cleaning_report")
    parts: list[str] = []
    ch_py = _collect_python_from_chapters(body_chapters)
    if ch_py:
        parts.append(ch_py)
    audit_py = _collect_python_from_audit(cleaning_report)
    if audit_py:
        parts.append(audit_py)
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# 内置翻译器：Python → Stata / R / EViews
# ---------------------------------------------------------------------------
def _translate_line_to_stata(line: str) -> str:
    """单行 Python → Stata 翻译（关键词映射）。未知行降级为注释。"""
    s = line.strip()
    if not s or s.startswith("#"):
        return line

    # import 语句 → Stata 不需要
    if s.startswith("import ") or s.startswith("from "):
        return f"* {line}  (Stata 无需显式 import)"

    # pd.read_csv / pandas.read_csv → import delimited
    m = re.search(r'read_csv\(\s*[\'"]([^\'"]+)[\'"]\s*\)', s)
    if m:
        path = m.group(1)
        return f'import delimited "{path}", clear'

    # df.describe() → summarize
    if re.search(r'\.describe\(\)', s):
        return "summarize"

    # df.corr() → correlate
    if re.search(r'\.corr\(\)', s):
        return "correlate"

    # df.head() → list in 1/5
    if re.search(r'\.head\(\s*\d*\s*\)', s):
        return "list in 1/5"

    # df.info() → describe, short
    if re.search(r'\.info\(\)', s):
        return "describe, short"

    # df.dropna() → drop if missing
    if re.search(r'\.dropna\(\)', s):
        return "drop if missing(*)"

    # sm.add_constant(X) → Stata 自动加常数项，无需显式
    if "add_constant" in s:
        return f"* {line}  (Stata regress 默认带常数项)"

    # sm.OLS(y, X).fit() → regress y X
    m = re.search(r'OLS\(\s*([^,]+),\s*([^)]+)\)\.fit\(\)', s)
    if m:
        y = m.group(1).strip()
        x = m.group(2).strip()
        # 去掉外层括号 / list 语法
        y = re.sub(r'[\[\]\'"]', '', y).strip()
        x = re.sub(r'[\[\]\'"]', '', x).strip()
        x_vars = re.split(r'[,\s]+', x)
        x_vars = [v for v in x_vars if v]
        return f"regress {y} {' '.join(x_vars)}"

    # OLS 赋值 model = ... → regress（上面已处理）
    if "OLS" in s and "fit" in s:
        return f"* {line}  → regress"

    # print(model.summary()) → 无对应，注释
    if re.search(r'print\(.+\.summary\(\)\)', s):
        return "* 显示回归结果"

    # df.groupby('X') → by X:
    m = re.search(r'\.groupby\(\s*[\'"]([^\'"]+)[\'"]\s*\)', s)
    if m:
        return f"by {m.group(1)}:"

    # df.plot(...) / plt.show() → graph
    if ".plot(" in s or "plt.show" in s:
        return "graph"

    # df = pd.DataFrame(...) → 注释
    if "DataFrame(" in s:
        return f"* {line}  (Stata 通过 import 导入数据)"

    # 未知行：保留为注释
    return f"* {line}"


def _translate_line_to_r(line: str) -> str:
    """单行 Python → R 翻译。未知行降级为注释。"""
    s = line.strip()
    if not s or s.startswith("#"):
        return line

    # import pandas as pd → 注释（R 用 library）
    if s.startswith("import pandas"):
        return "library(data.table)  # 或 library(pandas)"
    if s.startswith("import statsmodels"):
        return "library(stats)  # lm() 在 base stats 里"
    if s.startswith("import ") or s.startswith("from "):
        return f"# {line}  (R 用 library())"

    # pd.read_csv / pandas.read_csv → read.csv
    m = re.search(r'(\w+)\s*=\s*\w+\.read_csv\(\s*[\'"]([^\'"]+)[\'"]\s*\)', s)
    if m:
        var = m.group(1)
        path = m.group(2)
        return f'{var} <- read.csv("{path}")'
    m = re.search(r'read_csv\(\s*[\'"]([^\'"]+)[\'"]\s*\)', s)
    if m:
        return f'df <- read.csv("{m.group(1)}")'

    # df.describe() → summary(df)
    if re.search(r'(\w+)\.describe\(\)', s):
        return "summary(df)"

    # df.corr() → cor(df)
    if re.search(r'(\w+)\.corr\(\)', s):
        return "cor(df)"

    # df.head() → head(df)
    if re.search(r'(\w+)\.head\(\s*\d*\s*\)', s):
        return "head(df)"

    # df.info() → str(df)
    if re.search(r'(\w+)\.info\(\)', s):
        return "str(df)"

    # df.dropna() → na.omit(df)
    m = re.search(r'(\w+)\s*=\s*(\w+)\.dropna\(\)', s)
    if m:
        var = m.group(1)
        src = m.group(2)
        return f"{var} <- na.omit({src})"
    if re.search(r'\.dropna\(\)', s):
        return "df <- na.omit(df)"

    # sm.add_constant(X) → R lm 默认带截距
    if "add_constant" in s:
        return f"# {line}  (R lm() 默认带截距)"

    # sm.OLS(y, X).fit() → lm(y ~ X)
    m = re.search(r'OLS\(\s*([^,]+),\s*([^)]+)\)\.fit\(\)', s)
    if m:
        y = m.group(1).strip()
        x = m.group(2).strip()
        # 处理 X = df[['a', 'b']] 形式：转成 a + b
        y = re.sub(r'[\[\]\'"]', '', y).strip()
        x_clean = re.sub(r'[\[\]\'"]', '', x).strip()
        x_vars = [v.strip() for v in re.split(r'[,\s]+', x_clean) if v.strip()]
        if len(x_vars) > 1:
            rhs = " + ".join(x_vars)
        else:
            rhs = x_vars[0] if x_vars else "x"
        return f"model <- lm({y} ~ {rhs}, data=df)"

    if "OLS" in s and "fit" in s:
        return f"# {line}  → lm()"

    # print(model.summary()) → summary(model)
    m = re.search(r'print\((\w+)\.summary\(\)\)', s)
    if m:
        return f"summary({m.group(1)})"

    # df.groupby('X') → group_by
    m = re.search(r'\.groupby\(\s*[\'"]([^\'"]+)[\'"]\s*\)', s)
    if m:
        return f"group_by({m.group(1)})"

    # df.plot() / plt.show()
    if ".plot(" in s or "plt.show" in s:
        return "plot(df)"

    # 未知行
    return f"# {line}"


def _translate_line_to_eviews(line: str) -> str:
    """单行 Python → EViews 翻译。未知行降级为注释。"""
    s = line.strip()
    if not s or s.startswith("#"):
        return line

    # import → EViews 不需要
    if s.startswith("import ") or s.startswith("from "):
        return f"' {line}  (EViews 无需显式 import)"

    # pd.read_csv → import
    m = re.search(r'read_csv\(\s*[\'"]([^\'"]+)[\'"]\s*\)', s)
    if m:
        path = m.group(1)
        # EViews import 命令
        return f'import {path}'

    # df.describe() → stats
    if re.search(r'\.describe\(\)', s):
        return "stats"

    # df.corr() → cor
    if re.search(r'\.corr\(\)', s):
        return "cor"

    # df.head() → show 1 5
    if re.search(r'\.head\(\s*\d*\s*\)', s):
        return "show 1 5"

    # df.info() → 注释
    if re.search(r'\.info\(\)', s):
        return "' 显示数据结构"

    # df.dropna() → smpl if na
    if re.search(r'\.dropna\(\)', s):
        return "smpl if wage<>na"

    # sm.add_constant → EViews ls 默认带常数
    if "add_constant" in s:
        return f"' {line}  (EViews ls 默认带常数 c)"

    # sm.OLS(y, X).fit() → ls y X
    m = re.search(r'OLS\(\s*([^,]+),\s*([^)]+)\)\.fit\(\)', s)
    if m:
        y = m.group(1).strip()
        x = m.group(2).strip()
        y = re.sub(r'[\[\]\'"]', '', y).strip()
        x_clean = re.sub(r'[\[\]\'"]', '', x).strip()
        x_vars = [v.strip() for v in re.split(r'[,\s]+', x_clean) if v.strip()]
        rhs = " ".join(x_vars) if x_vars else "x"
        return f"ls {y} c {rhs}"

    if "OLS" in s and "fit" in s:
        return f"' {line}  → ls"

    # print(model.summary()) → 显示
    if re.search(r'print\(.+\.summary\(\)\)', s):
        return "' 显示回归结果"

    # df.groupby('X') → sort + by
    m = re.search(r'\.groupby\(\s*[\'"]([^\'"]+)[\'"]\s*\)', s)
    if m:
        return f"sort {m.group(1)}"

    # df.plot() / plt.show() → graph
    if ".plot(" in s or "plt.show" in s:
        return "graph"

    # 未知行
    return f"' {line}"


def _as_controls(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(part).strip() for part in value if str(part).strip()]


def _first_text(*sources: Any, keys: tuple[str, ...], default: str = "") -> str:
    for src in sources:
        if not isinstance(src, dict):
            continue
        for key in keys:
            raw = src.get(key)
            if raw is None:
                continue
            text = str(raw).strip()
            if text:
                return text
    return default


def _direction_model(state: EconPaperState) -> dict[str, Any]:
    """Read outcome / treatment / panel columns from direction or spec."""
    spec = state.get("main_specification")
    rd = state.get("research_direction")
    spec = spec if isinstance(spec, dict) else {}
    rd = rd if isinstance(rd, dict) else {}
    csv_path = state.get("csv_path") or "data.csv"
    csv_name = Path(str(csv_path)).name or "data.csv"
    outcome = _first_text(spec, rd, keys=("outcome", "outcome_col", "dv"), default="y")
    treatment = _first_text(
        spec, rd, keys=("treatment", "treatment_col", "iv"), default="treat"
    )
    id_col = _first_text(spec, rd, keys=("id_col", "id", "unit_col", "unit"))
    time_col = _first_text(spec, rd, keys=("time_col", "time", "year"))
    controls = _as_controls(spec.get("controls")) or _as_controls(rd.get("controls"))
    skip = {outcome, treatment, id_col, time_col}
    controls = [col for col in controls if col not in skip]
    return {
        "csv": csv_name,
        "outcome": outcome,
        "treatment": treatment,
        "controls": controls,
        "id_col": id_col,
        "time_col": time_col,
        "panel": bool(id_col and time_col),
    }


def _scripts_from_direction(model: dict[str, Any]) -> dict[str, str]:
    """Usable Stata xtreg/reghdfe + R fixest/felm when chapters have no Python."""
    y = model["outcome"]
    treat = model["treatment"]
    controls = model["controls"]
    rhs_space = " ".join([treat, *controls])
    rhs_plus = " + ".join([treat, *controls])
    csv = model["csv"]
    note = (
        "Chapter text had no ```python fences. "
        "Script is built from the session research direction, not StatsPAI."
    )

    py_formula = f"{y} ~ {rhs_plus}"
    py = (
        '"""Auto-generated Python script from research direction.\n\n'
        f"{note}\n"
        '"""\n'
        "import pandas as pd\n"
        "import statsmodels.formula.api as smf\n\n"
        f'df = pd.read_csv("{csv}")\n'
        f'model = smf.ols("{py_formula}", data=df).fit()\n'
        "print(model.summary())\n"
    )

    stata = [
        "* Auto-generated Stata script from research direction",
        f"* {note}",
        "clear all",
        f'import delimited "{csv}", clear',
    ]
    if model["panel"]:
        i, t = model["id_col"], model["time_col"]
        stata.extend(
            [
                f"xtset {i} {t}",
                f"xtreg {y} {rhs_space}, fe vce(cluster {i})",
                f"reghdfe {y} {rhs_space}, absorb({i} {t}) vce(cluster {i})",
            ]
        )
    else:
        stata.append(f"regress {y} {rhs_space}")

    r = [
        "# Auto-generated R script from research direction",
        f"# {note}",
        "library(fixest)",
        "library(lfe)",
        f'df <- read.csv("{csv}")',
    ]
    if model["panel"]:
        i, t = model["id_col"], model["time_col"]
        fe = f"{i} + {t}"
        r.extend(
            [
                f"model_feols <- feols({y} ~ {rhs_plus} | {fe}, data = df, cluster = ~{i})",
                f"model_felm <- felm({y} ~ {rhs_plus} | {fe} | 0 | {i}, data = df)",
                "summary(model_feols)",
            ]
        )
    else:
        r.extend(
            [
                f"model <- lm({y} ~ {rhs_plus}, data = df)",
                "summary(model)",
            ]
        )

    eviews = [
        "' Auto-generated EViews script from research direction",
        f"' {note}",
        f"import {csv}",
        f"ls {y} c {rhs_space}",
    ]
    return {
        "py": py,
        "stata": "\n".join(stata) + "\n",
        "r": "\n".join(r) + "\n",
        "eviews": "\n".join(eviews) + "\n",
    }


def _translate_block(python_code: str, lang: str) -> str:
    """整段 Python 代码翻译成目标语言。"""
    if not python_code.strip():
        if lang == "stata":
            return "* Auto-generated Stata script (econpaper T-09)\n* 无 Python 代码可翻译\n"
        if lang == "r":
            return "# Auto-generated R script (econpaper T-09)\n# 无 Python 代码可翻译\n"
        return "' Auto-generated EViews script (econpaper T-09)\n' 无 Python 代码可翻译\n"

    header_map = {
        "stata": "* Auto-generated Stata script (econpaper T-09)\n"
                 "* 由 Python 代码翻译而来，覆盖常见 pandas/statsmodels 操作\n\n",
        "r": "# Auto-generated R script (econpaper T-09)\n"
            "# 由 Python 代码翻译而来，覆盖常见 pandas/statsmodels 操作\n\n",
        "eviews": "' Auto-generated EViews script (econpaper T-09)\n"
                  "' 由 Python 代码翻译而来，覆盖常见 pandas/statsmodels 操作\n\n",
    }
    line_fn = {
        "stata": _translate_line_to_stata,
        "r": _translate_line_to_r,
        "eviews": _translate_line_to_eviews,
    }[lang]

    lines = python_code.splitlines()
    translated = [line_fn(ln) for ln in lines]
    return header_map[lang] + "\n".join(translated) + "\n"


# ---------------------------------------------------------------------------
# 节点入口
# ---------------------------------------------------------------------------
def translate_code(state: EconPaperState) -> TranslateCodeOutput:
    """收集 Python 代码片段，翻译成 Stata/R/EViews。

    返回 ``{"code_translations": [{"lang", "code", "filename"}, ...]}``，
    固定 4 条：py / stata / r / eviews。
    """
    python_code = _collect_python(state)

    if python_code.strip():
        py_code = (
            '"""Auto-generated Python script (econpaper T-09).\n\n'
            "由 body_chapters 与 cleaning audit 合并而来。\n"
            '"""\n\n'
            + python_code
        )
        translations: list[dict] = [
            {"lang": "py", "code": py_code, "filename": "analysis.py"},
            {
                "lang": "stata",
                "code": _translate_block(python_code, "stata"),
                "filename": "analysis.do",
            },
            {
                "lang": "r",
                "code": _translate_block(python_code, "r"),
                "filename": "analysis.R",
            },
            {
                "lang": "eviews",
                "code": _translate_block(python_code, "eviews"),
                "filename": "analysis.m",
            },
        ]
        return {"code_translations": translations}

    scripts = _scripts_from_direction(_direction_model(state))
    return {
        "code_translations": [
            {"lang": "py", "code": scripts["py"], "filename": "analysis.py"},
            {"lang": "stata", "code": scripts["stata"], "filename": "analysis.do"},
            {"lang": "r", "code": scripts["r"], "filename": "analysis.R"},
            {"lang": "eviews", "code": scripts["eviews"], "filename": "analysis.m"},
        ]
    }
