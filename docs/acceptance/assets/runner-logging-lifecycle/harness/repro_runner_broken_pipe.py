"""Full-stack reproduction harness for issue #30 (runner logging lifecycle).

Drives the REAL product stack in an isolated environment:

- backend: uvicorn main:app on a dedicated port (default 8002) with its own
  ECONPAPER_LOCAL_STATE_ROOT, DEBUG=true, ECONPAPER_LLM=mock.
- runner: ``python -m runner`` as a subprocess whose fd1+fd2 either both point
  to a pipe whose read end is already closed (the production incident form,
  verified by lsof in the 2026-09-06 audit) or to a healthy log file.
- one real ``POST /demos/card`` upload run is admitted and awaited to a
  terminal state through the public API.

The harness is read-only with respect to product code: it never patches the
app. Evidence-only instrumentation for the runner process family is injected
via PYTHONPATH (sitecustomize.py in this directory, activated by
RUNNER_LOG_EVIDENCE_FILE).

Usage:
    python repro_runner_broken_pipe.py --phase pre|post \
        --condition dead-pipe|healthy-stderr --evidence-dir DIR \
        [--port 8002] [--workdir DIR] [--timeout 300]

Exit code is 0 when the run reached a terminal state (any terminal state);
the evidence JSON records which state. Script failures exit non-zero.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parents[5]
BACKEND = REPO / "backend"
HARNESS_DIR = Path(__file__).resolve().parent
VENV_PYTHON = BACKEND / ".venv" / "bin" / "python"

TERMINAL_RUN_STATES = {"SUCCEEDED", "FAILED", "CANCELLED"}


def _wait_health(client: httpx.Client, deadline: float) -> None:
    while time.monotonic() < deadline:
        try:
            resp = client.get("/health")
            if resp.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.5)
    raise RuntimeError("backend did not become healthy in time")


def _wait_terminal(client: httpx.Client, run_id: str, deadline: float) -> dict:
    last = {}
    while time.monotonic() < deadline:
        resp = client.get(f"/runs/{run_id}")
        if resp.status_code == 200:
            last = resp.json()
            if last.get("status") in TERMINAL_RUN_STATES:
                return last
        time.sleep(1.0)
    raise RuntimeError(f"run {run_id} did not terminate in time; last={last}")


def _session_snapshot(client: httpx.Client, session_id: str) -> dict:
    resp = client.get(f"/sessions/{session_id}")
    resp.raise_for_status()
    full = resp.json()
    research = full.get("research") or {}
    datasets = full.get("datasets") or full.get("data") or []
    return {
        "session_id": session_id,
        "upload_readiness": full.get("upload_readiness"),
        "keys": sorted(full.keys()),
        "dataset_count": len(datasets) if isinstance(datasets, list) else None,
        "has_research_lab": bool(research),
        "active_run": full.get("active_run"),
        "degradations": full.get("degradations"),
    }


def _lsof_runner(pid: int) -> str:
    try:
        completed = subprocess.run(
            ["lsof", "-p", str(pid), "-a", "-d", "0,1,2"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return completed.stdout
    except (OSError, subprocess.SubprocessError) as exc:
        return f"lsof failed: {exc}"


def _dir_listing(root: Path, limit: int = 200) -> list[dict]:
    items: list[dict] = []
    if not root.exists():
        return items
    for path in sorted(root.rglob("*")):
        if path.is_file():
            items.append(
                {
                    "path": str(path.relative_to(root)),
                    "bytes": path.stat().st_size,
                }
            )
        if len(items) >= limit:
            break
    return items


def _sqlite_dump(db_path: Path, run_id: str) -> dict:
    if not db_path.exists():
        return {"error": f"no database at {db_path}"}
    uri = f"file:{db_path}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True, timeout=5)
    except sqlite3.Error as exc:
        return {"error": f"connect failed: {exc}"}
    try:
        run_row = conn.execute(
            "SELECT run_id, session_id, kind, status, error, attempt, "
            "lease_owner, created_at, updated_at FROM runs WHERE run_id=?",
            (run_id,),
        ).fetchone()
        columns = (
            "run_id",
            "session_id",
            "kind",
            "status",
            "error",
            "attempt",
            "lease_owner",
            "created_at",
            "updated_at",
        )
        run_record = dict(zip(columns, run_row)) if run_row else None
        events = [
            {"seq": row[0], "event_type": row[1], "created_at": row[2]}
            for row in conn.execute(
                "SELECT seq, event_type, created_at FROM run_events "
                "WHERE run_id=? ORDER BY seq",
                (run_id,),
            ).fetchall()
        ]
        session_state = conn.execute(
            "SELECT state FROM research_sessions WHERE session_id=("
            "SELECT session_id FROM runs WHERE run_id=?)",
            (run_id,),
        ).fetchone()
        state_json = session_state[0] if session_state else None
        state_excerpt: object = None
        if state_json:
            try:
                parsed = json.loads(state_json)
                state_excerpt = {
                    "upload_readiness": parsed.get("upload_readiness"),
                    "has_uploaded_datasets": bool(
                        parsed.get("uploaded_datasets")
                    ),
                    "dataset_meta_keys": sorted(
                        (parsed.get("dataset_meta") or {}).keys()
                    )
                    if isinstance(parsed.get("dataset_meta"), dict)
                    else None,
                    "csv_path_present": bool(parsed.get("csv_path")),
                }
            except json.JSONDecodeError:
                state_excerpt = "unparseable state json"
        return {
            "run": run_record,
            "run_events": events,
            "run_event_count": len(events),
            "session_state_excerpt": state_excerpt,
        }
    finally:
        conn.close()


def _stop(process: subprocess.Popen, name: str) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        try:
            process.terminate()
        except OSError:
            return
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        process.wait(timeout=10)
    print(f"[harness] stopped {name} pid={process.pid}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("pre", "post"), required=True)
    parser.add_argument(
        "--condition", choices=("dead-pipe", "healthy-stderr"), required=True
    )
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8002)
    parser.add_argument("--workdir", type=Path, default=None)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--keep-workdir", action="store_true")
    args = parser.parse_args()

    if sys.executable != str(VENV_PYTHON):
        print(
            f"[harness] re-exec with backend venv python ({VENV_PYTHON})",
            flush=True,
        )
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__, *sys.argv[1:]])

    workdir = args.workdir or Path(
        f"/tmp/econpaper-runner-logging-{args.phase}-{args.condition}"
    )
    if workdir.exists() and not args.keep_workdir:
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    state_root = workdir / "state"
    evidence_dir = args.evidence_dir
    evidence_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.update(
        {
            "DEBUG": "true",
            "ECONPAPER_LLM": "mock",
            "ECONPAPER_LOCAL_STATE_ROOT": str(state_root),
            "RUNNER_CONCURRENCY": "1",
            "PYTHONPATH": f"{REPO}:{BACKEND}",
            "ECONPAPER_RUNNER_LOG_FILE": str(
                state_root / "log" / "runner.log"
            ),
        }
    )

    backend_log = open(workdir / "backend.log", "ab")
    backend = subprocess.Popen(
        [
            str(VENV_PYTHON),
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.port),
        ],
        cwd=BACKEND,
        env=env,
        stdout=backend_log,
        stderr=backend_log,
        start_new_session=True,
    )
    print(f"[harness] backend pid={backend.pid} port={args.port}", flush=True)

    base = f"http://127.0.0.1:{args.port}"
    runner = None
    runner_log_handle = None
    pipe_write_end = None
    try:
        with httpx.Client(timeout=30, base_url=base) as client:
            _wait_health(client, time.monotonic() + 90)

            runner_env = env.copy()
            runner_env["PYTHONPATH"] = f"{HARNESS_DIR}:{REPO}:{BACKEND}"
            runner_env["RUNNER_LOG_EVIDENCE_FILE"] = str(
                workdir / "runner-logging-evidence.log"
            )

            if args.condition == "dead-pipe":
                # The production incident form: both fd1 and fd2 point at a
                # pipe whose read end is closed before the runner logs
                # anything. lsof snapshot below documents the shape.
                read_end, write_end = os.pipe()
                os.close(read_end)
                pipe_write_end = write_end
                stdout_target = write_end
                stderr_target = write_end
            else:
                runner_log_handle = open(
                    workdir / "runner-console.log", "ab"
                )
                stdout_target = runner_log_handle.fileno()
                stderr_target = runner_log_handle.fileno()

            runner = subprocess.Popen(
                [
                    str(VENV_PYTHON),
                    "-m",
                    "runner",
                    "--poll-seconds",
                    "0.2",
                    "--concurrency",
                    "1",
                ],
                cwd=BACKEND,
                env=runner_env,
                stdout=stdout_target,
                stderr=stderr_target,
                start_new_session=True,
            )
            if pipe_write_end is not None:
                os.close(pipe_write_end)
                pipe_write_end = None
            if runner_log_handle is not None:
                runner_log_handle.close()
                runner_log_handle = None
            print(
                f"[harness] runner pid={runner.pid} condition={args.condition}",
                flush=True,
            )
            time.sleep(1.0)
            lsof = _lsof_runner(runner.pid)
            (evidence_dir / "runner-lsof.txt").write_text(
                f"# condition={args.condition} phase={args.phase} "
                f"runner_pid={runner.pid}\n{lsof}\n",
                encoding="utf-8",
            )

            key = str(uuid.uuid4())
            resp = client.post(
                "/demos/card",
                json=None,
                headers={"Idempotency-Key": key},
            )
            print(
                f"[harness] POST /demos/card -> {resp.status_code}",
                flush=True,
            )
            if resp.status_code != 202:
                raise RuntimeError(f"demo card admission failed: {resp.text}")
            accepted = resp.json()
            run_id = accepted["run_id"]
            session_id = accepted["session_id"]

            summary: dict = {
                "phase": args.phase,
                "condition": args.condition,
                "port": args.port,
                "state_root": str(state_root),
                "backend_pid": backend.pid,
                "runner_pid": runner.pid,
                "idempotency_key": key,
                "run_id": run_id,
                "session_id": session_id,
            }

            run = _wait_terminal(client, run_id, time.monotonic() + args.timeout)
            summary["run_api"] = run
            summary["session_api"] = _session_snapshot(client, session_id)
            print(
                f"[harness] run terminal: status={run.get('status')} "
                f"error={run.get('error')!r}",
                flush=True,
            )
    finally:
        if runner is not None:
            _stop(runner, "runner")
        _stop(backend, "backend")
        if pipe_write_end is not None:
            try:
                os.close(pipe_write_end)
            except OSError:
                pass
        if runner_log_handle is not None:
            runner_log_handle.close()
        backend_log.close()

    # Processes are down; read the isolated sqlite state read-only.
    summary["db"] = _sqlite_dump(state_root / "db" / "econpaper.db", run_id)
    summary["uploads_listing"] = _dir_listing(state_root / "uploads")
    summary["runs_listing"] = _dir_listing(state_root / "runs")

    evidence_log = workdir / "runner-logging-evidence.log"
    if evidence_log.exists():
        content = evidence_log.read_text(encoding="utf-8", errors="replace")
        (evidence_dir / "runner-logging-evidence.log").write_text(
            content, encoding="utf-8"
        )
        summary["logging_evidence_lines"] = len(content.splitlines())
    else:
        summary["logging_evidence_lines"] = 0

    for name in ("backend.log", "runner-console.log"):
        source = workdir / name
        if source.exists():
            text = source.read_text(encoding="utf-8", errors="replace")
            (evidence_dir / name).write_text(text, encoding="utf-8")
            summary[f"{name}_lines"] = len(text.splitlines())

    # The durable file channel configured through ECONPAPER_RUNNER_LOG_FILE.
    runner_file_log = state_root / "log" / "runner.log"
    if runner_file_log.exists():
        text = runner_file_log.read_text(encoding="utf-8", errors="replace")
        (evidence_dir / "runner-file.log").write_text(text, encoding="utf-8")
        summary["runner_file_log_lines"] = len(text.splitlines())

    (evidence_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        "[harness] summary written to "
        f"{evidence_dir / 'summary.json'}",
        flush=True,
    )
    if not args.keep_workdir:
        shutil.rmtree(workdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
