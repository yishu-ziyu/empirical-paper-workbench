from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class AgentTaskQueueApiTests(unittest.TestCase):
    """BDD: Agent Task Queue 只能从 approved SupervisorPlan 派生，且默认摘要优先。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="agent-task-queue-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "agent-task-queue",
                "title": "Agent Task Queue Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]
        self._approve_research_states()

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_create_queue_requires_approved_supervisor_plan(self) -> None:
        """行为 1：没有 approved SupervisorPlan 时，不允许创建任务队列。"""
        missing = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(missing.status_code, 409, msg=missing.text)
        self.assertEqual(missing.json()["error"]["code"], "supervisor_plan_required")
        self.assertFalse((self.project_root / "state" / "product" / "agent_task_queue.json").exists())

        self._write_supervisor_plan(status="needs_review", can_dispatch=False)

        blocked = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "supervisor_plan_not_approved")
        self.assertFalse((self.project_root / "state" / "product" / "agent_task_queue.json").exists())

    def test_bdd_2_approved_plan_persists_summary_first_agent_task_queue(self) -> None:
        """行为 2：approved SupervisorPlan 可以生成摘要优先的 Agent Task Queue。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True)

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        queue = response.json()["agent_task_queue"]
        self.assertEqual(queue["status"], "ready_for_dispatch")
        self.assertEqual(queue["evidence_level"], "local_file")
        self.assertEqual(queue["source_supervisor_plan"]["status"], "approved")
        self.assertEqual(queue["source_supervisor_plan"]["version"], 3)
        self.assertTrue(queue["ui_contract"]["summary_first"])
        self.assertTrue(queue["ui_contract"]["details_collapsed_by_default"])
        self.assertEqual(queue["summary"]["total_tasks"], 2)
        self.assertEqual(queue["summary"]["queued_count"], 2)
        self.assertEqual(queue["summary"]["blocked_count"], 0)
        self.assertEqual(queue["summary"]["owner_agents"], ["pipeline_data", "pipeline_execution"])
        self.assertEqual(queue["tasks"][0]["owner_agent"], "pipeline_data")
        self.assertEqual(queue["tasks"][0]["role"], "Data Agent")
        self.assertEqual(queue["tasks"][0]["title"], "检查数据和变量角色")
        self.assertEqual(queue["tasks"][0]["status"], "queued")
        self.assertEqual(queue["tasks"][0]["blockers"], [])
        self.assertIn("supervisor_plan", queue["tasks"][0]["input_evidence"])
        self.assertIn("output_requirements", queue["tasks"][0])
        self.assertIn("risk_flags", queue["tasks"][0])
        self.assertEqual(queue["tasks"][0]["audit_log"][0]["event"], "task_created_from_supervisor_plan")

        saved_path = self.project_root / "state" / "product" / "agent_task_queue.json"
        self.assertTrue(saved_path.exists())
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["summary"]["total_tasks"], 2)
        self.assertEqual(saved["path"], "state/product/agent_task_queue.json")

    def test_bdd_3_get_returns_persisted_queue_or_empty_blocked_state(self) -> None:
        """行为 3：GET API 必须跨 session 恢复队列，未创建时返回可解释空态。"""
        empty = self.client.get(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(empty.status_code, 200, msg=empty.text)
        self.assertEqual(empty.json()["agent_task_queue"]["status"], "empty")
        self.assertFalse(empty.json()["agent_task_queue"]["can_create"])
        self.assertEqual(empty.json()["agent_task_queue"]["blockers"][0]["code"], "supervisor_plan_required")

        self._write_supervisor_plan(status="approved", can_dispatch=True)
        created = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")
        self.assertEqual(created.status_code, 201, msg=created.text)

        restored = self.client.get(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(restored.status_code, 200, msg=restored.text)
        self.assertEqual(restored.json()["agent_task_queue"]["status"], "ready_for_dispatch")
        self.assertEqual(restored.json()["agent_task_queue"]["summary"]["total_tasks"], 2)

    def test_bdd_4_queue_creation_does_not_mutate_research_states_or_supervisor_plan(self) -> None:
        """行为 4：创建队列不能篡改已确认研究状态或已批准计划。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True)
        state_paths = [
            self.project_root / "state" / "product" / "research_question.json",
            self.project_root / "state" / "product" / "variable_roles.json",
            self.project_root / "state" / "product" / "design_spec.json",
            self.project_root / "state" / "product" / "run_plan.json",
            self.project_root / "state" / "product" / "supervisor_plan.json",
        ]
        before = {path.name: path.read_text(encoding="utf-8") for path in state_paths}

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        after = {path.name: path.read_text(encoding="utf-8") for path in state_paths}
        self.assertEqual(before, after)

    def test_bdd_7_empty_subagent_dispatch_blocks_queue_creation(self) -> None:
        """边界：approved plan 没有子 Agent 分工时，不能创建空派工队列。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True, subagent_dispatch=[])

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "subagent_dispatch_required")
        self.assertFalse((self.project_root / "state" / "product" / "agent_task_queue.json").exists())

    def test_bdd_9_queue_tasks_inherit_internal_skill_bindings_from_supervisor_plan(self) -> None:
        """行为 9：任务队列必须把 SupervisorPlan 推荐的 internal skills 绑定到对应 Agent 任务。"""
        self._write_supervisor_plan(
            status="approved",
            can_dispatch=True,
            subagent_dispatch=[
                {
                    "agent_id": "pipeline_literature",
                    "role": "LiteratureAgent",
                    "task": "递归检索文献、数据线索和变量证据",
                },
                {
                    "agent_id": "pipeline_method",
                    "role": "MethodAgent",
                    "task": "检查 DID 识别门",
                },
            ],
            recommended_internal_skills=[
                {
                    "id": "cap_internal_skill_recursive_research_search",
                    "skill_id": "recursive_research_search",
                    "name": "递归研究搜索",
                    "owner_agent": "LiteratureAgent",
                    "allowed_agents": ["Supervisor", "LiteratureAgent", "ReviewerAgent"],
                    "stage": "recursive_search",
                    "risk_level": "medium",
                    "status": "checklist",
                    "dispatch_targets": ["pipeline_literature"],
                    "quality_gates": {
                        "machine_checkable": ["aers:eval:citation-hygiene-no-fake-refs"],
                        "manual_review": ["source_relevance_review"],
                    },
                    "human_confirmation": {
                        "required_before": ["formal_literature_review_writeback"],
                        "approver_role": "human_researcher",
                    },
                    "formal_write_targets": [],
                    "canonical_policy": {
                        "auto_mode": {
                            "can_generate_patch_proposal": True,
                            "can_write_canonical": False,
                            "proposal_status": "needs_human_review",
                        }
                    },
                },
                {
                    "id": "cap_internal_skill_did_staggered_identification_gate",
                    "skill_id": "did_staggered_identification_gate",
                    "name": "交错 DID 识别门",
                    "owner_agent": "MethodAgent",
                    "allowed_agents": ["Supervisor", "MethodAgent", "ExecutionAgent", "ReviewerAgent"],
                    "stage": "method_design",
                    "risk_level": "high",
                    "status": "checklist",
                    "dispatch_targets": ["pipeline_method"],
                    "quality_gates": {
                        "machine_checkable": ["aers:eval:did-staggered-recovery"],
                        "manual_review": ["parallel_trends_substantive_review"],
                    },
                    "human_confirmation": {
                        "required_before": ["default_run_plan_inclusion", "formal_method_writeback"],
                        "approver_role": "human_researcher",
                    },
                    "formal_write_targets": [],
                    "canonical_policy": {
                        "auto_mode": {
                            "can_generate_patch_proposal": True,
                            "can_write_canonical": False,
                            "proposal_status": "needs_human_review",
                        }
                    },
                },
            ],
        )

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        queue = response.json()["agent_task_queue"]
        self.assertEqual(queue["summary"]["internal_skill_count"], 2)
        self.assertEqual(queue["summary"]["high_risk_internal_skill_count"], 1)

        literature_task = queue["tasks"][0]
        method_task = queue["tasks"][1]
        self.assertEqual(literature_task["internal_skill_bindings"][0]["skill_id"], "recursive_research_search")
        self.assertEqual(method_task["internal_skill_bindings"][0]["skill_id"], "did_staggered_identification_gate")
        self.assertEqual(method_task["internal_skill_bindings"][0]["formal_write_targets"], [])
        self.assertFalse(method_task["internal_skill_bindings"][0]["canonical_policy"]["auto_mode"]["can_write_canonical"])
        self.assertEqual(method_task["next_action"], "dispatch_review_required")
        self.assertFalse(method_task["can_execute"])
        self.assertIn(
            "aers:eval:did-staggered-recovery",
            method_task["internal_skill_bindings"][0]["quality_gates"]["machine_checkable"],
        )
        self.assertEqual(
            method_task["internal_skill_bindings"][0]["next_action"],
            "review_internal_skill_before_execution",
        )

    def test_bdd_10_queue_preserves_llm_semantic_skill_reason_for_dispatch_review(self) -> None:
        """行为 10：派工队列必须保留 LLM Supervisor 解释过的 skill 绑定理由。"""
        self._write_supervisor_plan(
            status="approved",
            can_dispatch=True,
            subagent_dispatch=[
                {
                    "agent_id": "pipeline_reviewer",
                    "role": "ReviewerAgent",
                    "task": "审阅写作出口和投稿预检",
                },
            ],
            recommended_internal_skills=[
                {
                    "id": "cap_internal_skill_aer_abstract_submission_preflight",
                    "skill_id": "aer_abstract_submission_preflight",
                    "name": "AER-like 投稿预检",
                    "owner_agent": "ReviewerAgent",
                    "allowed_agents": ["Supervisor", "ReviewerAgent", "ManuscriptAgent", "ExportAgent"],
                    "stage": "review_export",
                    "risk_level": "medium",
                    "status": "checklist",
                    "dispatch_targets": ["pipeline_reviewer"],
                    "matched_reason": "",
                    "selection_source": "llm_semantic_judgment",
                    "semantic_selection_reason": "用户选择顶刊标准，需要先检查摘要、表格说明和披露边界。",
                    "llm_semantic_judgment": {
                        "reason": "用户选择顶刊标准，需要先检查摘要、表格说明和披露边界。",
                        "evidence_fit": "写作出口前缺少投稿格式和 disclosure 核验。",
                        "agent_fit": "ReviewerAgent 负责审阅出口质量。",
                        "risk_note": "不能静默导出正式投稿包。",
                        "human_review_note": "正式导出前必须由研究者确认。",
                        "confidence": "medium",
                    },
                    "quality_gates": {
                        "machine_checkable": ["aers:eval:aer-abstract-100words"],
                        "manual_review": ["contribution_claim_review"],
                    },
                    "human_confirmation": {
                        "required_before": ["formal_submission_package_export"],
                        "approver_role": "human_researcher",
                    },
                    "formal_write_targets": [],
                    "canonical_policy": {
                        "auto_mode": {
                            "can_generate_patch_proposal": True,
                            "can_write_canonical": False,
                            "proposal_status": "needs_human_review",
                        }
                    },
                },
            ],
        )

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        binding = response.json()["agent_task_queue"]["tasks"][0]["internal_skill_bindings"][0]
        self.assertEqual(binding["skill_id"], "aer_abstract_submission_preflight")
        self.assertEqual(binding["selection_source"], "llm_semantic_judgment")
        self.assertEqual(
            binding["semantic_selection_reason"],
            "用户选择顶刊标准，需要先检查摘要、表格说明和披露边界。",
        )
        self.assertEqual(
            binding["llm_semantic_judgment"]["risk_note"],
            "不能静默导出正式投稿包。",
        )
        self.assertFalse(binding["canonical_policy"]["auto_mode"]["can_write_canonical"])

    def test_bdd_11_queue_exposes_user_facing_skill_reason_artifacts_and_boundary(self) -> None:
        """行为 11：每个队列任务必须能解释绑定 skill 的理由、预期产物和执行边界。"""
        self._write_supervisor_plan(
            status="approved",
            can_dispatch=True,
            subagent_dispatch=[
                {
                    "agent_id": "pipeline_literature",
                    "role": "LiteratureAgent",
                    "task": "递归检索文献、数据线索和变量证据",
                },
            ],
            recommended_internal_skills=[
                {
                    "id": "cap_internal_skill_recursive_research_search",
                    "skill_id": "recursive_research_search",
                    "name": "递归研究搜索",
                    "owner_agent": "LiteratureAgent",
                    "allowed_agents": ["Supervisor", "LiteratureAgent", "ReviewerAgent"],
                    "stage": "recursive_search",
                    "risk_level": "medium",
                    "status": "checklist",
                    "dispatch_targets": ["pipeline_literature"],
                    "selection_source": "registry_and_llm_semantic_judgment",
                    "semantic_selection_reason": "题目需要先从文献、数据和变量证据形成递归搜索图。",
                    "expected_artifacts": ["LiteratureSeedPackage", "search_query_graph", "verification_queue"],
                    "execution_boundary": "review_only_until_dispatch_approved",
                    "skill_sources": [
                        {
                            "name": "Auto-Empirical-Research-Skills",
                            "url": "https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills",
                            "license": "CC-BY-SA-4.0",
                        }
                    ],
                    "quality_gates": {
                        "machine_checkable": ["aers:eval:citation-hygiene-no-fake-refs"],
                        "manual_review": ["source_relevance_review"],
                    },
                    "human_confirmation": {
                        "required_before": ["formal_literature_review_writeback"],
                        "approver_role": "human_researcher",
                    },
                    "formal_write_targets": [],
                    "canonical_policy": {
                        "auto_mode": {
                            "can_generate_patch_proposal": True,
                            "can_write_canonical": False,
                            "proposal_status": "needs_human_review",
                        }
                    },
                },
            ],
        )

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        binding = response.json()["agent_task_queue"]["tasks"][0]["internal_skill_bindings"][0]
        self.assertEqual(binding["skill_id"], "recursive_research_search")
        self.assertEqual(
            binding["why_this_skill"],
            "题目需要先从文献、数据和变量证据形成递归搜索图。",
        )
        self.assertEqual(
            binding["expected_artifacts"],
            ["LiteratureSeedPackage", "search_query_graph", "verification_queue"],
        )
        self.assertEqual(binding["execution_boundary"], "review_only_until_dispatch_approved")
        self.assertEqual(binding["skill_sources"][0]["name"], "Auto-Empirical-Research-Skills")
        self.assertFalse(binding["can_execute_without_human_review"])

    def test_bdd_12_execute_endpoint_requires_selected_backend_without_mutating_task(self) -> None:
        """行为 12：执行 API 必须先要求后端选择，不能把未选后端任务写成失败。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True)
        created = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")
        self.assertEqual(created.status_code, 201, msg=created.text)
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_02/dispatch-review",
            json={"action": "approve", "note": "可以进入后端选择"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_02/execute"
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "execution_backend_required")
        queue = self.client.get(f"/api/v1/projects/{self.project_id}/agent-task-queue").json()[
            "agent_task_queue"
        ]
        task = queue["tasks"][1]
        self.assertEqual(task["status"], "reviewed_for_dispatch")
        self.assertEqual(task["next_action"], "select_execution_backend")
        self.assertNotIn("execution_result", task)

    def test_bdd_13_reviewed_task_can_select_codex_backend_and_execute_through_api(self) -> None:
        """行为 13：已审阅任务可以通过 API 选择 Codex 后端并生成可审阅脚本。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True)
        created = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")
        self.assertEqual(created.status_code, 201, msg=created.text)
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_02/dispatch-review",
            json={"action": "approve", "note": "先生成脚本草案"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        selected = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_02/select-backend",
            json={"backend_id": "codex"},
        )

        self.assertEqual(selected.status_code, 200, msg=selected.text)
        selected_task = selected.json()["agent_task_queue"]["tasks"][1]
        self.assertEqual(selected_task["status"], "backend_selected")
        self.assertEqual(selected_task["selected_backend"]["id"], "codex")
        self.assertEqual(
            selected_task["selected_backend"]["execution_boundary"]["kind"],
            "draft_code_generation",
        )

        executed = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_02/execute"
        )

        self.assertEqual(executed.status_code, 200, msg=executed.text)
        body = executed.json()
        self.assertEqual(body["execution_result"]["engine"], "codex")
        self.assertEqual(body["execution_result"]["evidence_level"], "local_file")
        artifact_path = self.project_root / body["execution_result"]["artifact_path"]
        self.assertTrue(artifact_path.exists())
        task = body["agent_task_queue"]["tasks"][1]
        self.assertEqual(task["status"], "succeeded")
        self.assertEqual(task["execution_result"]["engine"], "codex")

    def test_bdd_14_queue_exposes_llm_intervention_handoff_contract(self) -> None:
        """行为 14：队列必须说明 LLM 何时判断、何时交还确定性服务、何处人工确认。"""
        self._write_supervisor_plan(
            status="approved",
            can_dispatch=True,
            subagent_dispatch=[
                {
                    "agent_id": "pipeline_literature",
                    "role": "LiteratureAgent",
                    "task": "递归检索文献、数据线索和变量证据",
                },
            ],
            recommended_internal_skills=[
                {
                    "id": "cap_internal_skill_recursive_research_search",
                    "skill_id": "recursive_research_search",
                    "name": "递归研究搜索",
                    "owner_agent": "LiteratureAgent",
                    "stage": "recursive_search",
                    "risk_level": "medium",
                    "dispatch_targets": ["pipeline_literature"],
                    "selection_source": "registry_and_llm_semantic_judgment",
                    "semantic_selection_reason": "题目需要先从文献、数据和变量证据形成递归搜索图。",
                    "expected_artifacts": ["LiteratureSeedPackage", "search_query_graph"],
                    "execution_boundary": "review_only_until_dispatch_approved",
                },
            ],
            llm_intervention_plan={
                "contract_version": "llm_intervention.v1",
                "default_policy": "llm_plans_deterministic_executes_human_promotes",
                "stage_handoffs": [
                    {
                        "stage": "skill_selection",
                        "llm_role": "解释为什么选择 Skill，并列出缺失证据。",
                        "deterministic_owner": "internal_skill_registry",
                        "handoff_condition": "Skill id、来源、适用理由和执行边界写入 SupervisorPlan。",
                        "human_gate": "review_internal_skill_before_execution",
                        "formal_boundary": "draft_only_until_human_review",
                    },
                    {
                        "stage": "agent_task_queue",
                        "llm_role": "把研究路线拆成子 Agent 任务摘要。",
                        "deterministic_owner": "agent_task_queue_service",
                        "handoff_condition": "任务队列持久化为 local_file，默认不可执行。",
                        "human_gate": "dispatch_review_required",
                        "formal_boundary": "draft_only_until_human_review",
                    },
                ],
            },
        )

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        queue = response.json()["agent_task_queue"]
        self.assertEqual(queue["llm_intervention_contract"]["contract_version"], "llm_intervention.v1")
        self.assertEqual(
            queue["llm_intervention_contract"]["default_policy"],
            "llm_plans_deterministic_executes_human_promotes",
        )
        self.assertIn("llm_intervention_contract", queue["ui_contract"]["hidden_by_default"])

        handoff = queue["tasks"][0]["llm_intervention_handoff"]
        self.assertEqual(handoff["stage"], "skill_selection")
        self.assertEqual(handoff["llm_role"], "解释为什么选择 Skill，并列出缺失证据。")
        self.assertEqual(handoff["deterministic_owner"], "internal_skill_registry")
        self.assertEqual(handoff["human_gate"], "review_internal_skill_before_execution")
        self.assertEqual(handoff["formal_boundary"], "draft_only_until_human_review")
        self.assertEqual(
            handoff["selected_skill_reason"],
            "题目需要先从文献、数据和变量证据形成递归搜索图。",
        )
        self.assertFalse(queue["tasks"][0]["can_execute"])

    def test_bdd_15_queue_and_tasks_expose_one_primary_next_action(self) -> None:
        """行为 15：队列必须从任务状态推导一个清晰的下一步动作。"""
        self._write_supervisor_plan(
            status="approved",
            can_dispatch=True,
            subagent_dispatch=[
                {
                    "agent_id": "pipeline_execution",
                    "role": "ExecutionAgent",
                    "task": "执行并验证模型",
                },
            ],
        )

        created = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(created.status_code, 201, msg=created.text)
        created_queue = created.json()["agent_task_queue"]
        self.assertEqual(created_queue["primary_action"]["id"], "dispatch_review_required")
        self.assertEqual(created_queue["primary_action"]["task_id"], "agent_task_01")
        self.assertEqual(created_queue["tasks"][0]["primary_action"]["label"], "打开派工审阅")
        self.assertIn("不能直接执行", created_queue["tasks"][0]["primary_action"]["reason"])

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/dispatch-review",
            json={"action": "approve", "note": "可以进入后端选择"},
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        reviewed_queue = reviewed.json()["agent_task_queue"]
        self.assertEqual(reviewed_queue["primary_action"]["id"], "select_execution_backend")
        self.assertEqual(reviewed_queue["tasks"][0]["primary_action"]["label"], "选择执行后端")

        selected = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/select-backend",
            json={"backend_id": "codex"},
        )

        self.assertEqual(selected.status_code, 200, msg=selected.text)
        selected_queue = selected.json()["agent_task_queue"]
        self.assertEqual(selected_queue["primary_action"]["id"], "execute_agent_task")
        self.assertEqual(selected_queue["tasks"][0]["primary_action"]["label"], "开始真实执行")
        self.assertTrue(selected_queue["tasks"][0]["primary_action"]["enabled"])

        executed = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/execute"
        )

        self.assertEqual(executed.status_code, 200, msg=executed.text)
        executed_queue = executed.json()["agent_task_queue"]
        self.assertEqual(executed_queue["primary_action"]["id"], "review_execution_result")
        self.assertEqual(executed_queue["tasks"][0]["primary_action"]["label"], "查看运行结果")
        self.assertFalse(executed_queue["tasks"][0]["primary_action"]["writes_formal_layer"])

    def test_bdd_16_default_llm_intervention_contract_maps_full_product_chain(self) -> None:
        """行为 16：默认 LLM 介入契约必须覆盖从选题到导出预检的主链路。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True)

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        contract = response.json()["agent_task_queue"]["llm_intervention_contract"]
        handoffs = {item["stage"]: item for item in contract["stage_handoffs"]}
        expected_stages = [
            "topic_intake",
            "supervisor_plan",
            "skill_selection",
            "agent_task_queue",
            "literature_search",
            "data_variables",
            "method_design",
            "execution_experiment",
            "writing",
            "review_export",
        ]

        self.assertEqual(contract["contract_version"], "llm_intervention.v1")
        self.assertEqual(contract["product_chain"], expected_stages)
        for stage in expected_stages:
            self.assertIn(stage, handoffs)
            self.assertIn("llm_role", handoffs[stage])
            self.assertIn("deterministic_owner", handoffs[stage])
            self.assertIn("agent_team_policy", handoffs[stage])
            self.assertIn("control_returns_to_user_when", handoffs[stage])
            self.assertFalse(handoffs[stage]["writes_formal_layer"])

        self.assertEqual(handoffs["topic_intake"]["deterministic_owner"], "research_question_service")
        self.assertEqual(handoffs["supervisor_plan"]["human_gate"], "review_supervisor_plan")
        self.assertEqual(handoffs["agent_task_queue"]["human_gate"], "dispatch_review_required")
        self.assertEqual(handoffs["execution_experiment"]["deterministic_owner"], "execution_backend_router")
        self.assertEqual(handoffs["review_export"]["human_gate"], "export_preflight_review")

    def _write_supervisor_plan(
        self,
        status: str,
        can_dispatch: bool,
        subagent_dispatch: list[dict] | None = None,
        recommended_internal_skills: list[dict] | None = None,
        llm_intervention_plan: dict | None = None,
    ) -> None:
        path = self.project_root / "state" / "product" / "supervisor_plan.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        plan = {
            "id": "supervisor_plan",
            "version": 3,
            "status": status,
            "can_dispatch": can_dispatch,
            "evidence_level": "local_execution",
            "objective": "把 approved plan 拆成可审阅任务队列",
            "path": "state/product/supervisor_plan.json",
            "input_research_question": {
                "question": "培训是否影响工资？",
                "topic_session_id": "topic_session_v1",
                "version": 1,
            },
            "input_evidence": {
                "research_question_path": "state/product/research_question.json",
                "variable_role_set_path": "state/product/variable_roles.json",
                "design_spec_path": "state/product/design_spec.json",
                "run_plan_path": "state/product/run_plan.json",
            },
            "stage_plan": [
                {"stage": "数据与变量", "goal": "复核字段角色与样本口径", "status": "planned"},
                {"stage": "实证执行", "goal": "运行 OLS 并交叉验证 StatsPAI", "status": "planned"},
            ],
            "subagent_dispatch": subagent_dispatch
            if subagent_dispatch is not None
            else [
                {"agent_id": "pipeline_data", "role": "Data Agent", "task": "检查数据和变量角色"},
                {"agent_id": "pipeline_execution", "role": "Execution Agent", "task": "执行并验证模型"},
            ],
            "evidence_requirements": [
                {"id": "dataset_profile", "requirement": "保留字段画像和样本量", "evidence_level": "local_file"},
                {"id": "model_run", "requirement": "保留运行日志和回归结果", "evidence_level": "local_execution"},
            ],
            "risks": [
                {"id": "heuristic_roles", "level": "medium", "description": "变量角色候选不能直接进入论文"}
            ],
            "human_gates": [
                {"id": "review_supervisor_plan", "label": "人工确认 SupervisorPlan", "required": True}
            ],
            "recommended_internal_skills": recommended_internal_skills or [],
        }
        if llm_intervention_plan is not None:
            plan["llm_intervention_plan"] = llm_intervention_plan
        path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    def _approve_research_states(self) -> None:
        question = self.client.put(
            f"/api/v1/projects/{self.project_id}/research-question/current",
            json={"question": "培训是否影响工资？", "source": "project_seed", "note": "选题已确认。"},
        )
        self.assertEqual(question.status_code, 200, msg=question.text)
        roles = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "Data/Final/analysis_sample.csv",
                "roles": {
                    "outcome": ["wage"],
                    "treatment": ["trained"],
                    "controls": ["edu", "experience"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
                "note": "变量角色已确认。",
            },
        )
        self.assertEqual(roles.status_code, 200, msg=roles.text)
        design = self.client.put(
            f"/api/v1/projects/{self.project_id}/design-spec",
            json={
                "research_question": "培训是否影响工资？",
                "identification_strategy": {
                    "name": "baseline_ols",
                    "summary": "在已确认控制变量下估计培训对工资的相关关系。",
                    "assumptions": ["控制教育和经验后，处理变量外生。"],
                    "threats": ["遗漏变量偏误", "样本选择偏误"],
                },
                "model": {
                    "estimator": "ols",
                    "formula": "wage ~ trained + edu + experience",
                    "fixed_effects": [],
                    "cluster_by": [],
                    "sample_filter": "all",
                },
                "note": "研究设计已确认。",
            },
        )
        self.assertEqual(design.status_code, 200, msg=design.text)
        draft = self.client.get(f"/api/v1/projects/{self.project_id}/run-plan").json()["run_plan"]
        run_plan = self.client.put(
            f"/api/v1/projects/{self.project_id}/run-plan",
            json={"tasks": draft["tasks"], "outputs": draft["outputs"], "note": "执行计划已确认。"},
        )
        self.assertEqual(run_plan.status_code, 200, msg=run_plan.text)

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: agent-task-queue\n  title: Agent Task Queue Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n12,0,14,5\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


class AgentTaskQueueFrontendTests(unittest.TestCase):
    """BDD: Overview 必须把 Agent Task Queue 做成摘要优先的干净派工台。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_frontend_contains_summary_first_queue_surface(self) -> None:
        """行为 5：前端必须有摘要优先的 Agent Task Queue 面板。"""
        self.assertIn("agent-task-queue-panel", self.index_html)
        self.assertIn("agent-task-queue-body", self.index_html)
        self.assertIn("renderAgentTaskQueue", self.app_js)
        self.assertIn("agent-task-queue-summary", self.app_js)
        self.assertIn("任务总数", self.app_js)
        self.assertIn("负责人 Agent", self.app_js)
        self.assertIn("阻塞项", self.app_js)
        self.assertIn(".agent-task-queue-card", self.styles_css)

    def test_bdd_6_frontend_can_create_queue_only_as_explicit_action(self) -> None:
        """行为 6：未创建队列时，前端必须显示明确的人工创建按钮和安全边界。"""
        self.assertIn("v2api.agentTaskQueue.create", self.app_js)
        self.assertIn("handleCreateAgentTaskQueue", self.app_js)
        self.assertIn("data-agent-task-create-action", self.app_js)
        self.assertIn("创建 Agent 任务队列", self.app_js)
        self.assertIn("不会自动执行或改写研究状态", self.app_js)

    def test_bdd_8_task_details_are_progressively_disclosed(self) -> None:
        """行为 8：输入证据、输出要求、风险和审计日志必须默认折叠。"""
        self.assertIn("agent-task-progressive-disclosure", self.app_js)
        self.assertIn("查看任务详情", self.app_js)
        self.assertIn("输入证据", self.app_js)
        self.assertIn("输出要求", self.app_js)
        self.assertIn("审计日志", self.app_js)
        self.assertIn("details_collapsed_by_default", self.app_js)

    def test_bdd_9_frontend_exposes_internal_skill_explanation_in_task_details(self) -> None:
        """行为 9：任务详情必须解释绑定了哪个 Skill、为什么选它、产物和执行边界。"""
        self.assertIn("renderAgentTaskSkillBindings", self.app_js)
        self.assertIn("internal_skill_bindings", self.app_js)
        self.assertIn("why_this_skill", self.app_js)
        self.assertIn("为什么选这个 Skill", self.app_js)
        self.assertIn("预期产物", self.app_js)
        self.assertIn("执行边界", self.app_js)
        self.assertIn("Skill 来源", self.app_js)
        self.assertIn(".agent-task-skill-binding", self.styles_css)

    def test_bdd_10_journey_view_renders_supervisor_plan_and_task_queue(self) -> None:
        """行为 10：进入工作台首页后，SupervisorPlan 与 Agent Task Queue 不能停留在空容器。"""
        journey_start = self.app_js.index("function renderJourney()")
        journey_end = self.app_js.index("// --- Data & Variables Page ---", journey_start)
        journey_body = self.app_js[journey_start:journey_end]

        self.assertIn("renderSupervisorPlan();", journey_body)
        self.assertIn("renderAgentTaskQueue();", journey_body)

    def test_bdd_11_frontend_exposes_backend_selection_reason_fallback_and_boundary(self) -> None:
        """行为 11：后端选择不能只显示名字，必须解释选择理由、失败后备选和执行边界。"""
        self.assertIn("renderAgentTaskBackendDetails", self.app_js)
        self.assertIn("selection_reason", self.app_js)
        self.assertIn("fallback_backend_ids", self.app_js)
        self.assertIn("execution_boundary", self.app_js)
        self.assertIn("为什么选这个后端", self.app_js)
        self.assertIn("失败后备选", self.app_js)
        self.assertIn("正式层边界", self.app_js)
        self.assertIn(".agent-task-backend-details", self.styles_css)

    def test_bdd_12_legacy_backend_selection_still_has_human_explanation(self) -> None:
        """行为 12：旧任务只有后端 id 时，也必须显示兼容的人话解释。"""
        self.assertIn("backendDefaultSelectionReason", self.app_js)
        self.assertIn("backendDefaultFallbackIds", self.app_js)
        self.assertIn("backendDefaultExecutionBoundary", self.app_js)
        self.assertIn("适合本地统计执行、结构化结果和可追溯产物", self.app_js)
        self.assertIn("python_ols_adapter", self.app_js)
        self.assertIn("can_enter_formal_layer_automatically: false", self.app_js)

    def test_bdd_13_succeeded_task_exposes_result_handoff(self) -> None:
        """行为 13：任务执行成功后，必须展示结果路径、日志线索、自检状态和下一步。"""
        self.assertIn("renderAgentTaskExecutionHandoff", self.app_js)
        self.assertIn("结果文件", self.app_js)
        self.assertIn("运行清单", self.app_js)
        self.assertIn("评估器状态", self.app_js)
        self.assertIn("下一步动作", self.app_js)
        self.assertIn("result_artifact_path", self.app_js)
        self.assertIn("manifest_artifact_path", self.app_js)
        self.assertIn(".agent-task-execution-handoff", self.styles_css)

    def test_bdd_14_frontend_renders_queue_primary_action_guidance(self) -> None:
        """行为 14：任务队列必须直接显示后端给出的主动作和理由。"""
        self.assertIn("renderAgentTaskPrimaryAction", self.app_js)
        self.assertIn("primary_action", self.app_js)
        self.assertIn("当前建议动作", self.app_js)
        self.assertIn("为什么现在做这一步", self.app_js)
        self.assertIn(".agent-task-primary-action", self.styles_css)
        self.assertIn("20260608-p0h-primary-action", self.index_html)


if __name__ == "__main__":
    unittest.main()
