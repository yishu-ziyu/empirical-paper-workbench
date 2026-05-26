import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalPaperPackageManifestCliTests(unittest.TestCase):
    """BDD: P5-B creates a formal package manifest after P5-A approval."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-paper-package-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_24_builds_package_manifest_and_skeleton_after_approval(self) -> None:
        approval_before = (self.project_root / "Results" / "json" / "formal_writeback_approval.json").read_text(
            encoding="utf-8"
        )
        protected_before = self._snapshot_protected_state()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_paper_package_manifest.json"
        review_path = self.project_root / "Reviews" / "formal_paper_package_manifest.md"
        package_root = self.project_root / "Submissions" / "formal_package"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(package_root.exists())

        manifest = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "p5.formal_paper_package_manifest.v1")
        self.assertEqual(manifest["status"], "formal_package_manifest_ready")
        self.assertTrue(manifest["can_build_package"])
        self.assertFalse(manifest["this_command_wrote_formal_state"])
        self.assertFalse(manifest["this_command_wrote_final_outputs"])
        self.assertFalse(manifest["formal_state_guard"]["changed"])
        self.assertEqual(manifest["source_approval"], "Results/json/formal_writeback_approval.json")
        self.assertEqual(manifest["approval_state_path"], "state/product/writeback_approvals.json")
        self.assertEqual(manifest["package_root"], "Submissions/formal_package")
        self.assertEqual(
            [item["category"] for item in manifest["package_sections"]],
            ["sections", "citations", "method_narrative", "result_tables", "reproducibility"],
        )

        for section in manifest["package_sections"]:
            self.assertTrue((self.project_root / section["directory"]).exists(), section["directory"])
            self.assertEqual(section["write_status"], "skeleton_only")
            self.assertEqual(section["evidence_level"], "local_file")

        readme_path = package_root / "README.md"
        self.assertTrue(readme_path.exists())
        self.assertIn("P5-B 正式论文包骨架", readme_path.read_text(encoding="utf-8"))

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P5-B 正式 paper package manifest", review_text)
        self.assertIn("formal_package_manifest_ready", review_text)

        self.assertEqual(
            (self.project_root / "Results" / "json" / "formal_writeback_approval.json").read_text(encoding="utf-8"),
            approval_before,
        )
        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.pdf").exists())
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "manuscript" / "paper.md").exists())

    def test_bdd_24_blocks_when_approval_report_is_not_approved(self) -> None:
        approval_path = self.project_root / "Results" / "json" / "formal_writeback_approval.json"
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
        approval["status"] = "needs_revision"
        approval["can_enter_p5"] = False
        approval_path.write_text(json.dumps(approval, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        manifest = json.loads(
            (self.project_root / "Results" / "json" / "formal_paper_package_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["status"], "blocked_by_approval")
        self.assertFalse(manifest["can_build_package"])
        self.assertIn("approval_report_not_approved_for_p5", manifest["blocking_reasons"])
        self.assertFalse((self.project_root / "Submissions" / "formal_package").exists())

    def test_bdd_24_blocks_when_state_ledger_does_not_match_report(self) -> None:
        ledger_path = self.project_root / "state" / "product" / "writeback_approvals.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger["formal_preflight_approvals"] = {}
        ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        manifest = json.loads(
            (self.project_root / "Results" / "json" / "formal_paper_package_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["status"], "blocked_by_approval")
        self.assertFalse(manifest["can_build_package"])
        self.assertIn("approval_state_missing_formal_entry", manifest["blocking_reasons"])
        self.assertFalse((self.project_root / "Submissions" / "formal_package").exists())

    def _run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_paper_package_manifest.py"),
                "--project-root",
                str(self.project_root),
                "--approval-report",
                "Results/json/formal_writeback_approval.json",
                "--approval-state",
                "state/product/writeback_approvals.json",
                "--output-report",
                "Results/json/formal_paper_package_manifest.json",
                "--output-review",
                "Reviews/formal_paper_package_manifest.md",
                "--package-root",
                "Submissions/formal_package",
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
        state_dir = root / "state" / "product"
        for directory in [results_dir, state_dir]:
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

        approval_entry = {
            "id": "formal_writeback_approval_formal_writeback_preflight",
            "preflight_id": "formal_writeback_preflight",
            "status": "approved",
            "writeback_scope_categories": [
                "sections",
                "citations",
                "method_narrative",
                "result_tables",
                "reproducibility",
            ],
            "can_enter_p5": True,
            "can_write_formal_package": True,
            "this_command_wrote_formal_state": False,
        }
        (state_dir / "writeback_approvals.json").write_text(
            json.dumps(
                {
                    "schema_version": "product.writeback_approvals.v1",
                    "approvals": {"legacy_candidate": {"status": "approved"}},
                    "formal_preflight_approvals": {
                        "formal_writeback_preflight": approval_entry,
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (results_dir / "formal_writeback_approval.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_writeback_approval.v1",
                    "source_preflight": "Results/json/formal_writeback_preflight.json",
                    "approval_path": "state/product/writeback_approvals.json",
                    "status": "approved_for_p5",
                    "can_enter_p5": True,
                    "can_write_formal_package": True,
                    "this_command_wrote_formal_state": False,
                    "writeback_scope_categories": [
                        "sections",
                        "citations",
                        "method_narrative",
                        "result_tables",
                        "reproducibility",
                    ],
                    "approval_entry": approval_entry,
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
