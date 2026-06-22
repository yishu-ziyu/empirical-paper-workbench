from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.product_control_demo_audit_service import (
    EXPECTED_DEMO_SLUG,
    EXPECTED_DEMO_TOPIC,
    run_product_control_demo_topic_binding_audit,
)
from Product.backend.registry import ensure_registry


class ProductControlDemoTopicBindingAuditTests(unittest.TestCase):
    """BDD: P0-A must block stale topic state before Agent Queue work continues."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="p0a-topic-binding-"))
        self.project_root = self.tmp / "project"
        self._create_minimal_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p0a_blocks_old_runtime_state_and_current_material_contamination(self) -> None:
        """行为 2-4：旧运行态和当前材料污染必须阻断进入 P0-B。"""
        self._write_json(
            "state/product/research_question.json",
            {
                "status": "confirmed",
                "question": "工业机器人应用对劳动力市场匹配效率的影响",
            },
        )
        self._write_json(
            "state/product/supervisor_plan.json",
            {
                "status": "approved",
                "research_question": "effect of trained on wage",
            },
        )
        self._write_json(
            "state/product/agent_task_queue.json",
            {
                "status": "ready_for_dispatch",
                "source_supervisor_plan": {"research_question": "effect of trained on wage"},
            },
        )
        self._write_text(
            "Tasks/parent-education-wage/literature.md",
            "# Literature\n\nIndustrial Robots and Labor Markets stub for parental education.\n",
        )
        self._write_text(
            "Tasks/parent-education-wage/variables.yaml",
            "topic: '---'\nvariables:\n  - year_robot\n  - robot_density\n  - ln_robot\n",
        )

        report = run_product_control_demo_topic_binding_audit(self.project_root, persist=True)

        self.assertEqual(report["expected_topic"], EXPECTED_DEMO_TOPIC)
        self.assertEqual(report["expected_slug"], EXPECTED_DEMO_SLUG)
        self.assertEqual(report["status"], "blocked_by_topic_contamination")
        self.assertFalse(report["can_proceed_to_p0b"])
        issue_ids = {issue["id"] for issue in report["critical_issues"]}
        self.assertIn("research_question_mismatch", issue_ids)
        self.assertIn("supervisor_plan_stale_topic", issue_ids)
        self.assertIn("agent_task_queue_stale_topic", issue_ids)
        self.assertIn("topic_literature_contamination", issue_ids)
        self.assertIn("topic_variables_contamination", issue_ids)

        self.assertTrue((self.project_root / "Results/json/product_control_demo_topic_binding_audit.json").exists())
        review = self.project_root / "Reviews/product_control_demo_topic_binding_audit.md"
        self.assertTrue(review.exists())
        self.assertIn("blocked_by_topic_contamination", review.read_text(encoding="utf-8"))

    def test_bdd_p0a_passes_clean_current_surfaces_and_allows_historical_references(self) -> None:
        """行为 5：历史记录可以含旧题，干净的当前 surface 不能被误阻断。"""
        self._write_clean_runtime_state()
        self._write_text(
            "Tasks/current-stage.md",
            "历史快照：工业机器人、CHARLS DID 和 CGSS 都是旧阶段记录，不是当前产品绑定。\n",
        )

        report = run_product_control_demo_topic_binding_audit(self.project_root, persist=False)

        self.assertEqual(report["status"], "ready_for_p0b")
        self.assertTrue(report["can_proceed_to_p0b"])
        self.assertEqual(report["critical_issues"], [])
        scanned_paths = {surface["path"] for surface in report["surfaces"]}
        self.assertNotIn("Tasks/current-stage.md", scanned_paths)

    def test_bdd_p0a_does_not_mutate_existing_runtime_state(self) -> None:
        """行为 2：审计只暴露污染，不静默改写旧 ResearchQuestion。"""
        original = json.dumps(
            {
                "status": "confirmed",
                "question": "工业机器人应用对劳动力市场匹配效率的影响",
            },
            ensure_ascii=False,
            indent=2,
        )
        path = self.project_root / "state/product/research_question.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(original, encoding="utf-8")

        report = run_product_control_demo_topic_binding_audit(self.project_root, persist=True)

        self.assertEqual(report["status"], "blocked_by_topic_contamination")
        self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_bdd_p0a_api_returns_persisted_audit_for_registered_project(self) -> None:
        """行为 6：产品 API 必须能返回同一份可复用审计结果。"""
        original_product_root = product_app.PRODUCT_ROOT
        original_repo_root = product_app.REPO_ROOT
        repo_root = self.tmp / "repo"
        product_root = repo_root / "Product"
        product_root.mkdir(parents=True)
        ensure_registry(product_root, repo_root)
        product_app.PRODUCT_ROOT = product_root
        product_app.REPO_ROOT = repo_root
        try:
            client = TestClient(product_app.app)
            response = client.post(
                "/api/v1/projects",
                json={
                    "slug": "parent-education-wage",
                    "title": "Parent Education Wage",
                    "project_root": str(self.project_root),
                    "language": "zh",
                },
            )
            self.assertEqual(response.status_code, 201, msg=response.text)
            project_id = response.json()["id"]

            audit_response = client.get(
                f"/api/v1/projects/{project_id}/topic-binding-audit"
            )

            self.assertEqual(audit_response.status_code, 200, msg=audit_response.text)
            body = audit_response.json()
            self.assertEqual(body["expected_topic"], EXPECTED_DEMO_TOPIC)
            self.assertIn(body["status"], {"ready_for_p0b", "blocked_by_topic_contamination"})
            self.assertTrue((self.project_root / "Results/json/product_control_demo_topic_binding_audit.json").exists())
        finally:
            product_app.PRODUCT_ROOT = original_product_root
            product_app.REPO_ROOT = original_repo_root

    def test_bdd_p0a_uses_project_topic_binding_instead_of_hardcoded_demo_topic(self) -> None:
        """行为 7：P0-A 是项目 topic binding 审计，不是父母教育题目的硬编码。"""
        custom_topic = "数字普惠金融对家庭创业的影响"
        custom_slug = "digital-finance-entrepreneurship"
        shutil.rmtree(self.project_root / "Tasks" / "parent-education-wage")
        self._write_json(
            "state/product/topic_binding.json",
            {
                "expected_topic": custom_topic,
                "expected_slug": custom_slug,
                "binding_type": "project_topic_binding",
            },
        )
        self._write_json(
            "state/product/research_question.json",
            {"status": "confirmed", "question": custom_topic},
        )
        self._write_text(
            f"Tasks/{custom_slug}/brief.md",
            f"# {custom_topic}\n\n当前项目 topic binding。\n",
        )
        self._write_text(
            f"Tasks/{custom_slug}/literature.md",
            "# Literature\n\nDigital finance and household entrepreneurship.\n",
        )
        self._write_text(
            f"Tasks/{custom_slug}/variables.yaml",
            "topic_slug: digital-finance-entrepreneurship\nvariables:\n  - digital_finance\n  - entrepreneurship\n",
        )
        self._write_json(
            f"Tasks/{custom_slug}/design.json",
            {"topic": custom_topic, "treatment": "digital_finance", "outcome": "entrepreneurship"},
        )

        report = run_product_control_demo_topic_binding_audit(self.project_root, persist=False)

        self.assertEqual(report["status"], "ready_for_p0b")
        self.assertEqual(report["expected_topic"], custom_topic)
        self.assertEqual(report["expected_slug"], custom_slug)
        self.assertEqual(report["topic_binding"]["source"], "state/product/topic_binding.json")
        scanned_paths = {surface["path"] for surface in report["surfaces"]}
        self.assertIn(f"Tasks/{custom_slug}/brief.md", scanned_paths)
        self.assertNotIn("Tasks/parent-education-wage/brief.md", scanned_paths)

    def _create_minimal_project(self, project_root: Path) -> None:
        self._write_text("paper.yaml", "project:\n  slug: parent-education-wage\n")
        self._write_text("Program/run_paper.py", "print('ok')\n")
        self._write_json(
            "state/product/topic_binding.json",
            {
                "expected_topic": EXPECTED_DEMO_TOPIC,
                "expected_slug": EXPECTED_DEMO_SLUG,
                "binding_type": "demo_acceptance_line",
            },
        )
        self._write_text(
            "Tasks/parent-education-wage/brief.md",
            "# 父母受教育水平对子女工资收入的影响\n\n当前产品控制 demo 题目。\n",
        )
        self._write_text(
            "Tasks/parent-education-wage/literature.md",
            "# Literature\n\nParent education and intergenerational wage transmission.\n",
        )
        self._write_text(
            "Tasks/parent-education-wage/variables.yaml",
            "topic: parent-education-wage\nvariables:\n  - parent_education\n  - child_wage\n",
        )
        self._write_json(
            "Tasks/parent-education-wage/design.json",
            {"topic": EXPECTED_DEMO_TOPIC, "outcome": "child_wage", "treatment": "parent_education"},
        )

    def _write_clean_runtime_state(self) -> None:
        self._write_json(
            "state/product/research_question.json",
            {"status": "confirmed", "question": EXPECTED_DEMO_TOPIC},
        )
        self._write_json(
            "state/product/supervisor_plan.json",
            {"status": "approved", "research_question": EXPECTED_DEMO_TOPIC},
        )
        self._write_json(
            "state/product/agent_task_queue.json",
            {"status": "ready_for_dispatch", "source_supervisor_plan": {"research_question": EXPECTED_DEMO_TOPIC}},
        )

    def _write_text(self, relative_path: str, content: str) -> None:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_json(self, relative_path: str, payload: dict) -> None:
        self._write_text(relative_path, json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
