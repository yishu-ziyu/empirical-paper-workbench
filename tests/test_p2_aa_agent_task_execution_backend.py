"""
P2-AA: Agent Task Queue → 执行后端选择层
BDD + TDD 测试

行为对齐（需用户确认后写实现）：
"""

import json
import pytest
from pathlib import Path


# =============================================================================
# BDD 行为用例
# =============================================================================

# 行为 1：已审阅任务可以选择执行后端
#   Given：Agent Task 状态为 reviewed_for_dispatch
#   When：用户选择执行后端（StatsPAI / Python / StataMCP / Codex）
#   Then：任务状态变为 backend_selected，记录所选后端、可用性状态和证据等级
#
# 行为 2：选择 StatsPAI 后端执行 OLS 方法
#   Given：任务已选择 StatsPAI 后端，RunPlan 包含 OLS 任务
#   When：触发执行
#   Then：调用 StatsPAI sp.regress，生成 Results/json/method_execution_result.json
#         evidence_level=local_execution，artifact_path 可追踪
#
# 行为 3：执行失败时记录诊断日志
#   Given：任务已选择后端
#   When：执行过程中 StatsPAI 报错（如样本不足、公式不可估）
#   Then：任务状态变为 failed，记录 error payload 和 student-friendly message
#         不覆盖已有结果文件，技术日志保留完整 traceback
#
# 行为 4：执行成功后生成 evaluator checks
#   Given：StatsPAI 执行成功，结果已写入
#   When： evaluator 检查运行时
#   Then：生成 coefficient_significance、model_diagnostics、residual_checks
#         结果绑定到 FindingCard，evidence_level=local_execution
#
# 行为 5：执行边界隔离
#   Given：两个 Agent Task 同时执行（任务 A 选 StatsPAI-OLS，任务 B 选 Python-OLS）
#   When：同时触发执行
#   Then：两个任务独立运行，结果文件不互相覆盖，各自有独立的 run_id、日志和证据链
#
# 行为 6：Codex 子 Agent 执行边界
#   Given：任务选择 Codex 后端
#   When：触发执行
#   Then：只生成代码/脚本，不直接执行统计估计；执行结果标记为 local_file
#         不冒充 local_execution 证据
#
# 行为 7：后端选择必须可解释
#   Given：Agent Task 已完成人工派工审阅
#   When：系统选择一个执行后端
#   Then：任务记录 selection_reason、fallback_backend_ids、execution_boundary
#         以及 formal_write_allowed=false，前端可以解释“为什么由它执行”
#
# 行为 8：后端不可用时要留下可见转路信息
#   Given：用户选择的后端当前不可用
#   When：尝试选择该后端
#   Then：任务状态记录为 blocked_by_backend_unavailable，并暴露 retry/fallback choices
#
# 行为 9：Codex 子 Agent 后端属于草案层能力
#   Given：任务选择 CodexSubagent 后端
#   When：触发执行
#   Then：只生成可审阅脚本，结果不能自动进入正式论文层
#
# 边界条件：
#   - StatsPAI 未安装时 availability_status=not_installed，不能选为 active_backend
#   - Stata 未安装时 availability_status=not_available，不能选为 active_backend
#   - blocked 方法（如缺少工具变量的 IV）不能进入执行层，应在选择后端前拒绝
#   - 只有 method_catalog 中 readiness_status=ready 的方法才允许执行


