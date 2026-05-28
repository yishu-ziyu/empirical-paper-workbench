import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_writeback_execute import (
    build_auto_mode_formal_writeback_execute,
    write_auto_mode_formal_writeback_execute_outputs,
)


class AutoModeFormalWritebackExecuteTests(unittest.TestCase):
    """BDD: P7-M separates dry-run from apply manifest recording."""

    def test_bdd_p7m_ready_preflight_supports_dry_run_planning(self) -> None:
        """行为 1：ready execution preflight 可 dry-run 计划，但不写正式层。"""
        report = build_auto_mode_formal_writeback_execute(
            self._ready_execution_preflight(),
            mode="dry-run",
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_writeback_execute.v1")
        self.assertEqual(report["status"], "formal_writeback_dry_run_ready")
        self.assertEqual(report["mode"], "dry-run")
        self.assertTrue(report["can_apply_with_confirmation"])
        self.assertFalse(report["apply_manifest_recorded"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        categories = {operation["category"] for operation in report["planned_operations"]}
        self.assertEqual(
            categories,
            {
                "manuscript",
                "bibliography",
                "method_review",
                "statistical_results",
                "reproducibility",
                "package_artifacts",
            },
        )

    def test_bdd_p7m_blocks_when_execution_preflight_is_not_ready(self) -> None:
        """行为 2：P7-L blocked 时 execute 不能绕过。"""
        report = build_auto_mode_formal_writeback_execute(
            self._blocked_execution_preflight(),
            mode="dry-run",
        )

        self.assertEqual(report["status"], "blocked_by_execution_preflight")
        self.assertFalse(report["can_apply_with_confirmation"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertIn("execution_preflight_not_ready", report["blocking_reasons"])
        self.assertEqual(report["planned_operations"], [])

    def test_bdd_p7m_apply_requires_explicit_confirmation(self) -> None:
        """行为 3：apply 缺 confirm 时阻断。"""
        report = build_auto_mode_formal_writeback_execute(
            self._ready_execution_preflight(),
            mode="apply",
            confirm_apply=False,
            reviewer="unit_test_reviewer",
            note="Apply manifest request.",
        )

        self.assertEqual(report["status"], "blocked_by_missing_apply_confirmation")
        self.assertFalse(report["apply_manifest_recorded"])
        self.assertIn("confirm_apply_required", report["blocking_reasons"])

    def test_bdd_p7m_apply_requires_reviewer_and_note(self) -> None:
        """行为 4：apply 缺 reviewer/note 时阻断。"""
        report = build_auto_mode_formal_writeback_execute(
            self._ready_execution_preflight(),
            mode="apply",
            confirm_apply=True,
            reviewer="",
            note="",
        )

        self.assertEqual(report["status"], "blocked_by_apply_metadata")
        self.assertFalse(report["apply_manifest_recorded"])
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("apply_note_required", report["blocking_reasons"])

    def test_bdd_p7m_confirmed_apply_records_manifest_only(self) -> None:
        """行为 5：确认 apply 只写 apply manifest 和审计产物，不写正式层。"""
        report = build_auto_mode_formal_writeback_execute(
            self._ready_execution_preflight(),
            mode="apply",
            confirm_apply=True,
            reviewer="unit_test_reviewer",
            note="Record apply manifest for later target adapters.",
            apply_manifest_path=Path("workspace/formal_writeback_apply/custom/formal_writeback_apply_manifest.json"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path, manifest_path = write_auto_mode_formal_writeback_execute_outputs(
                project_root,
                report,
                apply_manifest_path=Path("workspace/formal_writeback_apply/custom/formal_writeback_apply_manifest.json"),
            )

            self.assertEqual(report["status"], "formal_writeback_apply_manifest_recorded")
            self.assertTrue(report["apply_manifest_recorded"])
            self.assertEqual(
                report["apply_manifest_path"],
                "workspace/formal_writeback_apply/custom/formal_writeback_apply_manifest.json",
            )
            self.assertFalse(report["formal_writeback_executed"])
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIsNotNone(manifest_path)
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], "p7.auto_mode_formal_writeback_apply_manifest.v1")
            self.assertEqual(len(manifest["operations"]), 6)
            self.assertFalse((project_root / "state/product/auto_mode_formal_writeback_execute.json").exists())
            self.assertFalse((project_root / "Manuscripts/sections/introduction.md").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())

    def test_bdd_p7m_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 6：CLI 默认读取当前 blocked preflight，写 blocked dry-run。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_writeback_execution_preflight.json",
                self._blocked_execution_preflight(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_writeback_execute.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_execution_preflight", result.stdout)
            self.assertIn("formal_writeback_executed=false", result.stdout)
            self.assertIn("apply_manifest_recorded=false", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_writeback_execute.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_writeback_execute.md").exists())
            self.assertFalse((project_root / "workspace/formal_writeback_apply/auto_mode/formal_writeback_apply_manifest.json").exists())

    def _ready_execution_preflight(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_writeback_execution_preflight.v1",
            "status": "ready_for_formal_writeback_execution_review",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "can_request_formal_writeback_execution": True,
            "requires_explicit_execute_command": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "execution_plan": [
                self._execution_item("manuscript"),
                self._execution_item("bibliography"),
                self._execution_item("method_review"),
                self._execution_item("statistical_results"),
                self._execution_item("reproducibility"),
                self._execution_item("package_artifacts"),
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_execution_preflight(self) -> dict:
        preflight = self._ready_execution_preflight()
        preflight["status"] = "blocked_by_formal_writeback_approval"
        preflight["can_request_formal_writeback_execution"] = False
        preflight["blocking_reasons"] = ["formal_writeback_approval_not_effective"]
        preflight["execution_plan"] = []
        return preflight

    def _execution_item(self, category: str) -> dict:
        return {
            "category": category,
            "label": category.replace("_", " ").title(),
            "evidence_refs": [{"target": f"{category}.md", "kind": "unit_test"}],
            "execution_status": "pending_explicit_execute_command",
            "requires_explicit_execute_command": True,
            "executed_by_this_command": False,
            "writeback_target_group": f"{category}_targets",
            "next_gates": ["formal_target_adapter"],
        }

    def _clean_boundary_flags(self) -> dict:
        return {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "reran_models": False,
            "modified_statistical_execution_artifacts": False,
        }

    def _source_paths(self) -> dict:
        return {
            "formal_writeback_execution_preflight": "Results/json/auto_mode_formal_writeback_execution_preflight.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
