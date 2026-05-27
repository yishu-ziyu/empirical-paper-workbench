import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class TopicToPaperCapabilityAuditCliTests(unittest.TestCase):
    """BDD: the workbench must state what is truly reproducible from a topic."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="topic-to-paper-audit-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_48_ready_formal_package_still_reports_remaining_topic_to_paper_gaps(self) -> None:
        result = self._run_cli("工业机器人对于劳动力市场匹配效率的影响")
        self.assertEqual(result.returncode, 0, result.stderr)

        report = self._read_report()
        self.assertEqual(report["schema_version"], "p6.topic_to_paper_capability_audit.v1")
        self.assertEqual(report["research_topic"], "工业机器人对于劳动力市场匹配效率的影响")
        self.assertEqual(report["status"], "ready_for_human_review_reproduction")
        self.assertEqual(report["current_topic_reproducibility"], "reproducible_with_existing_pipeline_and_human_review")
        self.assertEqual(report["general_topic_automation"], "not_yet_general_auto_paper_generation")

        gates = report["gates"]
        self.assertEqual(gates["formal_package"]["status"], "ready")
        self.assertEqual(gates["manual_acceptance"]["status"], "pending_human_review")
        self.assertEqual(gates["paper_structure_length"]["status"], "needs_work")
        self.assertEqual(gates["literature_review"]["status"], "needs_human_review")
        self.assertEqual(gates["method_gate"]["status"], "needs_human_review")
        self.assertEqual(gates["reviewer_revision_loop"]["status"], "ready_for_human_review")
        self.assertEqual(gates["final_artifacts"]["status"], "ready")

        self.assertIn("Submissions/formal_package/paper.pdf", report["review_targets"])
        self.assertIn("Submissions/formal_package/paper.docx", report["review_targets"])
        self.assertIn("expand_underdeveloped_sections", report["next_tasks"])
        self.assertIn("run_cnki_manual_search", report["next_tasks"])
        self.assertIn("run_weak_iv_robust_inference", report["next_tasks"])
        self.assertFalse(report["boundary_flags"]["this_command_generated_new_paper"])
        self.assertFalse(report["boundary_flags"]["this_command_modified_formal_package"])
        self.assertFalse(report["boundary_flags"]["this_command_accepted_package"])

        review = (self.project_root / "Reviews" / "topic_to_paper_capability_audit.md").read_text(encoding="utf-8")
        self.assertIn("当前题目可以复现到正式包，但仍需要人工审阅", review)
        self.assertIn("任意新题目全自动成文：尚未成立", review)

    def test_bdd_48_blocks_when_formal_package_is_not_ready(self) -> None:
        summary_path = self.project_root / "state" / "product" / "formal_submission_package_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["status"] = "blocked_by_package_artifacts"
        summary["ready_for_manual_acceptance"] = False
        summary["blocking_reasons"] = ["paper_pdf_missing"]
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli("一个还没有跑通的题目")
        self.assertEqual(result.returncode, 2, result.stderr)
        report = self._read_report()

        self.assertEqual(report["status"], "blocked_before_paper_package_review")
        self.assertEqual(report["gates"]["formal_package"]["status"], "blocked")
        self.assertIn("paper_pdf_missing", report["blocking_reasons"])
        self.assertEqual(report["current_topic_reproducibility"], "not_reproducible_until_formal_package_ready")

    def test_bdd_49_new_cgss_topic_outputs_plain_language_gap_matrix(self) -> None:
        self._write_json(
            self.project_root / "state" / "product" / "research_question.json",
            {
                "question": "工业机器人应用对劳动力市场匹配效率的影响",
                "status": "confirmed",
            },
        )

        result = self._run_cli("社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析")
        self.assertEqual(result.returncode, 3, result.stderr)

        report = self._read_report()
        self.assertEqual(report["status"], "new_topic_requires_data_binding")
        self.assertEqual(report["paper_package_acceptance_target"]["level"], "master_thesis_or_course_paper_first_draft_pdf_package")
        self.assertIn("先把题目、数据、变量、方法、文献和修订链路接起来", report["plain_language_summary"])

        matrix = report["capability_gap_matrix"]
        self.assertEqual(
            [item["id"] for item in matrix],
            [
                "topic_to_data_binding",
                "expert_variable_role_selection",
                "method_family_gate",
                "literature_review_loop",
                "review_revision_and_export_loop",
            ],
        )
        self.assertEqual(matrix[0]["owner_agent"], "DataAgent")
        self.assertEqual(matrix[0]["status"], "needs_work")
        self.assertIn("CGSS", matrix[0]["current_state"])
        self.assertEqual(matrix[1]["owner_agent"], "Supervisor+MethodAgent")
        self.assertEqual(matrix[2]["owner_agent"], "MethodAgent")
        self.assertEqual(matrix[3]["owner_agent"], "LiteratureAgent")
        self.assertEqual(matrix[4]["owner_agent"], "ReviewerAgent+ExportAgent")
        self.assertTrue(all(item["done_when"] for item in matrix))

        routing = report["agent_team_routing"]
        self.assertEqual(routing["first_agent_to_call"], "DataAgent")
        self.assertIn("run_cgss_data_discovery", routing["next_cli_nodes"])
        self.assertIn("bind_topic_to_cgss_dataset", report["next_tasks"])
        self.assertIn("run_cgss_data_discovery", report["next_tasks"])
        self.assertNotIn("run_weak_iv_robust_inference", report["next_tasks"])

        review = (self.project_root / "Reviews" / "topic_to_paper_capability_audit.md").read_text(encoding="utf-8")
        self.assertIn("先追求：硕士课程论文/毕业论文初稿级完整 PDF 包", review)
        self.assertIn("DataAgent：把 CGSS 数据、字段和样本口径接到题目", review)
        self.assertIn("这不是不能写文章，而是还没有把 CGSS 新题目接入主链路", review)

    def _run_cli(self, topic: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "topic_to_paper_capability_audit.py"),
                "--project-root",
                str(self.project_root),
                "--topic",
                topic,
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def _read_report(self) -> dict:
        return json.loads(
            (self.project_root / "Results" / "json" / "topic_to_paper_capability_audit.json").read_text(
                encoding="utf-8"
            )
        )

    def _seed_project(self, root: Path) -> None:
        for directory in [
            root / "Results" / "json",
            root / "state" / "product",
            root / "Reviews",
            root / "Submissions" / "formal_package",
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        self._write_json(
            root / "state" / "product" / "formal_submission_package_summary.json",
            {
                "schema_version": "p6.formal_submission_package_summary.v1",
                "status": "ready_for_manual_acceptance",
                "ready_for_manual_acceptance": True,
                "blocking_reasons": [],
                "artifacts": {
                    "paper_pdf": {"path": "Submissions/formal_package/paper.pdf", "exists": True, "bytes": 100},
                    "paper_docx": {"path": "Submissions/formal_package/paper.docx", "exists": True, "bytes": 50},
                },
                "open_targets": [
                    {"id": "paper_pdf", "path": "Submissions/formal_package/paper.pdf"},
                    {"id": "paper_docx", "path": "Submissions/formal_package/paper.docx"},
                ],
            },
        )
        self._write_json(
            root / "state" / "product" / "formal_submission_package_manual_acceptance.json",
            {
                "schema_version": "p6.formal_submission_package_manual_acceptance.v1",
                "status": "pending_human_manual_acceptance",
                "decision": "defer",
                "accepted": False,
                "blocking_reasons": [],
            },
        )
        self._write_json(
            root / "Results" / "json" / "paper_quality_report.json",
            {
                "schema_version": "p4.paper_quality.v1",
                "verdict": ["too_thin", "section_length_gate_required"],
                "word_count": {"main_text_words": 162},
                "recommended_next_tasks": [
                    {"id": "expand_underdeveloped_sections"},
                    {"id": "expand_working_paper_sections"},
                ],
            },
        )
        self._write_json(
            root / "Results" / "json" / "literature_package_report.json",
            {
                "schema_version": "p4.literature_package.v1",
                "status": "needs_human_review",
                "counts": {"verified_count": 9},
                "missing_evidence": [{"id": "cnki_china_context_not_verified"}],
                "recommended_next_tasks": ["run_cnki_manual_search"],
            },
        )
        self._write_json(
            root / "Results" / "json" / "method_gate_report.json",
            {
                "schema_version": "p4.method_gate.v1",
                "status": "needs_human_review",
                "blocking_items": [],
                "yellow_items": ["missing_weak_iv_robust_inference"],
                "red_items": [],
                "recommended_next_tasks": [{"id": "run_weak_iv_robust_inference"}],
            },
        )
        self._write_json(
            root / "Results" / "json" / "paper_revision_round.json",
            {
                "schema_version": "p4.paper_revision_round.v1",
                "status": "ready_for_human_review",
                "revision_items": [{"id": "expand_underdeveloped_sections"}],
                "next_action": {"id": "review_revision_round"},
            },
        )
        (root / "Submissions" / "formal_package" / "paper.pdf").write_bytes(b"%PDF fixture")
        (root / "Submissions" / "formal_package" / "paper.docx").write_bytes(b"docx fixture")

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
