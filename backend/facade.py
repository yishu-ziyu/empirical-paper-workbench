"""ADR-0003 Stage B: AgentFacade.

The facade decouples HTTP routers from the agent layer (LangGraph graph
+ node functions + cleaning steps). Routers depend only on the facade;
the facade is the single place that imports ``graph``, ``nodes.X``, and
``cleaning.X``.

Single module-level instance: ``facade = AgentFacade()``. Routers do
``from facade import facade`` and call methods on it.

Test patches: tests that previously patched ``routers.X.node_func`` should
patch the corresponding ``facade.<func>_node`` module-level name below
(e.g. ``facade.rollback_chapter_node``, ``facade.export_docx_node``,
``facade.generate_chapter_node``). Each facade method looks up its node
function via module globals at call time, so ``monkeypatch.setattr`` on
these names propagates immediately.
"""
from __future__ import annotations

import os
import shutil
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, List, Optional

import run_store
from config import settings
from fastapi import HTTPException

# ---------------------------------------------------------------------------
# Agent imports. Defensive so module load does not crash if agent deps
# are missing (e.g. partial CI build, agent/ not yet on sys.path).
# ---------------------------------------------------------------------------
try:
    from graph import graph as _graph  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - agent deps missing in some envs
    _graph = None

try:
    from nodes.set_direction import set_direction as set_direction_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    set_direction_node = None

try:
    from nodes.generate_outline import generate_outline as generate_outline_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    generate_outline_node = None

try:
    from nodes.identification_verify import identification_verify as identification_verify_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    identification_verify_node = None

try:
    from nodes.estimate import estimate as estimate_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    estimate_node = None

try:
    from nodes.robustness_check import robustness_check as robustness_check_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    robustness_check_node = None

try:
    from nodes.generate_chapter import generate_chapter as generate_chapter_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    generate_chapter_node = None

try:
    from nodes.review_chapter import review_chapter as review_chapter_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    review_chapter_node = None

try:
    from nodes.search_literature import search_literature as search_literature_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    search_literature_node = None

try:
    from nodes.citation_graph import build_citation_graph as build_citation_graph_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    build_citation_graph_node = None

try:
    from nodes.rollback import rollback_chapter as rollback_chapter_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - rollback node optional
    rollback_chapter_node = None

try:
    from nodes.export_docx import export_docx as export_docx_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    export_docx_node = None

try:
    from cleaning.transform import TransformStep as TransformStepCls  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    TransformStepCls = None

try:
    from cleaning.filter import FilterStep as FilterStepCls  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    FilterStepCls = None

try:
    from cleaning.balance import BalanceStep as BalanceStepCls  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    BalanceStepCls = None

try:
    from cleaning.profiling import _detect_dataset_type as detect_dataset_type_fn  # type: ignore[import-not-found]
    from cleaning.profiling import _load_charls_config as load_charls_config_fn  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    detect_dataset_type_fn = None
    load_charls_config_fn = None


