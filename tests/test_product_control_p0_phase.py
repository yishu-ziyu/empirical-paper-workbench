from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.product_control_phase_service import run_product_control_p0_phase
from Product.backend.registry import ensure_registry


class ProductControlP0PhaseTests(unittest.TestCase):
    """BDD: P0-A/B/C/D should run as one topic-bound phase package."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="p0-phase-"))
        self.project_root = self.tmp / "project"
        self._create_project(
            topic="数字普惠金融对家庭创业的影响",
            slug="digital-finance-entrepreneurship",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p0_phase_generates_topic_bound_queue_audit_and_portfolio_package(self) -> None:
        """行为 1-4：P0 阶段连续生成 Queue、Evidence Audit 和作品集包。"""
        report = run_product_control_p0_phase(self.project_root)

        self.assertEqual(report["status"], "p0_phase_ready_for_review")
        self.assertEqual(report["topic_binding"]["expected_topic"], "数字普惠金融对家庭创业的影响")

        queue = json.loads((self.project_root / "state/product/agent_task_queue.json").read_text(encoding="utf-8"))
        self.assertEqual(queue["summary"]["total_tasks"], 6)
        self.assertEqual(queue["source_supervisor_plan"]["research_question"], "数字普惠金融对家庭创业的影响")
        self.assertEqual(
            [task["role"] for task in queue["tasks"]],
            [
                "ResearchBriefAgent",
                "DataAgent",
                "VariableAgent",
                "MethodAgent",
                "ExecutionAgent",
                "EvidenceAuditAgent",
            ],
        )
        self.assertTrue(all(task["can_execute"] is False for task in queue["tasks"]))
        self.assertTrue(all(task["next_action"] == "dispatch_review_required" for task in queue["tasks"]))

        evidence = json.loads(
            (self.project_root / "Results/json/product_control_demo_evidence_audit.json").read_text(encoding="utf-8")
        )
        self.assertEqual(evidence["status"], "p0_evidence_audit_ready")
        check_ids = {check["id"] for check in evidence["checks"]}
        self.assertIn("topic_binding_audit", check_ids)
        self.assertIn("agent_task_queue", check_ids)
        self.assertIn("real_literature_candidates", check_ids)
        self.assertIn("dataset_variable_binding", check_ids)
        self.assertIn("formal_boundary", check_ids)

        portfolio_script = self.project_root / "docs/product-control/07_作品集Demo脚本.md"
        self.assertTrue(portfolio_script.exists())
        script_text = portfolio_script.read_text(encoding="utf-8")
        self.assertIn("数字普惠金融对家庭创业的影响", script_text)
        self.assertIn("```mermaid", script_text)
        self.assertIn("ResearchBriefAgent", script_text)
        self.assertIn("EvidenceAuditAgent", script_text)

    def test_bdd_p0_phase_api_runs_registered_project_package(self) -> None:
        """行为 5：产品 API 必须能按 project_id 触发完整 P0 阶段包。"""
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
                    "slug": "digital-finance-entrepreneurship",
                    "title": "Digital Finance Entrepreneurship",
                    "project_root": str(self.project_root),
                    "language": "zh",
                },
            )
            self.assertEqual(response.status_code, 201, msg=response.text)
            project_id = response.json()["id"]

            p0_response = client.post(f"/api/v1/projects/{project_id}/product-control/p0-phase")

            self.assertEqual(p0_response.status_code, 201, msg=p0_response.text)
            body = p0_response.json()
            self.assertEqual(body["status"], "p0_phase_ready_for_review")
            self.assertEqual(body["project"]["id"], project_id)
            self.assertEqual(body["topic_binding"]["expected_topic"], "数字普惠金融对家庭创业的影响")
            self.assertEqual(body["summary"]["task_count"], 6)
            self.assertTrue((self.project_root / "docs/product-control/07_作品集Demo脚本.md").exists())
        finally:
            product_app.PRODUCT_ROOT = original_product_root
            product_app.REPO_ROOT = original_repo_root

    def _create_project(self, topic: str, slug: str) -> None:
        self._write_text("paper.yaml", f"research:\n  question: {topic}\n")
        self._write_text("Program/run_paper.py", "print('ok')\n")
        self._write_json(
            "state/product/topic_binding.json",
            {
                "expected_topic": topic,
                "expected_slug": slug,
                "binding_type": "demo_acceptance_line",
            },
        )
        self._write_json(
            "state/product/research_question.json",
            {
                "id": "research_question",
                "status": "confirmed",
                "question": topic,
                "version": 1,
            },
        )
        self._write_text(f"Tasks/{slug}/brief.md", f"# {topic}\n\n当前项目任务书。\n")
        self._write_text(
            f"Tasks/{slug}/literature.md",
            "# Literature\n\n当前等待真实文献检索。\n",
        )
        self._write_text(
            f"Tasks/{slug}/variables.yaml",
            f"topic_slug: {slug}\nvariables:\n  - treatment\n  - outcome\n",
        )
        self._write_json(f"Tasks/{slug}/design.json", {"topic": topic, "method": "to_be_reviewed"})

    def _write_text(self, relative_path: str, content: str) -> None:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_json(self, relative_path: str, payload: dict) -> None:
        self._write_text(relative_path, json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
