import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from reportlab.pdfgen import canvas


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalPdfFinalWritebackCliTests(unittest.TestCase):
    """BDD: P6-A promotes only the approved PDF candidate into the final package."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-pdf-final-writeback-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root, approved=True)

    def test_bdd_35_writes_final_pdf_after_explicit_approval_only(self) -> None:
        protected_before = self._snapshot_protected_state()
        p5_ledgers_before = self._snapshot_p5_ledgers()
        candidate_pdf = self.project_root / "Submissions" / "formal_package" / "paper_candidate.pdf"
        candidate_qmd = self.project_root / "Submissions" / "formal_package" / "manuscript" / "paper_candidate.qmd"
        candidate_pdf_before = candidate_pdf.read_bytes()
        candidate_qmd_before = candidate_qmd.read_text(encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        final_pdf = self.project_root / "Submissions" / "formal_package" / "paper.pdf"
        final_docx = self.project_root / "Submissions" / "formal_package" / "paper.docx"
        report_path = self.project_root / "Results" / "json" / "formal_pdf_final_writeback.json"
        review_path = self.project_root / "Reviews" / "formal_pdf_final_writeback.md"
        self.assertTrue(final_pdf.exists())
        self.assertFalse(final_docx.exists())
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.formal_pdf_final_writeback.v1")
        self.assertEqual(report["status"], "final_pdf_written")
        self.assertTrue(report["final_writeback_authorized"])
        self.assertTrue(report["this_command_wrote_final_pdf"])
        self.assertFalse(report["this_command_wrote_docx"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["source_candidate_pdf"], "Submissions/formal_package/paper_candidate.pdf")
        self.assertEqual(report["final_pdf"], "Submissions/formal_package/paper.pdf")
        self.assertEqual(report["source_candidate_pdf_sha256"], self._sha256(candidate_pdf))
        self.assertEqual(report["final_pdf_sha256"], self._sha256(final_pdf))
        self.assertEqual(report["source_candidate_pdf_sha256"], report["final_pdf_sha256"])
        self.assertEqual(report["source_candidate_pdf_bytes"], final_pdf.stat().st_size)
        self.assertEqual(report["next_action"]["id"], "docx_export_preflight")

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P6-A 最终 PDF 写回", review_text)
        self.assertIn("final_pdf_written", review_text)

        self.assertEqual(candidate_pdf.read_bytes(), candidate_pdf_before)
        self.assertEqual(candidate_qmd.read_text(encoding="utf-8"), candidate_qmd_before)
        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertEqual(self._snapshot_p5_ledgers(), p5_ledgers_before)

    def test_bdd_35_blocks_without_explicit_final_approval(self) -> None:
        self._seed_project(self.project_root, approved=False)

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_pdf_final_writeback.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_final_approval")
        self.assertFalse(report["final_writeback_authorized"])
        self.assertIn("final_approval_not_authorized", report["blocking_reasons"])
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.pdf").exists())
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())

    def test_bdd_35_blocks_when_approval_points_to_a_different_candidate(self) -> None:
        approval_path = self.project_root / "Results" / "json" / "formal_pdf_final_approval.json"
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
        approval["candidate_pdf"] = "Submissions/formal_package/other_candidate.pdf"
        approval_path.write_text(json.dumps(approval, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_pdf_final_writeback.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_candidate_integrity")
        self.assertIn("candidate_pdf_mismatch", report["blocking_reasons"])
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.pdf").exists())

    def _run_cli(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_pdf_final_writeback.py"),
                "--project-root",
                str(self.project_root),
                "--candidate-report",
                "Results/json/formal_pdf_candidate_report.json",
                "--final-preflight",
                "Results/json/formal_pdf_final_writeback_preflight.json",
                "--approval-report",
                "Results/json/formal_pdf_final_approval.json",
                "--approval-ledger",
                "state/product/writeback_approvals.json",
                "--output-report",
                "Results/json/formal_pdf_final_writeback.json",
                "--output-review",
                "Reviews/formal_pdf_final_writeback.md",
                "--output-pdf",
                "Submissions/formal_package/paper.pdf",
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

    def _snapshot_p5_ledgers(self) -> dict[str, str]:
        paths = [
            "Results/json/formal_pdf_candidate_report.json",
            "Results/json/formal_pdf_final_writeback_preflight.json",
            "Results/json/formal_pdf_final_approval.json",
            "state/product/writeback_approvals.json",
        ]
        return {path: (self.project_root / path).read_text(encoding="utf-8") for path in paths}

    def _seed_project(self, root: Path, *, approved: bool) -> None:
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

        qmd_path = qmd_dir / "paper_candidate.qmd"
        qmd_path.write_text("# Candidate\n\nCandidate source.\n", encoding="utf-8")
        pdf_path = package_dir / "paper_candidate.pdf"
        self._write_pdf(pdf_path)
        final_status = "approved_for_final_writeback" if approved else "needs_revision"
        (results_dir / "formal_pdf_candidate_report.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_pdf_candidate.v1",
                    "status": "pdf_candidate_ready",
                    "candidate_layer_only": True,
                    "output_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "output_pdf": "Submissions/formal_package/paper_candidate.pdf",
                    "output_pdf_exists": True,
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
                    "formal_state_guard": {"changed": False, "changed_paths": []},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (results_dir / "formal_pdf_final_writeback_preflight.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_pdf_final_writeback_preflight.v1",
                    "status": "ready_for_human_final_approval",
                    "can_request_final_approval": True,
                    "requires_human_approval": True,
                    "final_writeback_allowed": False,
                    "candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                    "candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "blocking_reasons": [],
                    "formal_state_guard": {"changed": False, "changed_paths": []},
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (results_dir / "formal_pdf_final_approval.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_pdf_final_approval.v1",
                    "status": final_status,
                    "can_enter_p6": approved,
                    "final_writeback_authorized": approved,
                    "candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                    "candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
                    "formal_state_guard": {"changed": False, "changed_paths": []},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (state_dir / "writeback_approvals.json").write_text(
            json.dumps(
                {
                    "schema_version": "product.writeback_approvals.v1",
                    "approvals": {},
                    "formal_preflight_approvals": {},
                    "final_pdf_approvals": {
                        "formal_pdf_candidate": {
                            "status": "approved" if approved else "needs_revision",
                            "can_enter_p6": approved,
                            "final_writeback_authorized": approved,
                            "candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                            "candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                        }
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
        pdf.drawString(72, 720, "Approved final PDF candidate")
        pdf.showPage()
        pdf.save()

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
