"""会话存储（facade 收敛 Task 1 / Task 4）。

职责一句话：**持有会话元数据与 session state，作为 facade 层的
单一真相（single source of truth），负责增删改查、CSV 路径与降级日志。**

Task 4 决策：以 `SessionStore.sessions` 为上层的**显式**状态存储，
LangGraph 的 checkpointer 只服务于完整 graph 管道（run_upload_pipeline）内部
的持久化，facade 不再对它做"先内存再 checkpoint"的隐式回退读取。

- 移除旧 `get_state` 里"先查 `_sessions`、再回退 `graph.get_state`"的隐式优先级
  分支；`get_state` 现在只读 `sessions[].state`（单一读取路径），未知 session
  直接 404。
- 单节点 HITL 写路径（generate_chapter / edit / regen / translate ...）一律走
  `save_state` / `update_state` 落进本存储，与 checkpointer 不存在双写分叉。
- `AgentFacade.__init__` 将 `self._sessions` / `self._degradations` 指向
  `self._store.sessions` / `self._store.degradations`，因此
  `facade._sessions == {}`、`facade._degradations.pop(sid)` 等既有断言/清理
  保持原语义。

持久化（P1-3）：写穿透到 ``settings.SESSIONS_PATH``（JSON，原子替换写），
启动时加载。进程重启 / 单机重新部署后 session、state、owner、CSV 路径、
降级日志均可恢复；磁盘写失败打 stderr 但不阻断主流程（与 run_store 的
fail-open 哲学一致，内存态仍是权威）。多副本部署仍需外置存储，当前单进程
部署形态下文件持久化已闭合"重启即失忆"的洞。
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from config import ensure_private_directory, ensure_private_file, settings


class SessionStore:
    """会话存储：元数据 + state + CSV 路径 + 降级日志（文件持久化）。"""

    def __init__(self) -> None:
        # 会话元数据 + state：
        #   {session_id: {"state": {...}, "csv_path": str, "user_id": int, ...}}
        # LangGraph 管道最终 state 也镜像到此处（run_upload_pipeline 落盘）。
        self.sessions: dict = {}
        # 降级日志（F7）：{session_id: [{node, reason, fallback, timestamp}]}
        self.degradations: dict[str, list[dict]] = {}
        self._path: Path = Path(settings.SESSIONS_PATH)
        self._load()
        self._flush()

    # ------------------------------------------------------------------
    # 文件持久化（write-through，原子替换写）
    # ------------------------------------------------------------------
    def _load(self) -> None:
        """启动恢复：读回上次进程的 sessions + degradations。"""
        path = self._path
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self.sessions = data.get("sessions", {}) or {}
                self.degradations = data.get("degradations", {}) or {}
        except Exception as exc:  # 损坏文件：备份后从空开始，不让启动崩
            print(
                f"⚠ SessionStore: failed to load {path} ({exc}); "
                "backing it up and starting fresh",
                file=sys.stderr,
            )
            try:
                path.rename(path.with_suffix(path.suffix + ".corrupt"))
            except Exception:
                pass

    def flush(self) -> None:
        """把内存态原子写入磁盘。失败打日志但不抛（fail-open）。"""
        try:
            ensure_private_directory(self._path.parent)
            tmp = self._path.with_suffix(self._path.suffix + ".tmp")
            tmp.write_text(
                json.dumps(
                    {"sessions": self.sessions, "degradations": self.degradations},
                    ensure_ascii=False,
                    default=str,
                ),
                encoding="utf-8",
            )
            ensure_private_file(tmp)
            os.replace(tmp, self._path)
            ensure_private_file(self._path)
        except Exception as exc:
            print(f"⚠ SessionStore: flush failed: {exc}", file=sys.stderr)

    def _flush(self) -> None:
        self.flush()

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------
    def has(self, session_id: str) -> bool:
        return session_id in self.sessions

    def create(self, session_id: str, user_id: Optional[int]) -> str:
        self.sessions[session_id] = {"user_id": user_id}
        self._flush()
        return session_id

    def get_owner(self, session_id: str) -> Optional[int]:
        entry = self.sessions.get(session_id)
        if entry is None:
            return None
        return entry.get("user_id")

    def list_by_user(self, user_id: int) -> list[str]:
        return [
            sid
            for sid, entry in self.sessions.items()
            if entry.get("user_id") == user_id
        ]

    def delete(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._flush()
            return True
        return False

    # ------------------------------------------------------------------
    # State（单一真相：只读本存储，不再回退 checkpointer）
    # ------------------------------------------------------------------
    def get_state(self, session_id: str) -> dict:
        """返回 session 的 state dict（未知 session 抛 404）。

        单一读取路径：只读 ``sessions[].state``。不做"先内存再 checkpoint"
        的隐式 fallback，避免状态分叉。
        """
        if session_id in self.sessions:
            return self.sessions[session_id].get("state", {}) or {}
        raise HTTPException(status_code=404, detail="Session not found")

    def save_state(self, session_id: str, state: dict) -> None:
        """覆盖 session 的 state（未知 session 抛 404）。"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        self.sessions[session_id]["state"] = state
        self._flush()

    def update_state(self, session_id: str, **fields) -> dict:
        """将字段合并进 state 并返回新 state。"""
        state = self.get_state(session_id)
        state = {**state, **fields}
        self.save_state(session_id, state)
        return state

    def get_entry(self, session_id: str) -> dict:
        """返回原始会话条目（metadata + csv_path + state 等）。"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        return self.sessions[session_id]

    # ------------------------------------------------------------------
    # CSV 路径 / 数据集元数据
    # ------------------------------------------------------------------
    def get_csv_path(self, session_id: str) -> str:
        """解析会话的 CSV 路径；本地缺失且 S3 可用时透明拉取缓存。"""
        entry = self.get_entry(session_id)
        csv_path = entry.get("csv_path")
        if not csv_path:
            state = entry.get("state", {}) or {}
            datasets = state.get("uploaded_datasets", []) or []
            if datasets and datasets[0].get("path"):
                csv_path = datasets[0]["path"]
        if not csv_path:
            raise HTTPException(
                status_code=400, detail="No dataset path in session"
            )

        # 本地文件不存在时，尝试从 S3 缓存拉取
        if not os.path.exists(csv_path) and settings.S3_ENDPOINT_URL:
            try:
                from storage.s3 import s3_fs as _s3_fs
                s3_remote = f"{session_id}/data.csv"
                if _s3_fs.exists(s3_remote):
                    cache_dir = Path(settings.S3_CACHE_DIR)
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    local_cache = cache_dir / f"{session_id}.csv"
                    _s3_fs.download_to_file(s3_remote, local_cache)
                    csv_path = str(local_cache)
                    entry["csv_path"] = csv_path
            except Exception:
                pass  # 降级：使用原始路径（会触发下游 404）

        return csv_path

    def set_csv_path(self, session_id: str, csv_path: str) -> None:
        """在会话条目上持久化 CSV 路径。"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {"state": {}}
        self.sessions[session_id]["csv_path"] = csv_path
        self._flush()

    def get_datasets(self, session_id: str) -> list:
        """返回会话数据集列表（清洗包装用）。"""
        entry = self.get_entry(session_id)
        csv_path = entry.get("csv_path")
        if csv_path:
            return [{"path": csv_path}]
        state = entry.get("state", {}) or {}
        return list(state.get("uploaded_datasets", []) or [])

    def save_datasets(self, session_id: str, datasets: list) -> None:
        """将数据集元数据写回会话 state。"""
        state = self.get_state(session_id)
        state["uploaded_datasets"] = datasets
        self.save_state(session_id, state)

    # ------------------------------------------------------------------
    # 降级日志（F7）
    # ------------------------------------------------------------------
    def record_degradation(
        self,
        session_id: str,
        node: str,
        reason: str,
        fallback: str,
        visible: bool = False,
    ) -> None:
        """记录一次降级事件。"""
        if session_id not in self.degradations:
            self.degradations[session_id] = []
        self.degradations[session_id].append({
            "node": node,
            "reason": reason,
            "fallback": fallback,
            "visible": visible,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self._flush()

    def get_degradations(self, session_id: str) -> list[dict]:
        """返回会话的降级日志。"""
        return self.degradations.get(session_id, [])

    # ------------------------------------------------------------------
    # 测试助手（保持 seed_state / drop_session 语义）
    # ------------------------------------------------------------------
    def seed(self, session_id: str, state: dict) -> None:
        """Test helper: 直接往会话存储注入 state。"""
        self.sessions[session_id] = {"state": state}
        self._flush()

    def drop(self, session_id: str) -> None:
        """Test helper: 从存储移除会话。"""
        self.sessions.pop(session_id, None)
        self._flush()
