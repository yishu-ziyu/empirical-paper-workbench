"""Replication script and package built from what actually ran.

Every specification run in the research lab records the estimator, the fitted
formula and the analysis dataset. This module turns those records back into the
exact calls ``services.spec_run`` made, so a reader can rerun them on the same
file and get the same numbers. It never rewrites a call it does not recognise:
unknown estimators are listed as not included, with the reason.

Scope: research-lab specification runs. The canonical estimate path
(``agent/nodes/estimate.py`` main flow, prewrite) is not covered yet.
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from services.spec_run import IV_DIAG_ENDOG, IV_DIAG_INSTRUMENTS, IV_DIAG_VCOV

DATA_FILENAME = "analysis_data.csv"
SCRIPT_FILENAME = "replication.py"


class NoComputations(LookupError):
    """The session has no specification runs to publish."""


class DatasetUnavailable(RuntimeError):
    """The analysis file is gone or no longer matches the recorded hash."""


def _runs(state: dict[str, Any]) -> list[dict[str, Any]]:
    lab = state.get("research_lab")
    if not isinstance(lab, dict):
        return []
    return [run for run in (lab.get("specification_runs") or []) if isinstance(run, dict)]


def _dataset(run: dict[str, Any]) -> dict[str, Any]:
    ds = run.get("analysis_dataset")
    return ds if isinstance(ds, dict) else {}


def build_record(state: dict[str, Any]) -> dict[str, Any]:
    """Ordered computation record for the session's specification runs.

    Runs are kept in the order they were stored. Only runs on the most recent
    analysis dataset are publishable in one script; runs on an earlier file
    are listed separately so nothing is silently dropped.
    """
    runs = _runs(state)
    if not runs:
        raise NoComputations("no specification runs")
    latest = _dataset(runs[-1])
    target_hash = latest.get("hash")
    included, other_data = [], []
    for run in runs:
        (included if _dataset(run).get("hash") == target_hash else other_data).append(run)
    environment = next((run["environment"] for run in reversed(included) if isinstance(run.get("environment"), dict)), None)
    return {
        "dataset": {
            "name": latest.get("name"),
            "path": latest.get("path"),
            "sha256": target_hash,
            "role": latest.get("role"),
            "rows": latest.get("rows"),
        },
        "environment": environment,
        "runs": included,
        "other_data_runs": other_data,
    }


def _call_lines(run: dict[str, Any], var: str) -> tuple[list[str], set[str]] | None:
    """The call ``spec_run`` made for this run, or ``None`` if not reproducible."""
    estimator = str(run.get("estimator") or "")
    formula = run.get("formula")
    if not isinstance(formula, str) or not formula:
        return None
    if estimator == "statspai.feols":
        return [f"{var} = statspai.feols(", f"    {formula!r},", "    data=df,", ")"], {"statspai"}
    if estimator == "statspai.ivreg":
        return [f"{var} = statspai.ivreg(", f"    {formula!r},", "    data=df,", ")"], {"statspai"}
    if estimator == "statsmodels.ols":
        return [f"{var} = smf.ols({formula!r}, data=df).fit()"], {"statsmodels"}
    return None


def _diag_lines(run: dict[str, Any], var: str) -> list[str]:
    diag = run.get("diagnostics")
    if not isinstance(diag, dict) or diag.get("test") != "effective_f_test" or diag.get("status") == "error":
        return []
    controls = diag.get("controls") or []
    exog = repr(list(controls)) if controls else "None"
    return [
        f"{var}_first_stage = statspai.effective_f_test(",
        "    df,",
        f"    endog={IV_DIAG_ENDOG!r},",
        f"    instruments={list(IV_DIAG_INSTRUMENTS)!r},",
        f"    exog={exog},",
        f"    vcov={IV_DIAG_VCOV!r},",
        ")",
        f"# 记录：first_stage_F = {_num(diag.get('first_stage_F'), 4)}，F_eff = {_num(diag.get('F_eff'), 4)}",
    ]


def _num(value: Any, digits: int) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "未记录"


def build_script(state: dict[str, Any], *, session_id: str = "", now: datetime | None = None) -> str:
    record = build_record(state)
    dataset = record["dataset"]
    env = record["environment"]
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M UTC")
    env_line = "、".join(f"{k} {v}" for k, v in env.items()) if env else "运行时环境未记录（该批运行早于环境记录功能）"

    body: list[str] = []
    imports: set[str] = set()
    not_included: list[str] = []
    for index, run in enumerate(record["runs"], start=1):
        var = f"run_{index}"
        label = run.get("label") or run.get("spec_id") or "未命名设定"
        header = f"# ---- [{index}] {label}（spec {run.get('spec_id')}，{run.get('relation') or 'exploratory'}）"
        call = _call_lines(run, var)
        status = str(run.get("status") or "ok")
        if call is None:
            not_included.append(f"[{index}] {label}：估计器 {run.get('estimator') or '未记录'} 没有可复现的调用记录")
            body += [header, f"# 这次计算未纳入脚本：估计器 {run.get('estimator') or '未记录'} 没有可复现的调用记录。", ""]
            continue
        lines, needs = call
        if status not in {"ok", "degraded"}:
            body += [header, f"# 这次运行在研究时失败（status={status}），下面是当时的调用，保留为注释。"]
            body += [f"# {line}" for line in lines]
            body.append("")
            continue
        imports |= needs
        body.append(header)
        body.append(
            f"# 记录：coef = {_num(run.get('coef'), 4)}，se = {_num(run.get('se'), 4)}，"
            f"n = {run.get('n') if run.get('n') is not None else '未记录'}，标准误 {run.get('covariance') or '未记录'}"
        )
        body += lines
        body += _diag_lines(run, var)
        body.append("")

    for run in record["other_data_runs"]:
        other = _dataset(run).get("hash") or "未记录"
        not_included.append(f"{run.get('label') or run.get('spec_id')}：使用了另一份数据（sha256 {other}）")

    head = [
        '"""econpaper 复现脚本',
        "",
        "这是本研究中每次设定运行实际执行的调用，按运行顺序排列。",
        f"把研究时使用的数据文件 {DATA_FILENAME} 放在本脚本旁边，运行 python {SCRIPT_FILENAME}；",
        "得到的数字应与证据中记录的一致（记录值写在每次调用上方的注释里）。",
        "",
        f"会话：{session_id or '未记录'}",
        f"生成时间：{stamp}",
        f"运行环境（记录于运行时）：{env_line}",
        '"""',
        "import hashlib",
        "",
        "import pandas as pd",
    ]
    if "statspai" in imports:
        head.append("import statspai")
    if "statsmodels" in imports:
        head.append("import statsmodels.formula.api as smf")
    head += [
        "",
        f"DATA = {DATA_FILENAME!r}",
        f"EXPECTED_SHA256 = {dataset['sha256']!r}",
        "",
        'with open(DATA, "rb") as fh:',
        "    digest = hashlib.sha256(fh.read()).hexdigest()",
        "if digest != EXPECTED_SHA256:",
        '    raise SystemExit(f"数据文件与研究时使用的不一致：期望 {EXPECTED_SHA256}，实际 {digest}")',
        "",
        "df = pd.read_csv(DATA)",
        "",
    ]
    tail: list[str] = []
    if not_included:
        tail += ["# ---- 未纳入本脚本的计算"] + [f"# {item}" for item in not_included] + [""]
    tail += [
        'if __name__ == "__main__":',
        f"    for name in {[f'run_{i}' for i in range(1, len(record['runs']) + 1)]!r}:",
        "        if name in globals():",
        '            print(f"==== {name} ====")',
        "            print(globals()[name])",
        "",
    ]
    return "\n".join(head + body + tail)


