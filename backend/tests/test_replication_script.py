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


def _unzip(blob: bytes, dest: Path) -> None:
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        assert sorted(zf.namelist()) == ["README.md", "analysis_data.csv", "replication.py"]
        zf.extractall(dest)


def test_package_reproduces_every_recorded_number(client, tmp_path):
    sid = _card_session(client, "repl-upload")
    runs = _run_space(client, sid, "repl-space")
    assert runs, "Card space should produce ok runs"

    resp = client.get(f"/sessions/{sid}/replication-package")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/zip"
    _unzip(resp.content, tmp_path)

    # the packaged data is byte-identical to the file the runs read
    packaged = (tmp_path / "analysis_data.csv").read_bytes()
    assert hashlib.sha256(packaged).hexdigest() == runs[-1]["analysis_dataset"]["hash"]

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        ns = runpy.run_path(str(tmp_path / "replication.py"))  # actually run it
    finally:
        os.chdir(cwd)

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
    _unzip(client.get(f"/sessions/{sid}/replication-package").content, tmp_path)
    with open(tmp_path / "analysis_data.csv", "a") as fh:
        fh.write("\n")
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(tmp_path / "replication.py"))
    finally:
        os.chdir(cwd)
    assert "不一致" in str(exc.value)
