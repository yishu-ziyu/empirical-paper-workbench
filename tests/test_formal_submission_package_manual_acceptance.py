import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalSubmissionPackageManualAcceptanceCliTests(unittest.TestCase):
    """BDD: P6-H4 records the human acceptance decision for the final submission package."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-package-manual-acceptance-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root, ready=True)

    def test_bdd_47_accept_records_human_decision_without_touching_formal_package(self) -> None:
        immutable_before = self._snapshot_immutable_package()
        protected_before = self._snapshot_protected_formal_state()

        result = self._run_cli("--decision", "accept", "--actor", "mahaoxuan", "--note", "PDF 和 DOCX 已人工验收。")
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_submission_package_manual_acceptance.json"
        state_path = self.project_root / "state" / "product" / "formal_submission_package_manual_acceptance.json"
        review_path = self.project_root / "Reviews" / "formal_submission_package_manual_acceptance.md"
        self.assertTrue(report_path.exists())
        self.assertTrue(state_path.exists())
        self.assertTrue(review_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(report, state)
        self.assertEqual(report["schema_version"], "p6.formal_submission_package_manual_acceptance.v1")
        self.assertEqual(report["status"], "formal_submission_package_accepted")
        self.assertEqual(report["decision"], "accept")
        self.assertEqual(report["actor"], "mahaoxuan")
        self.assertTrue(report["accepted"])
        self.assertFalse(report["needs_revision"])
        self.assertEqual(report["accepted_artifacts"]["paper_pdf"]["path"], "Submissions/formal_package/paper.pdf")
        self.assertEqual(report["accepted_artifacts"]["paper_docx"]["path"], "Submissions/formal_package/paper.docx")
        self.assertEqual(len(report["accepted_artifacts"]["paper_pdf"]["sha256"]), 64)
        self.assertEqual(len(report["accepted_artifacts"]["paper_docx"]["sha256"]), 64)
        self.assertFalse(report["boundary_flags"]["this_command_wrote_final_outputs"])
        self.assertFalse(report["boundary_flags"]["this_command_wrote_formal_research_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["next_action"]["id"], "freeze_submission_package_acceptance")

        self.assertIn("formal_submission_package_accepted", review_path.read_text(encoding="utf-8"))
        self.assertEqual(self._snapshot_immutable_package(), immutable_before)
        self.assertEqual(self._snapshot_protected_formal_state(), protected_before)

    def test_bdd_47_needs_revision_records_non_accepting_decision(self) -> None:
        result = self._run_cli("--decision", "needs_revision", "--actor", "mahaoxuan", "--note", "摘要页需要补一行说明。")
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_submission_package_manual_acceptance.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "formal_submission_package_needs_revision")
        self.assertEqual(report["decision"], "needs_revision")
        self.assertFalse(report["accepted"])
        self.assertTrue(report["needs_revision"])
        self.assertEqual(report["next_action"]["id"], "revise_formal_submission_package")

    def test_bdd_47_defer_records_pending_human_review_without_accepting_package(self) -> None:
        result = self._run_cli("--decision", "defer", "--actor", "codex", "--note", "等待用户打开 PDF 和 DOCX 后确认。")
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_submission_package_manual_acceptance.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "pending_human_manual_acceptance")
        self.assertEqual(report["decision"], "defer")
        self.assertFalse(report["accepted"])
        self.assertFalse(report["needs_revision"])
        self.assertEqual(report["next_action"]["id"], "open_and_review_pdf_docx")

    def test_bdd_47_blocks_when_summary_is_not_ready_for_manual_acceptance(self) -> None:
        self._seed_project(self.project_root, ready=False)
        protected_before = self._snapshot_protected_formal_state()

        result = self._run_cli("--decision", "accept", "--actor", "mahaoxuan", "--note", "尝试验收。")
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_submission_package_manual_acceptance.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_submission_package_summary")
        self.assertFalse(report["accepted"])
        self.assertIn("summary_not_ready_for_manual_acceptance", report["blocking_reasons"])
        self.assertEqual(self._snapshot_protected_formal_state(), protected_before)

    def _run_cli(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_submission_package_manual_acceptance.py"),
                "--project-root",
                str(self.project_root),
                "--summary",
                "state/product/formal_submission_package_summary.json",
                "--output-report",
                "Results/json/formal_submission_package_manual_acceptance.json",
                "--output-state",
                "state/product/formal_submission_package_manual_acceptance.json",
                "--output-review",
                "Reviews/formal_submission_package_manual_acceptance.md",
                *extra_args,
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def _snapshot_immutable_package(self) -> dict[str, bytes]:
        paths = [
            "Submissions/formal_package/paper.pdf",
            "Submissions/formal_package/paper.docx",
            "Submissions/formal_package/manifest.json",
            "state/product/formal_submission_package_summary.json",
        ]
        return {path: (self.project_root / path).read_bytes() for path in paths}

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

    def _seed_project(self, root: Path, *, ready: bool) -> None:
        results_dir = root / "Results" / "json"
        state_dir = root / "state" / "product"
        package_dir = root / "Submissions" / "formal_package"
        reviews_dir = root / "Reviews"
        for directory in [results_dir, state_dir, package_dir, reviews_dir]:
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
        package_manifest = package_dir / "manifest.json"
        paper_pdf.write_bytes(b"%PDF-1.4\n% accepted final pdf\n")
        paper_docx.write_bytes(b"PK\x03\x04 accepted final docx\n")
        package_manifest.write_text(json.dumps({"status": "formal_submission_package_ready"}), encoding="utf-8")

        summary = {
            "schema_version": "p6.formal_submission_package_summary.v1",
            "status": "ready_for_manual_acceptance" if ready else "blocked_by_package_consistency",
            "ready_for_manual_acceptance": ready,
            "artifacts": {
                "paper_pdf": {
                    "path": "Submissions/formal_package/paper.pdf",
                    "exists": True,
                    "bytes": paper_pdf.stat().st_size,
                    "sha256": self._sha256(paper_pdf),
                },
                "paper_docx": {
                    "path": "Submissions/formal_package/paper.docx",
                    "exists": True,
                    "bytes": paper_docx.stat().st_size,
                    "sha256": self._sha256(paper_docx),
                },
            },
            "manual_acceptance": {
                "status": "pending_manual_acceptance" if ready else "blocked",
                "next_action": "open_and_review_pdf_docx",
            },
            "blocking_reasons": [] if ready else ["paper_pdf_hash_mismatch:submission_manifest"],
            "formal_state_guard": {"changed": False, "changed_paths": []},
        }
        (state_dir / "formal_submission_package_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _sha256(self, path: Path) -> str:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest()