class AgentFacade:
    """Facade that wraps the agent layer for HTTP routers.

    Routers should depend only on this facade — they must not import
    ``graph``, ``nodes.X``, or ``cleaning.X`` directly. The facade:

    1. Owns the in-memory session store (``_sessions``) and exposes
       ``get_state`` / ``save_state`` / ``get_csv_path`` helpers.
    2. Wraps ``graph.invoke`` for the upload pipeline.
    3. Wraps each single-node direct call (state-driven HITL pattern).
    4. Wraps the cleaning step ``run()`` calls.
    """

    def __init__(self) -> None:
        # Session metadata store (csv_path, charls_config, etc.).
        # The LangGraph State itself is persisted in Postgres via the
        # checkpointer — this dict only holds thin metadata needed by
        # HTTP routers that does not flow through the graph.
        self._sessions: dict = {}
        # Degradation log (F7): each entry is
        # {node, reason, fallback, timestamp}
        self._degradations: dict[str, list[dict]] = {}

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------
    def create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> str:
        """Create an empty session and return its id.

        If ``user_id`` is provided, the session is owned by that user.
        Anonymous sessions (no user_id) are created for unauthenticated uploads.
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        self._sessions[session_id] = {"user_id": user_id}
        # Run 工件目录：会话创建即建档（trace/checkpoints/outputs 的根）
        try:
            run_store.write_manifest(session_id, user_id=user_id)
        except Exception:
            pass  # 工件记录失败不阻断主流程
        return session_id

    def has_session(self, session_id: str) -> bool:
        return session_id in self._sessions

    def get_session_owner(self, session_id: str) -> Optional[int]:
        """Return the user_id that owns this session, or None if anonymous."""
        entry = self._sessions.get(session_id)
        if entry is None:
            return None
        return entry.get("user_id")

    def list_sessions_by_user(self, user_id: int) -> list[str]:
        """Return all session IDs owned by the given user."""
        return [
            sid
            for sid, entry in self._sessions.items()
            if entry.get("user_id") == user_id
        ]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if it existed, False otherwise.

        会话删除同时清掉磁盘上的 run 工件目录（隐私优先：删就是删，
        不留残余的 trace/快照）。
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            shutil.rmtree(run_store.run_dir(session_id), ignore_errors=True)
            return True
        shutil.rmtree(run_store.run_dir(session_id), ignore_errors=True)
        return False

    @staticmethod
    def instrument_fields(state: dict) -> dict:
        """Desk readout + outline/chapters the UI can rehydrate after refresh."""
        diag = state.get("identification_diag") or {}
        report = diag.get("report") if isinstance(diag, dict) else None
        blockers = [str(item) for item in (state.get("write_blockers") or []) if item]
        if state.get("star_rating") == 0 and "star_0" not in blockers:
            blockers = ["star_0", *blockers]
        rob = state.get("robustness_results")
        rob_status = None
        if isinstance(rob, dict) and rob:
            degs = state.get("degradations") or []
            if any(
                isinstance(item, dict)
                and "robust" in str(item.get("node") or "").lower()
                for item in degs
            ):
                rob_status = "degraded"
            else:
                rob_status = "ran"
        outline = [
            item
            for item in (state.get("outline") or [])
            if isinstance(item, dict)
        ]
        body_chapters = [
            item
            for item in (state.get("body_chapters") or [])
            if isinstance(item, dict)
        ]
        return {
            "claim": state.get("claim"),
            "star_rating": state.get("star_rating"),
            "identification_failed": bool(state.get("identification_failed")),
            "identification_report": report,
            "results": state.get("results"),
            "estimate": state.get("estimate"),
            "literature_source": state.get("literature_source"),
            "write_blockers": blockers,
            "robustness_status": rob_status,
            "outline": outline,
            "body_chapters": body_chapters,
            "research_direction": state.get("research_direction"),
        }

    def get_state(self, session_id: str) -> dict:
        """Return the state dict for a session (404 if missing).

        Precedence:
        1. In-memory ``_sessions`` entry (used by the single-node call
           pattern: ``set_direction_and_outline`` / ``generate_chapter``).
        2. Postgres checkpointer (used by the full graph pipeline:
           ``run_upload_pipeline``). This is a fallback so that the
           single-node pattern always sees its own state, not the
           stale graph-invoked state from the checkpointer.
        """
        if session_id in self._sessions:
            return self._sessions[session_id].get("state", {}) or {}
        # Fallback to the Postgres checkpointer (full-graph sessions).
        if _graph is not None:
            try:
                config = {"configurable": {"thread_id": session_id}}
                checkpoint = _graph.get_state(config)
                if checkpoint and checkpoint.values:
                    # Mirror into in-memory for subsequent reads.
                    self._sessions[session_id] = {"state": dict(checkpoint.values)}
                    return dict(checkpoint.values)
            except Exception:
                pass
        raise HTTPException(status_code=404, detail="Session not found")

    def save_state(self, session_id: str, state: dict) -> None:
        """Overwrite the session state (in-memory metadata only).

        The LangGraph state is persisted by the checkpointer automatically
        during graph.invoke() — this method is kept for the thin metadata
        layer (csv_path, charls_config, etc.) that routers need.
        """
        if session_id not in self._sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        self._sessions[session_id]["state"] = state

    def update_state(self, session_id: str, **fields) -> dict:
        """Merge fields into the session state and return the new state."""
        state = self.get_state(session_id)
        state = {**state, **fields}
        self.save_state(session_id, state)
        return state

    def get_session_entry(self, session_id: str) -> dict:
        """Return the raw session entry (metadata + csv_path etc.)."""
        if session_id not in self._sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        return self._sessions[session_id]

    def get_csv_path(self, session_id: str) -> str:
        """Resolve the CSV path stored for this session.

        If the local file does not exist but an S3 object is available,
        download it to the local cache transparently.
        """
        entry = self.get_session_entry(session_id)
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
                    # 更新 entry 的 csv_path 指向缓存
                    entry["csv_path"] = csv_path
            except Exception:
                pass  # 降级：使用原始路径（会触发下游 404）

        return csv_path

    def set_csv_path(self, session_id: str, csv_path: str) -> None:
        """Persist the CSV path on the session entry."""
        if session_id not in self._sessions:
            self._sessions[session_id] = {"state": {}}
        self._sessions[session_id]["csv_path"] = csv_path

    def get_datasets(self, session_id: str) -> list:
        """Return the dataset list for a session (wrapped for cleaning)."""
        entry = self.get_session_entry(session_id)
        csv_path = entry.get("csv_path")
        if csv_path:
            return [{"path": csv_path}]
        state = entry.get("state", {}) or {}
        return list(state.get("uploaded_datasets", []) or [])

    def save_datasets(self, session_id: str, datasets: list) -> None:
        """Persist updated dataset meta back into the session state."""
        state = self.get_state(session_id)
        state["uploaded_datasets"] = datasets
        self.save_state(session_id, state)

    # ------------------------------------------------------------------
    # Run 工件追踪（trace / checkpoints，见 run_store.py）
    # ------------------------------------------------------------------
    def _tracked(
        self,
        session_id: str,
        node: str,
        snapshot_label: Optional[str] = None,
    ) -> Any:
        """计时追踪一个节点执行段：ok/error 事件 + 可选 state 快照。

        用法::

            with self._tracked(sid, "generate_chapter", "generate_chapter") as t:
                result = generate_chapter_node(state)
                t.set_detail(chapter_index=...)
        """
        return run_store.TrackedStep(
            session_id,
            node,
            snapshot_label=snapshot_label,
            get_state_fn=lambda: self._sessions.get(session_id, {}).get("state")
            or {},
        )

    def record_event(
        self,
        session_id: str,
        node: str,
        status: str = "ok",
        duration_ms: float | None = None,
        detail: dict | None = None,
    ) -> None:
        """公开事件入口：router 层的一次关键动作（如审批）也进 trace。"""
        try:
            run_store.append_event(
                session_id, node, status=status, duration_ms=duration_ms,
                detail=detail,
            )
        except Exception:
            pass

    def _workspace_dir(self, session_id: str) -> str:
        """run 目录下的 workspace 路径（节点产物 tex/pdf/清洗 sidecar 的家）。"""
        ws = run_store.ensure_run_dir(session_id) / "workspace"
        ws.mkdir(parents=True, exist_ok=True)
        return str(ws)

    # ------------------------------------------------------------------
    # Graph invocation (upload pipeline)
    # ------------------------------------------------------------------
    def run_upload_pipeline(self, session_id: str, csv_path: str) -> dict:
        """Run the full LangGraph pipeline on a freshly uploaded CSV.

        Stores the final state + csv_path on the session entry and returns
        the final state dict.
        """
        if _graph is None:
            raise HTTPException(
                status_code=503,
                detail="LangGraph graph not available (agent module missing)",
            )
        initial_state = {
            "session_id": session_id,
            "csv_path": str(csv_path),
            "uploaded_datasets": [{"path": str(csv_path), "format": "csv"}],
            # 节点产物（清洗 sidecar / 导出 tex-pdf-docx）落进 run 目录，
            # 不再散落在 tempfile 里随风而逝。
            "workspace": self._workspace_dir(session_id),
        }
        try:
            run_store.write_manifest(
                session_id, source_csv=str(csv_path)
            )
        except Exception:
            pass
        with self._tracked(
            session_id, "upload_pipeline", "upload_pipeline"
        ) as t:
            final_state = _graph.invoke(
                initial_state,
                config={"configurable": {"thread_id": session_id}},
            )
            if isinstance(final_state, dict):
                t.set_detail(
                    cleaning_steps=len(
                        (
                            (final_state.get("cleaning_report") or {}).get(
                                "steps"
                            )
                            or []
                        )
                    )
                    or None,
                    degraded=bool(final_state.get("degradations")) or None,
                )
        # Persist final state + csv_path on the entry. Preserve the existing
        # ``user_id`` if set (F10: session ownership).
        existing = self._sessions.get(session_id, {})
        self._sessions[session_id] = {
            "state": final_state if isinstance(final_state, dict) else {},
            "csv_path": str(csv_path),
            "user_id": existing.get("user_id"),
        }
        return self._sessions[session_id]["state"]

    # ------------------------------------------------------------------
    # Single-node calls (state-driven HITL pattern)
    # ------------------------------------------------------------------
    def set_direction_and_outline(
        self, session_id: str, research_direction: dict
    ) -> dict:
        """Run the shared pre-write path: identify → estimate → robustness → literature → outline."""
        if set_direction_node is None or generate_outline_node is None:
            raise HTTPException(
                status_code=503,
                detail="outline nodes not available (agent module missing)",
            )
        try:
            from engine.prewrite import run_prewrite
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"prewrite unavailable: {exc}",
            ) from exc
        state = self.get_state(session_id)
        state = {**state, "research_direction": research_direction}
        if not state.get("csv_path"):
            entry = self._sessions.get(session_id) or {}
            csv_path = entry.get("csv_path")
            if csv_path:
                state["csv_path"] = csv_path
        if not state.get("workspace"):
            state["workspace"] = self._workspace_dir(session_id)
        with self._tracked(session_id, "prewrite", "prewrite") as t:
            try:
                state = run_prewrite(state)
                t.set_detail(
                    star_rating=state.get("star_rating"),
                    claim=state.get("claim"),
                )
            finally:
                self.save_state(session_id, state)
        return state

    def run_identification_verify(self, session_id: str) -> dict:
        """Run identification verification after method selection.

        Reads current state, runs diagnostics, writes back to session.
        Returns diagnosis dict with passed/report.
        """
        if identification_verify_node is None:
            raise HTTPException(
                status_code=503,
                detail="identification_verify node not available",
            )
        state = self.get_state(session_id)
        result = identification_verify_node(state)
        state = {**state, **result}
        self.save_state(session_id, state)
        return {
            "passed": result.get("identification_failed") is not True,
            "diagnosis": result.get("identification_diag", {}),
            "star_rating": result.get("star_rating", 0),
            "identification_failed": result.get("identification_failed") is True,
        }

    def run_robustness_check(self, session_id: str) -> dict:
        """Run full robustness battery after main estimation.

        Returns summary table and detailed results.
        """
        if robustness_check_node is None:
            raise HTTPException(
                status_code=503,
                detail="robustness_check node not available",
            )
        state = self.get_state(session_id)
        result = robustness_check_node(state)
        state = {**state, **result}
        self.save_state(session_id, state)
        return result

    def resume_outline(
        self, session_id: str, user_adjusted_outline: Any
    ) -> dict:
        """Re-run generate_outline with a user-adjusted outline."""
        if generate_outline_node is None:
            raise HTTPException(
                status_code=503,
                detail="generate_outline node not available",
            )
        state = self.get_state(session_id)
        state = {**state, "user_adjusted_outline": user_adjusted_outline}
        state = {**state, "resumed": True}
        state = {**state, **generate_outline_node(state)}
        self.save_state(session_id, state)
        return state

    def generate_chapter(
        self,
        session_id: str,
        chapter: dict,
        render_kwargs: Optional[dict] = None,
    ) -> dict:
        """Run generate_chapter with the given chapter spec, return new state."""
        if generate_chapter_node is None:
            raise HTTPException(
                status_code=503,
                detail="generate_chapter node not available",
            )
        state = self.get_state(session_id)
        state = {**state, "current_chapter": chapter}
        try:
            from engine.readiness import TRUTH_KEYS
        except Exception:
            TRUTH_KEYS = frozenset()
        _blocked_render_keys = frozenset({"workspace", "csv_path", "user_id"})
        for k, v in (render_kwargs or {}).items():
            if k in TRUTH_KEYS or k in _blocked_render_keys:
                continue
            if k not in state or state.get(k) in (None, ""):
                state[k] = v
        try:
            with self._tracked(session_id, "generate_chapter") as t:
                result = generate_chapter_node(state)
                blockers = result.get("write_blockers") or []
                t.set_detail(chapter_type=chapter.get("type"), write_blocked=bool(result.get("write_blocked")), blockers=blockers or None)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return self._persist_after_chapter(
            session_id, state, result, node_name="generate_chapter"
        )

    def regenerate_chapter(self, session_id: str, chapter_index: int) -> dict:
        """Re-run generate_chapter on the given chapter index."""
        if generate_chapter_node is None:
            raise HTTPException(
                status_code=503,
                detail="generate_chapter node not available",
            )
        state = self.get_state(session_id)
        state = {**state, "current_chapter_index": chapter_index}
        try:
            with self._tracked(session_id, "regenerate_chapter") as t:
                result = generate_chapter_node(state)
                t.set_detail(chapter_index=chapter_index)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return self._persist_after_chapter(
            session_id, state, result, node_name="regenerate_chapter"
        )

    def edit_chapter(
        self,
        session_id: str,
        chapter_index: int,
        instruction: Optional[str] = None,
        content: Optional[str] = None,
    ) -> dict:
        """Apply a chat refine or persist a user markdown edit.

        One write path: instruction → ``revision_suggestions`` then
        ``generate_chapter`` (same as regenerate). content → prepend a
        new version and set status ``edited`` (no LLM).
        """
        instruction_text = (instruction or "").strip()
        content_text = content if content is None else str(content)
        if not instruction_text and content_text is None:
            raise HTTPException(
                status_code=400,
                detail="instruction or content is required",
            )
        if not instruction_text and not str(content_text or "").strip():
            raise HTTPException(
                status_code=400,
                detail="instruction or content is required",
            )

        state = self.get_state(session_id)
        body_chapters = list(state.get("body_chapters") or [])
        if chapter_index < 0 or chapter_index >= len(body_chapters):
            raise HTTPException(status_code=404, detail="Chapter index out of range")
        existing = body_chapters[chapter_index]
        if not isinstance(existing, dict) or not (existing.get("content") or existing.get("type")):
            raise HTTPException(status_code=404, detail="Chapter not found")

        if instruction_text:
            return self._refine_chapter(
                session_id, chapter_index, instruction_text, state, existing
            )
        markdown = str(content_text)
        if not markdown.strip():
            raise HTTPException(
                status_code=400,
                detail="instruction or content is required",
            )
        return self._persist_chapter_edit(
            session_id, chapter_index, markdown, state, existing
        )

    def _refine_chapter(
        self,
        session_id: str,
        chapter_index: int,
        instruction: str,
        state: dict,
        existing: dict,
    ) -> dict:
        """Stuff the user instruction into revision_suggestions, then regenerate."""
        suggestions = list(state.get("revision_suggestions") or [])
        while len(suggestions) <= chapter_index:
            suggestions.append("")
        current_md = existing.get("content") or ""
        if current_md:
            suggestions[chapter_index] = (
                f"{instruction}\n\n当前章节正文（请在此基础上修改，输出完整 markdown）：\n{current_md}"
            )
        else:
            suggestions[chapter_index] = instruction
        self.save_state(
            session_id, {**state, "revision_suggestions": suggestions}
        )
        return self.regenerate_chapter(session_id, chapter_index)

    def _persist_chapter_edit(
        self,
        session_id: str,
        chapter_index: int,
        content: str,
        state: dict,
        existing: dict,
    ) -> dict:
        """Persist user markdown as a new version. Export reads ``content``."""
        body_chapters = list(state.get("body_chapters") or [])
        chapter = dict(existing)
        versions = list(chapter.get("versions") or [])
        previous = chapter.get("content")
        if not versions and previous:
            versions = [previous]
        if not versions or versions[0] != content:
            versions = [content] + versions
        chapter["content"] = content
        chapter["status"] = "edited"
        chapter["versions"] = versions
        chapter["chapter_index"] = chapter_index
        body_chapters[chapter_index] = chapter
        state = {**state, "body_chapters": body_chapters}
        with self._tracked(session_id, "edit_chapter") as t:
            t.set_detail(chapter_index=chapter_index, mode="content")
            self.save_state(session_id, state)
        return state

    def _persist_after_chapter(
        self,
        session_id: str,
        state: dict,
        result: dict,
        node_name: str = "generate_chapter",
    ) -> dict:
        state = {**state, **result}
        if result.get("write_blocked"):
            self.save_state(session_id, state)
            raise HTTPException(
                status_code=409,
                detail={
                    "write_blocked": True,
                    "write_blockers": result.get("write_blockers") or [],
                },
            )
        if review_chapter_node is not None:
            reviewed = review_chapter_node(state)
            state = {**state, **reviewed}
            # "可查"落盘：评审分数 / 接地失败 / 降级与否进 trace，state 落快照
            try:
                scores = list(reviewed.get("review_scores") or [])
                run_store.append_event(
                    session_id,
                    "review_chapter",
                    status="ok",
                    detail={
                        "parent_node": node_name,
                        "score": scores[-1] if scores else None,
                        "grounding_failures": list(
                            state.get("grounding_failures") or []
                        )
                        or None,
                        "review_source": state.get("review_source"),
                        "degraded": bool(
                            reviewed.get("review_degraded")
                            or state.get("review_degraded")
                        )
                        or None,
                    },
                )
                run_store.snapshot_state(
                    session_id, f"{node_name}_reviewed", state
                )
            except Exception:
                pass
            if reviewed.get("review_degraded") or reviewed.get("review_source") == "mock_fallback":
                reason = "review_llm_unparseable_or_error"
                for item in reviewed.get("degradations") or []:
                    if isinstance(item, dict) and item.get("node") == "review_chapter":
                        reason = str(item.get("reason") or reason)
                        break
                self.record_degradation(
                    session_id,
                    node="review_chapter",
                    reason=reason,
                    fallback="mock_review_llm",
                    visible=True,
                )
        self.save_state(session_id, state)
        return state

    def rollback_chapter(
        self, session_id: str, chapter_index: int, version_index: int
    ) -> dict:
        """Run rollback_chapter node to restore a historical version."""
        if rollback_chapter_node is None:
            raise HTTPException(
                status_code=503,
                detail="rollback node not available (T-08a pending)",
            )
        state = self.get_state(session_id)
        state = {
            **state,
            "rollback_chapter_index": chapter_index,
            "rollback_version_index": version_index,
        }
        with self._tracked(session_id, "rollback_chapter", "rollback") as t:
            t.set_detail(chapter_index=chapter_index, version_index=version_index)
            try:
                result = rollback_chapter_node(state)
            except (IndexError, ValueError) as exc:
                raise HTTPException(status_code=400, detail=str(exc))
            state = {**state, **result}
            self.save_state(session_id, state)
            return state

    def export_document(self, session_id: str, template: str) -> dict:
        """Run export_docx node and return the result dict.

        The result carries ``latex_source`` / ``pdf_path`` / ``docx_path``
        / ``degraded``. The template is written into state before the call.
        """
        if export_docx_node is None:
            raise HTTPException(
                status_code=503,
                detail="export_docx node not available (agent module missing)",
            )
        state = self.get_state(session_id)
        if not state.get("workspace"):
            state["workspace"] = self._workspace_dir(session_id)
        state = {**state, "export_template": template}
        with self._tracked(
            session_id, "export_docx", "export", 
        ) as t:
            result = export_docx_node(state)
            t.set_detail(
                template=template,
                degraded=bool(result.get("degraded")) or None,
                pdf_path=result.get("pdf_path"),
                docx_path=result.get("docx_path"),
            )
            state = {**state, **result}
            self.save_state(session_id, state)
            # 导出产物登记为持久交付物：复制进 outputs/export/
            try:
                produced = [
                    Path(p)
                    for p in (
                        result.get("pdf_path"),
                        result.get("docx_path"),
                    )
                    if p
                ]
                # paper.tex 是始终存在的产物（degraded 时 pdf/docx 缺，
                # 但 LaTeX 源码永远可用——见 CONTEXT 的降级语义），一并归档。
                tex_candidate = Path(state.get("workspace") or "") / "paper.tex"
                if tex_candidate.is_file():
                    produced.append(tex_candidate)
                copied = run_store.register_export(session_id, produced)
                if copied:
                    t.set_detail(archived=[c["name"] for c in copied])
            except Exception:
                pass
        return result

    # ------------------------------------------------------------------
    # Cleaning step calls
    # ------------------------------------------------------------------
    def transform_variables(self, session_id: str, config: dict) -> list:
        """Run TransformStep.run on the session's datasets; return datasets."""
        if TransformStepCls is None:
            raise HTTPException(
                status_code=503,
                detail="transform step not available (agent module missing)",
            )
        datasets = self.get_datasets(session_id)
        step_config = {**config, "workspace": "/tmp", "order": 0}
        datasets, _report = TransformStepCls().run(datasets, step_config)
        self.save_datasets(session_id, datasets)
        return datasets

    def filter_sample(self, session_id: str, conditions: list) -> list:
        """Run FilterStep.run on the session's datasets; return datasets."""
        if FilterStepCls is None:
            raise HTTPException(
                status_code=503,
                detail="filter step not available (agent module missing)",
            )
        datasets = self.get_datasets(session_id)
        step_config = {
            "conditions": conditions,
            "workspace": "/tmp",
            "order": 0,
        }
        datasets, _report = FilterStepCls().run(datasets, step_config)
        self.save_datasets(session_id, datasets)
        return datasets

    def balance_panel(
        self, session_id: str, panel_id: str, time_col: str
    ) -> dict:
        """Run BalanceStep.run on the session's datasets; return report."""
        if BalanceStepCls is None:
            raise HTTPException(
                status_code=503,
                detail="balance step not available (agent module missing)",
            )
        datasets = self.get_datasets(session_id)
        _datasets, report = BalanceStepCls().run(
            datasets,
            {"panel_id": panel_id, "time_col": time_col},
        )
        return report

    # ------------------------------------------------------------------
    # CHARLS detection / confirm
    # ------------------------------------------------------------------
    def detect_charls(self, session_id: str) -> dict:
        """Run the profiling detector on the session CSV.

        Returns ``{dataset_type, charls_config?}``. ``charls_config`` is the
        parsed ``charls.yaml`` and is only included when the dataset is
        detected as CHARLS.
        """
        if detect_dataset_type_fn is None:
            raise HTTPException(
                status_code=503,
                detail="profiling detector not available",
            )
        import pandas as pd

        csv_path = self.get_csv_path(session_id)
        try:
            df = pd.read_csv(csv_path)
        except Exception as exc:
            raise HTTPException(
                status_code=400, detail=f"Failed to read CSV: {exc}"
            ) from exc

        dataset_type = detect_dataset_type_fn(df)
        response: dict = {"dataset_type": dataset_type}
        if dataset_type == "CHARLS":
            response["charls_config"] = (
                load_charls_config_fn() if load_charls_config_fn else {}
            )
        return response

    def confirm_charls(
        self,
        session_id: str,
        variable_mapping: dict,
        waves: list,
        filter_presets: list,
    ) -> dict:
        """Persist the user-confirmed CHARLS wizard config into state."""
        state = self.get_state(session_id)
        charls_config = {
            "variable_mapping": variable_mapping,
            "waves": waves,
            "filter_presets": filter_presets,
        }
        state["charls_config"] = charls_config
        self.save_state(session_id, state)
        # Mirror on the entry top-level (legacy charls.py behavior).
        if session_id in self._sessions:
            self._sessions[session_id]["charls_config"] = charls_config
        return charls_config

    # ------------------------------------------------------------------
    # ADR-0007: HITL 人工评审
    # ------------------------------------------------------------------
    def get_review(self, session_id: str) -> dict:
        """读当前 review_chapter 的最新评审结果，投影成单章评审信息。

        从 state 读 review_feedback / revision_suggestions / review_scores /
        review_rubrics / review_chapter_index / review_iteration /
        max_review_iterations，按 review_chapter_index（缺失时回退
        current_chapter_index - 1）取当前章的评审 slice。

        auto_decision 由后端计算（score >= 0.7 → "pass"，否则 "fail"），
        与 review_chapter.REVIEW_SCORE_THRESHOLD 保持一致。

        无评审数据时返回空默认值（feedback="", score=0.0, auto_decision="fail"），
        让前端渲染空态而非报错。
        """
        state = self.get_state(session_id)

        review_feedback = state.get("review_feedback", []) or []
        revision_suggestions = state.get("revision_suggestions", []) or []
        review_scores = state.get("review_scores", []) or []
        review_rubrics = state.get("review_rubrics", []) or []

        # 确定评审章索引：优先 review_chapter_index，回退 current_chapter_index - 1
        chapter_index = state.get("review_chapter_index")
        if chapter_index is None:
            current_idx = state.get("current_chapter_index", 0)
            chapter_index = current_idx - 1
        if not isinstance(chapter_index, int) or chapter_index < 0:
            chapter_index = 0

        # 越界保护：取索引处的值，越界则用空默认值
        feedback = (
            review_feedback[chapter_index]
            if chapter_index < len(review_feedback)
            else ""
        )
        suggestions = (
            revision_suggestions[chapter_index]
            if chapter_index < len(revision_suggestions)
            else ""
        )
        score = (
            review_scores[chapter_index]
            if chapter_index < len(review_scores)
            else 0.0
        )
        raw_rubric = (
            review_rubrics[chapter_index]
            if chapter_index < len(review_rubrics)
            else {}
        )
        rubric = raw_rubric if isinstance(raw_rubric, dict) else {}

        review_iteration = state.get("review_iteration", 0)
        max_review_iterations = state.get("max_review_iterations", 2)

        # auto_decision 由后端计算（阈值与 review_chapter.REVIEW_SCORE_THRESHOLD 一致）
        auto_decision = "pass" if score >= 0.7 else "fail"

        return {
            "chapter_index": chapter_index,
            "feedback": feedback,
            "suggestions": suggestions,
            "score": score,
            "rubric": rubric,
            "review_iteration": review_iteration,
            "max_review_iterations": max_review_iterations,
            "auto_decision": auto_decision,
            "review_source": state.get("review_source") or "",
            "review_degraded": bool(state.get("review_degraded")),
            "grounding_failures": list(state.get("grounding_failures") or []),
        }

    def submit_review_decision(
        self,
        session_id: str,
        decision: str,
        reviewer: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> dict:
        """写人工决策到 state，reject 时触发重生成。

        1. 校验 decision 合法性（accept / reject / force_pass）
        2. 写 hitl_decision / hitl_reviewer / hitl_comment 到 state
        3. 确定操作章索引（review_chapter_index，回退 current_chapter_index - 1）
        4. decision == "reject" 时调 regenerate_chapter 重生成该章
        5. 返回 {ok, decision, chapter_index, next_action}

        Fitness Function：不写 review_feedback / review_scores / review_rubrics
        （ADR 0004 评审字段只由 review_chapter 节点写）。
        """
        valid_decisions = {"accept", "reject", "force_pass"}
        if decision not in valid_decisions:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid decision: {decision!r}; "
                    f"expected one of {sorted(valid_decisions)}"
                ),
            )

        state = self.get_state(session_id)

        # 确定操作章索引
        chapter_index = state.get("review_chapter_index")
        if chapter_index is None:
            current_idx = state.get("current_chapter_index", 0)
            chapter_index = current_idx - 1
        if not isinstance(chapter_index, int) or chapter_index < 0:
            chapter_index = 0

        # 写 HITL 决策到 state（不写 review_* 字段）
        state = self.update_state(
            session_id,
            hitl_decision=decision,
            hitl_reviewer=reviewer,
            hitl_comment=comment,
        )
        from nodes.learning_labels import collect_learning_labels

        state = self.update_state(
            session_id,
            learning_labels=collect_learning_labels(state),
        )
        try:
            from nodes.label_store import (
                ARM_HUMAN,
                REVIEWER_HUMAN,
                append_event,
                event_from_decision,
            )

            append_event(
                event_from_decision(
                    {**state, "session_id": session_id},
                    decision=decision,
                    reviewer=reviewer,
                    comment=comment,
                    reviewer_kind=REVIEWER_HUMAN,
                    ab_arm=ARM_HUMAN,
                )
            )
        except Exception:
            # 落盘失败不挡决策；测试会直接打 label_store。
            pass

        # 人工评审决策落 trace（"可查"磁盘件：谁在什么时候放行/打回了哪章）
        self.record_event(
            session_id,
            "review_decision",
            status=decision,
            detail={"chapter_index": chapter_index, "reviewer": reviewer},
        )

        # reject → 触发重生成；accept / force_pass → proceed
        if decision == "reject":
            try:
                self.regenerate_chapter(session_id, chapter_index)
            except HTTPException as exc:
                # regenerate_chapter 不可用时不阻塞 decision 写入，
                # 由前端调既有 /regenerate 端点完成重生成（降级）
                if exc.status_code == 503:
                    pass
                else:
                    raise
            next_action = "regenerate"
        else:
            next_action = "proceed"

        return {
            "ok": True,
            "decision": decision,
            "chapter_index": chapter_index,
            "next_action": next_action,
        }

    # ------------------------------------------------------------------
    # Degradation tracking (F7: 异常处理与降级 UX)
    # ------------------------------------------------------------------
    def record_degradation(
        self,
        session_id: str,
        node: str,
        reason: str,
        fallback: str,
        visible: bool = False,
    ) -> None:
        """Record a degradation event for a session.

        Called by cleaning nodes and other parts of the pipeline when
        the primary method fails and a fallback is used.
        """
        if session_id not in self._degradations:
            self._degradations[session_id] = []
        from datetime import datetime, timezone

        self._degradations[session_id].append({
            "node": node,
            "reason": reason,
            "fallback": fallback,
            "visible": visible,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_degradations(self, session_id: str) -> list[dict]:
        """Return the degradation log for a session."""
        return self._degradations.get(session_id, [])

    def discuss_desk(self, notes: str, turns: list[dict] | None = None) -> dict:
        """空桌讨论：走统一 LLM 通道，失败时启发式降级。"""
        try:
            from desk.socratic import discuss
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=503, detail=f"desk discuss unavailable: {exc}") from exc
        return discuss(notes, turns or [])

    def transcribe_desk(self, raw: bytes, filename: str = "clip.webm") -> dict:
        try:
            from desk.stepfun_asr import transcribe_upload
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=503, detail=f"desk asr unavailable: {exc}") from exc
        text = transcribe_upload(raw, filename=filename)
        return {"text": text, "source": "stepfun"}

    def speak_desk(self, text: str) -> bytes:
        try:
            from desk.minimax_tts import synthesize
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=503, detail=f"desk tts unavailable: {exc}") from exc
        return synthesize(text)

    # ------------------------------------------------------------------
    # Test helpers
    # ------------------------------------------------------------------
    def seed_state(self, session_id: str, state: dict) -> None:
        """Test helper: directly inject state into the session store."""
        self._sessions[session_id] = {"state": state}

    def drop_session(self, session_id: str) -> None:
        """Test helper: remove a session from the store."""
        self._sessions.pop(session_id, None)


# Module-level singleton: routers import this.
facade = AgentFacade()
