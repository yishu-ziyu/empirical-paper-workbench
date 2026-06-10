from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class TraceLearningBadCaseApiTests(unittest.TestCase):
    """BDD: 用户反馈的坏案例必须进入可追踪改进账本，不能直接改正式研究状态。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="trace-learning-"))
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
                "slug": "trace-learning",
                "title": "Trace Learning Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_capture_bad_case_persists_trace_learning_ledger(self) -> None:
        """Given 用户指出坏案例；When 记录反馈；Then 账本保存原因、层级和回归测试目标。"""
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "agent_task_queue",
                "surface": "web_react",
                "page_url": "http://127.0.0.1:5173/react/react",
                "target_text": "步骤 1 分析研究问题",
                "agent_output": "这是因果推断类问题，关心工业机器人对蓝领工资的影响。",
                "user_feedback": "这个推断和我的题目一点关系都没有。",
                "expected_behavior": "系统应基于当前题目重新判断研究对象，不能套用旧 demo 题目。",
                "fix_layer": "eval_set",
                "severity": "high",
                "related_files": ["Product/web-react/src/components/BriefPanel.tsx"],
            },
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        payload = response.json()
        bad_case = payload["bad_case"]
        self.assertEqual(bad_case["status"], "captured")
        self.assertEqual(bad_case["stage"], "agent_task_queue")
        self.assertEqual(bad_case["fix_layer"], "eval_set")
        self.assertEqual(bad_case["user_feedback"], "这个推断和我的题目一点关系都没有。")
        self.assertFalse(bad_case["writes_formal_layer"])
        self.assertEqual(bad_case["next_action"], "turn_into_regression_test")
        self.assertEqual(bad_case["regression_target"]["kind"], "contract_test")
        self.assertEqual(payload["trace_learning"]["path"], "state/product/trace_learning_bad_cases.jsonl")
        self.assertIn("skill_playbook", payload["trace_learning"]["allowed_fix_layers"])

        ledger_path = self.project_root / "state" / "product" / "trace_learning_bad_cases.jsonl"
        self.assertTrue(ledger_path.exists())
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        saved = json.loads(lines[0])
        self.assertEqual(saved["id"], bad_case["id"])
        self.assertEqual(saved["trace_learning_version"], 1)

    def test_bdd_2_get_bad_cases_restores_saved_feedback_across_session(self) -> None:
        """Given 已保存坏案例；When 重新读取；Then 返回项目内全部 Trace Learning 记录。"""
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "search",
                "user_feedback": "文献检索结果没有围绕当前题目。",
                "expected_behavior": "检索词应从当前题目抽取。",
                "fix_layer": "retrieval",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases")

        self.assertEqual(response.status_code, 200, msg=response.text)
        trace_learning = response.json()["trace_learning"]
        self.assertEqual(trace_learning["case_count"], 1)
        self.assertEqual(trace_learning["bad_cases"][0]["fix_layer"], "retrieval")
        self.assertEqual(trace_learning["bad_cases"][0]["user_feedback"], "文献检索结果没有围绕当前题目。")

    def test_bdd_3_generate_regression_proposal_from_captured_bad_case(self) -> None:
        """Given 已捕获坏案例；When 生成回归建议；Then 返回待审阅测试建议而不写正式层。"""
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "surface": "web_react",
                "target_text": "分析研究问题",
                "agent_output": "错误套用了工业机器人题目。",
                "user_feedback": "这个推断和我的题目一点关系都没有。",
                "expected_behavior": "系统必须围绕当前题目重做语义判断。",
                "fix_layer": "decision_rule",
                "severity": "high",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        bad_case_id = created.json()["bad_case"]["id"]

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        proposal = response.json()["regression_proposal"]
        self.assertEqual(proposal["status"], "needs_review")
        self.assertEqual(proposal["source_bad_case_ids"], [bad_case_id])
        self.assertEqual(proposal["patch_layer"], "decision_rule")
        self.assertFalse(proposal["writes_formal_layer"])
        self.assertTrue(proposal["requires_human_review"])
        self.assertEqual(proposal["artifact_path"], "state/product/trace_learning_regression_proposals.jsonl")
        self.assertEqual(proposal["next_action"], "human_review_regression_proposal")
        self.assertGreaterEqual(len(proposal["suggested_tests"]), 1)
        first_test = proposal["suggested_tests"][0]
        self.assertEqual(first_test["source_bad_case_id"], bad_case_id)
        self.assertIn("Given", first_test["bdd"])
        self.assertIn("When", first_test["bdd"])
        self.assertIn("Then", first_test["bdd"])
        self.assertIn("这个推断和我的题目一点关系都没有", first_test["bdd"])

        proposal_path = self.project_root / "state" / "product" / "trace_learning_regression_proposals.jsonl"
        self.assertTrue(proposal_path.exists())
        saved = json.loads(proposal_path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(saved["id"], proposal["id"])

    def test_bdd_4_get_regression_proposals_restores_reviewable_suggestions(self) -> None:
        """Given 已生成回归建议；When 重新读取；Then 返回可审阅建议列表。"""
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "search",
                "user_feedback": "文献检索结果没有围绕当前题目。",
                "expected_behavior": "检索词应从当前题目抽取。",
                "fix_layer": "retrieval",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        proposed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )
        self.assertEqual(proposed.status_code, 201, msg=proposed.text)

        response = self.client.get(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        trace_learning = response.json()["trace_learning"]
        self.assertEqual(trace_learning["proposal_count"], 1)
        self.assertEqual(trace_learning["regression_proposals"][0]["id"], proposed.json()["regression_proposal"]["id"])
        self.assertEqual(trace_learning["regression_proposals"][0]["status"], "needs_review")
        self.assertEqual(trace_learning["regression_proposals"][0]["current_review_status"], "needs_review")
        self.assertIsNone(trace_learning["regression_proposals"][0]["latest_review_id"])
        self.assertTrue(trace_learning["regression_proposals"][0]["requires_human_review"])
        self.assertEqual(
            trace_learning["regression_proposals"][0]["next_action"],
            "human_review_regression_proposal",
        )
        self.assertEqual(
            trace_learning["regression_proposals"][0]["source_bad_case_ids"],
            [created.json()["bad_case"]["id"]],
        )

    def test_bdd_5_regression_proposal_requires_captured_bad_case(self) -> None:
        """Given 还没有坏案例；When 生成回归建议；Then API 阻止空建议。"""
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "no_captured_trace_learning_bad_cases")
        proposal_path = self.project_root / "state" / "product" / "trace_learning_regression_proposals.jsonl"
        self.assertFalse(proposal_path.exists())

    def test_bdd_6_regression_proposal_does_not_mutate_formal_research_states(self) -> None:
        """Given 正式层状态已存在；When 生成回归建议；Then 只写建议账本。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True, exist_ok=True)
        protected_states = {
            "research_question.json": {"question": "父母教育水平对子女工资水平的影响"},
            "variable_roles.json": {"roles": {"outcome": ["wage"], "treatment": ["parent_edu"]}},
            "design_spec.json": {"model": {"estimator": "ols"}},
            "run_plan.json": {"tasks": [{"id": "baseline"}]},
            "supervisor_plan.json": {"status": "approved", "can_dispatch": True},
            "agent_task_queue.json": {"status": "ready_for_dispatch", "tasks": []},
        }
        for name, payload in protected_states.items():
            (state_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        before = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "user_feedback": "这里把当前题目误判成旧题目。",
                "expected_behavior": "生成回归建议，不直接改写正式状态。",
                "fix_layer": "decision_rule",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        after = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}
        self.assertEqual(before, after)

    def test_bdd_6a_review_regression_proposal_records_human_decision(self) -> None:
        """Given 待审阅回归建议；When 人工批准；Then 只记录审阅决定和下一步补丁状态。"""
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "user_feedback": "这里把当前题目误判成旧题目。",
                "expected_behavior": "生成回归测试补丁前必须先人工审阅。",
                "fix_layer": "decision_rule",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        proposed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )
        self.assertEqual(proposed.status_code, 201, msg=proposed.text)
        proposal_id = proposed.json()["regression_proposal"]["id"]

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/review",
            json={
                "decision": "approve",
                "reviewer": "mahaoxuan",
                "note": "可以进入回归测试补丁，但不要自动改正式规则。",
            },
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        review = response.json()["regression_proposal_review"]
        self.assertEqual(review["proposal_id"], proposal_id)
        self.assertEqual(review["decision"], "approve")
        self.assertEqual(review["status"], "approved")
        self.assertEqual(review["reviewer"], "mahaoxuan")
        self.assertEqual(review["next_action"], "prepare_regression_test_patch")
        self.assertFalse(review["writes_formal_layer"])
        self.assertFalse(review["canonical_rule_write_allowed"])
        self.assertFalse(review["test_file_write_allowed"])
        self.assertEqual(review["artifact_path"], "state/product/trace_learning_regression_proposal_reviews.jsonl")

        review_path = self.project_root / "state" / "product" / "trace_learning_regression_proposal_reviews.jsonl"
        self.assertTrue(review_path.exists())
        saved = json.loads(review_path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(saved["id"], review["id"])

    def test_bdd_6b_get_regression_proposals_restores_review_records(self) -> None:
        """Given 已审阅回归建议；When 重新读取建议；Then 返回审阅账本和每个建议的最新状态。"""
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "search",
                "user_feedback": "检索结果没有围绕当前题目。",
                "expected_behavior": "先生成可审阅的回归测试建议。",
                "fix_layer": "retrieval",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        proposed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )
        self.assertEqual(proposed.status_code, 201, msg=proposed.text)
        proposal_id = proposed.json()["regression_proposal"]["id"]
        reviewed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/review",
            json={"decision": "request_revision", "reviewer": "mahaoxuan", "note": "需要把断言写得更窄。"},
        )
        self.assertEqual(reviewed.status_code, 201, msg=reviewed.text)

        response = self.client.get(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        trace_learning = response.json()["trace_learning"]
        self.assertEqual(trace_learning["proposal_count"], 1)
        self.assertEqual(trace_learning["review_count"], 1)
        self.assertEqual(trace_learning["proposal_reviews"][0]["decision"], "request_revision")
        self.assertEqual(trace_learning["proposal_reviews"][0]["status"], "needs_revision")
        self.assertEqual(trace_learning["review_status_by_proposal_id"][proposal_id], "needs_revision")
        self.assertEqual(trace_learning["regression_proposals"][0]["id"], proposal_id)
        self.assertEqual(trace_learning["regression_proposals"][0]["current_review_status"], "needs_revision")
        self.assertEqual(
            trace_learning["regression_proposals"][0]["latest_review_id"],
            trace_learning["proposal_reviews"][0]["id"],
        )

    def test_bdd_6c_review_requires_existing_regression_proposal(self) -> None:
        """Given 不存在的建议编号；When 试图审阅；Then API 阻止伪造审阅账本。"""
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/missing/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "missing"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "trace_learning_proposal_not_found")
        review_path = self.project_root / "state" / "product" / "trace_learning_regression_proposal_reviews.jsonl"
        self.assertFalse(review_path.exists())

    def test_bdd_6d_regression_proposal_review_does_not_mutate_formal_research_states(self) -> None:
        """Given 正式层状态已存在；When 审阅回归建议；Then 仍然只写审阅账本。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True, exist_ok=True)
        protected_states = {
            "research_question.json": {"question": "父母教育水平对子女工资水平的影响"},
            "variable_roles.json": {"roles": {"outcome": ["wage"], "treatment": ["parent_edu"]}},
            "design_spec.json": {"model": {"estimator": "ols"}},
            "run_plan.json": {"tasks": [{"id": "baseline"}]},
            "supervisor_plan.json": {"status": "approved", "can_dispatch": True},
            "agent_task_queue.json": {"status": "ready_for_dispatch", "tasks": []},
        }
        for name, payload in protected_states.items():
            (state_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "user_feedback": "这里把当前题目误判成旧题目。",
                "expected_behavior": "审阅只决定是否准备补丁。",
                "fix_layer": "decision_rule",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        proposed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )
        self.assertEqual(proposed.status_code, 201, msg=proposed.text)
        proposal_id = proposed.json()["regression_proposal"]["id"]
        before = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "进入补丁准备。"},
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        after = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}
        self.assertEqual(before, after)

    def test_bdd_6e_approved_regression_proposal_generates_reviewable_test_patch_proposal(self) -> None:
        """Given 回归建议已人工批准；When 生成测试补丁建议；Then 只写草案层补丁建议账本。"""
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "surface": "web_react",
                "target_text": "分析研究问题",
                "agent_output": "错误套用了工业机器人题目。",
                "user_feedback": "这个推断和我的题目一点关系都没有。",
                "expected_behavior": "系统必须围绕当前题目重做语义判断。",
                "fix_layer": "decision_rule",
                "severity": "high",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        proposed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )
        self.assertEqual(proposed.status_code, 201, msg=proposed.text)
        proposal_id = proposed.json()["regression_proposal"]["id"]
        reviewed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "可以准备测试补丁建议。"},
        )
        self.assertEqual(reviewed.status_code, 201, msg=reviewed.text)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/test-patch-proposals"
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        patch = response.json()["regression_test_patch_proposal"]
        self.assertEqual(patch["status"], "needs_review")
        self.assertEqual(patch["proposal_id"], proposal_id)
        self.assertEqual(patch["approved_review_id"], reviewed.json()["regression_proposal_review"]["id"])
        self.assertEqual(patch["patch_layer"], "decision_rule")
        self.assertFalse(patch["writes_formal_layer"])
        self.assertFalse(patch["test_file_write_allowed"])
        self.assertFalse(patch["canonical_rule_write_allowed"])
        self.assertTrue(patch["requires_human_review"])
        self.assertEqual(patch["next_action"], "human_review_regression_test_patch")
        self.assertEqual(
            patch["artifact_path"],
            "state/product/trace_learning_regression_test_patch_proposals.jsonl",
        )
        self.assertGreaterEqual(len(patch["proposed_test_cases"]), 1)
        first_case = patch["proposed_test_cases"][0]
        self.assertEqual(first_case["source_bad_case_id"], created.json()["bad_case"]["id"])
        self.assertEqual(first_case["target_file"], "tests/test_trace_learning.py")
        self.assertIn("Given", first_case["bdd"])
        self.assertIn("Then", first_case["bdd"])

        patch_path = self.project_root / "state" / "product" / "trace_learning_regression_test_patch_proposals.jsonl"
        self.assertTrue(patch_path.exists())
        saved = json.loads(patch_path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(saved["id"], patch["id"])

    def test_bdd_6f_test_patch_proposal_generation_is_idempotent_for_same_regression_proposal(self) -> None:
        """Given 同一回归建议已生成测试补丁建议；When 再次生成；Then 返回同一条建议而不重复追加。"""
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "user_feedback": "这里把当前题目误判成旧题目。",
                "expected_behavior": "重复点击生成测试补丁建议时不能追加重复记录。",
                "fix_layer": "decision_rule",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        proposed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )
        self.assertEqual(proposed.status_code, 201, msg=proposed.text)
        proposal_id = proposed.json()["regression_proposal"]["id"]
        reviewed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "可以准备测试补丁建议。"},
        )
        self.assertEqual(reviewed.status_code, 201, msg=reviewed.text)

        first = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/test-patch-proposals"
        )
        second = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/test-patch-proposals"
        )

        self.assertEqual(first.status_code, 201, msg=first.text)
        self.assertEqual(second.status_code, 201, msg=second.text)
        self.assertEqual(
            first.json()["regression_test_patch_proposal"]["id"],
            second.json()["regression_test_patch_proposal"]["id"],
        )
        patch_path = self.project_root / "state" / "product" / "trace_learning_regression_test_patch_proposals.jsonl"
        self.assertEqual(len(patch_path.read_text(encoding="utf-8").splitlines()), 1)

    def test_bdd_6g_test_patch_proposal_does_not_mutate_formal_research_states(self) -> None:
        """Given 正式层状态已存在；When 生成测试补丁建议；Then 仍然只写草案层补丁建议账本。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True, exist_ok=True)
        protected_states = {
            "research_question.json": {"question": "父母教育水平对子女工资水平的影响"},
            "variable_roles.json": {"roles": {"outcome": ["wage"], "treatment": ["parent_edu"]}},
            "design_spec.json": {"model": {"estimator": "ols"}},
            "run_plan.json": {"tasks": [{"id": "baseline"}]},
            "supervisor_plan.json": {"status": "approved", "can_dispatch": True},
            "agent_task_queue.json": {"status": "ready_for_dispatch", "tasks": []},
        }
        for name, payload in protected_states.items():
            (state_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "user_feedback": "这里把当前题目误判成旧题目。",
                "expected_behavior": "生成测试补丁建议不能改写正式研究状态。",
                "fix_layer": "decision_rule",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        proposed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )
        self.assertEqual(proposed.status_code, 201, msg=proposed.text)
        proposal_id = proposed.json()["regression_proposal"]["id"]
        reviewed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "可以准备测试补丁建议。"},
        )
        self.assertEqual(reviewed.status_code, 201, msg=reviewed.text)
        before = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/test-patch-proposals"
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        after = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}
        self.assertEqual(before, after)

    def test_bdd_6h_test_patch_proposal_requires_approved_regression_proposal(self) -> None:
        """Given 回归建议尚未批准；When 生成测试补丁建议；Then API 阻止越过人工审阅。"""
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "user_feedback": "这里把当前题目误判成旧题目。",
                "expected_behavior": "生成补丁建议前必须先人工批准回归建议。",
                "fix_layer": "decision_rule",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        proposed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )
        self.assertEqual(proposed.status_code, 201, msg=proposed.text)
        proposal_id = proposed.json()["regression_proposal"]["id"]

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/test-patch-proposals"
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "trace_learning_regression_proposal_approval_required")
        patch_path = self.project_root / "state" / "product" / "trace_learning_regression_test_patch_proposals.jsonl"
        self.assertFalse(patch_path.exists())

    def test_bdd_6i_review_test_patch_proposal_records_human_decision(self) -> None:
        """Given 测试补丁建议已生成；When 人工批准；Then 只追加补丁建议审阅账本。"""
        patch = self._create_reviewable_test_patch_proposal()
        patch_id = patch["id"]

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-test-patch-proposals/{patch_id}/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "确认这个测试补丁建议可以进入人工落地。"},
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        review = response.json()["regression_test_patch_proposal_review"]
        self.assertEqual(review["proposal_id"], patch_id)
        self.assertEqual(review["decision"], "approve")
        self.assertEqual(review["status"], "approved")
        self.assertEqual(review["reviewer"], "mahaoxuan")
        self.assertEqual(review["note"], "确认这个测试补丁建议可以进入人工落地。")
        self.assertEqual(review["next_action"], "human_apply_regression_test_patch")
        self.assertFalse(review["writes_formal_layer"])
        self.assertFalse(review["test_file_write_allowed"])
        self.assertFalse(review["canonical_rule_write_allowed"])
        self.assertEqual(
            review["artifact_path"],
            "state/product/trace_learning_regression_test_patch_proposal_reviews.jsonl",
        )

        review_path = self.project_root / "state" / "product" / "trace_learning_regression_test_patch_proposal_reviews.jsonl"
        self.assertTrue(review_path.exists())
        saved = json.loads(review_path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(saved["id"], review["id"])

    def test_bdd_6j_review_test_patch_proposal_supports_revision_and_rejection(self) -> None:
        """Given 测试补丁建议已生成；When 要求修订或拒绝；Then 审阅状态和下一步清晰写入账本。"""
        patch = self._create_reviewable_test_patch_proposal()
        patch_id = patch["id"]

        cases = [
            ("request_revision", "needs_revision", "revise_regression_test_patch_proposal"),
            ("reject", "rejected", "close_regression_test_patch_proposal"),
        ]
        for decision, expected_status, expected_next_action in cases:
            with self.subTest(decision=decision):
                response = self.client.post(
                    f"/api/v1/projects/{self.project_id}/trace-learning/regression-test-patch-proposals/{patch_id}/review",
                    json={"decision": decision, "reviewer": "mahaoxuan", "note": f"{decision} note"},
                )

                self.assertEqual(response.status_code, 201, msg=response.text)
                review = response.json()["regression_test_patch_proposal_review"]
                self.assertEqual(review["decision"], decision)
                self.assertEqual(review["status"], expected_status)
                self.assertEqual(review["next_action"], expected_next_action)
                self.assertFalse(review["writes_formal_layer"])
                self.assertFalse(review["test_file_write_allowed"])
                self.assertFalse(review["canonical_rule_write_allowed"])

        review_path = self.project_root / "state" / "product" / "trace_learning_regression_test_patch_proposal_reviews.jsonl"
        self.assertEqual(len(review_path.read_text(encoding="utf-8").splitlines()), 2)

    def test_bdd_6k_review_test_patch_proposal_requires_existing_patch_proposal(self) -> None:
        """Given 测试补丁建议不存在；When 试图审阅；Then API 阻止且不创建审阅账本。"""
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-test-patch-proposals/missing/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "missing"},
        )

        self.assertEqual(response.status_code, 409, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "trace_learning_test_patch_proposal_not_found")
        review_path = self.project_root / "state" / "product" / "trace_learning_regression_test_patch_proposal_reviews.jsonl"
        self.assertFalse(review_path.exists())

    def test_bdd_6l_test_patch_proposal_review_does_not_mutate_formal_tests_or_canonical_rules(self) -> None:
        """Given 正式状态、测试文件和规则文件已存在；When 审阅测试补丁建议；Then 只写审阅账本。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True, exist_ok=True)
        protected_states = {
            "research_question.json": {"question": "父母教育水平对子女工资水平的影响"},
            "variable_roles.json": {"roles": {"outcome": ["wage"], "treatment": ["parent_edu"]}},
            "design_spec.json": {"model": {"estimator": "ols"}},
            "run_plan.json": {"tasks": [{"id": "baseline"}]},
            "supervisor_plan.json": {"status": "approved", "can_dispatch": True},
            "agent_task_queue.json": {"status": "ready_for_dispatch", "tasks": []},
            "canonical_rules.json": {"rules": [{"id": "existing_rule"}]},
        }
        for name, payload in protected_states.items():
            (state_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tests_dir = self.repo_root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        test_file = tests_dir / "test_trace_learning.py"
        test_file.write_text("# existing tests stay unchanged\n", encoding="utf-8")
        before_states = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}
        before_test_file = test_file.read_text(encoding="utf-8")
        patch = self._create_reviewable_test_patch_proposal()

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-test-patch-proposals/{patch['id']}/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "只批准进入人工落地。"},
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        after_states = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}
        self.assertEqual(before_states, after_states)
        self.assertEqual(before_test_file, test_file.read_text(encoding="utf-8"))

    def test_bdd_6m_get_regression_proposals_restores_test_patch_proposal_reviews(self) -> None:
        """Given 测试补丁建议已有审阅；When 刷新读取建议；Then 返回补丁建议和最新审阅状态。"""
        patch = self._create_reviewable_test_patch_proposal()
        reviewed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-test-patch-proposals/{patch['id']}/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "批准人工落地。"},
        )
        self.assertEqual(reviewed.status_code, 201, msg=reviewed.text)
        review_id = reviewed.json()["regression_test_patch_proposal_review"]["id"]

        response = self.client.get(f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals")

        self.assertEqual(response.status_code, 200, msg=response.text)
        trace_learning = response.json()["trace_learning"]
        patch_proposals = trace_learning["regression_test_patch_proposals"]
        self.assertEqual(len(patch_proposals), 1)
        self.assertEqual(patch_proposals[0]["id"], patch["id"])
        self.assertEqual(patch_proposals[0]["current_review_status"], "approved")
        self.assertEqual(patch_proposals[0]["latest_review_id"], review_id)
        self.assertEqual(trace_learning["regression_test_patch_proposal_review_count"], 1)
        self.assertEqual(
            trace_learning["regression_test_patch_proposal_review_status_by_proposal_id"][patch["id"]],
            "approved",
        )

    def test_bdd_6n_idempotent_test_patch_generation_returns_review_status(self) -> None:
        """Given 测试补丁建议已审阅；When 再次生成同一建议；Then 返回同一建议及最新审阅状态。"""
        patch = self._create_reviewable_test_patch_proposal()
        reviewed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-test-patch-proposals/{patch['id']}/review",
            json={"decision": "request_revision", "reviewer": "mahaoxuan", "note": "补充边界说明。"},
        )
        self.assertEqual(reviewed.status_code, 201, msg=reviewed.text)
        review_id = reviewed.json()["regression_test_patch_proposal_review"]["id"]

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{patch['proposal_id']}/test-patch-proposals"
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        returned_patch = response.json()["regression_test_patch_proposal"]
        trace_learning = response.json()["trace_learning"]
        self.assertEqual(returned_patch["id"], patch["id"])
        self.assertEqual(returned_patch["current_review_status"], "needs_revision")
        self.assertEqual(returned_patch["latest_review_id"], review_id)
        self.assertEqual(trace_learning["review_count"], 1)
        self.assertEqual(trace_learning["latest_patch_proposal"]["current_review_status"], "needs_revision")

    def test_bdd_7_missing_user_feedback_is_rejected_without_creating_ledger(self) -> None:
        """Given 没有用户反馈正文；When 试图记录；Then API 拒绝且不创建账本。"""
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={"stage": "brief", "fix_layer": "memory"},
        )

        self.assertEqual(response.status_code, 422, msg=response.text)
        ledger_path = self.project_root / "state" / "product" / "trace_learning_bad_cases.jsonl"
        self.assertFalse(ledger_path.exists())

    def test_bdd_8_capture_bad_case_does_not_mutate_formal_research_states(self) -> None:
        """Given 正式层状态已存在；When 记录坏案例；Then 只写改进账本，不改研究设定。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True, exist_ok=True)
        protected_states = {
            "research_question.json": {"question": "父母教育水平对子女工资水平的影响"},
            "variable_roles.json": {"roles": {"outcome": ["wage"], "treatment": ["parent_edu"]}},
            "design_spec.json": {"model": {"estimator": "ols"}},
            "run_plan.json": {"tasks": [{"id": "baseline"}]},
            "supervisor_plan.json": {"status": "approved", "can_dispatch": True},
            "agent_task_queue.json": {"status": "ready_for_dispatch", "tasks": []},
        }
        for name, payload in protected_states.items():
            (state_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        before = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "user_feedback": "这里把当前题目误判成旧题目。",
                "expected_behavior": "进入回归测试，而不是改写正式状态。",
                "fix_layer": "decision_rule",
            },
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        after = {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_states}
        self.assertEqual(before, after)

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: trace-learning\n  title: Trace Learning Project\n"
            "research:\n  question: 父母教育水平对子女工资水平的影响\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,parent_edu,age,gender\n10,12,25,0\n12,16,28,1\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")

    def _create_reviewable_test_patch_proposal(self) -> dict:
        created = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={
                "stage": "brief",
                "surface": "web_react",
                "target_text": "分析研究问题",
                "agent_output": "错误套用了旧题目。",
                "user_feedback": "这个推断和我的题目一点关系都没有。",
                "expected_behavior": "系统必须围绕当前题目重做语义判断。",
                "fix_layer": "decision_rule",
                "severity": "high",
            },
        )
        self.assertEqual(created.status_code, 201, msg=created.text)
        proposed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals"
        )
        self.assertEqual(proposed.status_code, 201, msg=proposed.text)
        proposal_id = proposed.json()["regression_proposal"]["id"]
        reviewed = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/review",
            json={"decision": "approve", "reviewer": "mahaoxuan", "note": "可以准备测试补丁建议。"},
        )
        self.assertEqual(reviewed.status_code, 201, msg=reviewed.text)
        patch_response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/regression-proposals/{proposal_id}/test-patch-proposals"
        )
        self.assertEqual(patch_response.status_code, 201, msg=patch_response.text)
        return patch_response.json()["regression_test_patch_proposal"]


