from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry
from Product.backend.supervisor_plan_service import build_supervisor_plan_prompt, normalize_supervisor_plan


class SupervisorPlanApiTests(unittest.TestCase):
    """BDD: 本地 Codex Supervisor 只能生成可审阅计划，不能直接改写研究状态。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.original_path = os.environ.get("PATH", "")
        self.original_exec_env = os.environ.get("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="supervisor-plan-"))
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
                "slug": "supervisor-plan",
                "title": "Supervisor Plan Project",
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
        os.environ["PATH"] = self.original_path
        if self.original_exec_env is None:
            os.environ.pop("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC", None)
        else:
            os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = self.original_exec_env
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_generation_is_blocked_when_local_codex_execution_is_disabled(self) -> None:
        """行为 1：未启用本地 Codex 执行开关时，不能伪装生成 SupervisorPlan。"""
        self._install_fake_codex()
        os.environ.pop("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC", None)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/supervisor-plan",
            json={"objective": "规划下一轮实证执行", "note": "用户请求 P2-P"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "local_codex_execution_not_enabled")
        self.assertFalse((self.project_root / "state" / "product" / "supervisor_plan.json").exists())

    def test_bdd_2_enabled_local_codex_persists_needs_review_supervisor_plan(self) -> None:
        """行为 2：启用本地 Codex 后，系统必须持久化 local_execution 级别的待审计划。"""
        self._install_fake_codex()
        os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/supervisor-plan",
            json={"objective": "为 approved RunPlan 生成下一轮实证执行计划", "note": "进入 P2-P"},
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        plan = response.json()["supervisor_plan"]
        self.assertEqual(plan["status"], "needs_review")
        self.assertEqual(plan["evidence_level"], "local_execution")
        self.assertEqual(plan["provider"]["provider"], "local_codex")
        self.assertEqual(plan["objective"], "为 approved RunPlan 生成下一轮实证执行计划")
        self.assertEqual(plan["next_action"]["id"], "review_supervisor_plan")
        self.assertEqual(plan["subagent_dispatch"][0]["agent_id"], "pipeline_data")
        self.assertEqual(plan["input_research_question"]["question"], "培训是否影响工资？")
        self.assertEqual(plan["input_research_question"]["topic_session_id"], "topic_session_v1")
        self.assertEqual(plan["input_state_versions"]["research_question_version"], 1)
        self.assertEqual(plan["input_evidence"]["research_question_path"], "state/product/research_question.json")
        self.assertIn("不可直接改写 VariableRoleSet", plan["write_boundary"])

        saved_path = self.project_root / "state" / "product" / "supervisor_plan.json"
        self.assertTrue(saved_path.exists())
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "needs_review")
        self.assertEqual(saved["raw_output_path"], "state/product/supervisor_plan.raw.md")
        self.assertEqual(saved["input_research_question"]["version"], 1)

    def test_bdd_19_supervisor_plan_prompt_requests_reference_chain_policy(self) -> None:
        """行为 19：SupervisorPlan 提示词必须要求 LLM 规划文献/引用链路策略。"""
        prompt = build_supervisor_plan_prompt(
            project={
                "id": "p1",
                "title": "Project",
                "question": "社会资本是否影响居民主观幸福感？",
            },
            objective="规划下一轮递归文献检索、数据变量和方法选择。",
            research_question={
                "question": "社会资本是否影响居民主观幸福感？",
                "topic_session_id": "topic_session_v1",
                "version": 1,
                "status": "confirmed",
            },
            variable_roles={"version": 1, "status": "approved"},
            design_spec={"version": 1, "status": "approved"},
            run_plan={"version": 1, "status": "approved"},
        )

        for required in (
            "reference_chain_policy",
            "source_priority",
            "max_depth",
            "max_iterations",
            "CNKI",
            "Zotero",
            "draft_citation_policy",
            "formal_writeback_gate",
            "writes_formal_layer",
        ):
            self.assertIn(required, prompt)

    def test_bdd_7_generation_requires_confirmed_research_question(self) -> None:
        """行为 7：没有 confirmed ResearchQuestion 时，SupervisorPlan 不得生成。"""
        self._install_fake_codex()
        os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"
        research_question_path = self.project_root / "state" / "product" / "research_question.json"
        research_question_path.unlink()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/supervisor-plan",
            json={"objective": "尝试在无选题状态下派工", "note": "必须阻断"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "research_question_required")
        self.assertFalse((self.project_root / "state" / "product" / "supervisor_plan.json").exists())

    def test_bdd_3_supervisor_plan_does_not_mutate_approved_research_states(self) -> None:
        """行为 3：SupervisorPlan 只能引用已确认状态，不得直接改写它们。"""
        self._install_fake_codex()
        os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"
        state_paths = [
            self.project_root / "state" / "product" / "variable_roles.json",
            self.project_root / "state" / "product" / "design_spec.json",
            self.project_root / "state" / "product" / "run_plan.json",
        ]
        before = {path.name: path.read_text(encoding="utf-8") for path in state_paths}

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/supervisor-plan",
            json={"objective": "审阅下一轮任务边界", "note": "不允许改写状态"},
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        after = {path.name: path.read_text(encoding="utf-8") for path in state_paths}
        self.assertEqual(before, after)
        plan = response.json()["supervisor_plan"]
        self.assertEqual(plan["input_state_versions"]["research_question_version"], 1)
        self.assertEqual(plan["input_state_versions"]["variable_role_set_version"], 1)
        self.assertEqual(plan["input_state_versions"]["design_spec_version"], 1)
        self.assertEqual(plan["input_state_versions"]["run_plan_version"], 1)

    def test_bdd_4_get_returns_persisted_supervisor_plan(self) -> None:
        """行为 4：生成后 GET API 必须返回同一份可审阅计划。"""
        self._install_fake_codex()
        os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"
        create_response = self.client.post(
            f"/api/v1/projects/{self.project_id}/supervisor-plan",
            json={"objective": "生成可审阅执行计划", "note": "准备人工确认"},
        )
        self.assertEqual(create_response.status_code, 201, msg=create_response.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/supervisor-plan")

        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(response.json()["supervisor_plan"]["status"], "needs_review")
        self.assertEqual(response.json()["supervisor_plan"]["objective"], "生成可审阅执行计划")

    def test_bdd_9_approve_supervisor_plan_persists_human_review_and_allows_dispatch(self) -> None:
        """行为 9：人工 approve 后，SupervisorPlan 才能作为任务队列输入。"""
        self._generate_plan()

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/supervisor-plan/review",
            json={"action": "approve", "note": "计划可以进入下一步任务队列。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        plan = response.json()["supervisor_plan"]
        self.assertEqual(plan["status"], "approved")
        self.assertTrue(plan["can_dispatch"])
        self.assertEqual(plan["next_action"]["id"], "create_agent_task_queue")
        self.assertEqual(plan["human_review"]["action"], "approve")
        self.assertEqual(plan["human_review"]["note"], "计划可以进入下一步任务队列。")

        saved = json.loads((self.project_root / "state" / "product" / "supervisor_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "approved")
        self.assertTrue(saved["can_dispatch"])

    def test_bdd_10_reject_or_revision_blocks_dispatch(self) -> None:
        """行为 10：reject / needs_revision 必须阻止派工，并保存审阅意见。"""
        self._generate_plan()

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/supervisor-plan/review",
            json={"action": "needs_revision", "note": "证据要求还不够清楚。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        plan = response.json()["supervisor_plan"]
        self.assertEqual(plan["status"], "needs_revision")
        self.assertFalse(plan["can_dispatch"])
        self.assertEqual(plan["next_action"]["id"], "revise_supervisor_plan")
        self.assertEqual(plan["human_review"]["action"], "needs_revision")

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/supervisor-plan/review",
            json={"action": "reject", "note": "暂不采用。"},
        )
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(response.json()["supervisor_plan"]["status"], "rejected")
        self.assertFalse(response.json()["supervisor_plan"]["can_dispatch"])

    def test_bdd_11_review_requires_existing_plan_and_valid_action(self) -> None:
        """行为 11：不存在计划或非法审批动作必须被结构化拒绝。"""
        missing = self.client.put(
            f"/api/v1/projects/{self.project_id}/supervisor-plan/review",
            json={"action": "approve", "note": "不能审批不存在的计划。"},
        )
        self.assertEqual(missing.status_code, 409, msg=missing.text)
        self.assertEqual(missing.json()["error"]["code"], "supervisor_plan_required")

        self._generate_plan()
        invalid = self.client.put(
            f"/api/v1/projects/{self.project_id}/supervisor-plan/review",
            json={"action": "dispatch_now", "note": "非法动作。"},
        )
        self.assertEqual(invalid.status_code, 400, msg=invalid.text)
        self.assertEqual(invalid.json()["error"]["code"], "invalid_supervisor_plan_review_action")

    def test_bdd_12_supervisor_plan_review_does_not_mutate_research_states(self) -> None:
        """行为 12：审批计划不能改写 ResearchQuestion、VariableRoleSet、DesignSpec 或 RunPlan。"""
        self._generate_plan()
        state_paths = [
            self.project_root / "state" / "product" / "research_question.json",
            self.project_root / "state" / "product" / "variable_roles.json",
            self.project_root / "state" / "product" / "design_spec.json",
            self.project_root / "state" / "product" / "run_plan.json",
        ]
        before = {path.name: path.read_text(encoding="utf-8") for path in state_paths}

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/supervisor-plan/review",
            json={"action": "approve", "note": "只审批计划。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        after = {path.name: path.read_text(encoding="utf-8") for path in state_paths}
        self.assertEqual(before, after)

    def _generate_plan(self) -> dict:
        self._install_fake_codex()
        os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/supervisor-plan",
            json={"objective": "生成可审批的 SupervisorPlan", "note": "准备进入人工审批。"},
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        return response.json()["supervisor_plan"]

    def _approve_research_states(self) -> None:
        question = self.client.put(
            f"/api/v1/projects/{self.project_id}/research-question/current",
            json={
                "question": "培训是否影响工资？",
                "source": "project_seed",
                "note": "选题已确认。",
            },
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

    def _install_fake_codex(self) -> None:
        bin_dir = self.temp_dir / "bin"
        bin_dir.mkdir()
        codex = bin_dir / "codex"
        codex.write_text(
            """#!/usr/bin/env python3
