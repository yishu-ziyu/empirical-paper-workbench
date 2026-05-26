import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from reportlab.pdfgen import canvas


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalPdfCandidateReviewCliTests(unittest.TestCase):
    """BDD: P5-E4 reviews a PDF candidate and prepares final-writeback preflight."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-pdf-candidate-review-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root, candidate_ready=True)

    def test_bdd_33_writes_review_and_final_preflight_without_promoting_pdf(self) -> None:
        protected_before = self._snapshot_protected_state()
        candidate_pdf_before = (
            self.project_root / "Submissions" / "formal_package" / "paper_candidate.pdf"
        ).read_bytes()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        review_report_path = self.project_root / "Results" / "json" / "formal_pdf_candidate_review.json"
        review_doc_path = self.project_root / "Reviews" / "formal_pdf_candidate_review.md"
        final_preflight_path = self.project_root / "Results" / "json" / "formal_pdf_final_writeback_preflight.json"
        self.assertTrue(review_report_path.exists())
        self.assertTrue(review_doc_path.exists())
        self.assertTrue(final_preflight_path.exists())

        report = json.loads(review_report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p5.formal_pdf_candidate_review.v1")
        self.assertEqual(report["status"], "ready_for_final_approval_review")
        self.assertTrue(report["candidate_layer_only"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["this_command_wrote_final_outputs"])
        self.assertFalse(report["final_pdf_approved"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["candidate_pdf"], "Submissions/formal_package/paper_candidate.pdf")
        self.assertEqual(report["candidate_qmd"], "Submissions/formal_package/manuscript/paper_candidate.qmd")
        self.assertEqual(report["pdf_metadata"]["status"], "readable")
        self.assertGreaterEqual(report["pdf_metadata"]["pages"], 1)
        self.assertEqual(report["machine_review"]["blocking_checks"], [])
        self.assertEqual(report["next_action"]["id"], "human_review_pdf_candidate")

        preflight = json.loads(final_preflight_path.read_text(encoding="utf-8"))
        self.assertEqual(preflight["schema_version"], "p5.formal_pdf_final_writeback_preflight.v1")
        self.assertEqual(preflight["status"], "ready_for_human_final_approval")
        self.assertTrue(preflight["requires_human_approval"])
        self.assertFalse(preflight["final_writeback_allowed"])
        self.assertTrue(preflight["can_request_final_approval"])
        self.assertEqual(preflight["source_review"], "Results/json/formal_pdf_candidate_review.json")

        review_doc = review_doc_path.read_text(encoding="utf-8")
        self.assertIn("P5-E4 PDF 候选稿审阅", review_doc)
        self.assertIn("人工审阅入口", review_doc)
        self.assertIn("ready_for_final_approval_review", review_doc)

        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertEqual(
            (self.project_root / "Submissions" / "formal_package" / "paper_candidate.pdf").read_bytes(),
            candidate_pdf_before,
        )
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.pdf").exists())
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())

    def test_bdd_33_blocks_when_candidate_report_is_not_ready(self) -> None:
        report_path = self.project_root / "Results" / "json" / "formal_pdf_candidate_report.json"
        candidate = json.loads(report_path.read_text(encoding="utf-8"))
        candidate["status"] = "candidate_source_ready"
        candidate["output_pdf_exists"] = False
        report_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
        protected_before = self._snapshot_protected_state()

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_pdf_candidate_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_pdf_candidate_review")
        self.assertIn("candidate_report_not_pdf_ready", report["blocking_reasons"])
        self.assertFalse(report["can_request_final_approval"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])

        final_preflight = json.loads(
            (self.project_root / "Results" / "json" / "formal_pdf_final_writeback_preflight.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(final_preflight["status"], "blocked_by_pdf_candidate_review")
        self.assertFalse(final_preflight["can_request_final_approval"])
        self.assertFalse(final_preflight["final_writeback_allowed"])
        self.assertEqual(self._snapshot_protected_state(), protected_before)

    def _run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_pdf_candidate_review.py"),
                "--project-root",
                str(self.project_root),
                "--candidate-report",
                "Results/json/formal_pdf_candidate_report.json",
                "--output-report",
                "Results/json/formal_pdf_candidate_review.json",
                "--output-review",
                "Reviews/formal_pdf_candidate_review.md",
                "--output-final-preflight",
                "Results/json/formal_pdf_final_writeback_preflight.json",
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

    def _seed_project(self, root: Path, *, candidate_ready: bool) -> None:
        results_dir = root / "Results" / "json"
        state_dir = root / "state" / "product"
        package_dir = root / "Submissions" / "formal_package"
        qmd_dir = package_dir / "manuscript"
        for directory in [results_dir, state_dir, qmd_dir, root / "Reviews"]:
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
        qmd_path.write_text(
            "---\ntitle: Formal Paper Candidate\nformat: pdf\n---\n\n# Abstract\n\nCandidate abstract.\n",
            encoding="utf-8",
        )
        pdf_path = package_dir / "paper_candidate.pdf"
        self._write_pdf(pdf_path)
        (results_dir / "formal_pdf_candidate_report.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_pdf_candidate.v1",
                    "status": "pdf_candidate_ready" if candidate_ready else "candidate_source_ready",
                    "candidate_layer_only": True,
                    "output_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "output_pdf": "Submissions/formal_package/paper_candidate.pdf",
                    "output_pdf_exists": candidate_ready,
                    "section_count": 2,
                    "sections": [
                        {"section": "Abstract", "source_path": "sections/01-abstract.md"},
                        {"section": "Introduction", "source_path": "sections/02-introduction.md"},
                    ],
                    "render_result": {"attempted": True, "returncode": 0},
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
                    "formal_state_guard": {"changed": False, "changed_paths": []},
                    "preflight_report": "Results/json/formal_pdf_export_preflight.json",
                    "source_map": "Results/json/formal_manuscript_source_map.json",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _write_pdf(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        pdf = canvas.Canvas(str(path))
        pdf.drawString(72, 720, "Formal PDF candidate")
        pdf.showPage()
        pdf.save()