class TraceLearningFrontendContractTests(unittest.TestCase):
    """BDD: 任务队列页必须给用户一个显式入口，把发现的问题写入 Trace Learning。"""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.agent_task_queue = (
            root / "Product" / "web-react" / "src" / "components" / "AgentTaskQueuePanel.tsx"
        ).read_text(encoding="utf-8")

    def test_bdd_5_agent_queue_exposes_trace_learning_feedback_entry(self) -> None:
        """Given 用户在队列页发现问题；When 要反馈；Then 页面提供记录坏案例入口。"""
        self.assertIn("trace-learning-feedback", self.agent_task_queue)
        self.assertIn("trace-learning-capture", self.agent_task_queue)
        self.assertIn("/trace-learning/bad-cases", self.agent_task_queue)
        self.assertIn("写入改进账本", self.agent_task_queue)
        self.assertIn("不会改写正式研究状态", self.agent_task_queue)

    def test_bdd_6_agent_queue_exposes_regression_proposal_entry(self) -> None:
        """Given 坏案例已进入账本；When 用户要推进改进；Then 页面提供生成回归建议入口。"""
        self.assertIn("trace-learning-regression-proposal", self.agent_task_queue)
        self.assertIn("/trace-learning/regression-proposals", self.agent_task_queue)
        self.assertIn("生成回归建议", self.agent_task_queue)
        self.assertIn("等待人工审阅", self.agent_task_queue)
        self.assertLess(
            self.agent_task_queue.find("trace-learning-feedback__actions"),
            self.agent_task_queue.find("trace-learning-regression-proposal"),
        )

    def test_bdd_7_agent_queue_exposes_regression_proposal_review_boundary(self) -> None:
        """Given 回归建议等待人工处理；When 用户查看队列页；Then 页面说明审阅不会自动写测试或规则。"""
        self.assertIn("trace-learning-regression-proposal-review", self.agent_task_queue)
        self.assertIn("/trace-learning/regression-proposals/${", self.agent_task_queue)
        self.assertIn("/review", self.agent_task_queue)
        self.assertIn("审阅回归建议", self.agent_task_queue)
        self.assertIn("不会自动写测试文件", self.agent_task_queue)

    def test_bdd_8_agent_queue_restores_existing_reviewable_proposal(self) -> None:
        """Given 已有待审阅回归建议；When 用户刷新队列页；Then 页面从后端恢复可审阅建议。"""
        self.assertIn("loadTraceLearningRegressionProposals", self.agent_task_queue)
        self.assertIn('method: "GET"', self.agent_task_queue)
        self.assertIn("/trace-learning/regression-proposals", self.agent_task_queue)
        self.assertIn('current_review_status === "needs_review"', self.agent_task_queue)
        self.assertIn("setLatestTraceProposalId", self.agent_task_queue)
        self.assertIn("void loadTraceLearningRegressionProposals();", self.agent_task_queue)
        self.assertIn("current_review_status", self.agent_task_queue)
        self.assertIn("已有待审阅回归建议", self.agent_task_queue)

    def test_bdd_9_agent_queue_exposes_test_patch_proposal_after_review(self) -> None:
        """Given 回归建议已审阅通过；When 用户查看队列页；Then 页面提供生成测试补丁建议入口。"""
        self.assertIn("trace-learning-test-patch-proposal", self.agent_task_queue)
        self.assertIn("/test-patch-proposals", self.agent_task_queue)
        self.assertIn("生成测试补丁建议", self.agent_task_queue)
        self.assertIn("回归建议批准后，才会生成测试补丁建议", self.agent_task_queue)
        self.assertLess(
            self.agent_task_queue.find("trace-learning-regression-proposal-review"),
            self.agent_task_queue.find("trace-learning-test-patch-proposal"),
        )

    def test_bdd_10_agent_queue_exposes_test_patch_proposal_review_gate(self) -> None:
        """Given 测试补丁建议已生成；When 用户查看队列页；Then 页面提供人工审阅门且声明不会自动写入。"""
        self.assertIn("regression_test_patch_proposals", self.agent_task_queue)
        self.assertIn("isReviewableTraceLearningTestPatchProposal", self.agent_task_queue)
        self.assertIn("isReviewedTraceLearningTestPatchProposal", self.agent_task_queue)
        self.assertIn("reviewablePatchProposal", self.agent_task_queue)
        self.assertIn("reviewedPatchProposal", self.agent_task_queue)
        self.assertIn("rememberLatestTracePatchProposalId(reviewablePatchProposal?.id ?? null)", self.agent_task_queue)
        self.assertIn("isReviewableTraceLearningTestPatchProposal(patchProposal)", self.agent_task_queue)
        self.assertIn("isReviewedTraceLearningTestPatchProposal(patchProposal)", self.agent_task_queue)
        self.assertIn("测试补丁建议未进入待审阅状态，请刷新队列后重试。", self.agent_task_queue)
        self.assertNotIn("regression_test_patch_proposals?.find((proposal) => Boolean(proposal.id))", self.agent_task_queue)
        self.assertNotIn(
            "const patchProposalId = data.regression_test_patch_proposal?.id ?? null;\n"
            "      rememberLatestTracePatchProposalId(patchProposalId);",
            self.agent_task_queue,
        )
        self.assertIn("trace-learning-test-patch-proposal-review", self.agent_task_queue)
        self.assertIn("测试补丁建议审阅决定", self.agent_task_queue)
        self.assertIn("/trace-learning/regression-test-patch-proposals/${", self.agent_task_queue)
        self.assertIn("/review", self.agent_task_queue)
        self.assertIn("审阅测试补丁建议", self.agent_task_queue)
        self.assertIn("latestTracePatchProposalId", self.agent_task_queue)
        self.assertIn("已记录测试补丁建议审阅", self.agent_task_queue)
        self.assertIn("测试补丁建议已有审阅状态", self.agent_task_queue)
        self.assertIn("测试补丁建议不在后端返回结果中，请重新生成或刷新队列。", self.agent_task_queue)
        self.assertIn("测试补丁建议不存在，请重新生成或刷新队列。", self.agent_task_queue)
        self.assertIn("不会自动写测试文件", self.agent_task_queue)
        self.assertIn("不会改正式论文", self.agent_task_queue)
        self.assertIn("canonical 规则库", self.agent_task_queue)


if __name__ == "__main__":
    unittest.main()
