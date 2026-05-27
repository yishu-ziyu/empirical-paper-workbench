import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalSubmissionPackageSummaryCliTests(unittest.TestCase):
    """BDD: P6-E1 turns the P6-D manifest into a compact product acceptance state."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-submission-summary-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_39_writes_product_summary_without_opening_or_touching_outputs(self) -> None:
        protected_before = self._snapshot_protected_formal_state()
        immutable_before = self._snapshot_immutable_inputs()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_submission_package_summary.json"
        summary_path = self.project_root / "state" / "product" / "formal_submission_package_summary.json"
        review_path = self.project_root / "Reviews" / "formal_submission_package_summary.md"
        self.assertTrue(report_path.exists())
        self.assertTrue(summary_path.exists())
        self.assertTrue(review_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(report, summary)
        self.assertEqual(summary["schema_version"], "p6.formal_submission_package_summary.v1")
        self.assertEqual(summary["status"], "ready_for_manual_acceptance")
        self.assertTrue(summary["ready_for_manual_acceptance"])
        self.assertEqual(summary["source_manifest"]["path"], "Results/json/formal_submission_package_manifest.json")
        self.assertEqual(len(summary["source_manifest"]["sha256"]), 64)
        self.assertEqual(summary["manual_acceptance"]["status"], "pending_manual_acceptance")
        self.assertEqual(summary["manual_acceptance"]["next_action"], "open_and_review_pdf_docx")
        self.assertEqual({target["id"] for target in summary["open_targets"]}, {"paper_pdf", "paper_docx"})
        for target in summary["open_targets"]:
            self.assertIn("open", target["open_command"])
            self.assertTrue(target["exists"])
            self.assertGreater(target["bytes"], 0)
            self.assertEqual(len(target["sha256"]), 64)
        self.assertGreaterEqual(len(summary["visible_summary"]), 4)
        self.assertFalse(summary["boundary_flags"]["this_command_opened_files"])
        self.assertFalse(summary["boundary_flags"]["this_command_rendered_pdf"])
        self.assertFalse(summary["boundary_flags"]["this_command_rendered_docx"])
        self.assertFalse(summary["boundary_flags"]["this_command_wrote_final_outputs"])
        self.assertFalse(summary["boundary_flags"]["this_command_wrote_formal_research_state"])
        self.assertFalse(summary["formal_state_guard"]["changed"])

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P6-E 正式包产品验收入口", review_text)
        self.assertIn("ready_for_manual_acceptance", review_text)
        self.assertIn("Submissions/formal_package/paper.pdf", review_text)

        self.assertEqual(self._snapshot_protected_formal_state(), protected_before)
        self.assertEqual(self._snapshot_immutable_inputs(), immutable_before)

    def test_bdd_46_exposes_approved_candidate_snapshot_in_acceptance_summary(self) -> None:
        self._seed_approved_candidate_snapshot()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        summary = json.loads(
            (self.project_root / "state" / "product" / "formal_submission_package_summary.json").read_text(
                encoding="utf-8"
            )
        )
        snapshot_summary = summary["approved_candidate_snapshot"]
        self.assertEqual(snapshot_summary["status"], "available")
        self.assertEqual(snapshot_summary["authority"], "formal_pdf_final_writeback")
        self.assertEqual(snapshot_summary["approved_candidate"]["sha256"], summary["artifacts"]["paper_pdf"]["sha256"])
        self.assertEqual(snapshot_summary["recovered_from"]["path"], "Submissions/formal_package/paper.pdf")
        self.assertFalse(snapshot_summary["current_candidate"]["authoritative_for_current_formal_package"])
        self.assertEqual(snapshot_summary["current_candidate"]["treatment"], "historical_candidate_or_next_draft")
        self.assertIn("approved_candidate_authority", {item["id"] for item in summary["visible_summary"]})

    def test_bdd_39_blocks_when_submission_manifest_is_not_ready(self) -> None:
        report_path = self.project_root / "Results" / "json" / "formal_submission_package_manifest.json"
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        payload["status"] = "blocked_by_docx_export"
        payload["blocking_reasons"] = ["p6c_docx_export_not_exported"]
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        summary = json.loads(
            (self.project_root / "state" / "product" / "formal_submission_package_summary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(summary["status"], "blocked_by_submission_manifest")
        self.assertFalse(summary["ready_for_manual_acceptance"])
        self.assertIn("submission_manifest_not_ready", summary["blocking_reasons"])
        self.assertEqual(summary["open_targets"], [])

    def test_bdd_39_blocks_when_pdf_disappears_after_manifest(self) -> None:
        (self.project_root / "Submissions" / "formal_package" / "paper.pdf").unlink()

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        summary = json.loads(
            (self.project_root / "state" / "product" / "formal_submission_package_summary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(summary["status"], "blocked_by_package_artifacts")
        self.assertIn("paper_pdf_missing", summary["blocking_reasons"])
        self.assertEqual(summary["open_targets"], [])

    def test_bdd_39_blocks_when_docx_hash_no_longer_matches_manifest(self) -> None:
        (self.project_root / "Submissions" / "formal_package" / "paper.docx").write_bytes(b"mutated docx")

        result = self._run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)

        summary = json.loads(
            (self.project_root / "state" / "product" / "formal_submission_package_summary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(summary["status"], "blocked_by_package_consistency")
        self.assertIn("paper_docx_hash_mismatch:submission_manifest", summary["blocking_reasons"])
        self.assertEqual(summary["open_targets"], [])

    def _run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_submission_package_summary.py"),
                "--project-root",
                str(self.project_root),
                "--source-manifest",
                "Results/json/formal_submission_package_manifest.json",
                "--output-report",
                "Results/json/formal_submission_package_summary.json",
                "--output-summary",
                "state/product/formal_submission_package_summary.json",
                "--output-review",
                "Reviews/formal_submission_package_summary.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def _snapshot_protected_formal_state(self) -> dict[str, str]:
        state_dir = self.project_root / "state" / "product"
        protected_names = [
            "research_question.json",
            "variable_roles.json",
            "variable_role_set.json",
            "design_spec.json",
            "run_plan.json",
            "supervisor_plan.json",
            "agent_task_queue.json",
            "writeback_approvals.json",
        ]
        return {name: (state_dir / name).read_text(encoding="utf-8") for name in protected_names}

    def _snapshot_immutable_inputs(self) -> dict[str, bytes]:
        paths = [
            "Submissions/formal_package/paper.pdf",
            "Submissions/formal_package/paper.docx",
            "Submissions/formal_package/manifest.json",
            "Results/json/formal_submission_package_manifest.json",
        ]
        return {path: (self.project_root / path).read_bytes() for path in paths}

    def _seed_approved_candidate_snapshot(self) -> None:
        package_dir = self.project_root / "Submissions" / "formal_package"
        snapshot_path = package_dir / "provenance" / "approved_candidate_snapshot.json"
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        paper_pdf = package_dir / "paper.pdf"
        snapshot_path.write_text(
            json.dumps(
                {
                    "schema_version": "p6.approved_candidate_snapshot.v1",
                    "status": "approved_candidate_snapshot_frozen",
                    "authority": "formal_pdf_final_writeback",
                    "approved_candidate": {
                        "source_candidate_path_at_writeback": "Submissions/formal_package/paper_candidate.pdf",
                        "sha256": self._sha256(paper_pdf),
                        "bytes": paper_pdf.stat().st_size,
                    },
                    "recovered_from": {
                        "path": "Submissions/formal_package/paper.pdf",
                        "exists": True,
                        "sha256": self._sha256(paper_pdf),
                        "bytes": paper_pdf.stat().st_size,
                    },
                    "current_candidate": {
                        "path": "Submissions/formal_package/paper_candidate.pdf",
                        "exists": True,
                        "sha256": "draft-hash",
                        "bytes": paper_pdf.stat().st_size,
                        "authoritative_for_current_formal_package": False,
                        "treatment": "historical_candidate_or_next_draft",
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _seed_project(self, root: Path) -> None:
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

        paper_pdf = package_dir / "paper.pdf"
        paper_docx = package_dir / "paper.docx"
        paper_pdf.write_bytes(b"%PDF-1.4\n% final pdf fixture\n")
        paper_docx.write_bytes(b"PK\x03\x04 final docx fixture\n")
        pdf_hash = self._sha256(paper_pdf)
        docx_hash = self._sha256(paper_docx)
        artifact_payload = {
            "paper_pdf": {
                "path": "Submissions/formal_package/paper.pdf",
                "exists": True,
                "bytes": paper_pdf.stat().st_size,
                "sha256": pdf_hash,
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
            "generated_at": "2026-05-27T00:00:00+00:00",
            "status": "formal_submission_package_ready",
            "package_root": "Submissions/formal_package",
            "artifacts": artifact_payload,
            "manual_acceptance": {
                "human_status": "pending_manual_acceptance",
                "checklist": [
                    {"id": "open_pdf", "label": "打开 PDF，确认页面可读、标题和章节存在"},
                    {"id": "open_docx", "label": "打开 DOCX，确认正文、标题和引用字段可读"},
                    {"id": "fingerprints", "label": "核对 PDF/DOCX sha256 与 manifest 一致"},
                ],
            },
            "reproduce_commands": [
                ["python3", "Program/formal_submission_package_manifest.py", "--project-root", "."]
            ],
        }
        (package_dir / "manifest.json").write_text(
            json.dumps(package_manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report_payload = {
            **package_manifest,
            "package_manifest": "Submissions/formal_package/manifest.json",
            "package_manifest_written": True,
            "blocking_reasons": [],
            "boundary_flags": {
                "this_command_rendered_pdf": False,
                "this_command_rendered_docx": False,
                "this_command_wrote_final_outputs": False,
                "this_command_wrote_formal_state": False,
            },
            "formal_state_guard": {"changed": False, "changed_paths": []},
        }
        (results_dir / "formal_submission_package_manifest.json").write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _sha256(self, path: Path) -> str:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