import json
import sys
from pathlib import Path

if "--version" in sys.argv:
    print("codex-cli fake-supervisor")
    raise SystemExit(0)

output_path = Path(sys.argv[sys.argv.index("--output-last-message") + 1])
prompt = sys.argv[-1]
if "confirmed_research_question" not in prompt or "topic_session_v1" not in prompt:
    print("prompt missing confirmed research question context", file=sys.stderr)
    raise SystemExit(7)
payload = {
    "stage_plan": [
        {"stage": "数据与变量", "goal": "复核字段角色与样本口径", "status": "planned"},
        {"stage": "实证执行", "goal": "运行 OLS 并交叉验证 StatsPAI", "status": "planned"}
    ],
    "subagent_dispatch": [
        {"agent_id": "pipeline_data", "role": "Data Agent", "task": "检查数据和变量角色"},
        {"agent_id": "pipeline_execution", "role": "Execution Agent", "task": "执行并验证模型"}
    ],
    "evidence_requirements": [
        {"id": "dataset_profile", "requirement": "保留字段画像和样本量", "evidence_level": "local_file"},
        {"id": "model_run", "requirement": "保留运行日志和回归结果", "evidence_level": "local_execution"}
    ],
    "risks": [
        {"id": "heuristic_roles", "level": "medium", "description": "变量角色候选不能直接进入论文"}
    ],
    "human_gates": [
        {"id": "review_supervisor_plan", "label": "人工确认 SupervisorPlan", "required": True}
    ],
    "next_action": {"id": "review_supervisor_plan", "label": "审阅 SupervisorPlan"}
}
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
print("fake codex supervisor complete")
""",
            encoding="utf-8",
        )
        codex.chmod(0o755)
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{self.original_path}"

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: supervisor-plan\n  title: Supervisor Plan Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n12,0,14,5\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


class SupervisorPlanFrontendTests(unittest.TestCase):
    """BDD: 首页必须把 SupervisorPlan 作为可审阅对象呈现。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.index_html = (root / "Product" / "web" / "index.html").read_text(encoding="utf-8")
        cls.app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.styles_css = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

    def test_bdd_5_frontend_contains_supervisor_plan_review_surface(self) -> None:
        """行为 5：首页必须有生成和审阅 SupervisorPlan 的界面。"""
        self.assertIn("supervisor-plan-panel", self.index_html)
        self.assertIn("supervisor-plan-body", self.index_html)
        self.assertIn("renderSupervisorPlan", self.app_js)
        self.assertIn("handleGenerateSupervisorPlan", self.app_js)
        self.assertIn("v2api.supervisorPlan.generate", self.app_js)
        for label in ("生成 SupervisorPlan", "人工确认", "证据要求", "子 Agent 分工"):
            self.assertIn(label, self.app_js + self.index_html)
        self.assertIn("supervisor-plan-card", self.styles_css)

    def test_bdd_6_supervisor_plan_details_are_progressively_disclosed(self) -> None:
        """行为 6：SupervisorPlan 的高噪声审阅细节必须默认折叠，点击后再展开。"""
        self.assertIn("supervisor-plan-progressive-disclosure", self.app_js)
        self.assertIn('class="progressive-disclosure supervisor-plan-details"', self.app_js)
        self.assertIn("查看计划详情", self.app_js)
        self.assertIn("disclosure-panel", self.app_js)
        self.assertIn(".progressive-disclosure", self.styles_css)

    def test_bdd_8_frontend_shows_supervisor_plan_topic_binding(self) -> None:
        """行为 8：SupervisorPlan 审阅台必须显示绑定的研究选题和 TopicSession。"""
        self.assertIn("input_research_question", self.app_js)
        self.assertIn("绑定选题", self.app_js)
        self.assertIn("TopicSession", self.app_js)
        self.assertIn("ResearchQuestion 版本", self.app_js)

    def test_bdd_13_frontend_exposes_explicit_supervisor_plan_review_actions(self) -> None:
        """行为 13：前端必须提供 approve/reject/needs_revision 三个显式审批动作。"""
        self.assertIn("v2api.supervisorPlan.review", self.app_js)
        self.assertIn("handleReviewSupervisorPlan", self.app_js)
        self.assertIn("data-supervisor-plan-review-action", self.app_js)
        for label in ("批准计划", "要求修改", "驳回计划", "只有批准后的计划才能进入任务队列"):
            self.assertIn(label, self.app_js)

    def test_bdd_14_frontend_does_not_show_unreviewed_when_plan_is_already_approved(self) -> None:
        """行为 14：历史 approved SupervisorPlan 缺少 human_review 时，前端也不得显示尚未审批。"""
        self.assertIn("supervisorHumanReviewLabel", self.app_js)
        self.assertIn('plan.status === "approved"', self.app_js)
        self.assertIn("已批准", self.app_js)

    def test_bdd_18_frontend_exposes_internal_skill_review_contract(self) -> None:
        """行为 18：SupervisorPlan 审阅台必须显示推荐 Skill、选择理由、缺失证据和人工审阅状态。"""
        self.assertIn("renderSupervisorPlanSkillReview", self.app_js)
        self.assertIn("recommended_internal_skills", self.app_js)
        self.assertIn("skill_review_contract", self.app_js)
        self.assertIn("applicability_reason", self.app_js)
        self.assertIn("missing_evidence", self.app_js)
        self.assertIn("推荐 Skill", self.app_js)
        self.assertIn("选择理由", self.app_js)
        self.assertIn("缺失证据", self.app_js)
        self.assertIn("人工审阅状态", self.app_js)
        self.assertIn(".supervisor-plan-skill-review", self.styles_css)

    def test_bdd_15_supervisor_plan_recommends_internal_skills_from_plan_context(self) -> None:
        """行为 15：SupervisorPlan 必须把相关 internal skills 作为待审能力推荐，而不是自由发挥。"""
        generated = {
            "stage_plan": [
                {"stage": "递归搜索", "goal": "检索文献、数据和方法缺口", "status": "planned"},
                {"stage": "方法设计", "goal": "检查 DID 和 IV 识别门", "status": "planned"},
            ],
            "subagent_dispatch": [
                {
                    "agent_id": "pipeline_literature",
                    "role": "LiteratureAgent",
                    "task": "递归检索文献、数据线索与变量证据",
                },
                {
                    "agent_id": "pipeline_method",
                    "role": "MethodAgent",
                    "task": "检查 DID 与 IV 识别前置条件",
                },
            ],
            "evidence_requirements": [],
            "risks": [],
            "human_gates": [],
        }

        plan = normalize_supervisor_plan(
            generated=generated,
            project={"id": "p1", "title": "Project", "question": "政策冲击是否影响工资？"},
            objective="用 DID / IV 路线规划下一轮实证任务",
            note="绑定 internal skill registry",
            provider={"provider": "local_codex"},
            research_question={
                "question": "政策冲击是否影响工资？",
                "topic_session_id": "topic_session_v1",
                "version": 1,
                "status": "confirmed",
            },
            variable_roles={"version": 1, "status": "approved"},
            design_spec={
                "version": 1,
                "status": "approved",
                "identification_strategy": {"name": "did_iv_candidate"},
                "model": {"estimator": "did_iv"},
            },
            run_plan={"version": 1, "status": "approved"},
            version=2,
            timestamp="2026-06-08T00:00:00Z",
        )

        by_skill_id = {
            skill["skill_id"]: skill for skill in plan["recommended_internal_skills"]
        }

        self.assertIn("recursive_research_search", by_skill_id)
        self.assertIn("did_staggered_identification_gate", by_skill_id)
        self.assertIn("weak_iv_diagnostic_gate", by_skill_id)
        self.assertEqual(
            by_skill_id["recursive_research_search"]["dispatch_targets"],
            ["pipeline_literature"],
        )
        self.assertEqual(
            by_skill_id["did_staggered_identification_gate"]["dispatch_targets"],
            ["pipeline_method"],
        )
        self.assertEqual(by_skill_id["did_staggered_identification_gate"]["formal_write_targets"], [])
        self.assertFalse(
            by_skill_id["did_staggered_identification_gate"]["canonical_policy"]["auto_mode"]["can_write_canonical"]
        )
        self.assertIn(
            "aers:eval:did-staggered-recovery",
            by_skill_id["did_staggered_identification_gate"]["quality_gates"]["machine_checkable"],
        )
        self.assertIn(
            "default_run_plan_inclusion",
            by_skill_id["did_staggered_identification_gate"]["human_confirmation"]["required_before"],
        )

    def test_bdd_16_supervisor_plan_keeps_llm_semantic_skill_judgment(self) -> None:
        """行为 16：LLM Supervisor 选择 internal skill 时，必须保存可审阅的语义理由。"""
        generated = {
            "stage_plan": [
                {"stage": "质量检查", "goal": "判断是否需要更高标准的写作出口核验", "status": "planned"}
            ],
            "subagent_dispatch": [
                {
                    "agent_id": "pipeline_quality",
                    "role": "QualityAgent",
                    "task": "整理下一步质量检查任务",
                }
            ],
            "evidence_requirements": [],
            "risks": [],
            "human_gates": [],
            "internal_skill_judgments": [
                {
                    "skill_id": "aer_abstract_submission_preflight",
                    "reason": "用户选择顶刊标准，需要先检查摘要、表格说明和披露边界。",
                    "evidence_fit": "当前计划进入写作出口前，缺少摘要长度、图表说明和 disclosure 的核验项。",
                    "agent_fit": "ReviewerAgent/ManuscriptAgent 更适合做投稿前预检。",
                    "risk_note": "只生成预检和修订工单，不能静默导出正式投稿包。",
                    "human_review_note": "正式导出前必须由研究者确认。",
                    "confidence": "medium",
                },
                {
                    "skill_id": "unknown_external_skill",
                    "reason": "LLM 认为可能有用，但它不在本项目内部 registry 中。",
                },
            ],
        }

        plan = normalize_supervisor_plan(
            generated=generated,
            project={"id": "p1", "title": "Project", "question": "父母教育是否影响工资？"},
            objective="规划下一步质量检查",
            note="让 LLM 解释为什么选择 skill",
            provider={"provider": "local_codex"},
            research_question={
                "question": "父母教育是否影响工资？",
                "topic_session_id": "topic_session_v1",
                "version": 1,
                "status": "confirmed",
            },
            variable_roles={"version": 1, "status": "approved"},
            design_spec={"version": 1, "status": "approved"},
            run_plan={"version": 1, "status": "approved"},
            version=2,
            timestamp="2026-06-08T00:00:00Z",
        )

        by_skill_id = {
            skill["skill_id"]: skill for skill in plan["recommended_internal_skills"]
        }

        self.assertIn("aer_abstract_submission_preflight", by_skill_id)
        self.assertNotIn("unknown_external_skill", by_skill_id)
        aer_preflight = by_skill_id["aer_abstract_submission_preflight"]
        self.assertEqual(aer_preflight["selection_source"], "llm_semantic_judgment")
        self.assertEqual(
            aer_preflight["semantic_selection_reason"],
            "用户选择顶刊标准，需要先检查摘要、表格说明和披露边界。",
        )
        self.assertEqual(
            aer_preflight["llm_semantic_judgment"]["evidence_fit"],
            "当前计划进入写作出口前，缺少摘要长度、图表说明和 disclosure 的核验项。",
        )
        self.assertFalse(aer_preflight["canonical_policy"]["auto_mode"]["can_write_canonical"])
        self.assertEqual(plan["unmatched_internal_skill_judgments"][0]["skill_id"], "unknown_external_skill")

    def test_bdd_17_supervisor_plan_exposes_human_readable_skill_review_contract(self) -> None:
        """行为 17：SupervisorPlan 必须把 skill 选择变成用户可审阅的产品契约。"""
        generated = {
            "stage_plan": [
                {"stage": "递归搜索", "goal": "检索文献、数据和方法缺口", "status": "planned"},
            ],
            "subagent_dispatch": [
                {
                    "agent_id": "pipeline_literature",
                    "role": "LiteratureAgent",
                    "task": "递归检索文献、数据线索与变量证据",
                }
            ],
            "evidence_requirements": [],
            "risks": [],
            "human_gates": [],
            "internal_skill_judgments": [
                {
                    "skill_id": "recursive_research_search",
                    "reason": "题目需要先从文献、数据和变量证据形成递归搜索图。",
                    "evidence_fit": "当前只有题目和研究方向，缺少已验证文献与数据线索。",
                    "agent_fit": "LiteratureAgent 负责检索与证据归档。",
                    "risk_note": "检索结果只能进入草案层，不能直接写成正式综述。",
                    "human_review_note": "正式写入文献综述前需要人工确认引用。",
                    "confidence": "high",
                },
                {
                    "skill_id": "unknown_external_skill",
                    "reason": "LLM 提到了 registry 外部能力。",
                },
            ],
        }

        plan = normalize_supervisor_plan(
            generated=generated,
            project={"id": "p1", "title": "Project", "question": "社会资本是否影响幸福感？"},
            objective="规划递归研究搜索",
            note="把 skill 选择解释给用户",
            provider={"provider": "local_codex"},
            research_question={
                "question": "社会资本是否影响幸福感？",
                "topic_session_id": "topic_session_v1",
                "version": 1,
                "status": "confirmed",
            },
            variable_roles={"version": 1, "status": "approved"},
            design_spec={"version": 1, "status": "approved"},
            run_plan={"version": 1, "status": "approved"},
            version=2,
            timestamp="2026-06-08T00:00:00Z",
        )

        self.assertEqual(plan["skill_review_status"], "needs_human_skill_review")
        self.assertEqual(plan["selected_skill_ids"], ["recursive_research_search"])
        self.assertEqual(
            plan["applicability_reason"]["recursive_research_search"],
            "题目需要先从文献、数据和变量证据形成递归搜索图。",
        )
        self.assertEqual(plan["skill_sources"][0]["skill_id"], "recursive_research_search")
        self.assertEqual(plan["skill_sources"][0]["selection_source"], "registry_and_llm_semantic_judgment")
        self.assertIn("Auto-Empirical-Research-Skills", plan["skill_sources"][0]["external_source_names"])
        self.assertEqual(plan["missing_evidence"][0]["skill_id"], "recursive_research_search")
        self.assertIn("TaskBrief.approved", plan["missing_evidence"][0]["required_state"])
        self.assertEqual(plan["missing_evidence"][-1]["skill_id"], "unknown_external_skill")
        self.assertTrue(plan["skill_review_contract"]["human_review_required"])

    def test_bdd_20_supervisor_plan_keeps_reference_chain_policy_for_queue_contract(self) -> None:
        """行为 20：LLM 生成的文献/引用链路策略必须进入可审阅 SupervisorPlan。"""
        generated = {
            "stage_plan": [
                {"stage": "递归搜索", "goal": "先建立文献、变量和数据证据链", "status": "planned"},
            ],
            "subagent_dispatch": [
                {
                    "agent_id": "pipeline_literature",
                    "role": "LiteratureAgent",
                    "task": "递归检索中文和英文文献，形成引用候选池",
                }
            ],
            "evidence_requirements": [],
            "risks": [],
            "human_gates": [],
            "reference_chain_policy": {
                "contract_version": "reference_chain.v1",
                "status": "needs_review",
                "source_priority": ["cnki", "scholar", "zotero", "local_notes", "arxiv"],
                "sources": [
                    {
                        "id": "cnki",
                        "label": "CNKI",
                        "trigger": "中文制度背景、国内实证研究和硕博论文线索",
                        "mode": "manual_assisted_or_browser_assisted_search",
                    },
                    {
                        "id": "scholar",
                        "label": "Google Scholar",
                        "trigger": "英文引用网络和高被引实证文献",
                        "mode": "browser_or_manual_assisted_search",
                    },
                ],
                "max_depth": 2,
                "max_iterations": 5,
                "draft_citation_policy": "候选文献可以进入草案，但必须显示待核验状态。",
                "formal_writeback_gate": "review_literature_seed_package",
                "writes_formal_layer": True,
            },
        }

        plan = normalize_supervisor_plan(
            generated=generated,
            project={"id": "p1", "title": "Project", "question": "社会资本是否影响幸福感？"},
            objective="规划递归文献检索与证据链",
            note="保存引用链路策略",
            provider={"provider": "local_codex"},
            research_question={
                "question": "社会资本是否影响幸福感？",
                "topic_session_id": "topic_session_v1",
                "version": 1,
                "status": "confirmed",
            },
            variable_roles={"version": 1, "status": "approved"},
            design_spec={"version": 1, "status": "approved"},
            run_plan={"version": 1, "status": "approved"},
            version=2,
            timestamp="2026-06-08T00:00:00Z",
        )

        policy = plan["reference_chain_policy"]
        self.assertEqual(policy["contract_version"], "reference_chain.v1")
        self.assertEqual(policy["status"], "needs_review")
        self.assertEqual(policy["source_priority"], ["cnki", "scholar", "zotero", "local_notes", "arxiv"])
        self.assertEqual(policy["sources"][0]["id"], "cnki")
        self.assertEqual(policy["max_depth"], 2)
        self.assertEqual(policy["max_iterations"], 5)
        self.assertEqual(policy["formal_writeback_gate"], "review_literature_seed_package")
        self.assertFalse(policy["writes_formal_layer"])


if __name__ == "__main__":
    unittest.main()
