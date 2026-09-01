"""ADR-0003 Stage B：AgentFacade（facade 收敛重构后的薄门面包）。

对路由层与测试层，公共 API 完全不变：
- ``from facade import facade``（单例）
- ``from facade import AgentFacade``
- ``monkeypatch.setattr("facade.<node_name>", ...)`` 在方法调用时替换节点函数
  仍生效（``facade`` 包把 agent 节点/清洗类 re-export 到自身命名空间，节点方法
  以裸全局名解析，测试的 monkeypatch 能立刻传播）。

职责拆分（每个模块一句话）：
- ``_deps``         —— agent 依赖加载器：直接 import graph/节点/清洗类并快速失败。
- ``session_store`` —— 会话元数据 + state 的进程内单一真相，负责增删改查/CSV/降级日志。
- ``desk_client``   —— desk 能力（讨论/设计对话/语音）封装。
- 本文件（AgentFacade）—— 薄门面：组合上述协作者，编排 graph.invoke 与单节点
  HITL / 清洗 / 评审 / CHARLS / run 工件。

约束保持：不新增第三方依赖；对外方法签名、返回结构、错误码不变。
"""
from __future__ import annotations

import shutil
import uuid
from contextlib import contextmanager
from typing import Any, Iterator, List, Optional

import run_store
from fastapi import HTTPException

from . import desk_client
from ._deps import (
    BalanceStepCls,
    FilterStepCls,
    TransformStepCls,
    build_citation_graph_node,
    detect_dataset_type_fn,
    estimate_node,
    export_docx_node,
    generate_chapter_node,
    generate_outline_node,
    graph as _graph,
    identification_verify_node,
    load_charls_config_fn,
    review_chapter_node,
    robustness_check_node,
    rollback_chapter_node,
    search_literature_node,
    set_direction_node,
    translate_code_node,
)
from .session_store import SessionStore


