"""Run 工件存储（北极星："每一步可查" 从字段级落成磁盘级）。

每个 session 对应一个 run 目录（参照 Apodex FrontierAgent 的
``.apodex/runs/<session-id>/`` 布局），论文生成过程中的每一次节点执行、
每一份产物都在磁盘上有据可查：

    runs/<session_id>/
    ├── manifest.json          # 会话元信息（来源 CSV、导出清单等）
    ├── trace.jsonl            # 追加式事件流：一次节点执行 = 一行 JSON
    ├── checkpoints/           # 每个关键步骤后的完整 state 快照
    │   └── latest.json        # 始终指向最新快照
    └── outputs/               # 持久交付物（导出的 tex/pdf/docx 副本）
        └── export/

约定：
- trace.jsonl 只追加，永不改写；事件含 ISO 时间戳、毫秒耗时与状态。
- checkpoints 里存整个 state dict（默认 ``json.dumps(default=str)``）。
- outputs/export 下的文件是导出产物的稳定副本：源文件可能在 workspace
  里被后续覆盖，这里的副本是"当时交付的那一份"。
"""

from __future__ import annotations

import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from config import settings


def runs_root() -> Path:
    """所有 run 目录的根。环境变量 RUNS_DIR 可覆盖，默认 ./runs。"""
    return Path(settings.RUNS_DIR)


def run_dir(session_id: str) -> Path:
    """某 session 的 run 目录（不创建）。"""
    return runs_root() / session_id


def ensure_run_dir(session_id: str) -> Path:
    """创建（幂等）run 目录结构并返回其路径。"""
    d = run_dir(session_id)
    (d / "checkpoints").mkdir(parents=True, exist_ok=True)
    (d / "outputs" / "export").mkdir(parents=True, exist_ok=True)
    return d


def write_manifest(session_id: str, **fields: Any) -> dict:
    """写入 / 合并 manifest.json，返回合并后的内容。

    已有字段优先保留；调用方给的同名字段覆盖旧值。
    """
    d = ensure_run_dir(session_id)
    path = d / "manifest.json"
    manifest: dict = {}
    if path.exists():
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
    if "created_at" not in manifest:
        manifest["created_at"] = _now_iso()
    manifest.update(fields)
    manifest["session_id"] = session_id
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return manifest


def read_manifest(session_id: str) -> Optional[dict]:
    path = run_dir(session_id) / "manifest.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def append_event(
    session_id: str,
    node: str,
    status: str = "ok",
    duration_ms: Optional[float] = None,
    detail: Optional[dict] = None,
) -> Optional[dict]:
    """向 trace.jsonl 追加一条事件，返回写入的事件 dict。

    失败不抛异常：工件记录永远不能弄坏主流程（fail-open 观测面）。
    """
    event: dict = {
        "ts": _now_iso(),
        "node": node,
        "status": status,
    }
    if duration_ms is not None:
        event["duration_ms"] = round(duration_ms, 1)
    if detail:
        clean = {k: v for k, v in detail.items() if v is not None}
        if clean:
            event["detail"] = clean
    try:
        d = ensure_run_dir(session_id)
        with (d / "trace.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
        return event
    except Exception:
        return None


def snapshot_state(session_id: str, label: str, state: dict) -> Optional[str]:
    """把 state 完整快照到 checkpoints/，同时刷新 latest.json。"""
    seq_file = run_dir(session_id) / "checkpoints" / "_seq"
    try:
        d = ensure_run_dir(session_id)
        seq_file = d / "checkpoints" / "_seq"
        try:
            seq = int(seq_file.read_text().strip()) + 1
        except Exception:
            seq = 1
        seq_file.write_text(str(seq), encoding="utf-8")
        stamp = datetime.now(timezone.utc).strftime("%H%M%S%f")[:10]
        name = f"{seq:04d}_{label}_{stamp}.json"
        payload = json.dumps(state, ensure_ascii=False, indent=2, default=str)
        cp = d / "checkpoints" / name
        cp.write_text(payload, encoding="utf-8")
        (d / "checkpoints" / "latest.json").write_text(payload, encoding="utf-8")
        return str(cp)
    except Exception:
        return None


def register_export(session_id: str, paths: list[Path]) -> list[dict]:
    """把导出产物复制进 outputs/export/ 并登记到 manifest.exports。

    返回复制后的相对路径信息列表。缺失的源文件跳过（降级语义）。
    """
    copied: list[dict] = []
    dest_dir = ensure_run_dir(session_id) / "outputs" / "export"
    for p in paths:
        src = Path(p) if p else None
        if not src or not src.is_file():
            continue
        dest = dest_dir / src.name
        try:
            shutil.copy2(src, dest)
            copied.append({"name": dest.name, "bytes": dest.stat().st_size})
        except Exception:
            continue
    if copied:
        manifest = read_manifest(session_id) or {}
        exports = list(manifest.get("exports") or [])
        exports.append({"ts": _now_iso(), "files": copied})
        write_manifest(session_id, exports=exports)
    return copied


def tail_events(session_id: str, limit: int = 50) -> list[dict]:
    """读 trace.jsonl 最后 limit 条事件（旧→新顺序返回尾部）。"""
    path = run_dir(session_id) / "trace.jsonl"
    if not path.exists():
        return []
    events: list[dict] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        continue
    except Exception:
        return []
    return events[-limit:]


def list_files(session_id: str) -> list[dict]:
    """枚举 run 目录下全部文件（相对路径 + 字节数）。"""
    root = run_dir(session_id)
    out: list[dict] = []
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "_seq":
            out.append(
                {"path": str(p.relative_to(root)), "bytes": p.stat().st_size}
            )
    return out


class TrackedStep:
    """facade 用的计时追踪上下文管理器。

    用法::

        with TrackedStep(sid, "generate_chapter"):
            ...原逻辑...

    正常退出 → 记 ok 事件；抛异常 → 记 error 事件并原样重抛。
    异常时取 self.snapshot_state（若设置）仍会尝试快照当前 state，
    便于事后排查"死前状态"。
    """

    def __init__(
        self,
        session_id: str,
        node: str,
        snapshot_label: Optional[str] = None,
        get_state_fn=None,
        detail: Optional[dict] = None,
    ) -> None:
        self._sid = session_id
        self._node = node
        self._snapshot_label = snapshot_label
        self._get_state_fn = get_state_fn
        self._extra_detail = detail or {}
        self._t0 = time.perf_counter()

    def __enter__(self) -> "TrackedStep":
        self._t0 = time.perf_counter()
        return self

    def set_detail(self, **kw: Any) -> None:
        """运行中途补充 detail 字段（如评审分数）。"""
        self._extra_detail.update(kw)

    def __exit__(self, exc_type, exc, tb) -> bool:
        duration_ms = (time.perf_counter() - self._t0) * 1000.0
        status = "error" if exc_type else "ok"
        if exc_type is not None:
            self._extra_detail.setdefault("error", f"{exc_type.__name__}: {exc}")
        append_event(self._sid, self._node, status, duration_ms, self._extra_detail)
        if self._snapshot_label and self._get_state_fn is not None and not exc_type:
            try:
                snapshot_state(self._sid, self._snapshot_label, self._get_state_fn())
            except Exception:
                pass
        return False  # 不吞异常


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
