"""Replication package: the published script must reproduce what actually ran.

Contract: docs/acceptance/replication-script.md
"""
from __future__ import annotations

import asyncio
import hashlib
import io
import os
import runpy
import uuid
import zipfile
from pathlib import Path

import pytest

from facade import facade
from run_repository import RunRepository
from runner import process_one_run
from services.replication import (
    DatasetUnavailable,
    NoComputations,
    build_package,
    build_script,
)


def _headers() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid.uuid4())}


@pytest.fixture(autouse=True)
def _cleanup_sessions(client):
    from sqlalchemy import select

    from models.research_session import ResearchSession

    async def ids() -> set[str]:
        repo = RunRepository()
        async with repo._factory() as db:
            return set(await db.scalars(select(ResearchSession.session_id)))

    before = asyncio.run(ids())
    yield
    for session_id in asyncio.run(ids()) - before:
        facade.delete_session(session_id)


def _card_session(client, owner: str) -> str:
    accepted = client.post("/demos/card", headers=_headers())
    assert accepted.status_code == 202, accepted.text
    assert asyncio.run(process_one_run(owner=owner, run_id=accepted.json()["run_id"]))
    return accepted.json()["session_id"]


def _run_space(client, sid: str, owner: str) -> list[dict]:
    frozen = client.post(f"/sessions/{sid}/research/specification-space/freeze")
    assert frozen.status_code == 200, frozen.text
    resp = client.post(f"/sessions/{sid}/research/specification-space/run", headers=_headers())
    assert resp.status_code == 202, resp.text
    assert asyncio.run(process_one_run(owner=owner, run_id=resp.json()["run_id"]))
    lab = client.get(f"/sessions/{sid}/research").json()
    return list(lab["specification_runs"])  # script numbers every stored run, in order


def _effect(fit, var: str) -> tuple[float, float]:
    params = fit.params
    se = fit.std_errors if hasattr(fit, "std_errors") else fit.bse
    return float(params[var]), float(se[var])


def _unzip(blob: bytes, dest: Path) -> list[str]:
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        names = sorted(zf.namelist())
        assert "README.md" in names and "replication.py" in names
        zf.extractall(dest)
    return [n for n in names if n.startswith("data_") and n.endswith(".csv")]


def _run_script(folder: Path) -> dict:
    cwd = os.getcwd()
    os.chdir(folder)
    try:
        return runpy.run_path(str(folder / "replication.py"))  # actually run it
    finally:
        os.chdir(cwd)


def test_package_reproduces_every_recorded_number(client, tmp_path):
    sid = _card_session(client, "repl-upload")
    runs = _run_space(client, sid, "repl-space")
    assert runs, "Card space should produce ok runs"

    resp = client.get(f"/sessions/{sid}/replication-package")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/zip"
    data_files = _unzip(resp.content, tmp_path)

    # the packaged data is byte-identical to the file the runs read
    digest = runs[-1]["analysis_dataset"]["hash"]
    assert data_files == [f"data_{digest[:8]}.csv"]
    assert hashlib.sha256((tmp_path / data_files[0]).read_bytes()).hexdigest() == digest

    ns = _run_script(tmp_path)

    compared_fits = compared_f = 0
    for index, run in enumerate(runs, start=1):
        if run.get("status") != "ok":
            assert f"run_{index}" not in ns
            continue
        fit = ns[f"run_{index}"]
        compared_fits += 1
        coef, se = _effect(fit, "educ")
        assert round(coef, 4) == round(run["coef"], 4), (run["spec_id"], coef, run["coef"])
        assert round(se, 4) == round(run["se"], 4), (run["spec_id"], se, run["se"])
        diag = run.get("diagnostics") or {}
        if diag.get("test") == "effective_f_test" and diag.get("F_eff") is not None:
            got = ns[f"run_{index}_first_stage"]
            assert round(float(got["F_eff"]), 2) == round(diag["F_eff"], 2)
            assert round(float(got["first_stage_F"]), 2) == round(diag["first_stage_F"], 2)
            compared_f += 1
    assert compared_fits >= 2 and compared_f >= 1, (compared_fits, compared_f)


