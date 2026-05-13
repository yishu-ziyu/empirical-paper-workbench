from __future__ import annotations

import unittest
from pathlib import Path


class ObservableExecutionFrontendTests(unittest.TestCase):
    """BDD: 实证执行页必须消费真实 run observability，而不是展示静态骨架。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_1_execution_page_has_run_selector_and_header(self) -> None:
        """行为 1：实证执行页必须有 run 选择器和运行头，而不是只有 Phase A 骨架。"""
        for element_id in (
            "run-selector",
            "run-refresh-button",
            "observable-run-header",
            "observable-run-id",
            "observable-run-status",
            "observable-run-mode",
            "observable-run-evidence",
        ):
            self.assertIn(element_id, self.index_html)
        self.assertNotIn("实证执行将在 Phase C 接入", self.index_html)

    def test_bdd_2_frontend_loads_run_observability_endpoint(self) -> None:
        """行为 2：前端必须通过完整 observability endpoint 读取真实运行状态。"""
        self.assertIn("observability(projectId, runId)", self.app_js)
        self.assertIn("/observability", self.app_js)
        self.assertIn("loadRunObservability", self.app_js)
        self.assertIn("state.runObservability", self.app_js)

    def test_bdd_3_step_board_renders_real_steps(self) -> None:
        """行为 3：Step Board 必须渲染 steps.items 中的真实阶段。"""
        self.assertIn("observable-step-board", self.index_html)
        self.assertIn("renderObservableSteps", self.app_js)
        for field in ("step.actor", "step.status", "step.summary", "step.metadata"):
            self.assertIn(field, self.app_js)

    def test_bdd_4_event_stream_sorts_by_sequence(self) -> None:
        """行为 4：事件流必须按 sequence 升序展示。"""
        self.assertIn("observable-event-stream", self.index_html)
        self.assertIn("renderObservableEvents", self.app_js)
        self.assertIn(".sort((a, b) => (a.sequence || 0) - (b.sequence || 0))", self.app_js)
        for field in ("event.type", "event.actor", "event.message", "event.evidence_level"):
            self.assertIn(field, self.app_js)

    def test_bdd_5_hitl_gates_expose_resolve_actions(self) -> None:
        """行为 5：开放 HITL gate 必须提供 confirm/reject/adjust 处理动作。"""
        self.assertIn("observable-hitl-gates", self.index_html)
        self.assertIn("renderObservableGates", self.app_js)
        self.assertIn('data-gate-resolve-action="confirm"', self.app_js)
        self.assertIn('data-gate-resolve-action="reject"', self.app_js)
        self.assertIn('data-gate-resolve-action="adjust"', self.app_js)
        self.assertNotIn("P1 接入", self.app_js)

    def test_bdd_6_gate_resolve_posts_action_and_note(self) -> None:
        """行为 6：处理 gate 时必须向真实 API 提交 action 与 note。"""
        self.assertIn("resolveGate(projectId, runId, gateId, action, note)", self.app_js)
        self.assertIn("/gates/${gateId}/resolve", self.app_js)
        self.assertIn("JSON.stringify({ action, note })", self.app_js)
        self.assertIn("resolveObservableGate", self.app_js)
        self.assertIn("data-gate-note", self.app_js)

    def test_bdd_7_gate_resolve_refreshes_observability_and_shows_errors(self) -> None:
        """行为 7：处理成功后刷新 observability，失败时显示实证执行页错误。"""
        self.assertIn("await v2api.runs.resolveGate", self.app_js)
        self.assertIn("await loadRunObservability(state.selectedProjectId, state.selectedRunId)", self.app_js)
        self.assertIn('showV2Error("empirical-execution"', self.app_js)

    def test_bdd_8_resolved_gates_show_resolution_without_repeat_actions(self) -> None:
        """行为 8：已处理 gate 必须展示 resolution 并避免重复写入。"""
        self.assertIn('gate.status === "resolved"', self.app_js)
        self.assertIn("gate.resolution", self.app_js)
        self.assertIn("resolved_at", self.app_js)

    def test_bdd_9_artifact_evidence_panel_aggregates_traceable_outputs(self) -> None:
        """行为 9：产物证据面板必须从 steps/events 聚合真实产物和证据等级。"""
        self.assertIn("observable-artifact-evidence", self.index_html)
        self.assertIn("collectObservableArtifacts", self.app_js)
        self.assertIn("artifact_written", self.app_js)
        self.assertIn("local_execution", self.app_js)
        self.assertIn(".observable-grid", self.styles_css)

    def test_bdd_10_legacy_runs_without_observability_show_recoverable_state(self) -> None:
        """行为 10：历史 run 缺少 observability 文件时，页面必须显示可恢复提示。"""
        self.assertIn("handleMissingRunObservability", self.app_js)
        self.assertIn("error.status === 404", self.app_js)
        self.assertIn("缺少可观察执行轨迹", self.app_js)
        self.assertIn("完成执行计划后启动正式执行", self.app_js)

    def test_bdd_11_execution_page_shows_run_dataset_source(self) -> None:
        """行为 11：实证执行页必须直接展示当前 run 使用的数据文件和本地文件证据。"""
        self.assertIn("observable-dataset-source", self.index_html)
        self.assertIn("renderObservableDatasetSource", self.app_js)
        self.assertIn("observability.dataset_source", self.app_js)
        for field in ("dataset.row_count", "dataset.column_count", "dataset.path", "dataset.file_type"):
            self.assertIn(field, self.app_js)
        self.assertIn("未记录数据来源", self.app_js)
        self.assertIn(".observable-dataset-source", self.styles_css)

    def test_bdd_12_execution_page_shows_variable_roles_confirmation(self) -> None:
        """行为 12：实证执行页必须展示变量角色理解及其 HITL 确认状态。"""
        self.assertIn("observable-variable-roles", self.index_html)
        self.assertIn("renderObservableVariableRoles", self.app_js)
        self.assertIn("observability.variable_roles", self.app_js)
        for field in (
            "variableRoles.roles.outcome",
            "variableRoles.roles.treatment",
            "variableRoles.roles.controls",
            "variableRoles.confirmation_status",
            "variableRoles.confirmation_gate_id",
        ):
            self.assertIn(field, self.app_js)
        self.assertIn("未记录变量角色", self.app_js)
        self.assertIn(".observable-variable-roles", self.styles_css)

    def test_bdd_13_execution_page_uses_dense_console_layout(self) -> None:
        """行为 13：实证执行页必须是紧凑可扫读的执行控制台，而不是大号论文卡片。"""
        self.assertIn("execution-control-panel", self.index_html)
        self.assertIn("execution-context-grid", self.index_html)
        self.assertIn("#view-empirical-execution", self.styles_css)
        self.assertIn("font-family: -apple-system", self.styles_css)
        self.assertIn(".execution-context-grid", self.styles_css)
        self.assertIn("border-radius: 8px", self.styles_css)
        self.assertIn("grid-template-columns: minmax(260px, 0.8fr) minmax(320px, 1.2fr)", self.styles_css)
        self.assertIn(".observable-artifact-evidence .project-card", self.styles_css)
        self.assertIn("white-space: pre-wrap", self.styles_css)


if __name__ == "__main__":
    unittest.main()
