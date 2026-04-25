import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")


class MultiAgentOrchestrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="econ-orchestrator-test-"))
        self.project_root = self.temp_dir / "project"
        shutil.copytree(REPO_ROOT, self.project_root, dirs_exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_handoff_packet_uses_spec_fields(self) -> None:
        from Product.backend.orchestration_schema import HandoffPacket

        packet = HandoffPacket(
            run_id="run_test",
            agent="LiteratureAgent",
            stage="02_literature",
            inputs=["01_sources/literature_inventory.json"],
            outputs=["02_literature/core_literature_brief.md"],
            claims=["Core literature supports robot labor-market reallocation framing."],
            risks=["Strict matching efficiency is not directly identified."],
            next_agent="ResearchStrategistAgent",
            status="completed",
        )

        payload = packet.to_dict()
        self.assertEqual(payload["agent"], "LiteratureAgent")
        self.assertEqual(payload["next_agent"], "ResearchStrategistAgent")
        self.assertIn("risks", payload)

    def test_orchestration_creates_full_agent_handoffs_and_review_loop(self) -> None:
        from Product.backend.orchestrator import orchestrate_project

        result = orchestrate_project(self.project_root, run_live=False)

        run_dir = Path(result["run_root"])
        manifest_path = run_dir / "run_manifest.json"
        self.assertTrue(manifest_path.exists())

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["supervisor"]["status"], "completed")
        self.assertEqual(
            [agent["name"] for agent in manifest["agents"]],
            [
                "PreparationAgent",
                "LiteratureAgent",
                "ResearchStrategistAgent",
                "ModelingAgent",
                "VisualizationAgent",
                "WritingAgent",
                "ReviewerAgent",
                "FormatterAgent",
            ],
        )
        self.assertEqual(manifest["review_loop"]["status"], "completed")
        self.assertTrue((run_dir / "00_intake" / "preparation_handoff.json").exists())
        self.assertTrue((run_dir / "02_literature" / "literature_handoff.json").exists())
        self.assertTrue((run_dir / "06_writing" / "writing_handoff.json").exists())
        self.assertTrue((run_dir / "07_review" / "reviewer_decision.json").exists())

    def test_review_loop_creates_draft_and_reviewer_decision(self) -> None:
        from Product.backend.orchestrator import orchestrate_project

        result = orchestrate_project(self.project_root, run_live=False)

        run_dir = Path(result["run_root"])
        draft = run_dir / "06_writing" / "paper_draft.md"
        reviewer_packet = run_dir / "07_review" / "reviewer_decision.json"

        self.assertTrue(draft.exists())
        self.assertTrue(reviewer_packet.exists())

        review = json.loads(reviewer_packet.read_text(encoding="utf-8"))
        self.assertIn("revision_requests", review)
        self.assertGreaterEqual(len(review["revision_requests"]), 1)
        self.assertNotEqual(review["reviewer"], "WritingAgent")
        self.assertIn("matching-efficiency boundary", draft.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

