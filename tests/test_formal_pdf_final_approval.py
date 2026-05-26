import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from reportlab.pdfgen import canvas


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalPdfFinalApprovalCliTests(unittest.TestCase):
    """BDD: P5-E5 records explicit human approval before final PDF/docx writeback."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-pdf-final-approval-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_34_approve_authorizes_final_writeback_without_creating_final_outputs(self) -> None:
        preflight_path = self.project_root / "Results" / "json" / "formal_pdf_final_writeback_preflight.json"
        preflight_before = preflight_path.read_text(encoding="utf-8")
        protected_before = self._snapshot_protected_state()
        candidate_pdf_path = self.project_root / "Submissions" / "formal_package" / "paper_candidate.pdf"
        candidate_pdf_before = candidate_pdf_path.read_bytes()

        result = self._run_cli("--action", "approve", "--note", "批准候选 PDF 进入最终写回。")
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_pdf_final_approval.json"
        review_path = self.project_root / "Reviews" / "formal_pdf_final_approval.md"
        approval_path = self.project_root / "state" / "product" / "writeback_approvals.json"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(approval_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p5.formal_pdf_final_approval.v1")
        self.assertEqual(report["status"], "approved_for_final_writeback")
        self.assertEqual(report["action"], "approve")
        self.assertTrue(report["can_enter_p6"])
        self.assertTrue(report["final_writeback_authorized"])
        self.assertFalse(report["this_command_wrote_final_outputs"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["candidate_pdf"], "Submissions/formal_package/paper_candidate.pdf")
        self.assertEqual(report["candidate_qmd"], "Submissions/formal_package/manuscript/paper_candidate.qmd")

        ledger = json.loads(approval_path.read_text(encoding="utf-8"))
        self.assertEqual(ledger["approvals"], {"legacy_candidate": {"status": "approved"}})
        entry = ledger["final_pdf_approvals"]["formal_pdf_candidate"]
        self.assertEqual(entry["status"], "approved")
        self.assertTrue(entry["can_enter_p6"])
        self.assertTrue(entry["final_writeback_authorized"])
        self.assertEqual(entry["note"], "批准候选 PDF 进入最终写回。")

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P5-E5 最终写回人工批准", review_text)
        self.assertIn("approved_for_final_writeback", review_text)

        self.assertEqual(preflight_path.read_text(encoding="utf-8"), preflight_before)
        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertEqual(candidate_pdf_path.read_bytes(), candidate_pdf_before)
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.pdf").exists())
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())

    def test_bdd_34_needs_revision_records_non_authorizing_decision(self) -> None:
        result = self._run_cli("--action", "needs_revision", "--note", "先修订图表注释。")
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_pdf_final_approval.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "needs_revision")
        self.assertFalse(report["can_enter_p6"])
        self.assertFalse(report["final_writeback_authorized"])
        self.assertEqual(report["next_action"]["id"], "revise_pdf_candidate")

        ledger = json.loads(
            (self.project_root / "state" / "product" / "writeback_approvals.json").read_text(
                encoding="utf-8"
            )
        )
        entry = ledger["final_pdf_approvals"]["formal_pdf_candidate"]
        self.assertEqual(entry["status"], "needs_revision")
        self.assertFalse(entry["can_enter_p6"])

    def test_bdd_34_blocks_when_final_preflight_is_not_ready(self) -> None:
        preflight_path = self.project_root / "Results" / "json" / "formal_pdf_final_writeback_preflight.json"
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        preflight["status"] = "blocked_by_pdf_candidate_review"
        preflight["can_request_final_approval"] = False
        preflight["blocking_reasons"] = ["candidate_pdf_unreadable"]
        preflight_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
        protected_before = self._snapshot_protected_state()

        result = self._run_cli("--action", "approve", "--note", "尝试批准。")
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_pdf_final_approval.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_final_preflight")
        self.assertFalse(report["can_enter_p6"])
        self.assertFalse(report["final_writeback_authorized"])
        self.assertIn("candidate_pdf_unreadable", report["blocking_reasons"])

        ledger = json.loads(
            (self.project_root / "state" / "product" / "writeback_approvals.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertNotIn("formal_pdf_candidate", ledger.get("final_pdf_approvals", {}))
        self.assertEqual(self._snapshot_protected_state(), protected_before)

    def _run_cli(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_pdf_final_approval.py"),
                "--project-root",
                str(self.project_root),
                "--final-preflight",
                "Results/json/formal_pdf_final_writeback_preflight.json",
                "--output-report",
                "Results/json/formal_pdf_final_approval.json",
                "--output-review",
                "Reviews/formal_pdf_final_approval.md",
                *extra_args,
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def _snapshot_protected_state(self) -> dict[str, str]:
        state_dir = self.project_root / "state" / "product"
        return {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(state_dir.glob("*.json"))
            if path.name != "writeback_approvals.json"
        }

    def _seed_project(self, root: Path) -> None:
        results_dir = root / "Results" / "json"
        reviews_dir = root / "Reviews"
        state_dir = root / "state" / "product"
        package_dir = root / "Submissions" / "formal_package"
        qmd_dir = package_dir / "manuscript"
        for directory in [results_dir, reviews_dir, state_dir, qmd_dir]:
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

        (state_dir / "writeback_approvals.json").write_text(
            json.dumps(
                {
                    "schema_version": "product.writeback_approvals.v1",
                    "approvals": {"legacy_candidate": {"status": "approved"}},
                    "formal_preflight_approvals": {},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        qmd_path = qmd_dir / "paper_candidate.qmd"
        qmd_path.write_text("# Candidate\n\nCandidate source.\n", encoding="utf-8")
        pdf_path = package_dir / "paper_candidate.pdf"
        self._write_pdf(pdf_path)
        (results_dir / "formal_pdf_final_writeback_preflight.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_pdf_final_writeback_preflight.v1",
                    "status": "ready_for_human_final_approval",
                    "source_review": "Results/json/formal_pdf_candidate_review.json",
                    "candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                    "candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "requires_human_approval": True,
                    "can_request_final_approval": True,
                    "final_writeback_allowed": False,
                    "final_pdf_approved": False,
                    "blocking_reasons": [],
                    "approval_contract": {
                        "approval_path": "state/product/writeback_approvals.json",
                        "ready_for_approval": True,
                    },
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
                    "formal_state_guard": {
                        "changed": False,
                        "changed_paths": [],
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _write_pdf(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        pdf = canvas.Canvas(str(path))
        pdf.drawString(72, 720, "Final approval candidate")
        pdf.showPage()
        pdf.save()
