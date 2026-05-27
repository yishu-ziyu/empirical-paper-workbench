import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalPackageProvenanceLockCheckCliTests(unittest.TestCase):
    """BDD: P6-H1 checks whether the accepted formal package still has a locked candidate source."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-package-provenance-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root, candidate_matches_writeback=True)

    def test_bdd_44_marks_locked_when_candidate_and_final_artifacts_match_recorded_hashes(self) -> None:
        immutable_before = self._snapshot_immutable_inputs()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_package_provenance_lock_check.json"
        review_path = self.project_root / "Reviews" / "formal_package_provenance_lock_check.md"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.formal_package_provenance_lock_check.v1")
        self.assertEqual(report["status"], "provenance_locked")
        self.assertTrue(report["final_package_acceptance"]["can_continue_manual_acceptance"])
        self.assertEqual(report["candidate_source_lock"]["status"], "locked")
        self.assertEqual(report["final_artifact_lock"]["status"], "consistent")
        self.assertEqual(report["blocking_reasons"], [])
        self.assertEqual(report["warning_reasons"], [])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertFalse(report["boundary_flags"]["this_command_wrote_formal_state"])
        self.assertFalse(report["boundary_flags"]["this_command_wrote_final_outputs"])
        self.assertEqual(self._snapshot_immutable_inputs(), immutable_before)

    def test_bdd_44_warns_when_current_candidate_pdf_no_longer_matches_final_writeback_source(self) -> None:
        self._seed_project(self.project_root, candidate_matches_writeback=False)
        immutable_before = self._snapshot_immutable_inputs()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_package_provenance_lock_check.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "ready_for_manual_acceptance_with_provenance_warning")
        self.assertTrue(report["final_package_acceptance"]["can_continue_manual_acceptance"])
        self.assertEqual(report["candidate_source_lock"]["status"], "drifted")
        self.assertEqual(report["final_artifact_lock"]["status"], "consistent")
        self.assertIn("candidate_pdf_drifted_from_final_writeback_source", report["warning_reasons"])
        self.assertIn("candidate_pdf_same_size_but_hash_changed", report["warning_reasons"])
        self.assertEqual(report["blocking_reasons"], [])
        self.assertEqual(
            report["candidate_source_lock"]["recorded_sha256"],
            report["final_writeback"]["source_candidate_pdf_sha256"],
        )
        self.assertNotEqual(
            report["candidate_source_lock"]["current_sha256"],
            report["candidate_source_lock"]["recorded_sha256"],
        )
        self.assertEqual(
            {action["id"] for action in report["next_actions"]},
            {
                "freeze_approved_candidate_snapshot",
                "rerun_short_final_writeback_chain",
                "demote_current_candidate_as_historical",
            },
        )
        review_text = (self.project_root / "Reviews" / "formal_package_provenance_lock_check.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("candidate_pdf_drifted_from_final_writeback_source", review_text)
        self.assertIn("freeze_approved_candidate_snapshot", review_text)
        self.assertEqual(self._snapshot_immutable_inputs(), immutable_before)

    def test_bdd_44_blocks_when_final_pdf_no_longer_matches_the_submission_manifest(self) -> None:
        (self.project_root / "Submissions" / "formal_package" / "paper.pdf").write_bytes(b"mutated final pdf")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_package_provenance_lock_check.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_final_package_integrity")
        self.assertFalse(report["final_package_acceptance"]["can_continue_manual_acceptance"])
        self.assertEqual(report["final_artifact_lock"]["status"], "broken")
        self.assertIn("paper_pdf_hash_mismatch:submission_manifest", report["blocking_reasons"])

    def test_bdd_44_blocks_when_submission_summary_is_not_ready_for_manual_acceptance(self) -> None:
        summary_path = self.project_root / "Results" / "json" / "formal_submission_package_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["status"] = "blocked_by_package_consistency"
        summary["ready_for_manual_acceptance"] = False
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_package_provenance_lock_check.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_acceptance_summary")
        self.assertIn("formal_submission_package_summary_not_ready", report["blocking_reasons"])

    def _run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_package_provenance_lock_check.py"),
                "--project-root",
                str(self.project_root),
                "--final-writeback-report",
                "Results/json/formal_pdf_final_writeback.json",
                "--docx-export-report",
                "Results/json/formal_docx_export.json",
                "--submission-manifest-report",
                "Results/json/formal_submission_package_manifest.json",
                "--submission-summary-report",
                "Results/json/formal_submission_package_summary.json",
                "--package-manifest",
                "Submissions/formal_package/manifest.json",
                "--output-report",
                "Results/json/formal_package_provenance_lock_check.json",
                "--output-review",
                "Reviews/formal_package_provenance_lock_check.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def _snapshot_immutable_inputs(self) -> dict[str, bytes]:
        paths = [
            "Results/json/formal_pdf_final_writeback.json",
            "Results/json/formal_docx_export.json",
            "Results/json/formal_submission_package_manifest.json",
            "Results/json/formal_submission_package_summary.json",
            "Submissions/formal_package/paper_candidate.pdf",
            "Submissions/formal_package/paper.pdf",
            "Submissions/formal_package/paper.docx",
            "Submissions/formal_package/manifest.json",
        ]
        return {path: (self.project_root / path).read_bytes() for path in paths}

    def _seed_project(self, root: Path, *, candidate_matches_writeback: bool) -> None:
        results_dir = root / "Results" / "json"
        reviews_dir = root / "Reviews"
        state_dir = root / "state" / "product"
        package_dir = root / "Submissions" / "formal_package"
        for directory in [results_dir, reviews_dir, state_dir, package_dir]:
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

        original_candidate_bytes = b"%PDF-1.4\n% approved candidate fixture\n"
        drifted_candidate_bytes = b"%PDF-1.4\n% newer candidate draft\n"
        drifted_candidate_bytes = drifted_candidate_bytes.ljust(len(original_candidate_bytes), b"!")[
            : len(original_candidate_bytes)
        ]
        current_candidate_bytes = original_candidate_bytes if candidate_matches_writeback else drifted_candidate_bytes
        final_pdf = package_dir / "paper.pdf"
        candidate_pdf = package_dir / "paper_candidate.pdf"
        paper_docx = package_dir / "paper.docx"
        candidate_pdf.write_bytes(current_candidate_bytes)
        final_pdf.write_bytes(original_candidate_bytes)
        paper_docx.write_bytes(b"PK\x03\x04 final docx fixture\n")

        recorded_candidate_hash = self._sha256_bytes(original_candidate_bytes)
        final_pdf_hash = self._sha256(final_pdf)
        docx_hash = self._sha256(paper_docx)
        artifact_payload = {
            "paper_pdf": {
                "path": "Submissions/formal_package/paper.pdf",
                "exists": True,
                "bytes": final_pdf.stat().st_size,
                "sha256": final_pdf_hash,
                "source_report": "Results/json/formal_pdf_final_writeback.json",
            },
            "paper_docx": {
                "path": "Submissions/formal_package/paper.docx",
                "exists": True,
                "bytes": paper_docx.stat().st_size,
                "sha256": docx_hash,
                "source_report": "Results/json/formal_docx_export.json",
            },
        }
        package_manifest = {
            "schema_version": "p6.formal_submission_package_manifest.v1",
            "status": "formal_submission_package_ready",
            "artifacts": artifact_payload,
        }
        (package_dir / "manifest.json").write_text(
            json.dumps(package_manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (results_dir / "formal_pdf_final_writeback.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_pdf_final_writeback.v1",
                    "status": "final_pdf_written",
                    "source_candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                    "final_pdf": "Submissions/formal_package/paper.pdf",
                    "source_candidate_pdf_sha256": recorded_candidate_hash,
                    "final_pdf_sha256": final_pdf_hash,
                    "source_candidate_pdf_bytes": len(original_candidate_bytes),
                    "final_pdf_bytes": final_pdf.stat().st_size,
                    "final_writeback_authorized": True,
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
                    "docx": "Submissions/formal_package/paper.docx",
                    "docx_sha256": docx_hash,
                    "docx_bytes": paper_docx.stat().st_size,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (results_dir / "formal_submission_package_manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_submission_package_manifest.v1",
                    "status": "formal_submission_package_ready",
                    "package_manifest": "Submissions/formal_package/manifest.json",
                    "artifacts": artifact_payload,
                    "blocking_reasons": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (results_dir / "formal_submission_package_summary.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_submission_package_summary.v1",
                    "status": "ready_for_manual_acceptance",
                    "ready_for_manual_acceptance": True,
                    "blocking_reasons": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _sha256(self, path: Path) -> str:
        return self._sha256_bytes(path.read_bytes())

    def _sha256_bytes(self, payload: bytes) -> str:
        import hashlib

        return hashlib.sha256(payload).hexdigest()
