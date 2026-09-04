"""Run 工件目录（trace / checkpoints / outputs）契约测试。

北极星"每一步可查"的磁盘级落地面：
1. 上传管线 → lease-epoch 工作区 + 数据库 Run 事件存在
2. 章节生成 → generate_chapter 与 review_chapter 事件可读（含分数）
3. 审批硬证据门 409 → force 通过 → approve_chapter forced 事件
4. 人工评审决策 accept 落 trace
5. 导出 → outputs/export/ 有归档文件，export_docx 事件记录
6. 只读端点 GET /artifacts 与 GET /trace 形状正确；删除会话清空工件
"""

from __future__ import annotations

import asyncio
import shutil
import uuid

import run_store
from conftest import make_write_ready_state
from facade import facade
from run_repository import RunRepository


def _seed(**overrides) -> str:
    sid = f"test-run-{uuid.uuid4().hex[:10]}"
    facade.seed_state(sid, make_write_ready_state(**overrides))
    return sid


def test_upload_pipeline_writes_attempt_artifacts_and_durable_events(client, sample_csv_path):
    """Runner 将上传产物隔离到 lease epoch，并持久化有序 Run 事件。"""
    with open(sample_csv_path, "rb") as f:
        resp = client.post(
            "/upload",
            files={"file": ("sample.csv", f, "text/csv")},
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
    assert resp.status_code == 202, resp.text
    accepted = resp.json()
    from runner import process_one_run

    assert asyncio.run(
        process_one_run(owner="run-artifacts-test", run_id=accepted["run_id"])
    )
    sid = accepted["session_id"]

    files = {f["path"] for f in run_store.list_files(sid)}
    attempt_prefix = f"attempts/{accepted['run_id']}/epoch-1/"
    assert any(p.startswith(attempt_prefix) for p in files), (
        f"清洗产物应落在当前 lease epoch 工作区: {sorted(files)}"
    )

    events = asyncio.run(RunRepository().events_after(accepted["run_id"], 0))
    event_types = [event.event_type for event in events]
    assert event_types[0] == "run.accepted"
    assert "run.claimed" in event_types
    assert event_types[-1] == "run.succeeded"
    progress = [event.payload for event in events if event.event_type == "run.progress"]
    assert {item.get("node") for item in progress} == {"upload_data", "clean_data"}


def test_generate_and_review_events_traced(client):
    """写章后 trace 里有 generate_chapter 与 review_chapter（含分数）。"""
    sid = _seed()
    gen = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    assert gen.status_code == 200, gen.text

    events = run_store.tail_events(sid, limit=50)
    nodes = [e["node"] for e in events]
    assert "generate_chapter" in nodes
    assert "review_chapter" in nodes

    review = next(e for e in events if e["node"] == "review_chapter")
    assert isinstance(review["detail"].get("score"), float)

    files = {f["path"] for f in run_store.list_files(sid)}
    snap_files = [p for p in files if p.startswith("checkpoints/") and p != "checkpoints/_seq"]
    assert snap_files, f"应有 state 快照: {sorted(files)}"


def test_approve_gate_leaves_forced_trace(client):
    """409 → force 放行：approve_chapter 事件 status=forced 可查。"""
    sid = _seed()
    client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    blocked = client.post(f"/sessions/{sid}/approve-chapter", json={})
    assert blocked.status_code == 409

    events_before = [e["node"] for e in run_store.tail_events(sid, limit=50)]
    assert "approve_chapter" not in events_before, "被拒绝的审批不留事件"

    forced = client.post(
        f"/sessions/{sid}/approve-chapter", json={"force": True}
    )
    assert forced.status_code == 200

    events = run_store.tail_events(sid, limit=50)
    approve = [e for e in events if e["node"] == "approve_chapter"]
    assert len(approve) == 1
    assert approve[0]["status"] == "forced"
    assert approve[0]["detail"]["reviewer_bypassed_review"] is True


def test_clean_approval_traces_ok(client):
    """评审达标的章节正常审批 → approve_chapter status=ok。"""
    sid = _seed(
        body_chapters=[
            {
                "type": "intro",
                "title": "引言",
                "content": "正文。",
                "versions": ["v1"],
                "status": "generated",
            }
        ],
        review_scores=[0.95],
    )
    resp = client.post(f"/sessions/{sid}/approve-chapter", json={})
    assert resp.status_code == 200, resp.text
    approve = [
        e for e in run_store.tail_events(sid, limit=50)
        if e["node"] == "approve_chapter"
    ]
    assert len(approve) == 1
    assert approve[0]["status"] == "ok"
    assert "reviewer_bypassed_review" not in approve[0].get("detail", {})


def test_review_decision_traced(client):
    """人工 accept 决策落 trace。"""
    sid = _seed(
        body_chapters=[
            {
                "type": "intro",
                "title": "引言",
                "content": "正文。",
                "versions": ["v1"],
                "status": "generated",
            }
        ],
        review_scores=[0.9],
        current_chapter_index=1,
    )
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "accept", "reviewer": "human"},
    )
    assert resp.status_code == 200, resp.text
    dec = [
        e for e in run_store.tail_events(sid, limit=50)
        if e["node"] == "review_decision"
    ]
    assert len(dec) == 1
    assert dec[0]["status"] == "accept"
    assert dec[0]["detail"]["reviewer"] == "human"