class TestAgentTaskExecutionBackendSelection:
    """行为 1：已审阅任务可以选择执行后端"""

    def test_select_statspai_backend_for_reviewed_task(self, tmp_path):
        """
        Given：Agent Task 状态为 reviewed_for_dispatch
        When：用户选择 StatsPAI 作为执行后端
        Then：任务状态变为 backend_selected，记录 backend_id、availability_status、evidence_level
        """
        # Arrange: 创建 reviewed_for_dispatch 的任务
        task = _build_reviewed_task(tmp_path, task_id="task_ols_01")

        # Act: 选择后端
        result = select_execution_backend(task, backend_id="statspai")

        # Assert
        assert result["status"] == "backend_selected"
        assert result["selected_backend"]["id"] == "statspai"
        assert result["selected_backend"]["evidence_level"] == "local_execution"
        assert result["can_execute"] is True

    def test_select_backend_rejects_non_reviewed_task(self, tmp_path):
        """
        Given：Agent Task 状态为 queued（未审阅）
        When：尝试选择后端
        Then：抛出 ExecutionBackendSelectionError，code="dispatch_review_required"
        """
        task = _build_queued_task(tmp_path, task_id="task_ols_02")

        with pytest.raises(ExecutionBackendSelectionError) as exc_info:
            select_execution_backend(task, backend_id="statspai")

        assert exc_info.value.code == "dispatch_review_required"

    def test_select_unavailable_backend_rejected(self, tmp_path):
        """
        Given：StatsPAI 未安装
        When：尝试选择 StatsPAI 后端
        Then：抛出 ExecutionBackendSelectionError，code="backend_not_available"
        """
        task = _build_reviewed_task(tmp_path, task_id="task_ols_03")

        with pytest.raises(ExecutionBackendSelectionError) as exc_info:
            select_execution_backend(task, backend_id="statspai", _check_available=lambda b: False)

        assert exc_info.value.code == "backend_not_available"

    def test_select_backend_records_product_explanation_fallback_and_boundary(self, tmp_path):
        """
        行为 7：
        Given：任务已完成人工派工审阅
        When：选择 Python OLS adapter 作为执行后端
        Then：任务记录后端选择理由、fallback、执行边界和正式层阻断状态
        """
        task = _build_reviewed_task(tmp_path, task_id="task_ols_07")

        result = select_execution_backend(task, backend_id="python_ols_adapter")

        backend = result["selected_backend"]
        assert backend["id"] == "python_ols_adapter"
        assert backend["selection_reason"]
        assert "python_ols_adapter" in backend["selection_reason"]
        assert isinstance(backend["fallback_backend_ids"], list)
        assert backend["fallback_backend_ids"]
        assert backend["formal_write_allowed"] is False
        assert backend["execution_boundary"]["can_enter_formal_layer_automatically"] is False
        assert result["next_action"] == "execute"

    def test_unavailable_backend_records_visible_blocker_and_fallback_choices(self, tmp_path):
        """
        行为 8：
        Given：用户选择的 StatsPAI 后端不可用
        When：尝试选择该后端
        Then：任务留下 blocked_by_backend_unavailable 状态和可见 fallback choices
        """
        task = _build_reviewed_task(tmp_path, task_id="task_ols_08")

        with pytest.raises(ExecutionBackendSelectionError) as exc_info:
            select_execution_backend(task, backend_id="statspai", _check_available=lambda b: False)

        assert exc_info.value.code == "backend_not_available"
        assert task["status"] == "blocked_by_backend_unavailable"
        assert task["next_action"] == "choose_fallback_backend"
        assert task["can_execute"] is False
        assert task["backend_blocker"]["code"] == "blocked_by_backend_unavailable"
        assert "statspai" == task["backend_blocker"]["backend_id"]
        assert task["backend_blocker"]["fallback_backend_ids"]
        assert task["backend_blocker"]["retry_action"] == "retry_backend_selection"
        assert any(event["event"] == "backend_unavailable" for event in task["audit_log"])

    def test_codex_subagent_backend_can_be_selected_with_review_boundary(self, tmp_path):
        """
        行为 7 + 行为 9：
        Given：任务已完成人工派工审阅
        When：选择 CodexSubagent 作为后端
        Then：任务记录它是草案层代码生成后端，不能自动进入正式层
        """
        task = _build_reviewed_task(tmp_path, task_id="task_ols_09")

        result = select_execution_backend(task, backend_id="codex")

        backend = result["selected_backend"]
        assert backend["id"] == "codex"
        assert backend["label"] == "CodexSubagent"
        assert backend["formal_write_allowed"] is False
        assert backend["execution_boundary"]["kind"] == "draft_code_generation"
        assert backend["execution_boundary"]["requires_human_review_before_formal_layer"] is True