class AgentFacade:
    """组合 SessionStore / desk_client / graph 与各 agent 节点的薄门面。

    节点函数通过 facade 包命名空间的裸全局名在调用时解析，因此
    ``monkeypatch.setattr("facade.<node_name>", ...)`` 能即时替换。
    """

    def __init__(self) -> None:
        # 会话元数据 + state 的单一真相（Task 4：以 in-memory store 为显式存储，
        # 不再对 LangGraph checkpointer 做隐式回退）。
        self._store: SessionStore = SessionStore()
        # 保留旧引用：self._sessions / self._degradations 指向 store 同名 dict，
        # 让既有代码（facade._sessions[sid]["state"]）与测试断言语义不变。
        self._sessions: dict = self._store.sessions
        self._degradations: dict[str, list[dict]] = self._store.degradations

    # ------------------------------------------------------------------
    # Session 生命周期（编排 store + run 工件目录）
    # ------------------------------------------------------------------
    def create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> str:
        """Create an empty session and return its id.

        匿名会话（无 user_id）用于未登录上传。
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        self._store.create(session_id, user_id)
        # Run 工件目录：会话创建即建档（trace/checkpoints/outputs 的根）
        try:
            run_store.write_manifest(session_id, user_id=user_id)
        except Exception:
            pass  # 工件记录失败不阻断主流程
        return session_id

    def has_session(self, session_id: str) -> bool:
        return self._store.has(session_id)

    def get_session_owner(self, session_id: str) -> Optional[int]:
        """Return the user_id that owns this session, or None if anonymous."""
        return self._store.get_owner(session_id)

    def list_sessions_by_user(self, user_id: int) -> list[str]:
        """Return all session IDs owned by the given user."""
        return self._store.list_by_user(user_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if it existed, False otherwise.

        会话删除同时清掉磁盘上的 run 工件目录（隐私优先：删就是删）。
        """
        existed = self._store.delete(session_id)
        shutil.rmtree(run_store.run_dir(session_id), ignore_errors=True)
        return existed

    # ------------------------------------------------------------------
    # State 访问（薄代理 → SessionStore 单一真相）
    # ------------------------------------------------------------------
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
            "cleaning_report": state.get("cleaning_report"),
            "literature_source": state.get("literature_source"),
            "write_blockers": blockers,
            "robustness_status": rob_status,
            "outline": outline,
            "body_chapters": body_chapters,
            "research_direction": state.get("research_direction"),
        }

    def get_state(self, session_id: str) -> dict:
        """Return the state dict for a session (404 if missing).

        Task 4：单一读取路径只读进程内 store，不再回退 LangGraph checkpointer。
        """
        return self._store.get_state(session_id)

    def save_state(self, session_id: str, state: dict) -> None:
        """Overwrite the session state (in-memory store only)."""
        self._store.save_state(session_id, state)

    def update_state(self, session_id: str, **fields) -> dict:
        """Merge fields into the session state and return the new state."""
        return self._store.update_state(session_id, **fields)

    def get_session_entry(self, session_id: str) -> dict:
        """Return the raw session entry (metadata + csv_path etc.)."""
        return self._store.get_entry(session_id)

    def get_csv_path(self, session_id: str) -> str:
        """Resolve the CSV path stored for this session (S3 cache fallback)."""
        return self._store.get_csv_path(session_id)

    def set_csv_path(self, session_id: str, csv_path: str) -> None:
        """Persist the CSV path on the session entry."""
        self._store.set_csv_path(session_id, csv_path)

    def get_datasets(self, session_id: str) -> list:
        """Return the dataset list for a session (wrapped for cleaning)."""
        return self._store.get_datasets(session_id)

    def save_datasets(self, session_id: str, datasets: list) -> None:
        """Persist updated dataset meta back into the session state."""
        self._store.save_datasets(session_id, datasets)

    # ------------------------------------------------------------------
    # Run 工件追踪（trace / checkpoints，见 run_store.py）
    # ------------------------------------------------------------------
    def _tracked(
        self,
        session_id: str,
        node: str,
        snapshot_label: Optional[str] = None,
    ) -> Any:
        """计时追踪一个节点执行段：ok/error 事件 + 可选 state 快照。"""
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
        self._store.flush()
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
            from agent.engine.prewrite import run_prewrite
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

    def run_translate_code(self, session_id: str) -> dict:
        """Run translate_code and persist code_translations for /code-export.

        原 facade.py 曾有重复定义，此处收敛为唯一一份（Task 3）。
        """
        if translate_code_node is None:
            raise HTTPException(
                status_code=503,
                detail="translate_code node not available",
            )
        state = self.get_state(session_id)
        with self._tracked(session_id, "translate_code", "translate_code") as t:
            result = translate_code_node(state)
            state = {**state, **result}
            self.save_state(session_id, state)
            t.set_detail(n=len(result.get("code_translations") or []))
        return result

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
            from agent.engine.readiness import TRUTH_KEYS
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

    def regenerate_chapter(
        self,
        session_id: str,
        chapter_index: int,
        instruction: Optional[str] = None,
    ) -> dict:
        """Re-run generate_chapter on the given chapter index."""
        if generate_chapter_node is None:
            raise HTTPException(
                status_code=503,
                detail="generate_chapter node not available",
            )
        state = self.get_state(session_id)
        # resolve_slot prefers leftover current_chapter (set by POST
        # /generate-chapter). Index-based rewrite must honor this index.
        state = {
            **state,
            "current_chapter_index": chapter_index,
            "current_chapter": None,
        }
        if instruction:
            suggestions = list(state.get("revision_suggestions") or [])
            while len(suggestions) <= chapter_index:
                suggestions.append("")
            suggestions[chapter_index] = instruction
            state = {**state, "revision_suggestions": suggestions}
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
        """Apply a chat refine or persist a user markdown edit."""
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
        updates: dict = {"body_chapters": body_chapters}
        # Drop the pre-edit review so approve cannot pass on a stale score.
        for key, empty in (
            ("review_scores", None),
            ("review_feedback", ""),
        ):
            items = list(state.get(key) or [])
            if 0 <= chapter_index < len(items):
                items[chapter_index] = empty
                updates[key] = items
        state = {**state, **updates}
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
        # Write loop ends with downloadable Stata/R: fill translations after a
        # successful chapter write. Fail-open so a translate miss does not 500.
        try:
            translated = self.run_translate_code(session_id)
            state = {**state, **translated}
        except Exception:
            pass
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
        """Run export_docx node and return the result dict."""
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
            try:
                from pathlib import Path

                produced = [
                    Path(p)
                    for p in (
                        result.get("pdf_path"),
                        result.get("docx_path"),
                    )
                    if p
                ]
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
        """Run the profiling detector on the session CSV."""
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
            self._store.flush()
        return charls_config

    # ------------------------------------------------------------------
    # ADR-0007: HITL 人工评审
    # ------------------------------------------------------------------
    def get_review(self, session_id: str) -> dict:
        """读当前 review_chapter 的最新评审结果，投影成单章评审信息。"""
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
        if not isinstance(feedback, str):
            feedback = "" if feedback is None else str(feedback)
        suggestions = (
            revision_suggestions[chapter_index]
            if chapter_index < len(revision_suggestions)
            else ""
        )
        raw_score = (
            review_scores[chapter_index]
            if chapter_index < len(review_scores)
            else None
        )
        try:
            score = float(raw_score) if raw_score is not None else 0.0
        except (TypeError, ValueError):
            score = 0.0
        raw_rubric = (
            review_rubrics[chapter_index]
            if chapter_index < len(review_rubrics)
            else {}
        )
        rubric = raw_rubric if isinstance(raw_rubric, dict) else {}

        review_iteration = state.get("review_iteration", 0)
        max_review_iterations = state.get("max_review_iterations", 2)

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
        """写人工决策到 state，reject 时触发重生成。"""
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
        from agent.nodes.learning_labels import collect_learning_labels

        state = self.update_state(
            session_id,
            learning_labels=collect_learning_labels(state),
        )
        try:
            from agent.nodes.label_store import (
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

        # 人工评审决策落 trace
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
                # regenerate_chapter 不可用时不阻塞 decision 写入
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
    # Degradation tracking (F7) —— 薄代理 → SessionStore
    # ------------------------------------------------------------------
    def record_degradation(
        self,
        session_id: str,
        node: str,
        reason: str,
        fallback: str,
        visible: bool = False,
    ) -> None:
        """Record a degradation event for a session."""
        self._store.record_degradation(
            session_id, node, reason, fallback, visible=visible
        )

    def get_degradations(self, session_id: str) -> list[dict]:
        """Return the degradation log for a session."""
        return self._store.get_degradations(session_id)

    # ------------------------------------------------------------------
    # Desk（薄代理 → desk_client）
    # ------------------------------------------------------------------
    def discuss_desk(self, notes: str, turns: list[dict] | None = None) -> dict:
        """空桌讨论：走统一 LLM 通道，失败时启发式降级。"""
        return desk_client.discuss_desk(notes, turns or [])

    def design_chat_desk(
        self,
        notes: str,
        turns: list[dict],
        columns: list[str],
    ) -> dict:
        """设计对话：把念头聊成研究设定卡（dv/iv/controls/method 逐轮抽齐）。

        Task 5：取代 routers/desk.py 直接 ``from agent.desk.design_chat import
        design_chat`` 的旁路，统一从 facade 入口触达 agent。
        """
        return desk_client.design_chat_desk(notes, turns, columns)

    def transcribe_desk(self, raw: bytes, filename: str = "clip.webm") -> dict:
        return desk_client.transcribe_desk(raw, filename=filename)

    def speak_desk(self, text: str) -> bytes:
        return desk_client.speak_desk(text)

    # ------------------------------------------------------------------
    # Test helpers（薄代理 → SessionStore）
    # ------------------------------------------------------------------
    def seed_state(self, session_id: str, state: dict) -> None:
        """Test helper: directly inject state into the session store."""
        self._store.seed(session_id, state)

    def drop_session(self, session_id: str) -> None:
        """Test helper: remove a session from the store."""
        self._store.drop(session_id)


# Module-level singleton: routers import this.
facade = AgentFacade()