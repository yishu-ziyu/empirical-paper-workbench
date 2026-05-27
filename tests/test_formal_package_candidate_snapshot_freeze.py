import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalPackageCandidateSnapshotFreezeCliTests(unittest.TestCase):
    """BDD: P6-H2 freezes the approved candidate source without rewriting final artifacts."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="candidate-snapshot-freeze-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root, provenance_status="ready_for_manual_acceptance_with_provenance_warning")

    def test_bdd_45_freezes_approved_candidate_snapshot_from_final_writeback_record(self) -> None:
        immutable_before = self._snapshot_immutable_inputs()
        formal_state_before = self._snapshot_formal_state()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_package_candidate_snapshot_freeze.json"
        review_path = self.project_root / "Reviews" / "formal_package_candidate_snapshot_freeze.md"
        snapshot_path = self.project_root / "Submissions" / "formal_package" / "provenance" / "approved_candidate_snapshot.json"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(snapshot_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.formal_package_candidate_snapshot_freeze.v1")
        self.assertEqual(report["status"], "approved_candidate_snapshot_frozen")
        self.assertTrue(report["snapshot_written"])
        self.assertEqual(report["snapshot"]["path"], "Submissions/formal_package/provenance/approved_candidate_snapshot.json")
        self.assertEqual(snapshot["status"], "approved_candidate_snapshot_frozen")
        self.assertEqual(snapshot["authority"], "formal_pdf_final_writeback")
        self.assertEqual(snapshot["approved_candidate"]["sha256"], report["final_writeback"]["source_candidate_pdf_sha256"])
        self.assertEqual(snapshot["recovered_from"]["path"], "Submissions/formal_package/paper.pdf")
        self.assertFalse(snapshot["current_candidate"]["authoritative_for_current_formal_package"])
        self.assertEqual(snapshot["current_candidate"]["treatment"], "historical_candidate_or_next_draft")
        self.assertFalse(report["boundary_flags"]["this_command_wrote_final_outputs"])
        self.assertFalse(report["boundary_flags"]["this_command_wrote_formal_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(self._snapshot_immutable_inputs(), immutable_before)
        self.assertEqual(self._snapshot_formal_state(), formal_state_before)

    def test_bdd_45_blocks_when_provenance_lock_reports_broken_final_artifacts(self) -> None:
        self._seed_project(self.project_root, provenance_status="blocked_by_final_package_integrity")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_package_candidate_snapshot_freeze.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_provenance_lock")
        self.assertFalse(report["snapshot_written"])
        self.assertIn("provenance_lock_not_acceptance_ready", report["blocking_reasons"])
        self.assertFalse(
            (self.project_root / "Submissions" / "formal_package" / "provenance" / "approved_candidate_snapshot.json").exists()
        )

    def _run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_package_candidate_snapshot_freeze.py"),
                "--project-root",
                str(self.project_root),
                "--provenance-lock-report",
                "Results/json/formal_package_provenance_lock_check.json",
                "--final-writeback-report",
                "Results/json/formal_pdf_final_writeback.json",
                "--output-report",
                "Results/json/formal_package_candidate_snapshot_freeze.json",
                "--output-review",
                "Reviews/formal_package_candidate_snapshot_freeze.md",
                "--output-snapshot",
                "Submissions/formal_package/provenance/approved_candidate_snapshot.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def _snapshot_immutable_inputs(self) -> dict[str, bytes]:
        paths = [
            "Results/json/formal_package_provenance_lock_check.json",
            "Results/json/formal_pdf_final_writeback.json",
            "Submissions/formal_package/paper_candidate.pdf",
            "Submissions/formal_package/paper.pdf",
            "Submissions/formal_package/paper.docx",
            "Submissions/formal_package/manifest.json",
        ]
        return {path: (self.project_root / path).read_bytes() for path in paths}

    def _snapshot_formal_state(self) -> dict[str, str]:
        state_dir = self.project_root / "state" / "product"
        return {path.name: path.read_text(encoding="utf-8") for path in sorted(state_dir.glob("*.json"))}

    def _seed_project(self, root: Path, *, provenance_status: str) -> None:
        results_dir = root / "Results" / "json"
        state_dir = root / "state" / "product"
        package_dir = root / "Submissions" / "formal_package"
        for directory in [results_dir, state_dir, package_dir]:
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

        final_pdf = package_dir / "paper.pdf"
        candidate_pdf = package_dir / "paper_candidate.pdf"
        paper_docx = package_dir / "paper.docx"
        final_pdf.write_bytes(b"%PDF-1.4\n% approved candidate fixture\n")
        candidate_pdf.write_bytes(b"%PDF-1.4\n% newer candidate draft!!!!\n")
        paper_docx.write_bytes(b"PK\x03\x04 final docx fixture\n")
        final_pdf_sha = self._sha256(final_pdf)
        candidate_sha = self._sha256(candidate_pdf)
        (package_dir / "manifest.json").write_text(
            json.dumps({"status": "formal_submission_package_ready"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (results_dir / "formal_pdf_final_writeback.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_pdf_final_writeback.v1",
                    "status": "final_pdf_written",
                    "source_candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                    "final_pdf": "Submissions/formal_package/paper.pdf",
                    "source_candidate_pdf_sha256": final_pdf_sha,
                    "final_pdf_sha256": final_pdf_sha,
                    "source_candidate_pdf_bytes": final_pdf.stat().st_size,
                    "final_pdf_bytes": final_pdf.stat().st_size,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        blocking_reasons = ["paper_pdf_hash_mismatch:submission_manifest"] if provenance_status.startswith("blocked") else []
        (results_dir / "formal_package_provenance_lock_check.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.formal_package_provenance_lock_check.v1",
                    "status": provenance_status,
                    "final_package_acceptance": {
                        "can_continue_manual_acceptance": not blocking_reasons,
                        "status": "available" if not blocking_reasons else "blocked",
                    },
                    "candidate_source_lock": {
                        "status": "drifted",
                        "path": "Submissions/formal_package/paper_candidate.pdf",
                        "exists": True,
                        "recorded_bytes": final_pdf.stat().st_size,
                        "current_bytes": candidate_pdf.stat().st_size,
                        "recorded_sha256": final_pdf_sha,
                        "current_sha256": candidate_sha,
                        "warning_reasons": ["candidate_pdf_drifted_from_final_writeback_source"],
                    },
                    "final_artifact_lock": {
                        "status": "consistent" if not blocking_reasons else "broken",
                        "artifacts": {
                            "paper_pdf": {
                                "path": "Submissions/formal_package/paper.pdf",
                                "exists": True,
                                "bytes": final_pdf.stat().st_size,
                                "sha256": final_pdf_sha,
                                "blocking_reasons": [],
                            },
                            "paper_docx": {
                                "path": "Submissions/formal_package/paper.docx",
                                "exists": True,
                                "bytes": paper_docx.stat().st_size,
                                "sha256": self._sha256(paper_docx),
                                "blocking_reasons": [],
                            },
                        },
                        "blocking_reasons": blocking_reasons,
                    },
                    "blocking_reasons": blocking_reasons,
                    "warning_reasons": ["candidate_pdf_drifted_from_final_writeback_source"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _sha256(self, path: Path) -> str:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest()