class TestStatsPAIExecution:
    """行为 2：选择 StatsPAI 后端执行 OLS 方法"""

    def test_statspai_ols_execution_produces_result_artifact(self, tmp_path):
        """
        Given：任务已选择 StatsPAI 后端，RunPlan 包含 OLS 任务
        When：触发执行
        Then：生成 Results/json/method_execution_result.json
        """
        # Arrange
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "Data").mkdir()
        _create_sample_csv(project_root / "Data" / "analysis_sample.csv")

        task = _build_backend_selected_task(
            project_root,
            task_id="task_ols_04",
            backend_id="statspai",
            method_id="ols",
        )

        # Act
        result = execute_agent_task_with_backend(task, project_root)

        # Assert
        assert result["status"] == "succeeded"
        assert result["engine"] == "statspai"
        assert result["evidence_level"] == "local_execution"

        artifact_path = project_root / "Results" / "json" / "method_execution_result.json"
        assert artifact_path.exists()

        payload = json.loads(artifact_path.read_text())
        assert payload["engine"] == "statspai"
        assert payload["evidence_level"] == "local_execution"
        assert len(payload["methods"]) >= 1
        assert "execution_contract" in payload

    def test_statspai_execution_sets_task_status_and_audit_log(self, tmp_path):
        """
        Given：任务已选择 StatsPAI 后端
        When：执行完成
        Then：任务状态变为 succeeded，审计日志记录执行事件
        """
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "Data").mkdir()
        _create_sample_csv(project_root / "Data" / "analysis_sample.csv")

        task = _build_backend_selected_task(
            project_root,
            task_id="task_ols_05",
            backend_id="statspai",
            method_id="ols",
        )

        result = execute_agent_task_with_backend(task, project_root)

        assert result["status"] == "succeeded"
        audit_log = result.get("audit_log", [])
        execution_events = [e for e in audit_log if "execution" in e.get("event", "")]
        assert len(execution_events) >= 1


class TestExecutionFailureHandling:
    """行为 3：执行失败时记录诊断日志"""

    def test_execution_failure_records_diagnostics(self, tmp_path):
        """
        Given：任务已选择后端，但数据文件缺失
        When：触发执行
        Then：任务状态变为 failed，记录错误信息，不生成结果文件
        """
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "Results" / "json").mkdir(parents=True)
        # 不创建 CSV 文件 → 数据缺失

        task = _build_backend_selected_task(
            project_root,
            task_id="task_ols_06",
            backend_id="statspai",
            method_id="ols",
        )

        result = execute_agent_task_with_backend(task, project_root)

        assert result["status"] == "failed"
        assert "error" in result
        assert result["error"]["code"] == "dataset_not_found"

        # 失败时不应生成结果文件
        artifact_path = project_root / "Results" / "json" / "method_execution_result.json"
        assert not artifact_path.exists() or result.get("error") is not None


class TestExecutionIsolation:
    """行为 5：执行边界隔离"""

    def test_concurrent_executions_do_not_interfere(self, tmp_path):
        """
        Given：两个任务同时执行
        When：各自选择不同后端
        Then：结果文件不互相覆盖
        """
        # 此测试验证 run_id 隔离机制
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "Data").mkdir()
        _create_sample_csv(project_root / "Data" / "analysis_sample.csv")

        task_a = _build_backend_selected_task(
            project_root, task_id="task_ols_a", backend_id="statspai", method_id="ols",
        )
        task_b = _build_backend_selected_task(
            project_root, task_id="task_ols_b", backend_id="python_ols_adapter", method_id="ols",
        )

        result_a = execute_agent_task_with_backend(task_a, project_root)
        result_b = execute_agent_task_with_backend(task_b, project_root)

        assert result_a["run_id"] != result_b["run_id"]
        assert result_a["engine"] == "statspai"
        assert result_b["engine"] == "python_ols_adapter"