def test_script_endpoint_is_the_actual_calls(client):
    sid = _card_session(client, "repl-upload-2")
    runs = _run_space(client, sid, "repl-space-2")
    resp = client.get(f"/sessions/{sid}/replication-script")
    assert resp.status_code == 200
    assert 'filename="replication.py"' in resp.headers["content-disposition"]
    script = resp.text
    compile(script, "replication.py", "exec")
    for run in (r for r in runs if r.get("status") == "ok"):
        assert repr(run["formula"]) in script
        call = "statspai.ivreg(" if run["estimator"] == "statspai.ivreg" else "statspai.feols("
        assert call in script
    assert "translate" not in script.lower()


def test_no_runs_is_404(client):
    sid = _card_session(client, "repl-upload-3")
    assert client.get(f"/sessions/{sid}/replication-script").status_code == 404
    assert client.get(f"/sessions/{sid}/replication-package").status_code == 404


def _state(runs: list[dict], path: Path | None = None) -> dict:
    for run in runs:
        run.setdefault("analysis_dataset", {"hash": "h", "path": str(path) if path else None, "name": "x.csv"})
    return {"research_lab": {"specification_runs": runs}}


def test_agent_path_estimate_is_not_passed_off_as_executed():
    state = {"estimate": {"status": "ok", "estimator": "estimate_agent", "final_code": "print(1)", "analysis_dataset": {"hash": "h"}}}
    script = build_script(state)
    compile(script, "replication.py", "exec")
    assert "print(1)" not in script
    assert "尚未核实为实际执行的代码" in script


def test_unknown_estimator_is_listed_not_rewritten():
    state = _state([
        {"spec_id": "cs", "label": "Callaway–Sant'Anna", "estimator": "statspai.callaway_santanna", "formula": "y ~ d", "status": "ok"},
        {"spec_id": "ols", "label": "OLS", "estimator": "statspai.feols", "formula": "y ~ d", "status": "ok", "coef": 1.0, "se": 0.1, "n": 10},
    ])
    script = build_script(state)
    compile(script, "replication.py", "exec")
    assert "callaway_santanna(" not in script
    assert "这次计算未纳入脚本" in script
    assert "run_2 = statspai.feols(" in script


def test_failed_run_is_kept_as_comment():
    state = _state([{"spec_id": "iv", "label": "IV", "estimator": "statspai.ivreg", "formula": "y ~ (d ~ z)", "status": "error"}])
    script = build_script(state)
    compile(script, "replication.py", "exec")
    assert "# run_1 = statspai.ivreg(" in script
    assert "\nrun_1 = statspai.ivreg(" not in script


def test_no_runs_raises():
    with pytest.raises(NoComputations):
        build_script({"research_lab": {"specification_runs": []}})


def test_changed_data_is_refused(tmp_path):
    data = tmp_path / "a.csv"
    data.write_text("y,d\n1,0\n")
    state = _state([{"spec_id": "ols", "estimator": "statspai.feols", "formula": "y ~ d", "status": "ok"}], data)
    with pytest.raises(DatasetUnavailable):
        build_package(state)  # recorded hash "h" does not match the file


def test_script_stops_on_wrong_data(client, tmp_path):
    sid = _card_session(client, "repl-upload-4")
    _run_space(client, sid, "repl-space-4")
    data_files = _unzip(client.get(f"/sessions/{sid}/replication-package").content, tmp_path)
    with open(tmp_path / data_files[0], "a") as fh:
        fh.write("\n")
    with pytest.raises(SystemExit) as exc:
        _run_script(tmp_path)
    assert "不一致" in str(exc.value)


# ---------------------------------------------------------------------------
# main estimate (fixed dispatch): run estimate() for real, then the script
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[2]


