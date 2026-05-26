import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalSubmissionPackageManifestCliTests(unittest.TestCase):
    """BDD: P6-D summarizes the final package without regenerating outputs."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-submission-manifest-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_38_writes_manifest_and_acceptance_without_touching_final_outputs(self) -> None:
        protected_before = self._snapshot_protected_state()
        immutable_before = self._snapshot_immutable_inputs()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_submission_package_manifest.json"
        review_path = self.project_root / "Reviews" / "formal_submission_package_acceptance.md"
        package_manifest_path = self.project_root / "Submissions" / "formal_package" / "manifest.json"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(package_manifest_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.formal_submission_package_manifest.v1")
        self.assertEqual(report["status"], "formal_submission_package_ready")
        self.assertEqual(report["package_root"], "Submissions/formal_package")
        self.assertEqual(report["blocking_reasons"], [])
        self.assertEqual(report["artifacts"]["paper_pdf"]["path"], "Submissions/formal_package/paper.pdf")
        self.assertEqual(report["artifacts"]["paper_docx"]["path"], "Submissions/formal_package/paper.docx")
        self.assertEqual(len(report["artifacts"]["paper_pdf"]["sha256"]), 64)
        self.assertEqual(len(report["artifacts"]["paper_docx"]["sha256"]), 64)
        self.assertEqual(report["input_reports"]["p6a"]["status"], "final_pdf_written")
        self.assertEqual(report["input_reports"]["p6b"]["status"], "ready_for_docx_export")
        self.assertEqual(report["input_reports"]["p6c"]["status"], "docx_exported")
        self.assertTrue(report["consistency_checks"]["pdf_hash_matches_p6a"])
        self.assertTrue(report["consistency_checks"]["docx_hash_matches_p6c"])
        self.assertTrue(report["consistency_checks"]["p6b_expected_docx_matches_p6c"])
        self.assertTrue(report["consistency_checks"]["p6c_final_pdf_matches_p6a"])
        self.assertFalse(report["boundary_flags"]["this_command_rendered_pdf"])
        self.assertFalse(report["boundary_flags"]["this_command_rendered_docx"])
        self.assertFalse(report["boundary_flags"]["this_command_wrote_final_outputs"])
        self.assertFalse(report["boundary_flags"]["this_command_wrote_formal_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["manual_acceptance"]["human_status"], "pending_manual_acceptance")
        self.assertGreaterEqual(len(report["manual_acceptance"]["checklist"]), 4)
        self.assertIn("Program/formal_pdf_final_writeback.py", " ".join(report["reproduce_commands"][0]))
        self.assertIn("Program/formal_docx_export.py", " ".join(report["reproduce_commands"][2]))

        package_manifest = json.loads(package_manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(package_manifest["status"], "formal_submission_package_ready")
        self.assertEqual(package_manifest["artifacts"], report["artifacts"])

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P6-D 正式投稿包人工验收", review_text)
        self.assertIn("formal_submission_package_ready", review_text)
        self.assertIn("打开 PDF", review_text)

        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertEqual(self._snapshot_immutable_inputs(), immutable_before)

    def test_bdd_38_blocks_when_docx_export_report_is_not_exported(self) -> None:
        p6c_path = self.project_root / "Results" / "json" / "formal_docx_export.json"
        p6c = json.loads(p6c_path.read_text(encoding="utf-8"))
        p6c["status"] = "blocked_by_docx_export"
        p6c["blocking_reasons"] = ["pandoc_docx_export_failed"]
        p6c_path.write_text(json.dumps(p6c, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_submission_package_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_docx_export")
        self.assertIn("p6c_docx_export_not_exported", report["blocking_reasons"])
        self.assertFalse(report["package_manifest_written"])
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "manifest.json").exists())

    def test_bdd_38_blocks_when_final_docx_is_missing_without_touching_pdf(self) -> None:
        final_pdf = self.project_root / "Submissions" / "formal_package" / "paper.pdf"
        final_pdf_before = final_pdf.read_bytes()
        (self.project_root / "Submissions" / "formal_package" / "paper.docx").unlink()

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_submission_package_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_package_artifacts")
        self.assertIn("paper_docx_missing", report["blocking_reasons"])
        self.assertFalse(report["package_manifest_written"])
        self.assertEqual(final_pdf.read_bytes(), final_pdf_before)

    def test_bdd_38_blocks_when_p6_hash_does_not_match_artifact(self) -> None:
        p6a_path = self.project_root / "Results" / "json" / "formal_pdf_final_writeback.json"
        p6a = json.loads(p6a_path.read_text(encoding="utf-8"))
        p6a["final_pdf_sha256"] = "0" * 64
        p6a_path.write_text(json.dumps(p6a, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_submission_package_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_package_consistency")
        self.assertIn("paper_pdf_hash_mismatch:p6a", report["blocking_reasons"])
        self.assertFalse(report["package_manifest_written"])

    def _run_cli(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_submission_package_manifest.py"),
                "--project-root",
                str(self.project_root),
                "--output-report",
                "Results/json/formal_submission_package_manifest.json",
                "--output-review",
                "Reviews/formal_submission_package_acceptance.md",
                "--package-manifest",
                "Submissions/formal_package/manifest.json",
                *extra_args,
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def _snapshot_protected_state(self) -> dict[str, str]:
        state_dir = self.project_root / "state" / "product"
        return {path.name: path.read_text(encoding="utf-8") for path in sorted(state_dir.glob("*.json"))}

    def _snapshot_immutable_inputs(self) -> dict[str, bytes]:
        paths = [
            "Submissions/formal_package/paper.pdf",
            "Submissions/formal_package/paper.docx",
            "Submissions/formal_package/paper_candidate.pdf",
            "Submissions/formal_package/manuscript/paper_candidate.qmd",
            "Results/json/formal_pdf_final_writeback.json",
            "Results/json/formal_docx_export_preflight.json",
            "Results/json/formal_docx_export.json",
            "Results/logs/formal_docx_export.log",
            "Submissions/export_manifest.json",
        ]
        return {path: (self.project_root / path).read_bytes() for path in paths}

    def _seed_project(self, root: Path) -> None:
        results_dir = root / "Results" / "json"
        logs_dir = root / "Results" / "logs"
        state_dir = root / "state" / "product"
        package_dir = root / "Submissions" / "formal_package"
        qmd_dir = package_dir / "manuscript"
        for directory in [results_dir, logs_dir, state_dir, qmd_dir, root / "Submissions"]:
            directory.mkdir(parents=True, exist_ok=True)

        for name in [
            "research_question.json",
            "variable_roles.json",
            "variable_role_set.json",
            "design_spec.json",
            "run_plan.json",
            "supervisor_plan.json",
            "agent_task_queue.json",
            "writeback_approvals.json",
        ]:
            (state_dir / name).write_text(json.dumps({"name": name, "formal": True}), encoding="utf-8")

        paper_pdf = package_dir / "paper.pdf"
        paper_docx = package_dir / "paper.docx"
        candidate_pdf = package_dir / "paper_candidate.pdf"
        candidate_qmd = qmd_dir / "paper_candidate.qmd"
        paper_pdf.write_bytes(b"%PDF-1.4\n% final pdf fixture\n")
        paper_docx.write_bytes(b"PK\x03\x04 final docx fixture\n")
        candidate_pdf.write_bytes(b"%PDF-1.4\n% candidate pdf fixture\n")
        candidate_qmd.write_text("# Candidate\n\nFormal candidate source.\n", encoding="utf-8")
        (logs_dir / "formal_docx_export.log").write_text("pandoc ok\n", encoding="utf-8")
        (root / "Submissions" / "export_manifest.json").write_text(
            json.dumps({"status": "exported", "docx": "Submissions/formal_package/paper.docx"}),
            encoding="utf-8",
        )

        pdf_hash = self._sha256(paper_pdf)
        docx_hash = self._sha256(paper_docx)
        (results_dir / "formal_pdf_final_writeback.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_pdf_final_writeback.v1",
                    "status": "final_pdf_written",
                    "source_candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "final_pdf": "Submissions/formal_package/paper.pdf",
                    "final_pdf_sha256": pdf_hash,
                    "final_pdf_bytes": paper_pdf.stat().st_size,
                    "blocking_reasons": [],
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
                    "this_command_wrote_docx": False,
                    "this_command_wrote_formal_state": False,
                    "formal_state_guard": {"changed": False, "changed_paths": []},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (results_dir / "formal_docx_export.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_docx_export.v1",
                    "status": "docx_exported",
                    "source_preflight_report": "Results/json/formal_docx_export_preflight.json",
                    "source_candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    "final_pdf": "Submissions/formal_package/paper.pdf",
                    "docx": "Submissions/formal_package/paper.docx",
                    "docx_sha256": docx_hash,
                    "docx_bytes": paper_docx.stat().st_size,
                    "generic_export_manifest": "Submissions/export_manifest.json",
                    "log_path": "Results/logs/formal_docx_export.log",
                    "blocking_reasons": [],
                    "this_command_wrote_docx": True,
                    "this_command_wrote_pdf": False,
                    "this_command_wrote_formal_state": False,
                    "formal_state_guard": {"changed": False, "changed_paths": []},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _sha256(self, path: Path) -> str:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
