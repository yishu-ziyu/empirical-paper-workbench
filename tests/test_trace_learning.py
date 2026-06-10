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

    def test_bdd_3_missing_user_feedback_is_rejected_without_creating_ledger(self) -> None:
        """Given 没有用户反馈正文；When 试图记录；Then API 拒绝且不创建账本。"""
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/trace-learning/bad-cases",
            json={"stage": "brief", "fix_layer": "memory"},
        )

        self.assertEqual(response.status_code, 422, msg=response.text)
        ledger_path = self.project_root / "state" / "product" / "trace_learning_bad_cases.jsonl"
        self.assertFalse(ledger_path.exists())

    def test_bdd_4_capture_bad_case_does_not_mutate_formal_research_states(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