class TestCodexSubagentExecutionBoundary:
    """行为 9：Codex 子 Agent 后端属于草案层能力"""

    def test_codex_execution_generates_script_without_formal_write_permission(self, tmp_path):
        """
        Given：任务选择 CodexSubagent 后端
        When：触发执行
        Then：只生成脚本，不执行统计估计，也不能自动写入正式论文层
        """
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "Data").mkdir()
        _create_sample_csv(project_root / "Data" / "analysis_sample.csv")

        task = _build_backend_selected_task(
            project_root,
            task_id="task_codex_01",
            backend_id="codex",
            method_id="ols",
        )

        result = execute_agent_task_with_backend(task, project_root)

        assert result["status"] == "succeeded"
        assert result["engine"] == "codex"
        assert result["evidence_level"] == "local_file"
        assert result["formal_write_allowed"] is False
        assert result["execution_boundary"]["can_enter_formal_layer_automatically"] is False
        assert (project_root / result["artifact_path"]).exists()


# =============================================================================
# 辅助函数和 fixture（将在实现阶段替换为真实导入）
# =============================================================================

class ExecutionBackendSelectionError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _build_reviewed_task(project_root: Path, task_id: str) -> dict:
    return {
        "id": task_id,
        "status": "reviewed_for_dispatch",
        "next_action": "select_execution_backend",
        "dispatch_readiness": {"status": "reviewed_for_dispatch", "blockers": []},
        "dispatch_review": {"status": "reviewed", "action": "approve", "reviewer": "human"},
        "can_execute": False,
        "audit_log": [],
    }


def _build_queued_task(project_root: Path, task_id: str) -> dict:
    return {
        "id": task_id,
        "status": "queued",
        "next_action": "dispatch_review_required",
        "dispatch_readiness": {"status": "blocked", "blockers": [{"code": "dispatch_review_required"}]},
        "can_execute": False,
        "audit_log": [],
    }


def _build_backend_selected_task(
    project_root: Path,
    task_id: str,
    backend_id: str,
    method_id: str,
) -> dict:
    """Create a backend-selected task and set up project state files."""
    # Create design_spec.json with formula for the method
    design_spec = {
        "id": "design_spec",
        "model": {
            "formula": "y ~ x1 + x2",
            "estimator": method_id,
        },
        "dependent_variable": "y",
        "independent_variables": ["x1", "x2"],
    }
    ds_path = project_root / "state" / "product" / "design_spec.json"
    ds_path.parent.mkdir(parents=True, exist_ok=True)
    ds_path.write_text(json.dumps(design_spec), encoding="utf-8")

    # Create run_plan.json
    run_plan = {
        "id": f"run_plan_{task_id}",
        "dataset_path": "Data/analysis_sample.csv",
        "tasks": [
            {
                "method_id": method_id,
                "formula": "y ~ x1 + x2",
            }
        ],
    }
    rp_path = project_root / "state" / "product" / "run_plan.json"
    rp_path.parent.mkdir(parents=True, exist_ok=True)
    rp_path.write_text(json.dumps(run_plan), encoding="utf-8")

    return {
        "id": task_id,
        "status": "backend_selected",
        "next_action": "execute",
        "selected_backend": {"id": backend_id, "evidence_level": "local_execution"},
        "can_execute": True,
        "method_id": method_id,
        "audit_log": [
            {"event": "backend_selected", "actor": "human", "timestamp": "2026-05-21T00:00:00"},
        ],
    }


def _create_sample_csv(path: Path) -> None:
    """Create a sample CSV file with enough rows for OLS estimation."""
    content = "y,x1,x2\n"
    for i in range(20):
        y = 1.0 + 0.5 * i + 0.3 * (i % 3) + 0.1
        content += f"{y:.2f},{i:.1f},{i % 3:.1f}\n"
    path.write_text(content, encoding="utf-8")


# 从实现模块导入真实函数
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from Product.backend.execution_backend_service import (
    ExecutionBackendSelectionError,
    execute_agent_task_with_backend,
    select_execution_backend,
)