def _card_csv() -> Path:
    from services.card_demo import _candidate_wooldridge_paths

    for path in _candidate_wooldridge_paths():
        if path.is_file():
            return path
    pytest.skip("Card data not available")


def _rd_csv(folder: Path) -> Path:
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(7)
    x = rng.uniform(-1, 1, 1500)
    y = 0.4 * (x >= 0) + 0.8 * x + rng.normal(0, 0.3, x.size)
    path = folder / "rd.csv"
    pd.DataFrame({"x": x, "y": y}).to_csv(path, index=False)
    return path


def _scm_csv(folder: Path) -> Path:
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(11)
    rows = []
    for u in range(12):
        base = rng.normal(10, 1)
        for t in range(20):
            y = base + 0.3 * t + rng.normal(0, 0.2) + (2.0 if (u == 0 and t >= 12) else 0.0)
            rows.append({"unit": f"u{u}", "year": 2000 + t, "y": y})
    path = folder / "scm.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _main_estimate_cases(folder: Path):
    return [
        ("ols", REPO / "fixtures/classic-5/ck1994_long.csv", {"method": "ols", "formula": "fte ~ treated + period + treated:period", "treatment": "treated:period"}),
        ("iv", _card_csv(), {"method": "iv", "formula": "lwage ~ (educ ~ nearc4) + exper + expersq + black + south", "endogenous": "educ"}),
        ("rd", _rd_csv(folder), {"method": "rd", "outcome": "y", "running_var": "x", "cutoff": 0}),
        ("scm", _scm_csv(folder), {"method": "scm", "outcome": "y", "unit": "unit", "time": "year", "treated_unit": "u0", "treatment_time": 2012}),
    ]


@pytest.mark.parametrize("case", ["ols", "iv", "rd", "scm"])
def test_main_estimate_script_reproduces_recorded_numbers(case, tmp_path):
    from agent.nodes.estimate import effect_from_fit, estimate

    data_dir = tmp_path / "in"
    data_dir.mkdir()
    name, csv, spec = next(c for c in _main_estimate_cases(data_dir) if c[0] == case)
    out = estimate({"csv_path": str(csv), "main_specification": spec})
    est = out["estimate"]
    assert est["status"] in {"ok", "degraded"}, est
    # a successful estimate must carry its number (regression: RD/SCM reported ok with coef None)
    assert isinstance(est.get("coef"), float), (name, est.get("coef"))
    assert est.get("call"), f"{name}: call not recorded"
    assert est.get("environment", {}).get("python")

    pkg = tmp_path / "pkg"
    pkg.mkdir()
    _unzip(build_package({"estimate": est}), pkg)
    ns = _run_script(pkg)
    treatment = est.get("treatment")
    var = None if name in {"rd", "scm"} else treatment
    coef, se, _p, n = effect_from_fit(ns["run_1"], var)
    assert round(coef, 4) == round(est["coef"], 4), (name, coef, est["coef"])
    if est.get("se") is not None:
        assert round(se, 4) == round(est["se"], 4), (name, se, est["se"])


def test_spec_runs_and_main_estimate_on_different_files(tmp_path):
    """Two data sources → two files in the package, each loaded and checked."""
    from agent.nodes.estimate import estimate

    csv = REPO / "fixtures/classic-5/ck1994_long.csv"
    est = estimate({"csv_path": str(csv), "main_specification": {"method": "ols", "formula": "fte ~ treated", "treatment": "treated"}})["estimate"]
    rd_est = estimate({"csv_path": str(_rd_csv(tmp_path)), "main_specification": {"method": "rd", "outcome": "y", "running_var": "x"}})["estimate"]
    state = {"research_lab": {"specification_runs": [{**rd_est, "spec_id": "rd", "label": "RD"}]}, "estimate": est}
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    files = _unzip(build_package(state), pkg)
    assert len(files) == 2
    ns = _run_script(pkg)
    assert "run_1" in ns and "run_2" in ns
