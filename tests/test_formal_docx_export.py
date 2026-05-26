import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalDocxExportCliTests(unittest.TestCase):
    """BDD: P6-C materializes the formal docx after P6-B is ready."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-docx-export-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_37_exports_docx_from_ready_preflight_without_touching_formal_state(self) -> None:
        protected_before = self._snapshot_protected_state()
        p6_ledgers_before = self._snapshot_p6_ledgers()
        final_pdf = self.project_root / "Submissions" / "formal_package" / "paper.pdf"
        candidate_qmd = self.project_root / "Submissions" / "formal_package" / "manuscript" / "paper_candidate.qmd"
        final_pdf_before = final_pdf.read_bytes()
        candidate_qmd_before = candidate_qmd.read_text(encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        output_docx = self.project_root / "Submissions" / "formal_package" / "paper.docx"
        report_path = self.project_root / "Results" / "json" / "formal_docx_export.json"
        review_path = self.project_root / "Reviews" / "formal_docx_export.md"
        self.assertTrue(output_docx.exists())
        self.assertTrue(zipfile.is_zipfile(output_docx))
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.formal_docx_export.v1")
        self.assertEqual(report["status"], "docx_exported")
        self.assertEqual(report["source_preflight_report"], "Results/json/formal_docx_export_preflight.json")
        self.assertEqual(report["source_candidate_qmd"], "Submissions/formal_package/manuscript/paper_candidate.qmd")
        self.assertEqual(report["final_pdf"], "Submissions/formal_package/paper.pdf")
        self.assertEqual(report["docx"], "Submissions/formal_package/paper.docx")
        self.assertTrue(report["docx_exists"])
        self.assertGreater(report["docx_bytes"], 0)
        self.assertEqual(len(report["docx_sha256"]), 64)
        self.assertIn("Program/export_docx.py", report["export_command"])
        self.assertIn("Submissions/formal_package/paper.docx", report["export_command"])
        self.assertEqual(report["log_path"], "Results/logs/formal_docx_export.log")
        self.assertTrue(report["this_command_wrote_docx"])
        self.assertFalse(report["this_command_wrote_pdf"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P6-C 正式 docx 导出", review_text)
        self.assertIn("docx_exported", review_text)

        self.assertEqual(final_pdf.read_bytes(), final_pdf_before)
        self.assertEqual(candidate_qmd.read_text(encoding="utf-8"), candidate_qmd_before)
        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertEqual(self._snapshot_p6_ledgers(), p6_ledgers_before)

    def test_bdd_37_blocks_when_preflight_is_not_ready(self) -> None:
        preflight_path = self.project_root / "Results" / "json" / "formal_docx_export_preflight.json"
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        preflight["status"] = "blocked_by_docx_toolchain"
        preflight["can_export_docx"] = False
        preflight["blocking_reasons"] = ["pandoc_unavailable"]
        preflight_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_docx_export.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["status"], "blocked_by_docx_preflight")
        self.assertIn("preflight_not_ready", report["blocking_reasons"])
        self.assertIn("preflight_cannot_export_docx", report["blocking_reasons"])
        self.assertFalse(report["this_command_wrote_docx"])
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())
        self.assertTrue((self.project_root / "Submissions" / "formal_package" / "paper.pdf").exists())

    def test_bdd_37_blocks_when_candidate_qmd_is_missing_without_rolling_back_pdf(self) -> None:
        candidate_qmd = self.project_root / "Submissions" / "formal_package" / "manuscript" / "paper_candidate.qmd"
        candidate_qmd.unlink()

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_docx_export.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["status"], "blocked_by_docx_inputs")
        self.assertIn("candidate_qmd_missing", report["blocking_reasons"])
        self.assertFalse(report["this_command_wrote_docx"])
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())
        self.assertTrue((self.project_root / "Submissions" / "formal_package" / "paper.pdf").exists())

    def _run_cli(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_docx_export.py"),
                "--project-root",
                str(self.project_root),
                "--preflight-report",
                "Results/json/formal_docx_export_preflight.json",
                "--output-report",
                "Results/json/formal_docx_export.json",
                "--output-review",
                "Reviews/formal_docx_export.md",
                "--output-docx",
                "Submissions/formal_package/paper.docx",
                "--log-path",
                "Results/logs/formal_docx_export.log",
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
            "Results/json/formal_docx_export_preflight.json",
            "state/product/writeback_approvals.json",
        ]
        return {path: (self.project_root / path).read_text(encoding="utf-8") for path in paths}

    def _seed_project(self, root: Path) -> None:
        results_dir = root / "Results" / "json"
        state_dir = root / "state" / "product"
        package_dir = root / "Submissions" / "formal_package"
        qmd_dir = package_dir / "manuscript"
        manuscripts_dir = root / "Manuscripts"
        for directory in [results_dir, state_dir, qmd_dir, manuscripts_dir]:
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

        (manuscripts_dir / "references.bib").write_text("", encoding="utf-8")
        final_pdf = package_dir / "paper.pdf"
        final_pdf.write_bytes(b"%PDF-1.4\n% final pdf fixture\n")
        candidate_qmd = qmd_dir / "paper_candidate.qmd"
        candidate_qmd.write_text(
            "---\n"
            "title: Candidate\n"
            "---\n\n"
            "# Introduction\n\n"
            "This candidate manuscript is ready for formal docx export.\n",
            encoding="utf-8",
        )

        (results_dir / "formal_pdf_final_writeback.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_pdf_final_writeback.v1",
                    "status": "final_pdf_written",
                    "source_candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "final_pdf": "Submissions/formal_package/paper.pdf",
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
            json.dumps({"status": "approved_for_final_writeback", "can_enter_p6": True}, ensure_ascii=False),
            encoding="utf-8",
        )
        (results_dir / "formal_docx_export_preflight.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_docx_export_preflight.v1",
                    "status": "ready_for_docx_export",
                    "source_candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "final_pdf": "Submissions/formal_package/paper.pdf",
                    "expected_docx": "Submissions/formal_package/paper.docx",
                    "can_export_docx": True,
                    "blocking_reasons": [],
                    "export_command": [
                        "python3",
                        "Program/export_docx.py",
                        "--project-root",
                        ".",
                        "--source",
                        "Submissions/formal_package/manuscript/paper_candidate.qmd",
                        "--output",
                        "Submissions/formal_package/paper.docx",
                    ],
                    "this_command_wrote_docx": False,
                    "this_command_wrote_formal_state": False,
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
                    "final_pdf_approvals": {
                        "formal_pdf_candidate": {
                            "status": "approved",
                            "can_enter_p6": True,
                            "final_writeback_authorized": True,
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
