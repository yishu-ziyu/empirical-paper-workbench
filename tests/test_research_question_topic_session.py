from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ResearchQuestionTopicSessionTests(unittest.TestCase):
    """BDD: 首页确认的研究选题必须成为后端可审计 TopicSession。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="research-question-"))
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
                "slug": "research-question",
                "title": "Research Question Project",
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

    def test_bdd_1_get_current_question_uses_project_seed_without_persisting(self) -> None:
        """行为 1：没有人工确认时，API 返回 project seed 草稿但不创建状态文件。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/research-question/current")

        self.assertEqual(response.status_code, 200, msg=response.text)
        question = response.json()["research_question"]
        self.assertEqual(question["status"], "draft_from_project")
        self.assertEqual(question["question"], "培训是否影响工资？")
        self.assertEqual(question["evidence_level"], "local_file")
        self.assertEqual(question["source"], "project_seed")
        self.assertEqual(question["path"], "state/product/research_question.json")
        self.assertFalse(question["exists"])
        self.assertFalse((self.project_root / "state" / "product" / "research_question.json").exists())

    def test_bdd_2_confirm_question_persists_topic_session(self) -> None:
        """行为 2：确认选题后，系统写入可跨 Session 恢复的 ResearchQuestion 状态。"""
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/research-question/current",
            json={
                "question": "机器人应用是否影响劳动力市场匹配效率？",
                "source": "user_input",
                "note": "首页输入后确认。",
            },
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        question = response.json()["research_question"]
        self.assertEqual(question["status"], "confirmed")
        self.assertEqual(question["question"], "机器人应用是否影响劳动力市场匹配效率？")
        self.assertEqual(question["version"], 1)
        self.assertEqual(question["evidence_level"], "local_file")
        self.assertEqual(question["source"], "user_input")
        self.assertEqual(question["decision_events"][0]["action"], "confirm_research_question")

        saved_path = self.project_root / "state" / "product" / "research_question.json"
        self.assertTrue(saved_path.exists())
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["question"], "机器人应用是否影响劳动力市场匹配效率？")

        get_response = self.client.get(f"/api/v1/projects/{self.project_id}/research-question/current")
        self.assertEqual(get_response.status_code, 200, msg=get_response.text)
        self.assertEqual(get_response.json()["research_question"]["question"], question["question"])

    def test_bdd_3_confirm_question_does_not_mutate_formal_research_states(self) -> None:
        """行为 3：保存选题不能自动创建或改写变量角色、研究设计和执行计划。"""
        protected_paths = [
            self.project_root / "state" / "product" / "variable_roles.json",
            self.project_root / "state" / "product" / "design_spec.json",
            self.project_root / "state" / "product" / "run_plan.json",
        ]
        before = {path.name: path.read_text(encoding="utf-8") if path.exists() else None for path in protected_paths}

        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/research-question/current",
            json={"question": "培训是否影响工资？", "source": "project_seed", "note": "沿用已有选题。"},
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        after = {path.name: path.read_text(encoding="utf-8") if path.exists() else None for path in protected_paths}
        self.assertEqual(before, after)

    def test_bdd_4_empty_question_is_rejected(self) -> None:
        """行为 4：空选题不能进入正式 TopicSession。"""
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/research-question/current",
            json={"question": "   ", "source": "user_input", "note": "空输入"},
        )

        self.assertEqual(response.status_code, 400, msg=response.text)
        self.assertEqual(response.json()["error"]["code"], "invalid_research_question")

    def test_bdd_5_overview_exposes_confirmed_research_question_state(self) -> None:
        """行为 5：overview 必须暴露已确认 ResearchQuestion，供后续状态机绑定。"""
        save_response = self.client.put(
            f"/api/v1/projects/{self.project_id}/research-question/current",
            json={"question": "培训是否影响工资？", "source": "project_seed", "note": "确认已有选题。"},
        )
        self.assertEqual(save_response.status_code, 200, msg=save_response.text)

        response = self.client.get(f"/api/v1/projects/{self.project_id}/overview")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["research_question"], "培训是否影响工资？")
        self.assertEqual(body["research_question_state"]["status"], "confirmed")
        stages = {stage["id"]: stage for stage in body["workflow_contract"]["canonical_stages"]}
        self.assertEqual(stages["research_question"]["status"], "completed")

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: research-question\n  title: Research Question Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
