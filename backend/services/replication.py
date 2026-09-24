"""Replication script and package built from what actually ran.

Estimator calls are recorded at the call site (``call`` on the estimate
payload and on each specification run; see ``agent.nodes.estimate.call_record``).
This module renders those records back into the same calls, so a reader can
rerun them on the same files and get the same numbers. It never invents a call:
anything it cannot render is listed as not included, with the reason.

Covered: research-lab specification runs, and the main estimate produced by
fixed dispatch. Not covered yet: the estimate-agent path (its reported code is
not verified as executed), robustness checks, identification diagnostics
outside specification runs, cleaning steps and descriptive tables.
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from services.spec_run import IV_DIAG_ENDOG, IV_DIAG_INSTRUMENTS, IV_DIAG_VCOV

SCRIPT_FILENAME = "replication.py"

NOT_COVERED = [
    "稳健性检验与设定曲线",
    "设定运行之外的识别诊断",
    "数据清洗步骤（脚本从清洗后的分析文件开始）",
    "描述统计表",
]


class NoComputations(LookupError):
    """The session has nothing to replicate."""


class DatasetUnavailable(RuntimeError):
    """An analysis file is gone or no longer matches the recorded hash."""


def data_filename(sha256: str) -> str:
    return f"data_{sha256[:8]}.csv"


# ---------------------------------------------------------------------------
# record
# ---------------------------------------------------------------------------


def _dataset(item: dict[str, Any]) -> dict[str, Any]:
    ds = item.get("analysis_dataset")
    return ds if isinstance(ds, dict) else {}


def build_record(state: dict[str, Any]) -> dict[str, Any]:
    """Ordered computations: specification runs first, then the main estimate."""
    items: list[dict[str, Any]] = []
    lab = state.get("research_lab")
    if isinstance(lab, dict):
        for run in lab.get("specification_runs") or []:
            if isinstance(run, dict):
                items.append({**run, "_section": "设定运行"})
    estimate = state.get("estimate")
    if isinstance(estimate, dict) and estimate.get("status") in {"ok", "degraded"}:
        items.append({**estimate, "_section": "主估计（写进论文的结果）", "label": estimate.get("label") or "主估计"})
    if not items:
        raise NoComputations("no computations recorded")
    datasets: dict[str, dict[str, Any]] = {}
    for item in items:
        ds = _dataset(item)
        digest = ds.get("hash")
        if digest and digest not in datasets:
            datasets[digest] = {"sha256": digest, "path": ds.get("path"), "name": ds.get("name"), "file": data_filename(digest)}
    environment = next((i["environment"] for i in reversed(items) if isinstance(i.get("environment"), dict)), None)
    return {"items": items, "datasets": list(datasets.values()), "environment": environment}


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------


def _render_call(call: dict[str, Any], var: str) -> tuple[list[str], set[str]] | None:
    """One recorded call → source lines. ``None`` if the shape is unknown."""
    function = call.get("function")
    args = list(call.get("args") or [])
    kwargs = dict(call.get("kwargs") or {})
    if function == "statsmodels.ols":
        if len(args) != 1:
            return None
        cluster = kwargs.get("cluster")
        fit = f'cov_type="cluster", cov_kwds={{"groups": df[{cluster!r}]}}' if cluster is not None else ""
        return [f"{var} = smf.ols({args[0]!r}, data=df).fit({fit})"], {"statsmodels"}
    if not isinstance(function, str) or not function.startswith("statspai."):
        return None
    parts: list[str] = []
    if call.get("data") == "first":
        parts.append("df")
        parts += [repr(a) for a in args]
    elif call.get("data") == "data":
        parts += [repr(a) for a in args]
        parts.append("data=df")
    else:
        return None
    parts += [f"{k}={v!r}" for k, v in kwargs.items()]
    lines = [f"{var} = {function}("] + [f"    {p}," for p in parts] + [")"]
    return lines, {"statspai"}


def _legacy_call(item: dict[str, Any]) -> dict[str, Any] | None:
    """Specification runs recorded before ``call`` existed (spec_run defaults)."""
    estimator = str(item.get("estimator") or "")
    formula = item.get("formula")
    if not isinstance(formula, str) or not formula:
        return None
    if estimator in {"statspai.feols", "statspai.ivreg"}:
        return {"function": estimator, "data": "data", "args": [formula], "kwargs": {}}
    if estimator == "statsmodels.ols":
        return {"function": "statsmodels.ols", "data": "data", "args": [formula], "kwargs": {}}
    return None


def _legacy_diag_call(diag: dict[str, Any]) -> dict[str, Any]:
    controls = diag.get("controls") or []
    return {
        "function": "statspai.effective_f_test",
        "data": "first",
        "args": [],
        "kwargs": {
            "endog": IV_DIAG_ENDOG,
            "instruments": list(IV_DIAG_INSTRUMENTS),
            "exog": list(controls) or None,
            "vcov": IV_DIAG_VCOV,
        },
    }


def _num(value: Any, digits: int) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "未记录"


def _reason_not_reproducible(item: dict[str, Any]) -> str:
    if item.get("final_code") and not item.get("call"):
        return "估计 Agent 路径：它报告的代码尚未核实为实际执行的代码"
    return f"估计器 {item.get('estimator') or '未记录'} 没有可复现的调用记录"


def build_script(state: dict[str, Any], *, session_id: str = "", now: datetime | None = None) -> str:
    record = build_record(state)
    env = record["environment"]
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M UTC")
    env_line = "、".join(f"{k} {v}" for k, v in env.items()) if env else "运行时环境未记录（该批运行早于环境记录功能）"
    files = {ds["sha256"]: ds["file"] for ds in record["datasets"]}

    body: list[str] = []
    imports: set[str] = set()
    not_included: list[str] = []
    current_data: str | None = None
    for index, item in enumerate(record["items"], start=1):
        var = f"run_{index}"
        label = item.get("label") or item.get("spec_id") or "未命名"
        spec = f"spec {item['spec_id']}，" if item.get("spec_id") else ""
        header = f"# ---- [{index}] {item['_section']} · {label}（{spec}{item.get('relation') or item.get('method') or ''}）"
        call = item.get("call") if isinstance(item.get("call"), dict) else _legacy_call(item)
        rendered = _render_call(call, var) if call else None
        digest = _dataset(item).get("hash")
        if rendered is None or not digest:
            reason = _reason_not_reproducible(item) if rendered is None else "没有记录读取的数据文件"
            not_included.append(f"[{index}] {label}：{reason}")
            body += [header, f"# 这次计算未纳入脚本：{reason}。", ""]
            continue
        lines, needs = rendered
        status = str(item.get("status") or "ok")
        if status not in {"ok", "degraded"}:
            body += [header, f"# 这次运行在研究时失败（status={status}），下面是当时的调用，保留为注释。"]
            body += [f"# {line}" for line in lines] + [""]
            continue
        imports |= needs
        body.append(header)
        if digest != current_data:
            body.append(f"df = load({files[digest]!r}, {digest!r})")
            current_data = digest
        body.append(
            f"# 记录：coef = {_num(item.get('coef'), 4)}，se = {_num(item.get('se'), 4)}，"
            f"n = {item.get('n') if item.get('n') is not None else '未记录'}"
            + (f"，标准误 {item['covariance']}" if item.get("covariance") else "")
        )
        body += lines
        diag = item.get("diagnostics")
        if isinstance(diag, dict) and diag.get("test") == "effective_f_test" and diag.get("status") != "error":
            diag_call = diag.get("call") if isinstance(diag.get("call"), dict) else _legacy_diag_call(diag)
            diag_lines = _render_call(diag_call, f"{var}_first_stage")
            if diag_lines:
                body += diag_lines[0]
                body.append(f"# 记录：first_stage_F = {_num(diag.get('first_stage_F'), 4)}，F_eff = {_num(diag.get('F_eff'), 4)}")
        body.append("")

    head = [
        '"""econpaper 复现脚本',
        "",
        "这是本研究中实际执行的计算调用，按运行顺序排列；每次调用上方的注释是研究时记录的结果。",
        "把复现包里的数据文件放在本脚本旁边，运行 python " + SCRIPT_FILENAME + "。",
        "",
        "本脚本覆盖：研究台账的设定运行、主估计。尚未覆盖：" + "、".join(NOT_COVERED) + "。",
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
        "",
        "def load(path, expected_sha256):",
        '    """读入研究时使用的数据文件；内容与记录不符就停止。"""',
        '    with open(path, "rb") as fh:',
        "        digest = hashlib.sha256(fh.read()).hexdigest()",
        "    if digest != expected_sha256:",
        '        raise SystemExit(f"{path} 与研究时使用的数据不一致：期望 {expected_sha256}，实际 {digest}")',
        "    return pd.read_csv(path)",
        "",
        "",
    ]
    tail: list[str] = []
    if not_included:
        tail += ["# ---- 未纳入本脚本的计算"] + [f"# {x}" for x in not_included] + [""]
    names = [f"run_{i}" for i in range(1, len(record["items"]) + 1)]
    tail += [
        'if __name__ == "__main__":',
        f"    for name in {names!r}:",
        "        if name in globals():",
        '            print(f"==== {name} ====")',
        "            print(globals()[name])",
        "",
    ]
    return "\n".join(head + body + tail)


