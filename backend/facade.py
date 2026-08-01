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
import uuid
from pathlib import Path
from typing import Any, List, Optional

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
    from nodes.generate_chapter import generate_chapter as generate_chapter_node  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    generate_chapter_node = None

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
        """Delete a session. Returns True if it existed, False otherwise."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

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
        }
        final_state = _graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": session_id}},
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
        """Run set_direction + generate_outline, persist, return new state."""
        if set_direction_node is None or generate_outline_node is None:
            raise HTTPException(
                status_code=503,
                detail="outline nodes not available (agent module missing)",
            )
        state = self.get_state(session_id)
        state = {**state, "research_direction": research_direction}
        state = {**state, **set_direction_node(state)}
        state = {**state, **generate_outline_node(state)}
        self.save_state(session_id, state)
        return state

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
        for k, v in (render_kwargs or {}).items():
            if k not in state or state.get(k) in (None, ""):
                state[k] = v
        try:
            result = generate_chapter_node(state)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        state = {**state, **result}
        self.save_state(session_id, state)
        return state

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
            result = generate_chapter_node(state)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        state = {**state, **result}
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
        state = {**state, "export_template": template}
        result = export_docx_node(state)
        # Persist the export_template + result back to state so subsequent
        # requests see the rendered paths.
        state = {**state, **result}
        self.save_state(session_id, state)
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_degradations(self, session_id: str) -> list[dict]:
        """Return the degradation log for a session."""
        return self._degradations.get(session_id, [])

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