def test_export_archives_outputs_to_run_dir(client):
    """导出后 outputs/export/ 至少归档 paper.tex；export_docx 事件可查。"""
    sid = _seed()
    gen = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    assert gen.status_code == 200, gen.text

    export = client.get(
        f"/sessions/{sid}/doc-export", params={"format": "tex"}
    )
    assert export.status_code == 200, export.text
    body = {}  # tex 端点返回纯文本；归档信息从 trace 断言
    archived = run_store.list_files(sid)
    exported_files = {
        f["path"] for f in archived if f["path"].startswith("outputs/export/")
    }
    degraded = bool(body.get("degraded"))
    if not degraded:
        assert exported_files, (
            f"非降级导出必须有归档: {sorted(exported_files)} | body={body}"
        )
        assert any(p.endswith("paper.tex") for p in exported_files)
    event = next(
        e for e in run_store.tail_events(sid, limit=50)
        if e["node"] == "export_docx"
    )
    assert event["detail"]["template"] == "cn_journal"


def test_artifacts_and_trace_endpoints(client):
    """GET /artifacts 与 /trace 返回模型形状正确。"""
    sid = _seed()
    facade.record_event(sid, "ping_node", status="ok", detail={"k": "v"})
    a = client.get(f"/sessions/{sid}/artifacts")
    assert a.status_code == 200
    body = a.json()
    assert body["session_id"] == sid
    assert body["exists"] is True
    assert isinstance(body["files"], list)
    t = client.get(f"/sessions/{sid}/trace?limit=10")
    assert t.status_code == 200
    tb = t.json()
    assert tb["events"], "至少有一条 ping_node 事件"
    assert tb["events"][-1]["node"] == "ping_node"

    missing = client.get("/sessions/does-not-exist/artifacts")
    assert missing.status_code == 404


def test_delete_session_removes_run_dir():
    """删除会话同时清除磁盘工件（隐私优先）。"""
    sid = f"test-run-del-{uuid.uuid4().hex[:8]}"
    facade.create_session(session_id=sid)
    run_store.append_event(sid, "some_node")
    d = run_store.run_dir(sid)
    assert d.exists()

    assert facade.delete_session(sid) is True
    assert not d.exists()
    # 二次删除：会话已不存在，返回 False 且不抛错
    assert facade.delete_session(sid) is False


def test_delete_session_logs_remote_artifact_failure(monkeypatch, caplog):
    from config import settings
    from storage.s3 import s3_fs

    sid = facade.create_session()
    monkeypatch.setattr(settings, "S3_ENDPOINT_URL", "http://object-store.invalid")
    monkeypatch.setattr(s3_fs, "delete", lambda _remote_path: False)

    with caplog.at_level("WARNING", logger="facade"):
        assert facade.delete_session(sid) is True

    assert "remote_session_artifact_delete_failed" in caplog.text


def teardown_function() -> None:
    """兜底清理：测试产生的 run 目录不留在本地。"""
    root = run_store.runs_root()
    if root.exists():
        for child in root.glob("test-run-*"):
            shutil.rmtree(child, ignore_errors=True)