def _readme(record: dict[str, Any]) -> str:
    rows = [f"- `{ds['file']}`：研究时读取的数据文件，sha256 `{ds['sha256']}`。" for ds in record["datasets"]]
    return "\n".join(
        [
            "# 复现包",
            "",
            f"- `{SCRIPT_FILENAME}`：本研究实际执行的计算调用，按运行顺序排列。",
            *rows,
            "",
            "运行：",
            "",
            "```bash",
            "pip install pandas statspai",
            f"python {SCRIPT_FILENAME}",
            "```",
            "",
            "脚本读每份数据前先校验 sha256，再逐条重跑。每次调用上方的注释写着研究时记录的结果，可以直接对照。",
            "",
            "尚未覆盖：" + "、".join(NOT_COVERED) + "。",
            "",
        ]
    )


def build_package(state: dict[str, Any], *, session_id: str = "") -> bytes:
    """Zip with the script, every analysis file it reads, and a README."""
    record = build_record(state)
    blobs: dict[str, bytes] = {}
    for ds in record["datasets"]:
        path = ds.get("path")
        if not path or not Path(str(path)).is_file():
            raise DatasetUnavailable(f"analysis dataset {ds['file']} is no longer available")
        data = Path(str(path)).read_bytes()
        if hashlib.sha256(data).hexdigest() != ds["sha256"]:
            raise DatasetUnavailable(f"analysis dataset {ds['file']} changed since it was recorded")
        blobs[ds["file"]] = data
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(SCRIPT_FILENAME, build_script(state, session_id=session_id))
        for name, data in blobs.items():
            zf.writestr(name, data)
        zf.writestr("README.md", _readme(record))
    return buf.getvalue()