def _readme(record: dict[str, Any]) -> str:
    dataset = record["dataset"]
    return "\n".join(
        [
            "# 复现包",
            "",
            f"- `{SCRIPT_FILENAME}`：本研究实际执行的计算调用，按运行顺序排列。",
            f"- `{DATA_FILENAME}`：研究时读取的数据文件，sha256 `{dataset['sha256']}`。",
            "",
            "运行：",
            "",
            "```bash",
            "pip install pandas statspai",
            f"python {SCRIPT_FILENAME}",
            "```",
            "",
            "脚本会先校验数据文件的 sha256，再逐条重跑。每次调用上方的注释写着研究时记录的结果，可以直接对照。",
            "",
        ]
    )


def build_package(state: dict[str, Any], *, session_id: str = "") -> bytes:
    """Zip with the script, the exact analysis file and a README."""
    record = build_record(state)
    path = record["dataset"].get("path")
    if not path or not Path(str(path)).is_file():
        raise DatasetUnavailable("analysis dataset file is no longer available")
    data = Path(str(path)).read_bytes()
    if hashlib.sha256(data).hexdigest() != record["dataset"]["sha256"]:
        raise DatasetUnavailable("analysis dataset changed since the runs were recorded")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(SCRIPT_FILENAME, build_script(state, session_id=session_id))
        zf.writestr(DATA_FILENAME, data)
        zf.writestr("README.md", _readme(record))
    return buf.getvalue()
