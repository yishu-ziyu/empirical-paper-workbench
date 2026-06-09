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

    def test_bdd_17_reference_chain_policy_enters_queue_and_literature_task(self) -> None:
        """行为 17：文献/引用链路策略必须进入队列，并被文献任务继承。"""
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
                    "task": "检查识别策略和方法门",
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
                    "expected_artifacts": ["LiteratureSeedPackage", "search_query_graph", "citation_verification_queue"],
                    "execution_boundary": "review_only_until_dispatch_approved",
                },
            ],
            reference_chain_policy={
                "contract_version": "reference_chain.v1",
                "status": "needs_review",
                "source_priority": ["cnki", "scholar", "zotero", "local_notes", "arxiv"],
                "sources": [
                    {
                        "id": "cnki",
                        "label": "CNKI",
                        "trigger": "中文制度背景、本土文献和中文关键词扩展。",
                        "mode": "manual_assisted_or_browser_assisted_search",
                    }
                ],
                "writes_formal_layer": True,
            },
        )

        response = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")

        self.assertEqual(response.status_code, 201, msg=response.text)
        queue = response.json()["agent_task_queue"]
        policy = queue["reference_chain_policy"]
        source_ids = [source["id"] for source in policy["sources"]]

        self.assertEqual(policy["contract_version"], "reference_chain.v1")
        self.assertEqual(policy["status"], "needs_review")
        self.assertEqual(policy["max_depth"], 2)
        self.assertEqual(policy["max_iterations"], 5)
        self.assertEqual(policy["source_priority"], ["cnki", "scholar", "zotero", "local_notes", "arxiv"])
        self.assertEqual(
            source_ids,
            ["arxiv", "scholar", "cnki", "zotero", "local_notes"],
        )
        self.assertEqual(policy["sources"][2]["mode"], "manual_assisted_or_browser_assisted_search")
        self.assertIn("citation_verification_queue", policy["required_artifacts"])
        self.assertEqual(policy["candidate_reference_states"], ["candidate", "verified", "rejected"])
        self.assertEqual(
            policy["draft_citation_policy"],
            "candidate_references_may_enter_draft_with_visible_review_state",
        )
        self.assertEqual(policy["formal_writeback_gate"], "review_literature_seed_package")
        self.assertFalse(policy["writes_formal_layer"])
        self.assertIn("reference_chain_policy", queue["ui_contract"]["hidden_by_default"])

        literature_task = queue["tasks"][0]
        method_task = queue["tasks"][1]
        self.assertEqual(literature_task["reference_chain_policy"]["status"], "needs_review")
        self.assertEqual(
            literature_task["reference_chain_policy"]["source_priority"],
            ["cnki", "scholar", "zotero", "local_notes", "arxiv"],
        )
        self.assertEqual(literature_task["reference_chain_policy"]["formal_writeback_gate"], "review_literature_seed_package")
        self.assertFalse(literature_task["reference_chain_policy"]["writes_formal_layer"])
        self.assertNotIn("reference_chain_policy", method_task)

    def test_bdd_18_literature_task_codex_execution_writes_candidate_reference_seed_package(self) -> None:
        """行为 18：文献任务执行时先生成候选来源种子包，不宣称引用已验证。"""
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
                    "expected_artifacts": ["LiteratureSeedPackage", "search_query_graph", "citation_verification_queue"],
                    "execution_boundary": "review_only_until_dispatch_approved",
                },
            ],
            reference_chain_policy={
                "contract_version": "reference_chain.v1",
                "status": "needs_review",
                "source_priority": ["cnki", "scholar", "zotero", "local_notes", "arxiv"],
                "max_depth": 2,
                "max_iterations": 5,
                "formal_writeback_gate": "review_literature_seed_package",
                "writes_formal_layer": True,
            },
        )
        created = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")
        self.assertEqual(created.status_code, 201, msg=created.text)
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/dispatch-review",
            json={"action": "approve", "note": "先生成候选来源种子包"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        selected = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/select-backend",
            json={"backend_id": "codex"},
        )
        self.assertEqual(selected.status_code, 200, msg=selected.text)

        executed = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/execute"
        )

        self.assertEqual(executed.status_code, 200, msg=executed.text)
        result = executed.json()["execution_result"]
        self.assertEqual(result["engine"], "codex")
        self.assertEqual(result["execution_kind"], "reference_chain_seed_package")
        self.assertEqual(result["evidence_level"], "local_file")
        self.assertFalse(result["formal_write_allowed"])
        self.assertFalse(result["writes_formal_layer"])
        review = result["result_review"]
        self.assertEqual(review["title"], "候选来源种子包")
        self.assertEqual(review["artifact_path"], result["artifact_path"])
        self.assertEqual(review["review_gate"], "review_literature_seed_package")
        self.assertEqual(review["next_action"], "review_literature_seed_package")
        self.assertEqual(review["reference_state"], "candidate")
        self.assertFalse(review["claims_verified_citations"])
        self.assertFalse(review["can_enter_formal_layer"])
        self.assertIn("候选检索式是否覆盖研究题目", review["review_focus"])
        artifact_path = self.project_root / result["artifact_path"]
        self.assertTrue(artifact_path.exists())

        package = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual(package["schema_version"], "p1.reference_chain_seed_package.v1")
        self.assertEqual(package["status"], "candidate_reference_seed_package_ready")
        self.assertEqual(package["source_priority"], ["cnki", "scholar", "zotero", "local_notes", "arxiv"])
        self.assertEqual(package["max_depth"], 2)
        self.assertEqual(package["max_iterations"], 5)
        self.assertEqual(package["formal_writeback_gate"], "review_literature_seed_package")
        self.assertFalse(package["writes_formal_layer"])
        self.assertGreaterEqual(len(package["candidate_queries"]), 5)
        self.assertTrue(
            all(query["review_state"] == "candidate" for query in package["candidate_queries"])
        )
        self.assertTrue(
            all(not query["can_enter_formal_layer"] for query in package["candidate_queries"])
        )
        self.assertEqual(package["citation_verification_policy"]["default_state"], "candidate")
        self.assertIn("verified_requires", package["citation_verification_policy"])
        self.assertFalse(package["claims_verified_citations"])

    def test_bdd_19_reference_seed_package_review_only_promotes_to_draft_layer(self) -> None:
        """行为 19：候选来源种子包通过人工审阅后，只能进入草稿综述，不能写入正式层。"""
        self._execute_reference_seed_package_task()

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/reference-seed-review",
            json={"action": "approve_for_draft", "note": "可以进入草稿综述，但引用仍需补查。"},
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        task = reviewed.json()["agent_task_queue"]["tasks"][0]
        review = task["reference_seed_review"]
        self.assertEqual(review["status"], "approved_for_draft")
        self.assertEqual(review["review_gate"], "review_literature_seed_package")
        self.assertTrue(review["draft_layer_allowed"])
        self.assertFalse(review["formal_write_allowed"])
        self.assertEqual(review["reference_state"], "candidate")
        self.assertIn("草稿综述", review["next_action_label"])
        self.assertEqual(task["status"], "reviewed_for_draft")
        self.assertEqual(task["next_action"], "draft_literature_review")
        self.assertEqual(task["primary_action"]["id"], "draft_literature_review")
        self.assertEqual(task["primary_action"]["label"], "进入草稿综述")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertFalse(task["execution_result"]["result_review"]["can_enter_formal_layer"])
        self.assertEqual(task["execution_result"]["result_review"]["last_review_action"], "approve_for_draft")
        self.assertEqual(task["audit_log"][-1]["event"], "reference_seed_package_reviewed")

        saved = json.loads(
            (self.project_root / "state" / "product" / "agent_task_queue.json").read_text(encoding="utf-8")
        )
        self.assertEqual(saved["tasks"][0]["reference_seed_review"]["status"], "approved_for_draft")

    def test_bdd_20_reference_seed_package_review_requires_seed_package_result(self) -> None:
        """行为 20：没有候选来源种子包执行结果时，不能伪造文献种子包审阅。"""
        self._write_supervisor_plan(status="approved", can_dispatch=True)
        created = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")
        self.assertEqual(created.status_code, 201, msg=created.text)

        blocked = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/reference-seed-review",
            json={"action": "approve_for_draft", "note": "还没有真实种子包。"},
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "reference_seed_package_required")

    def test_bdd_21_approved_seed_package_generates_draft_layer_literature_review(self) -> None:
        """行为 21：通过审阅的候选来源种子包可以生成草稿层文献综述，但不能写入正式层。"""
        self._execute_reference_seed_package_task()
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/reference-seed-review",
            json={"action": "approve_for_draft", "note": "可以进入草稿综述。"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)

        drafted = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-literature-review"
        )

        self.assertEqual(drafted.status_code, 200, msg=drafted.text)
        task = drafted.json()["agent_task_queue"]["tasks"][0]
        draft = task["draft_literature_review"]
        self.assertEqual(draft["status"], "draft_ready")
        self.assertEqual(draft["draft_layer"], "exploratory")
        self.assertEqual(draft["source_review_gate"], "review_literature_seed_package")
        self.assertFalse(draft["formal_write_allowed"])
        self.assertFalse(draft["claims_verified_citations"])
        self.assertEqual(draft["next_action"], "review_draft_literature_review")
        self.assertIn("候选来源种子包", draft["limitations"])
        self.assertEqual(task["status"], "draft_literature_review_ready")
        self.assertEqual(task["next_action"], "review_draft_literature_review")
        self.assertEqual(task["primary_action"]["id"], "review_draft_literature_review")
        self.assertEqual(task["primary_action"]["label"], "审阅草稿综述")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(task["audit_log"][-1]["event"], "draft_literature_review_generated")

        draft_path = self.project_root / draft["artifact_path"]
        self.assertTrue(draft_path.exists())
        draft_text = draft_path.read_text(encoding="utf-8")
        self.assertIn("# 文献综述草稿", draft_text)
        self.assertIn("培训是否影响工资？", draft_text)
        self.assertIn("候选检索式", draft_text)
        self.assertIn("草稿层边界", draft_text)

    def test_bdd_22_draft_literature_review_requires_approved_seed_package(self) -> None:
        """行为 22：候选来源包未通过人工审阅时，不能跳过门禁直接生成综述草稿。"""
        self._execute_reference_seed_package_task()

        blocked = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-literature-review"
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "reference_seed_review_required")

    def test_bdd_23_reviewed_draft_literature_review_opens_citation_verification_tasks(self) -> None:
        """行为 23：草稿综述通过人工审阅后，只能打开引用核验任务，不能声明引用已验证。"""
        self._generate_draft_literature_review_task()

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-literature-review-review",
            json={"action": "approve_for_citation_verification", "note": "草稿结构可进入引用核验。"},
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        task = reviewed.json()["agent_task_queue"]["tasks"][0]
        review = task["draft_literature_review_review"]
        self.assertEqual(review["status"], "approved_for_citation_verification")
        self.assertEqual(review["review_gate"], "review_draft_literature_review")
        self.assertTrue(review["citation_verification_allowed"])
        self.assertFalse(review["formal_write_allowed"])
        self.assertFalse(review["claims_verified_citations"])
        self.assertEqual(task["status"], "citation_verification_ready")
        self.assertEqual(task["next_action"], "verify_citations")
        self.assertEqual(task["primary_action"]["id"], "verify_citations")
        self.assertEqual(task["primary_action"]["label"], "进入引用核验")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])

        citation_tasks = task["citation_verification_tasks"]
        self.assertGreaterEqual(len(citation_tasks), 5)
        self.assertTrue(all(item["status"] == "pending" for item in citation_tasks))
        self.assertTrue(all(item["citation_state"] == "candidate" for item in citation_tasks))
        self.assertTrue(all(not item["formal_write_allowed"] for item in citation_tasks))
        self.assertTrue(all(not item["claims_verified_citations"] for item in citation_tasks))
        self.assertIn("authors", citation_tasks[0]["required_checks"])
        self.assertIn("doi_or_stable_url", citation_tasks[0]["required_checks"])
        self.assertEqual(task["audit_log"][-1]["event"], "draft_literature_review_reviewed")

        saved = json.loads(
            (self.project_root / "state" / "product" / "agent_task_queue.json").read_text(encoding="utf-8")
        )
        self.assertEqual(saved["tasks"][0]["status"], "citation_verification_ready")
        self.assertEqual(saved["tasks"][0]["citation_verification_tasks"][0]["status"], "pending")

    def test_bdd_24_draft_literature_review_review_requires_draft(self) -> None:
        """行为 24：没有综述草稿时，不能伪造草稿审阅并打开引用核验队列。"""
        self._execute_reference_seed_package_task()

        blocked = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-literature-review-review",
            json={"action": "approve_for_citation_verification", "note": "还没有草稿。"},
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "draft_literature_review_required")

    def test_bdd_25_records_single_citation_verification_evidence(self) -> None:
        """行为 25：单条候选引用可以写入人工或连接器证据，但父任务仍等待剩余引用。"""
        self._open_citation_verification_tasks()

        verified = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/citation-verification/citation_verification_01",
            json=self._valid_citation_evidence_payload(),
        )

        self.assertEqual(verified.status_code, 200, msg=verified.text)
        task = verified.json()["agent_task_queue"]["tasks"][0]
        citation_task = task["citation_verification_tasks"][0]
        self.assertEqual(citation_task["status"], "verified")
        self.assertEqual(citation_task["citation_state"], "verified")
        self.assertEqual(citation_task["evidence_record"]["connector"], "manual")
        self.assertEqual(citation_task["evidence_record"]["doi_or_stable_url"], "https://doi.org/10.1257/aer.20200123")
        self.assertFalse(citation_task["formal_write_allowed"])
        self.assertTrue(citation_task["claims_verified_citations"])
        self.assertEqual(task["status"], "citation_verification_ready")
        self.assertEqual(task["next_action"], "verify_citations")
        self.assertEqual(task["citation_verification_summary"]["verified_count"], 1)
        self.assertGreater(task["citation_verification_summary"]["pending_count"], 0)
        self.assertEqual(task["audit_log"][-1]["event"], "citation_verification_evidence_recorded")

    def test_bdd_26_blocks_incomplete_citation_verification_evidence(self) -> None:
        """行为 26：引用核验证据缺少必需字段时，不能污染候选引用任务。"""
        self._open_citation_verification_tasks()
        before = (self.project_root / "state" / "product" / "agent_task_queue.json").read_text(encoding="utf-8")
        payload = self._valid_citation_evidence_payload()
        payload.pop("doi_or_stable_url")

        blocked = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/citation-verification/citation_verification_01",
            json=payload,
        )

        self.assertEqual(blocked.status_code, 400, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "citation_verification_evidence_incomplete")
        after = (self.project_root / "state" / "product" / "agent_task_queue.json").read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_bdd_27_all_verified_citations_write_verification_log(self) -> None:
        """行为 27：全部候选引用核验完成后，写出 citation_verification_log.json 并开放下一步。"""
        response = self._complete_citation_verification()

        self.assertIsNotNone(response)
        task = response.json()["agent_task_queue"]["tasks"][0]
        citation_tasks = task["citation_verification_tasks"]
        self.assertEqual(task["status"], "citation_verification_complete")
        self.assertEqual(task["next_action"], "generate_verified_literature_package")
        self.assertEqual(task["primary_action"]["id"], "generate_verified_literature_package")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(task["citation_verification_summary"]["pending_count"], 0)
        self.assertEqual(task["citation_verification_summary"]["verified_count"], len(citation_tasks))
        log_record = task["citation_verification_log"]
        self.assertEqual(log_record["status"], "verified")
        self.assertTrue(log_record["claims_verified_citations"])
        self.assertFalse(log_record["formal_write_allowed"])

        log_path = self.project_root / "Results" / "json" / "citation_verification_log.json"
        self.assertTrue(log_path.exists())
        log = json.loads(log_path.read_text(encoding="utf-8"))
        self.assertEqual(log["schema_version"], "citation_verification_log.v1")
        self.assertEqual(log["verified_count"], len(citation_tasks))
        self.assertTrue(log["claims_verified_citations"])

    def test_bdd_28_verified_citation_log_generates_literature_package(self) -> None:
        """行为 28：核验日志可以生成草稿层已核验文献包，供后续论文草稿使用。"""
        self._complete_citation_verification()

        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/verified-literature-package"
        )

        self.assertEqual(generated.status_code, 200, msg=generated.text)
        task = generated.json()["agent_task_queue"]["tasks"][0]
        package = task["verified_literature_package"]
        self.assertEqual(task["status"], "verified_literature_package_ready")
        self.assertEqual(task["next_action"], "review_verified_literature_package")
        self.assertEqual(task["primary_action"]["id"], "review_verified_literature_package")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(package["status"], "verified_literature_package_ready")
        self.assertTrue(package["claims_verified_citations"])
        self.assertFalse(package["formal_write_allowed"])
        self.assertEqual(package["source_log_artifact_path"], "Results/json/citation_verification_log.json")
        self.assertGreaterEqual(package["verified_reference_count"], 5)

        artifact_path = self.project_root / package["artifact_path"]
        self.assertTrue(artifact_path.exists())
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual(artifact["schema_version"], "p1.verified_literature_package.v1")
        self.assertTrue(artifact["claims_verified_citations"])
        self.assertFalse(artifact["formal_write_allowed"])
        self.assertEqual(len(artifact["verified_references"]), package["verified_reference_count"])
        self.assertEqual(artifact["verified_references"][0]["evidence_level"], "verified_source_record")
        self.assertIn("citation_text", artifact["verified_references"][0])
        self.assertEqual(task["audit_log"][-1]["event"], "verified_literature_package_generated")

    def test_bdd_29_verified_literature_package_requires_complete_citation_log(self) -> None:
        """行为 29：引用核验未完成时，不能跳过门禁生成已核验文献包。"""
        self._open_citation_verification_tasks()

        blocked = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/verified-literature-package"
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "citation_verification_complete_required")
        self.assertFalse((self.project_root / "Results" / "json" / "verified_literature_package.json").exists())

    def test_bdd_30_review_verified_literature_package_opens_manuscript_citation_plan(self) -> None:
        """行为 30：已核验文献包通过人工审阅后，才开放论文引用计划。"""
        self._generate_verified_literature_package()

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/verified-literature-package-review",
            json={"action": "approve_for_manuscript_citations", "note": "引用元数据和来源证据可用于草稿引用计划。"},
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        task = reviewed.json()["agent_task_queue"]["tasks"][0]
        review = task["verified_literature_package_review"]
        self.assertEqual(review["status"], "approved_for_manuscript_citations")
        self.assertEqual(review["review_gate"], "review_verified_literature_package")
        self.assertTrue(review["manuscript_citation_plan_allowed"])
        self.assertFalse(review["formal_write_allowed"])
        self.assertEqual(task["status"], "verified_literature_package_approved")
        self.assertEqual(task["next_action"], "generate_manuscript_citation_plan")
        self.assertEqual(task["primary_action"]["id"], "generate_manuscript_citation_plan")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(task["audit_log"][-1]["event"], "verified_literature_package_reviewed")

    def test_bdd_31_verified_literature_package_review_requires_package(self) -> None:
        """行为 31：没有已核验文献包时，不能伪造文献包审阅。"""
        self._complete_citation_verification()

        blocked = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/verified-literature-package-review",
            json={"action": "approve_for_manuscript_citations", "note": "还没有文献包。"},
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "verified_literature_package_required")

    def test_bdd_32_approved_literature_package_generates_manuscript_citation_plan(self) -> None:
        """行为 32：通过审阅的已核验文献包可以生成草稿层论文引用计划。"""
        self._approve_verified_literature_package()

        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/manuscript-citation-plan"
        )

        self.assertEqual(generated.status_code, 200, msg=generated.text)
        task = generated.json()["agent_task_queue"]["tasks"][0]
        plan_summary = task["manuscript_citation_plan"]
        self.assertEqual(task["status"], "manuscript_citation_plan_ready")
        self.assertEqual(task["next_action"], "review_manuscript_citation_plan")
        self.assertEqual(task["primary_action"]["id"], "review_manuscript_citation_plan")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertFalse(plan_summary["formal_write_allowed"])
        self.assertEqual(plan_summary["source_artifact_path"], "Results/json/verified_literature_package.json")
        self.assertGreaterEqual(plan_summary["citation_binding_count"], 5)

        artifact_path = self.project_root / plan_summary["artifact_path"]
        self.assertTrue(artifact_path.exists())
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual(artifact["schema_version"], "p1.manuscript_citation_plan.v1")
        self.assertEqual(artifact["source_review_gate"], "review_verified_literature_package")
        self.assertEqual(artifact["generated_from_review_status"], "approved_for_manuscript_citations")
        self.assertFalse(artifact["formal_write_allowed"])
        self.assertEqual(len(artifact["citation_bindings"]), plan_summary["citation_binding_count"])
        self.assertIn("citation_text", artifact["citation_bindings"][0])
        self.assertIn("target_sections", artifact["citation_bindings"][0])
        self.assertEqual(task["audit_log"][-1]["event"], "manuscript_citation_plan_generated")

    def test_bdd_33_manuscript_citation_plan_requires_approved_literature_package(self) -> None:
        """行为 33：文献包未通过审阅时，不能跳过门禁生成论文引用计划。"""
        self._generate_verified_literature_package()

        blocked = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/manuscript-citation-plan"
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "verified_literature_package_review_required")
        self.assertFalse((self.project_root / "Results" / "json" / "manuscript_citation_plan.json").exists())

    def test_bdd_34_review_manuscript_citation_plan_opens_draft_section_planning(self) -> None:
        """行为 34：论文引用计划通过人工审阅后，才开放章节草稿规划。"""
        self._generate_manuscript_citation_plan()

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/manuscript-citation-plan-review",
            json={"action": "approve_for_draft_sections", "note": "引用绑定可以进入章节草稿规划。"},
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        task = reviewed.json()["agent_task_queue"]["tasks"][0]
        review = task["manuscript_citation_plan_review"]
        self.assertEqual(review["status"], "approved_for_draft_sections")
        self.assertEqual(review["review_gate"], "review_manuscript_citation_plan")
        self.assertTrue(review["draft_section_plan_allowed"])
        self.assertFalse(review["formal_write_allowed"])
        self.assertEqual(task["status"], "manuscript_citation_plan_approved")
        self.assertEqual(task["next_action"], "generate_draft_section_plan")
        self.assertEqual(task["primary_action"]["id"], "generate_draft_section_plan")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(task["audit_log"][-1]["event"], "manuscript_citation_plan_reviewed")

    def test_bdd_35_manuscript_citation_plan_review_requires_plan(self) -> None:
        """行为 35：没有论文引用计划时，不能伪造引用计划审阅。"""
        self._approve_verified_literature_package()

        blocked = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/manuscript-citation-plan-review",
            json={"action": "approve_for_draft_sections", "note": "还没有引用计划。"},
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "manuscript_citation_plan_required")

    def test_bdd_36_approved_manuscript_citation_plan_generates_draft_section_plan(self) -> None:
        """行为 36：已批准的引用计划可以生成章节草稿计划，但不写入正式正文。"""
        self._approve_manuscript_citation_plan()

        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-plan"
        )

        self.assertEqual(generated.status_code, 200, msg=generated.text)
        task = generated.json()["agent_task_queue"]["tasks"][0]
        plan_summary = task["draft_section_plan"]
        self.assertEqual(task["status"], "draft_section_plan_ready")
        self.assertEqual(task["next_action"], "review_draft_section_plan")
        self.assertEqual(task["primary_action"]["id"], "review_draft_section_plan")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertFalse(plan_summary["formal_write_allowed"])
        self.assertEqual(plan_summary["source_artifact_path"], "Results/json/manuscript_citation_plan.json")
        self.assertGreaterEqual(plan_summary["section_count"], 3)
        self.assertGreaterEqual(plan_summary["citation_binding_count"], 5)

        artifact_path = self.project_root / plan_summary["artifact_path"]
        self.assertTrue(artifact_path.exists())
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual(artifact["schema_version"], "p1.draft_section_plan.v1")
        self.assertEqual(artifact["source_review_gate"], "review_manuscript_citation_plan")
        self.assertEqual(artifact["generated_from_review_status"], "approved_for_draft_sections")
        self.assertEqual(artifact["draft_layer"], "draft_section_plan")
        self.assertFalse(artifact["formal_write_allowed"])
        self.assertEqual(len(artifact["sections"]), plan_summary["section_count"])
        self.assertIn("section_id", artifact["sections"][0])
        self.assertIn("citation_binding_ids", artifact["sections"][0])
        self.assertEqual(task["audit_log"][-1]["event"], "draft_section_plan_generated")

    def test_bdd_37_draft_section_plan_requires_approved_citation_plan(self) -> None:
        """行为 37：引用计划未通过审阅时，不能跳过门禁生成章节草稿计划。"""
        self._generate_manuscript_citation_plan()

        blocked = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-plan"
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "manuscript_citation_plan_review_required")
        self.assertFalse((self.project_root / "Results" / "json" / "draft_section_plan.json").exists())

    def test_bdd_38_review_draft_section_plan_opens_section_task_generation(self) -> None:
        """行为 38：章节草稿计划通过人工审阅后，才开放章节草稿任务包。"""
        self._generate_draft_section_plan()

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-plan-review",
            json={"action": "approve_for_section_tasks", "note": "章节边界和引用绑定可以进入草稿任务包。"},
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        task = reviewed.json()["agent_task_queue"]["tasks"][0]
        review = task["draft_section_plan_review"]
        self.assertEqual(review["status"], "approved_for_section_tasks")
        self.assertEqual(review["review_gate"], "review_draft_section_plan")
        self.assertTrue(review["section_task_generation_allowed"])
        self.assertFalse(review["formal_write_allowed"])
        self.assertEqual(task["status"], "draft_section_plan_approved")
        self.assertEqual(task["next_action"], "generate_draft_section_tasks")
        self.assertEqual(task["primary_action"]["id"], "generate_draft_section_tasks")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(task["audit_log"][-1]["event"], "draft_section_plan_reviewed")

        artifact = json.loads((self.project_root / "Results" / "json" / "draft_section_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(artifact["review"]["status"], "approved_for_section_tasks")
        self.assertTrue(artifact["section_task_generation_allowed"])
        self.assertFalse(artifact["formal_write_allowed"])

    def test_bdd_39_draft_section_plan_review_requires_plan(self) -> None:
        """行为 39：没有章节草稿计划时，不能伪造章节计划审阅。"""
        self._approve_manuscript_citation_plan()

        blocked = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-plan-review",
            json={"action": "approve_for_section_tasks", "note": "还没有章节草稿计划。"},
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "draft_section_plan_required")

    def test_bdd_40_approved_draft_section_plan_generates_section_task_package(self) -> None:
        """行为 40：通过审阅的章节计划可以生成章节草稿任务包，但仍不写正式正文。"""
        self._approve_draft_section_plan()

        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-tasks"
        )

        self.assertEqual(generated.status_code, 200, msg=generated.text)
        task = generated.json()["agent_task_queue"]["tasks"][0]
        package = task["draft_section_tasks"]
        self.assertEqual(package["status"], "draft_section_tasks_ready")
        self.assertEqual(package["schema_version"], "p1.draft_section_tasks.v1")
        self.assertEqual(package["source_review_gate"], "review_draft_section_plan")
        self.assertEqual(package["generated_from_review_status"], "approved_for_section_tasks")
        self.assertGreaterEqual(package["task_count"], 4)
        self.assertFalse(package["formal_write_allowed"])
        self.assertFalse(package["writes_formal_layer"])
        self.assertEqual(package["next_action"], "review_draft_section_tasks")
        self.assertEqual(task["status"], "draft_section_tasks_ready")
        self.assertEqual(task["next_action"], "review_draft_section_tasks")
        self.assertEqual(task["primary_action"]["id"], "review_draft_section_tasks")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(task["audit_log"][-1]["event"], "draft_section_tasks_generated")

        artifact = self.project_root / package["artifact_path"]
        self.assertTrue(artifact.exists())
        artifact_data = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertEqual(artifact_data["schema_version"], "p1.draft_section_tasks.v1")
        self.assertEqual(artifact_data["review"]["status"], "pending")
        self.assertTrue(all(item["requires_human_review"] for item in artifact_data["tasks"]))
        self.assertTrue(all(not item["formal_write_allowed"] for item in artifact_data["tasks"]))
        self.assertIn("citation_binding_ids", artifact_data["tasks"][0])

    def test_bdd_41_draft_section_tasks_require_approved_section_plan(self) -> None:
        """行为 41：章节计划未通过人工审阅时，不能跳过门禁生成章节任务包。"""
        self._generate_draft_section_plan()

        blocked = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-tasks"
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "draft_section_plan_review_required")
        self.assertFalse((self.project_root / "Results" / "json" / "draft_section_tasks.json").exists())

    def test_bdd_42_review_draft_section_tasks_opens_writer_agent_draft_generation(self) -> None:
        """行为 42：章节草稿任务包通过人工审阅后，才开放 WriterAgent 草稿生成。"""
        self._generate_draft_section_tasks()

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-tasks-review",
            json={"action": "approve_for_writer_agent", "note": "章节任务范围和引用绑定可以进入 WriterAgent。"},
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        task = reviewed.json()["agent_task_queue"]["tasks"][0]
        review = task["draft_section_tasks_review"]
        self.assertEqual(review["status"], "approved_for_writer_agent")
        self.assertEqual(review["review_gate"], "review_draft_section_tasks")
        self.assertTrue(review["writer_agent_allowed"])
        self.assertFalse(review["formal_write_allowed"])
        self.assertFalse(review["writes_formal_layer"])
        self.assertEqual(task["status"], "draft_section_tasks_approved")
        self.assertEqual(task["next_action"], "generate_section_drafts")
        self.assertEqual(task["primary_action"]["id"], "generate_section_drafts")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(task["audit_log"][-1]["event"], "draft_section_tasks_reviewed")

        artifact = json.loads((self.project_root / "Results" / "json" / "draft_section_tasks.json").read_text(encoding="utf-8"))
        self.assertEqual(artifact["review"]["status"], "approved_for_writer_agent")
        self.assertTrue(artifact["writer_agent_allowed"])
        self.assertFalse(artifact["formal_write_allowed"])

    def test_bdd_43_draft_section_tasks_review_requires_task_package(self) -> None:
        """行为 43：没有章节草稿任务包时，不能伪造任务包审阅。"""
        self._approve_draft_section_plan()

        blocked = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-tasks-review",
            json={"action": "approve_for_writer_agent", "note": "还没有章节任务包。"},
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "draft_section_tasks_required")

    def test_bdd_44_approved_draft_section_tasks_generate_draft_layer_section_files(self) -> None:
        """行为 44：通过审阅的章节任务包可以生成草稿层章节文件，但正式层继续锁定。"""
        self._approve_draft_section_tasks()

        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/section-drafts"
        )

        self.assertEqual(generated.status_code, 200, msg=generated.text)
        task = generated.json()["agent_task_queue"]["tasks"][0]
        drafts = task["section_drafts"]
        self.assertEqual(drafts["status"], "section_drafts_ready")
        self.assertEqual(drafts["schema_version"], "p1.section_drafts.v1")
        self.assertEqual(drafts["draft_layer"], "section_drafts")
        self.assertEqual(drafts["source_review_gate"], "review_draft_section_tasks")
        self.assertEqual(drafts["generated_from_review_status"], "approved_for_writer_agent")
        self.assertGreaterEqual(drafts["section_count"], 4)
        self.assertTrue(drafts["requires_human_review"])
        self.assertFalse(drafts["formal_write_allowed"])
        self.assertFalse(drafts["writes_formal_layer"])
        self.assertEqual(drafts["next_action"], "review_section_drafts")
        self.assertEqual(task["status"], "section_drafts_ready")
        self.assertEqual(task["next_action"], "review_section_drafts")
        self.assertEqual(task["primary_action"]["id"], "review_section_drafts")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(task["audit_log"][-1]["event"], "section_drafts_generated")

        manifest = self.project_root / drafts["artifact_path"]
        self.assertTrue(manifest.exists())
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest_data["schema_version"], "p1.section_drafts.v1")
        self.assertEqual(manifest_data["status"], "section_drafts_ready")
        self.assertEqual(manifest_data["writer_agent"]["mode"], "draft_only")
        self.assertFalse(manifest_data["formal_write_allowed"])
        self.assertFalse(manifest_data["writes_formal_layer"])
        self.assertTrue(manifest_data["requires_human_review"])
        self.assertGreaterEqual(len(manifest_data["sections"]), 4)
        for section in manifest_data["sections"]:
            draft_path = self.project_root / section["artifact_path"]
            self.assertTrue(draft_path.exists())
            draft_text = draft_path.read_text(encoding="utf-8")
            self.assertIn("草稿层章节", draft_text)
            self.assertIn("正式层写回：未批准", draft_text)
            self.assertIn(section["section_title"], draft_text)
            self.assertTrue(section["requires_human_review"])
            self.assertFalse(section["formal_write_allowed"])

    def test_bdd_45_section_drafts_require_approved_task_package(self) -> None:
        """行为 45：章节任务包未通过人工审阅时，不能直接生成章节草稿。"""
        self._generate_draft_section_tasks()

        blocked = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/section-drafts"
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "draft_section_tasks_review_required")
        self.assertFalse((self.project_root / "Results" / "json" / "section_drafts.json").exists())

    def test_bdd_46_section_drafts_review_requires_generated_drafts(self) -> None:
        """行为 46：没有已生成章节草稿时，不能伪造草稿审阅。"""
        self._approve_draft_section_tasks()

        blocked = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/section-drafts-review",
            json={"action": "approve_for_formal_writeback_preflight", "note": "还没有草稿文件。"},
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "section_drafts_required")
        self.assertFalse(
            (self.project_root / "Results" / "json" / "section_draft_formal_writeback_preflight.json").exists()
        )

    def test_bdd_47_approved_section_drafts_create_formal_writeback_preflight_without_formal_write(self) -> None:
        """行为 47：通过章节草稿审阅后，只生成正式写回预检，不静默改正式层。"""
        self._generate_section_drafts()
        formal_target = self.project_root / "Manuscripts" / "sections" / "introduction.md"
        formal_target.parent.mkdir(parents=True)
        formal_target.write_text("正式层原文，不能被草稿审阅覆盖。\n", encoding="utf-8")

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/section-drafts-review",
            json={
                "action": "approve_for_formal_writeback_preflight",
                "note": "章节草稿可以进入正式写回预检。",
            },
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        task = reviewed.json()["agent_task_queue"]["tasks"][0]
        review = task["section_drafts_review"]
        preflight = task["formal_writeback_preflight"]
        self.assertEqual(review["status"], "approved_for_formal_writeback_preflight")
        self.assertTrue(review["formal_writeback_preflight_allowed"])
        self.assertFalse(review["formal_write_allowed"])
        self.assertEqual(preflight["status"], "formal_writeback_preflight_ready")
        self.assertEqual(preflight["schema_version"], "p1.formal_writeback_preflight.v1")
        self.assertEqual(preflight["source_review_gate"], "review_section_drafts")
        self.assertGreaterEqual(preflight["target_count"], 4)
        self.assertFalse(preflight["formal_write_allowed"])
        self.assertFalse(preflight["writes_formal_layer"])
        self.assertTrue(preflight["requires_human_review"])
        self.assertEqual(task["status"], "formal_writeback_preflight_ready")
        self.assertEqual(task["next_action"], "review_formal_writeback_preflight")
        self.assertEqual(task["primary_action"]["id"], "review_formal_writeback_preflight")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(task["audit_log"][-1]["event"], "formal_writeback_preflight_created")

        self.assertEqual(formal_target.read_text(encoding="utf-8"), "正式层原文，不能被草稿审阅覆盖。\n")
        preflight_path = self.project_root / preflight["artifact_path"]
        self.assertTrue(preflight_path.exists())
        artifact = json.loads(preflight_path.read_text(encoding="utf-8"))
        self.assertEqual(artifact["schema_version"], "p1.formal_writeback_preflight.v1")
        self.assertFalse(artifact["formal_write_allowed"])
        self.assertFalse(artifact["writes_formal_layer"])
        self.assertTrue(artifact["requires_human_review"])
        self.assertGreaterEqual(len(artifact["targets"]), 4)
        for target in artifact["targets"]:
            self.assertIn("draft_artifact_path", target)
            self.assertIn("formal_target_path", target)
            self.assertTrue(target["requires_human_review"])
            self.assertFalse(target["formal_write_allowed"])

    def test_bdd_48_formal_writeback_requires_preflight(self) -> None:
        """行为 48：没有正式写回预检时，不能直接批准写入正式层。"""
        self._generate_section_drafts()

        blocked = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/formal-writeback-preflight-review",
            json={"action": "approve_formal_writeback", "note": "尝试跳过正式写回预检。"},
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "formal_writeback_preflight_required")
        self.assertFalse((self.project_root / "Results" / "json" / "formal_writeback_manifest.json").exists())

    def test_bdd_49_approved_formal_writeback_preflight_writes_formal_sections_with_manifest(self) -> None:
        """行为 49：人工批准正式写回预检后，才写入正式层章节并生成写回清单。"""
        self._generate_section_drafts()
        preflight_response = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/section-drafts-review",
            json={
                "action": "approve_for_formal_writeback_preflight",
                "note": "章节草稿可进入正式写回预检。",
            },
        )
        self.assertEqual(preflight_response.status_code, 200, msg=preflight_response.text)
        task = preflight_response.json()["agent_task_queue"]["tasks"][0]
        preflight_path = self.project_root / task["formal_writeback_preflight"]["artifact_path"]
        preflight_artifact = json.loads(preflight_path.read_text(encoding="utf-8"))
        first_target = self.project_root / preflight_artifact["targets"][0]["formal_target_path"]
        first_target.parent.mkdir(parents=True)
        first_target.write_text("旧正式层内容，应被明确批准后的写回替换。\n", encoding="utf-8")

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/formal-writeback-preflight-review",
            json={"action": "approve_formal_writeback", "note": "批准写入正式层章节。"},
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        task = reviewed.json()["agent_task_queue"]["tasks"][0]
        manifest = task["formal_writeback_manifest"]
        self.assertEqual(task["status"], "formal_sections_written")
        self.assertEqual(task["next_action"], "prepare_export_preflight")
        self.assertEqual(task["primary_action"]["id"], "prepare_export_preflight")
        self.assertFalse(task["primary_action"]["writes_formal_layer"])
        self.assertEqual(manifest["status"], "formal_sections_written")
        self.assertEqual(manifest["schema_version"], "p1.formal_writeback_manifest.v1")
        self.assertEqual(manifest["review_status"], "approved_formal_writeback")
        self.assertEqual(manifest["written_count"], len(preflight_artifact["targets"]))
        self.assertTrue(manifest["writes_formal_layer"])
        self.assertEqual(task["audit_log"][-1]["event"], "formal_sections_written")

        manifest_path = self.project_root / manifest["artifact_path"]
        self.assertTrue(manifest_path.exists())
        manifest_artifact = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest_artifact["status"], "formal_sections_written")
        self.assertEqual(manifest_artifact["review"]["note"], "批准写入正式层章节。")
        self.assertEqual(len(manifest_artifact["targets"]), len(preflight_artifact["targets"]))
        self.assertTrue(any(target["previous_exists"] for target in manifest_artifact["targets"]))
        for target in manifest_artifact["targets"]:
            formal_path = self.project_root / target["formal_target_path"]
            self.assertTrue(formal_path.exists())
            text = formal_path.read_text(encoding="utf-8")
            self.assertIn("正式层写回：已批准", text)
            self.assertIn(target["section_title"], text)

        updated_preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        self.assertEqual(updated_preflight["review"]["status"], "approved_formal_writeback")
        self.assertTrue(updated_preflight["formal_write_allowed"])
        self.assertTrue(updated_preflight["writes_formal_layer"])

    def test_bdd_50_rejected_formal_writeback_preflight_does_not_write_formal_sections(self) -> None:
        """行为 50：拒绝正式写回预检时，正式层不发生写入。"""
        self._generate_section_drafts()
        preflight_response = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/section-drafts-review",
            json={
                "action": "approve_for_formal_writeback_preflight",
                "note": "章节草稿可进入正式写回预检。",
            },
        )
        self.assertEqual(preflight_response.status_code, 200, msg=preflight_response.text)
        task = preflight_response.json()["agent_task_queue"]["tasks"][0]
        preflight_path = self.project_root / task["formal_writeback_preflight"]["artifact_path"]
        preflight_artifact = json.loads(preflight_path.read_text(encoding="utf-8"))

        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/formal-writeback-preflight-review",
            json={"action": "reject", "note": "正式写回目标还需要重新审阅。"},
        )

        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        task = reviewed.json()["agent_task_queue"]["tasks"][0]
        self.assertEqual(task["status"], "formal_writeback_preflight_rejected")
        self.assertEqual(task["next_action"], "replace_section_drafts")
        self.assertNotIn("formal_writeback_manifest", task)
        self.assertEqual(task["audit_log"][-1]["event"], "formal_writeback_preflight_reviewed")
        for target in preflight_artifact["targets"]:
            self.assertFalse((self.project_root / target["formal_target_path"]).exists())

    def test_bdd_51_export_preflight_requires_written_formal_sections(self) -> None:
        """行为 51：没有已批准写入的正式章节时，不能进入导出预检。"""
        self._generate_section_drafts()

        blocked = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/formal-export-preflight",
            json={"note": "尝试跳过正式章节写入。"},
        )

        self.assertEqual(blocked.status_code, 409, msg=blocked.text)
        self.assertEqual(blocked.json()["error"]["code"], "formal_sections_required")
        self.assertFalse((self.project_root / "Results" / "json" / "agent_task_export_preflight.json").exists())

    def test_bdd_52_written_formal_sections_generate_export_preflight_console(self) -> None:
        """行为 52：正式章节写入后，可以生成导出预检台，但不直接生成 PDF/DOCX。"""
        self._approve_formal_writeback()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/formal-export-preflight",
            json={"note": "检查正式章节能否进入 PDF/DOCX 导出。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        task = response.json()["agent_task_queue"]["tasks"][0]
        preflight = task["formal_export_preflight"]
        self.assertEqual(preflight["schema_version"], "p1.agent_task_export_preflight.v1")
        self.assertEqual(preflight["source_review_gate"], "review_formal_writeback_preflight")
        self.assertEqual(preflight["source_task_id"], "agent_task_01")
        self.assertEqual(preflight["status"], "formal_export_preflight_ready")
        self.assertEqual(preflight["section_count"], task["formal_writeback_manifest"]["written_count"])
        self.assertEqual(preflight["missing_section_count"], 0)
        self.assertFalse(preflight["writes_formal_layer"])
        self.assertFalse(preflight["wrote_pdf"])
        self.assertFalse(preflight["wrote_docx"])
        self.assertEqual(preflight["next_action"], "run_pdf_export_preflight")
        self.assertEqual(task["status"], "formal_export_preflight_ready")
        self.assertEqual(task["next_action"], "run_pdf_export_preflight")
        self.assertEqual(task["primary_action"]["id"], "run_pdf_export_preflight")
        self.assertEqual(task["audit_log"][-1]["event"], "formal_export_preflight_generated")

        preflight_path = self.project_root / preflight["artifact_path"]
        self.assertTrue(preflight_path.exists())
        preflight_artifact = json.loads(preflight_path.read_text(encoding="utf-8"))
        self.assertEqual(preflight_artifact["note"], "检查正式章节能否进入 PDF/DOCX 导出。")
        self.assertFalse(preflight_artifact["outputs_written"]["pdf"])
        self.assertFalse(preflight_artifact["outputs_written"]["docx"])
        self.assertIn("Submissions/formal_package/paper_candidate.pdf", preflight_artifact["targets"]["pdf_candidate"])
        self.assertIn("Submissions/formal_package/paper.docx", preflight_artifact["targets"]["docx"])
        self.assertEqual(preflight_artifact["agent_followups"], [])
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())

    def test_bdd_53_export_preflight_turns_missing_sections_into_agent_followups(self) -> None:
        """行为 53：导出预检发现正式章节缺失时，必须转成后续 Agent 任务，不只显示错误。"""
        writeback = self._approve_formal_writeback()
        task = writeback.json()["agent_task_queue"]["tasks"][0]
        manifest_path = self.project_root / task["formal_writeback_manifest"]["artifact_path"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        missing_target = manifest["targets"][0]
        (self.project_root / missing_target["formal_target_path"]).unlink()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/formal-export-preflight",
            json={"note": "检查缺失正式章节如何处理。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        task = response.json()["agent_task_queue"]["tasks"][0]
        preflight = task["formal_export_preflight"]
        self.assertEqual(preflight["status"], "formal_export_preflight_blocked")
        self.assertEqual(preflight["missing_section_count"], 1)
        self.assertEqual(preflight["next_action"], "resolve_export_preflight_blockers")
        self.assertEqual(task["status"], "formal_export_preflight_blocked")
        self.assertEqual(task["next_action"], "resolve_export_preflight_blockers")
        self.assertEqual(task["primary_action"]["id"], "resolve_export_preflight_blockers")
        self.assertEqual(task["blockers"][0]["code"], "formal_section_missing")
        self.assertEqual(task["export_preflight_followups"][0]["owner_agent"], "ManuscriptAgent")
        self.assertIn(missing_target["formal_target_path"], task["export_preflight_followups"][0]["description"])

    def _generate_draft_literature_review_task(self) -> None:
        self._execute_reference_seed_package_task()
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/reference-seed-review",
            json={"action": "approve_for_draft", "note": "可以进入草稿综述。"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        drafted = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-literature-review"
        )
        self.assertEqual(drafted.status_code, 200, msg=drafted.text)

    def _open_citation_verification_tasks(self) -> None:
        self._generate_draft_literature_review_task()
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-literature-review-review",
            json={"action": "approve_for_citation_verification", "note": "草稿可进入引用核验。"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)

    def _valid_citation_evidence_payload(
        self,
        *,
        title: str = "Verified empirical reference",
        doi: str = "https://doi.org/10.1257/aer.20200123",
    ) -> dict:
        return {
            "connector": "manual",
            "authors": ["Acemoglu", "Restrepo"],
            "year": "2020",
            "title": title,
            "venue": "American Economic Review",
            "doi_or_stable_url": doi,
            "relevance": "direct",
            "evidence_url": doi,
            "note": "人工核对作者、年份、题名、来源和稳定链接。",
        }

    def _complete_citation_verification(self):
        self._open_citation_verification_tasks()
        queue = json.loads((self.project_root / "state" / "product" / "agent_task_queue.json").read_text(encoding="utf-8"))
        citation_tasks = queue["tasks"][0]["citation_verification_tasks"]
        response = None
        for index, citation_task in enumerate(citation_tasks, start=1):
            payload = self._valid_citation_evidence_payload(
                title=f"Verified citation {index}",
                doi=f"https://doi.org/10.1257/aer.2020{index:04d}",
            )
            response = self.client.put(
                f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/citation-verification/{citation_task['id']}",
                json=payload,
            )
            self.assertEqual(response.status_code, 200, msg=response.text)
        return response

    def _generate_verified_literature_package(self):
        self._complete_citation_verification()
        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/verified-literature-package"
        )
        self.assertEqual(generated.status_code, 200, msg=generated.text)
        return generated

    def _approve_verified_literature_package(self):
        self._generate_verified_literature_package()
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/verified-literature-package-review",
            json={"action": "approve_for_manuscript_citations", "note": "可进入引用计划。"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        return reviewed

    def _generate_manuscript_citation_plan(self):
        self._approve_verified_literature_package()
        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/manuscript-citation-plan"
        )
        self.assertEqual(generated.status_code, 200, msg=generated.text)
        return generated

    def _approve_manuscript_citation_plan(self):
        self._generate_manuscript_citation_plan()
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/manuscript-citation-plan-review",
            json={"action": "approve_for_draft_sections", "note": "可进入章节草稿计划。"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        return reviewed

    def _generate_draft_section_plan(self):
        self._approve_manuscript_citation_plan()
        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-plan"
        )
        self.assertEqual(generated.status_code, 200, msg=generated.text)
        return generated

    def _approve_draft_section_plan(self):
        self._generate_draft_section_plan()
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-plan-review",
            json={"action": "approve_for_section_tasks", "note": "章节计划可以进入任务包。"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        return reviewed

    def _generate_draft_section_tasks(self):
        self._approve_draft_section_plan()
        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-tasks"
        )
        self.assertEqual(generated.status_code, 200, msg=generated.text)
        return generated

    def _approve_draft_section_tasks(self):
        self._generate_draft_section_tasks()
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/draft-section-tasks-review",
            json={"action": "approve_for_writer_agent", "note": "章节任务包可以进入 WriterAgent 草稿生成。"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        return reviewed

    def _generate_section_drafts(self):
        self._approve_draft_section_tasks()
        generated = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/section-drafts"
        )
        self.assertEqual(generated.status_code, 200, msg=generated.text)
        return generated

    def _approve_formal_writeback(self):
        self._generate_section_drafts()
        preflight_response = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/section-drafts-review",
            json={
                "action": "approve_for_formal_writeback_preflight",
                "note": "章节草稿可进入正式写回预检。",
            },
        )
        self.assertEqual(preflight_response.status_code, 200, msg=preflight_response.text)
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/formal-writeback-preflight-review",
            json={"action": "approve_formal_writeback", "note": "批准写入正式层章节。"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        return reviewed

    def _execute_reference_seed_package_task(self) -> None:
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
                    "expected_artifacts": ["LiteratureSeedPackage", "search_query_graph", "citation_verification_queue"],
                    "execution_boundary": "review_only_until_dispatch_approved",
                },
            ],
            reference_chain_policy={
                "contract_version": "reference_chain.v1",
                "status": "needs_review",
                "source_priority": ["cnki", "scholar", "zotero", "local_notes", "arxiv"],
                "max_depth": 2,
                "max_iterations": 5,
                "formal_writeback_gate": "review_literature_seed_package",
                "writes_formal_layer": True,
            },
        )
        created = self.client.post(f"/api/v1/projects/{self.project_id}/agent-task-queue")
        self.assertEqual(created.status_code, 201, msg=created.text)
        reviewed = self.client.put(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/dispatch-review",
            json={"action": "approve", "note": "先生成候选来源种子包"},
        )
        self.assertEqual(reviewed.status_code, 200, msg=reviewed.text)
        selected = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/select-backend",
            json={"backend_id": "codex"},
        )
        self.assertEqual(selected.status_code, 200, msg=selected.text)
        executed = self.client.post(
            f"/api/v1/projects/{self.project_id}/agent-task-queue/tasks/agent_task_01/execute"
        )
        self.assertEqual(executed.status_code, 200, msg=executed.text)

    def _write_supervisor_plan(
        self,
        status: str,
        can_dispatch: bool,
        subagent_dispatch: list[dict] | None = None,
        recommended_internal_skills: list[dict] | None = None,
        llm_intervention_plan: dict | None = None,
        reference_chain_policy: dict | None = None,
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
        if reference_chain_policy is not None:
            plan["reference_chain_policy"] = reference_chain_policy
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
        cls.root = root
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")
        cls.react_agent_task_queue = (
            root / "Product" / "web-react" / "src" / "components" / "AgentTaskQueuePanel.tsx"
        ).read_text(encoding="utf-8")
        cls.react_api_base = (root / "Product" / "web-react" / "src" / "lib" / "apiBase.ts").read_text(
            encoding="utf-8"
        )
        cls.react_styles_css = (root / "Product" / "web-react" / "src" / "styles.css").read_text(encoding="utf-8")

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

    def test_bdd_15_frontend_exposes_reference_chain_policy_in_literature_task_details(self) -> None:
        """行为 15：文献类任务详情必须说明引用链路来源、检索边界和正式层写回门。"""
        self.assertIn("renderReferenceChainPolicy", self.app_js)
        self.assertIn("task.reference_chain_policy", self.app_js)
        self.assertIn("agent-task-reference-policy", self.app_js)
        self.assertIn("source_priority", self.app_js)
        self.assertIn("formal_writeback_gate", self.app_js)
        self.assertIn("writes_formal_layer", self.app_js)
        self.assertIn("任务引用链路", self.app_js)
        self.assertIn(".reference-chain-policy", self.styles_css)

    def test_bdd_16_frontend_exposes_reference_seed_package_result_review(self) -> None:
        """行为 16：候选来源种子包执行完成后，前端必须展示审阅入口和候选引用边界。"""
        self.assertIn("renderReferenceSeedPackageResultReview", self.app_js)
        self.assertIn("result_review", self.app_js)
        self.assertIn("reference_chain_seed_package", self.app_js)
        self.assertIn("候选来源种子包", self.app_js)
        self.assertIn("候选检索式", self.app_js)
        self.assertIn("review_literature_seed_package", self.app_js)
        self.assertIn("不宣称已验证引用", self.app_js)
        self.assertIn(".agent-task-reference-seed-result", self.styles_css)

    def test_bdd_17_frontend_exposes_reference_seed_package_review_actions(self) -> None:
        """行为 17：前端必须提供候选来源种子包审阅动作，并明确只进入草稿层。"""
        self.assertIn("reviewReferenceSeedPackage", self.app_js)
        self.assertIn("handleReferenceSeedPackageReview", self.app_js)
        self.assertIn("data-reference-seed-review-action", self.app_js)
        self.assertIn("approve_for_draft", self.app_js)
        self.assertIn("进入草稿综述", self.app_js)
        self.assertIn("要求修订", self.app_js)
        self.assertIn("拒绝种子包", self.app_js)
        self.assertIn("不会写入正式层", self.app_js)
        self.assertIn(".agent-task-reference-seed-result__actions", self.styles_css)

    def test_bdd_18_frontend_exposes_draft_literature_review_generation(self) -> None:
        """行为 18：前端必须能从已审阅候选来源包进入草稿层文献综述生成。"""
        self.assertIn("draftLiteratureReview", self.app_js)
        self.assertIn("handleDraftLiteratureReview", self.app_js)
        self.assertIn("data-draft-literature-review-action", self.app_js)
        self.assertIn("草稿层文献综述", self.app_js)
        self.assertIn("审阅草稿综述", self.app_js)
        self.assertIn("不写入正式层", self.app_js)
        self.assertIn(".agent-task-literature-draft", self.styles_css)

    def test_bdd_19_frontend_exposes_draft_review_and_citation_verification(self) -> None:
        """行为 19：前端必须能审阅草稿综述，并展示引用核验任务队列。"""
        self.assertIn("reviewDraftLiteratureReview", self.app_js)
        self.assertIn("handleDraftLiteratureReviewReview", self.app_js)
        self.assertIn("data-draft-literature-review-review-action", self.app_js)
        self.assertIn("approve_for_citation_verification", self.app_js)
        self.assertIn("进入引用核验", self.app_js)
        self.assertIn("引用核验任务", self.app_js)
        self.assertIn("不宣称引用已验证", self.app_js)
        self.assertIn(".agent-task-citation-verification", self.styles_css)

    def test_bdd_20_frontend_exposes_citation_evidence_recording_state(self) -> None:
        """行为 20：前端必须展示引用核验证据状态和证据记录入口。"""
        self.assertIn("recordCitationVerificationEvidence", self.app_js)
        self.assertIn("handleCitationVerificationEvidence", self.app_js)
        self.assertIn("data-citation-verification-evidence-action", self.app_js)
        self.assertIn("记录核验证据", self.app_js)
        self.assertIn("已核验证据", self.app_js)
        self.assertIn("等待补证", self.app_js)
        self.assertIn(".agent-task-citation-evidence", self.styles_css)

    def test_bdd_21_frontend_exposes_verified_literature_package_action(self) -> None:
        """行为 21：前端必须能从引用核验完成态生成已核验文献包。"""
        self.assertIn("generateVerifiedLiteraturePackage", self.app_js)
        self.assertIn("handleVerifiedLiteraturePackage", self.app_js)
        self.assertIn("data-verified-literature-package-action", self.app_js)
        self.assertIn("生成已核验文献包", self.app_js)
        self.assertIn("已核验文献包", self.app_js)
        self.assertIn(".agent-task-verified-literature-package", self.styles_css)

    def test_bdd_22_frontend_exposes_verified_literature_package_review_gate(self) -> None:
        """行为 22：前端必须能审阅已核验文献包，再开放论文引用计划。"""
        self.assertIn("reviewVerifiedLiteraturePackage", self.app_js)
        self.assertIn("handleVerifiedLiteraturePackageReview", self.app_js)
        self.assertIn("data-verified-literature-package-review-action", self.app_js)
        self.assertIn("批准进入引用计划", self.app_js)
        self.assertIn("verified_literature_package_review", self.app_js)
        self.assertIn(".agent-task-verified-literature-package__review", self.styles_css)

    def test_bdd_23_frontend_exposes_manuscript_citation_plan_generation(self) -> None:
        """行为 23：前端必须能从已批准文献包生成论文引用计划。"""
        self.assertIn("generateManuscriptCitationPlan", self.app_js)
        self.assertIn("handleManuscriptCitationPlan", self.app_js)
        self.assertIn("data-manuscript-citation-plan-action", self.app_js)
        self.assertIn("生成论文引用计划", self.app_js)
        self.assertIn("manuscript_citation_plan", self.app_js)
        self.assertIn(".agent-task-manuscript-citation-plan", self.styles_css)

    def test_bdd_24_frontend_exposes_manuscript_citation_plan_review_gate(self) -> None:
        """行为 24：前端必须能审阅论文引用计划，再开放章节草稿规划。"""
        self.assertIn("reviewManuscriptCitationPlan", self.app_js)
        self.assertIn("handleManuscriptCitationPlanReview", self.app_js)
        self.assertIn("data-manuscript-citation-plan-review-action", self.app_js)
        self.assertIn("批准进入章节草稿", self.app_js)
        self.assertIn("manuscript_citation_plan_review", self.app_js)
        self.assertIn(".agent-task-manuscript-citation-plan__review", self.styles_css)

    def test_bdd_25_frontend_exposes_draft_section_plan_generation(self) -> None:
        """行为 25：前端必须能从已批准引用计划生成章节草稿计划。"""
        self.assertIn("generateDraftSectionPlan", self.app_js)
        self.assertIn("handleDraftSectionPlan", self.app_js)
        self.assertIn("data-draft-section-plan-action", self.app_js)
        self.assertIn("生成章节草稿计划", self.app_js)
        self.assertIn("draft_section_plan", self.app_js)
        self.assertIn(".agent-task-draft-section-plan", self.styles_css)

    def test_bdd_26_frontend_exposes_draft_section_plan_review_gate(self) -> None:
        """行为 26：前端必须能审阅章节草稿计划，再开放章节草稿任务包。"""
        self.assertIn("reviewDraftSectionPlan", self.app_js)
        self.assertIn("handleDraftSectionPlanReview", self.app_js)
        self.assertIn("data-draft-section-plan-review-action", self.app_js)
        self.assertIn("批准生成章节任务", self.app_js)
        self.assertIn("draft_section_plan_review", self.app_js)
        self.assertIn(".agent-task-draft-section-plan__review", self.styles_css)

    def test_bdd_27_frontend_exposes_draft_section_task_package_generation(self) -> None:
        """行为 27：前端必须能从已批准章节计划生成并展示章节草稿任务包。"""
        self.assertIn("generateDraftSectionTasks", self.app_js)
        self.assertIn("handleDraftSectionTasks", self.app_js)
        self.assertIn("data-draft-section-tasks-action", self.app_js)
        self.assertIn("renderDraftSectionTasks", self.app_js)
        self.assertIn("生成章节草稿任务包", self.app_js)
        self.assertIn("生成后进入章节任务审阅", self.app_js)
        self.assertIn("正式层保持锁定", self.app_js)
        self.assertIn("agent-task-draft-section-tasks__checkpoint", self.app_js)
        self.assertIn("draft_section_tasks", self.app_js)
        self.assertIn(".agent-task-draft-section-tasks", self.styles_css)
        self.assertIn(".agent-task-draft-section-tasks__checkpoint", self.styles_css)

    def test_bdd_28_frontend_exposes_draft_section_task_package_review_gate(self) -> None:
        """行为 28：前端必须能审阅章节任务包，再开放 WriterAgent 草稿生成入口。"""
        self.assertIn("reviewDraftSectionTasks", self.app_js)
        self.assertIn("handleDraftSectionTasksReview", self.app_js)
        self.assertIn("data-draft-section-tasks-review-action", self.app_js)
        self.assertIn("批准给 WriterAgent", self.app_js)
        self.assertIn("生成章节草稿", self.app_js)
        self.assertIn("draft_section_tasks_review", self.app_js)
        self.assertIn("正式层仍保持锁定", self.app_js)
        self.assertIn(".agent-task-draft-section-tasks__review", self.styles_css)

    def test_bdd_29_frontend_exposes_section_drafts_generation_and_review_state(self) -> None:
        """行为 29：前端必须能生成章节草稿，并展示草稿已生成、等待审阅和正式层锁定。"""
        self.assertIn("generateSectionDrafts", self.app_js)
        self.assertIn("handleSectionDrafts", self.app_js)
        self.assertIn("data-section-drafts-action", self.app_js)
        self.assertIn("renderSectionDrafts", self.app_js)
        self.assertIn("章节草稿已生成", self.app_js)
        self.assertIn("等待人工审阅", self.app_js)
        self.assertIn("正式层仍保持锁定", self.app_js)
        self.assertIn("section_drafts", self.app_js)
        self.assertIn(".agent-task-section-drafts", self.styles_css)
        self.assertIn("generateSectionDrafts", self.react_agent_task_queue)
        self.assertIn("section-drafts-result", self.react_agent_task_queue)
        self.assertIn("WriterAgent 只写草稿层章节", self.react_agent_task_queue)
        self.assertIn("agent-task-queue-drafts", self.react_styles_css)

    def test_bdd_30_frontend_exposes_section_drafts_review_and_formal_writeback_preflight(self) -> None:
        """行为 30：前端必须能审阅章节草稿，并展示正式写回预检入口和正式层锁定。"""
        self.assertIn("reviewSectionDrafts", self.app_js)
        self.assertIn("handleSectionDraftsReview", self.app_js)
        self.assertIn("data-section-drafts-review-action", self.app_js)
        self.assertIn("approve_for_formal_writeback_preflight", self.app_js)
        self.assertIn("正式写回预检", self.app_js)
        self.assertIn("formal_writeback_preflight", self.app_js)
        self.assertIn(".agent-task-section-drafts__review", self.styles_css)
        self.assertIn(".agent-task-formal-writeback-preflight", self.styles_css)
        self.assertIn("reviewSectionDrafts", self.react_agent_task_queue)
        self.assertIn("section-drafts-review", self.react_agent_task_queue)
        self.assertIn("正式写回预检已准备", self.react_agent_task_queue)
        self.assertIn("agent-task-queue-preflight", self.react_styles_css)

    def test_bdd_31_frontend_exposes_formal_writeback_preflight_review_and_written_state(self) -> None:
        """行为 31：前端必须能审阅正式写回预检，并展示正式层写入结果。"""
        self.assertIn("reviewFormalWritebackPreflight", self.app_js)
        self.assertIn("handleFormalWritebackPreflightReview", self.app_js)
        self.assertIn("data-formal-writeback-preflight-review-action", self.app_js)
        self.assertIn("approve_formal_writeback", self.app_js)
        self.assertIn("批准写入正式层", self.app_js)
        self.assertIn("正式章节已写入", self.app_js)
        self.assertIn("formal_writeback_manifest", self.app_js)
        self.assertIn(".agent-task-formal-writeback-preflight__review", self.styles_css)
        self.assertIn(".agent-task-formal-writeback-result", self.styles_css)
        self.assertIn("reviewFormalWritebackPreflight", self.react_agent_task_queue)
        self.assertIn("formal-writeback-preflight-review", self.react_agent_task_queue)
        self.assertIn("批准写入正式层", self.react_agent_task_queue)
        self.assertIn("正式章节已写入", self.react_agent_task_queue)
        self.assertIn("formal_writeback_manifest", self.react_agent_task_queue)
        self.assertIn("agent-task-queue-formal-writeback", self.react_styles_css)

    def test_bdd_32_frontend_exposes_formal_export_preflight_console(self) -> None:
        """行为 32：前端必须把正式章节后的下一步做成导出预检台。"""
        self.assertIn("generateFormalExportPreflight", self.app_js)
        self.assertIn("handleFormalExportPreflight", self.app_js)
        self.assertIn("data-formal-export-preflight-action", self.app_js)
        self.assertIn("导出预检台", self.app_js)
        self.assertIn("formal_export_preflight", self.app_js)
        self.assertIn("resolve_export_preflight_blockers", self.app_js)
        self.assertIn("agent-task-formal-export-preflight", self.styles_css)
        self.assertIn("generateFormalExportPreflight", self.react_agent_task_queue)
        self.assertIn("formal-export-preflight", self.react_agent_task_queue)
        self.assertIn("导出预检台", self.react_agent_task_queue)
        self.assertIn("formal_export_preflight", self.react_agent_task_queue)
        self.assertIn("agent-task-queue-export-preflight", self.react_styles_css)

    def test_bdd_33_react_frontend_can_pin_local_api_base_from_url(self) -> None:
        """行为 33：本地验收时，前端必须能从 URL 绑定真实后端地址。"""
        self.assertIn("api_base", self.react_api_base)
        self.assertIn("apiBase", self.react_api_base)
        self.assertIn("URLSearchParams", self.react_api_base)
        self.assertIn("localStorage", self.react_api_base)
        self.assertIn("empiricalWorkbench.apiBase", self.react_api_base)


if __name__ == "__main__":
    unittest.main()
