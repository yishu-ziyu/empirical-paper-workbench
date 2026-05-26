import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalDocxExportPreflightCliTests(unittest.TestCase):
    """BDD: P6-B verifies docx export readiness without generating docx."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-docx-export-preflight-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_36_marks_docx_export_ready_without_generating_docx(self) -> None:
        protected_before = self._snapshot_protected_state()
        p6_ledgers_before = self._snapshot_p6_ledgers()
        final_pdf = self.project_root / "Submissions" / "formal_package" / "paper.pdf"
        candidate_qmd = self.project_root / "Submissions" / "formal_package" / "manuscript" / "paper_candidate.qmd"
        final_pdf_before = final_pdf.read_bytes()
        candidate_qmd_before = candidate_qmd.read_text(encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        output_docx = self.project_root / "Submissions" / "formal_package" / "paper.docx"
        report_path = self.project_root / "Results" / "json" / "formal_docx_export_preflight.json"
        review_path = self.project_root / "Reviews" / "formal_docx_export_preflight.md"
        self.assertFalse(output_docx.exists())
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.formal_docx_export_preflight.v1")
        self.assertEqual(report["status"], "ready_for_docx_export")
        self.assertTrue(report["can_export_docx"])
        self.assertEqual(report["source_final_pdf_writeback"], "Results/json/formal_pdf_final_writeback.json")
        self.assertEqual(report["source_candidate_qmd"], "Submissions/formal_package/manuscript/paper_candidate.qmd")
        self.assertEqual(report["final_pdf"], "Submissions/formal_package/paper.pdf")
        self.assertEqual(report["expected_docx"], "Submissions/formal_package/paper.docx")
        self.assertIn("Program/export_docx.py", report["export_command"])
        self.assertIn("Submissions/formal_package/paper.docx", report["export_command"])
        self.assertTrue(report["pandoc"]["available"])
        self.assertTrue(report["pandoc"]["path"])
        self.assertFalse(report["this_command_wrote_docx"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["next_action"]["id"], "run_formal_docx_export")

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P6-B docx 导出预检", review_text)
        self.assertIn("ready_for_docx_export", review_text)

        self.assertEqual(final_pdf.read_bytes(), final_pdf_before)
        self.assertEqual(candidate_qmd.read_text(encoding="utf-8"), candidate_qmd_before)
        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertEqual(self._snapshot_p6_ledgers(), p6_ledgers_before)

    def test_bdd_36_blocks_when_final_pdf_writeback_is_not_complete(self) -> None:
        writeback_path = self.project_root / "Results" / "json" / "formal_pdf_final_writeback.json"
        writeback = json.loads(writeback_path.read_text(encoding="utf-8"))
        writeback["status"] = "blocked_by_final_approval"
        writeback["final_writeback_authorized"] = False
        writeback_path.write_text(json.dumps(writeback, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_docx_export_preflight.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_final_pdf_writeback")
        self.assertFalse(report["can_export_docx"])
        self.assertIn("final_pdf_writeback_not_complete", report["blocking_reasons"])
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())

    def test_bdd_36_blocks_when_pandoc_is_unavailable(self) -> None:
        result = self._run_cli("--pandoc-bin", "definitely-missing-pandoc-for-test")
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_docx_export_preflight.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_docx_toolchain")
        self.assertFalse(report["can_export_docx"])
        self.assertIn("pandoc_unavailable", report["blocking_reasons"])
        self.assertFalse(report["pandoc"]["available"])
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())

    def _run_cli(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_docx_export_preflight.py"),
                "--project-root",
                str(self.project_root),
                "--final-writeback-report",
                "Results/json/formal_pdf_final_writeback.json",
                "--approval-report",
                "Results/json/formal_pdf_final_approval.json",
                "--approval-ledger",
                "state/product/writeback_approvals.json",
                "--output-report",
                "Results/json/formal_docx_export_preflight.json",
                "--output-review",
                "Reviews/formal_docx_export_preflight.md",
                "--expected-docx",
                "Submissions/formal_package/paper.docx",
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

    def _snapshot_p6_ledgers(self) -> dict[str, str]:
        paths = [
            "Results/json/formal_pdf_final_writeback.json",
            "Results/json/formal_pdf_final_approval.json",
            "state/product/writeback_approvals.json",
        ]
        return {path: (self.project_root / path).read_text(encoding="utf-8") for path in paths}

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

        final_pdf = package_dir / "paper.pdf"
        final_pdf.write_bytes(b"%PDF-1.4\n% final pdf fixture\n")
        candidate_qmd = qmd_dir / "paper_candidate.qmd"
        candidate_qmd.write_text("# Candidate\n\nCandidate source.\n", encoding="utf-8")

        (results_dir / "formal_pdf_final_writeback.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_pdf_final_writeback.v1",
                    "status": "final_pdf_written",
                    "source_approval_report": "Results/json/formal_pdf_final_approval.json",
                    "source_approval_ledger": "state/product/writeback_approvals.json",
                    "source_candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "final_pdf": "Submissions/formal_package/paper.pdf",
                    "final_pdf_exists": True,
                    "blocking_reasons": [],
                    "final_writeback_authorized": True,
                    "this_command_wrote_final_pdf": True,
                    "this_command_wrote_docx": False,
                    "this_command_wrote_formal_state": False,
                    "formal_state_guard": {"changed": False, "changed_paths": []},
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
                    "status": "approved_for_final_writeback",
                    "can_enter_p6": True,
                    "final_writeback_authorized": True,
                    "candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                    "candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
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
                    "approvals": {"legacy_candidate": {"status": "approved"}},
                    "final_pdf_approvals": {
                        "formal_pdf_candidate": {
                            "status": "approved",
                            "can_enter_p6": True,
                            "final_writeback_authorized": True,
                            "candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                        }
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
