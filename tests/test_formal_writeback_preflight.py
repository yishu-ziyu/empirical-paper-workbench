import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalWritebackPreflightCliTests(unittest.TestCase):
    """BDD: P4-J creates a formal writeback preview without changing formal state."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-writeback-preflight-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_22_preflight_lists_writeback_scope_without_formal_state_changes(self) -> None:
        gate_path = self.project_root / "Results" / "json" / "paper_revision_gate_recompute.json"
        gate_before = gate_path.read_text(encoding="utf-8")
        protected_files = list((self.project_root / "state" / "product").glob("*.json"))
        protected_before = {path: path.read_text(encoding="utf-8") for path in protected_files}

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_writeback_preflight.py"),
                "--project-root",
                str(self.project_root),
                "--gate-recompute",
                "Results/json/paper_revision_gate_recompute.json",
                "--output-report",
                "Results/json/formal_writeback_preflight.json",
                "--output-review",
                "Reviews/formal_writeback_preflight.md",
                "--output-preview",
                "Manuscripts/generated/previews/formal_writeback_preflight.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_writeback_preflight.json"
        review_path = self.project_root / "Reviews" / "formal_writeback_preflight.md"
        preview_path = self.project_root / "Manuscripts" / "generated" / "previews" / "formal_writeback_preflight.md"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(preview_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p4.formal_writeback_preflight.v1")
        self.assertEqual(report["status"], "ready_for_human_approval")
        self.assertEqual(report["source_gate_recompute"], "Results/json/paper_revision_gate_recompute.json")
        self.assertTrue(report["draft_layer_only"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertTrue(report["requires_human_approval"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["next_action"]["id"], "human_approve_formal_package")
        self.assertEqual(report["agent_team_schedule"]["call_when"], "before_formal_writeback_preflight")
        self.assertEqual(report["agent_team_schedule"]["recall_when"], "after_formal_writeback_preflight_written")
        self.assertEqual(report["agent_team_schedule"]["next_call_when"], "after_human_approval_before_p5_formal_package")

        categories = {item["category"] for item in report["writeback_scope"]}
        self.assertEqual(
            categories,
            {"sections", "citations", "method_narrative", "result_tables", "reproducibility"},
        )
        for item in report["writeback_scope"]:
            self.assertEqual(item["approval_status"], "pending_human_approval")
            self.assertTrue(item["evidence_refs"])
            self.assertFalse(item["can_write_product_state"])

        review_text = review_path.read_text(encoding="utf-8")
        preview_text = preview_path.read_text(encoding="utf-8")
        self.assertIn("P4-J 正式写回预检", review_text)
        self.assertIn("章节扩写", preview_text)
        self.assertIn("方法叙述", preview_text)
        self.assertIn("复现说明", preview_text)

        self.assertEqual(gate_path.read_text(encoding="utf-8"), gate_before)
        for path, content in protected_before.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_bdd_22_preflight_blocks_when_gate_recompute_is_not_ready(self) -> None:
        gate_path = self.project_root / "Results" / "json" / "paper_revision_gate_recompute.json"
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        gate["status"] = "needs_revision_work"
        gate["task_results"][0]["status"] = "still_blocking"
        gate["status_counts"] = {"cleared": 4, "still_blocking": 1, "manual_review_required": 0}
        gate_path.write_text(json.dumps(gate, ensure_ascii=False, indent=2), encoding="utf-8")

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_writeback_preflight.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_writeback_preflight.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_gate_recompute")
        self.assertEqual(report["blocking_reasons"], ["gate_recompute_not_ready", "uncleared_revision_tasks"])
        self.assertEqual(report["next_action"]["id"], "rerun_revision_gate_recompute")
        self.assertEqual(report["writeback_scope"], [])
        self.assertFalse(report["formal_writeback_allowed"])

    def _seed_project(self, root: Path) -> None:
        results_dir = root / "Results" / "json"
        reviews_dir = root / "Reviews"
        state_dir = root / "state" / "product"
        manuscripts_dir = root / "Manuscripts" / "generated"
        data_dir = root / "Data" / "literature" / "processed"
        submissions_dir = root / "Submissions"
        for directory in [results_dir, reviews_dir, state_dir, manuscripts_dir, data_dir, submissions_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        for name in [
            "research_question.json",
            "variable_roles.json",
            "variable_role_set.json",
            "design_spec.json",
            "run_plan.json",
            "supervisor_plan.json",
            "agent_task_queue.json",
        ]:
            (state_dir / name).write_text(json.dumps({"name": name, "formal": True}), encoding="utf-8")

        (manuscripts_dir / "paper_package_draft.md").write_text(
            "# Working Paper Draft\n\n## Results\n\nDraft result section.\n",
            encoding="utf-8",
        )
        (data_dir / "verified_bibliography.csv").write_text("title,doi\nPaper,10.0000/example\n", encoding="utf-8")
        (data_dir / "contribution_matrix.md").write_text("| contribution | evidence |\n| --- | --- |\n", encoding="utf-8")
        (results_dir / "method_gate_report.json").write_text(
            json.dumps({"schema_version": "p4.method_gate.v1", "gate_status": "yellow"}, ensure_ascii=False),
            encoding="utf-8",
        )
        (results_dir / "method_diagnostics_report.json").write_text(
            json.dumps({"schema_version": "p4.method_diagnostics.v1"}, ensure_ascii=False),
            encoding="utf-8",
        )
        (results_dir / "method_execution_result.json").write_text(
            json.dumps({"schema_version": "p2.method_execution.v1"}, ensure_ascii=False),
            encoding="utf-8",
        )
        (results_dir / "paper_quality_report.json").write_text(
            json.dumps({"schema_version": "p4.paper_quality.v1", "verdict": []}, ensure_ascii=False),
            encoding="utf-8",
        )
        (results_dir / "reviewer_scorecard_report.json").write_text(
            json.dumps({"schema_version": "p4.reviewer_scorecard.v1", "overall_score": 82}, ensure_ascii=False),
            encoding="utf-8",
        )
        (submissions_dir / "cfps_robot_pdf_export_manifest.json").write_text(
            json.dumps({"schema_version": "p4.pdf_export_manifest.v1"}, ensure_ascii=False),
            encoding="utf-8",
        )

        task_results = [
            {
                "task_id": "expand_working_paper_sections",
                "agent": "ManuscriptAgent",
                "status": "cleared",
                "evidence_packet_path": "Reviews/agent_packets/manuscriptagent/expand-working-paper-sections.md",
                "evidence_items": [
                    {"path": "Manuscripts/generated/paper_package_draft.md", "exists": True},
                    {"path": "Results/json/paper_quality_report.json", "exists": True},
                ],
            },
            {
                "task_id": "build_literature_package",
                "agent": "LiteratureAgent",
                "status": "cleared",
                "evidence_packet_path": "Reviews/agent_packets/literatureagent/build-literature-package.md",
                "evidence_items": [
                    {"path": "Data/literature/processed/verified_bibliography.csv", "exists": True},
                    {"path": "Data/literature/processed/contribution_matrix.md", "exists": True},
                ],
            },
            {
                "task_id": "run_method_gate",
                "agent": "MethodAgent",
                "status": "cleared",
                "evidence_packet_path": "Reviews/agent_packets/methodagent/run-method-gate.md",
                "evidence_items": [{"path": "Results/json/method_gate_report.json", "exists": True}],
            },
            {
                "task_id": "explain_missing_drop_and_analysis_sample",
                "agent": "ExecutionAgent",
                "status": "cleared",
                "evidence_packet_path": "Reviews/agent_packets/executionagent/explain-missing-drop.md",
                "evidence_items": [{"path": "Results/json/method_execution_result.json", "exists": True}],
            },
            {
                "task_id": "run_reviewer_revision_loop",
                "agent": "ReviewerAgent",
                "status": "cleared",
                "evidence_packet_path": "Reviews/agent_packets/revieweragent/run-reviewer-revision-loop.md",
                "evidence_items": [{"path": "Results/json/reviewer_scorecard_report.json", "exists": True}],
            },
        ]
        (results_dir / "paper_revision_gate_recompute.json").write_text(
            json.dumps(
                {
                    "schema_version": "p4.paper_revision_gate_recompute.v1",
                    "source_evidence_manifest": "Results/json/paper_revision_evidence_packets.json",
                    "status": "ready_for_formal_writeback_preflight",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                    "status_counts": {"cleared": 5, "still_blocking": 0, "manual_review_required": 0},
                    "task_results": task_results,
                    "next_action": {"id": "formal_writeback_preflight"},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
