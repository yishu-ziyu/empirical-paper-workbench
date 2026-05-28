import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_materialization_execute import (
    build_auto_mode_formal_target_adapter_materialization_execute,
    write_auto_mode_formal_target_adapter_materialization_execute_outputs,
)


class AutoModeFormalTargetAdapterMaterializationExecuteTests(unittest.TestCase):
    """BDD: P7-Q gates adapter materialization and writes only candidate targets when confirmed."""

    def test_bdd_p7q_ready_preflight_supports_dry_run_planning(self) -> None:
        """行为 1：ready preflight 可 dry-run materialization plan。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._create_sources(project_root)
            report = build_auto_mode_formal_target_adapter_materialization_execute(
                project_root,
                self._ready_preflight(),
                mode="dry-run",
                source_paths=self._source_paths(),
            )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_target_adapter_materialization_execute.v1")
        self.assertEqual(report["status"], "adapter_materialization_dry_run_ready")
        self.assertTrue(report["can_materialize_with_confirmation"])
        self.assertFalse(report["candidate_targets_materialized"])
        self.assertFalse(report["formal_target_adapters_executed"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertEqual(len(report["materialization_operations"]), 6)
        self.assertTrue(
            all(item["operation_status"] == "planned_not_materialized" for item in report["materialization_operations"])
        )

    def test_bdd_p7q_current_blocked_preflight_blocks_materialization(self) -> None:
        """行为 2：当前 P7-P blocked 时不能生成 materialization operations。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_auto_mode_formal_target_adapter_materialization_execute(
                Path(tmpdir),
                self._blocked_preflight(),
                mode="dry-run",
            )

        self.assertEqual(report["status"], "blocked_by_materialization_preflight")
        self.assertFalse(report["can_materialize_with_confirmation"])
        self.assertEqual(report["materialization_operations"], [])
        self.assertIn("materialization_preflight_not_ready", report["blocking_reasons"])

    def test_bdd_p7q_materialize_requires_explicit_confirmation(self) -> None:
        """行为 3：materialize 缺 confirm 时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._create_sources(project_root)
            report = build_auto_mode_formal_target_adapter_materialization_execute(
                project_root,
                self._ready_preflight(),
                mode="materialize",
                confirm_materialize=False,
                reviewer="unit_test_reviewer",
                note="Materialize candidate targets.",
            )

        self.assertEqual(report["status"], "blocked_by_missing_materialization_confirmation")
        self.assertFalse(report["candidate_targets_materialized"])
        self.assertIn("confirm_materialize_required", report["blocking_reasons"])

    def test_bdd_p7q_materialize_requires_reviewer_and_note(self) -> None:
        """行为 4：materialize 缺 reviewer/note 时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._create_sources(project_root)
            report = build_auto_mode_formal_target_adapter_materialization_execute(
                project_root,
                self._ready_preflight(),
                mode="materialize",
                confirm_materialize=True,
                reviewer="",
                note="",
            )

        self.assertEqual(report["status"], "blocked_by_materialization_metadata")
        self.assertFalse(report["candidate_targets_materialized"])
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("materialization_note_required", report["blocking_reasons"])

    def test_bdd_p7q_confirmed_materialize_writes_candidate_targets_and_manifest_only(self) -> None:
        """行为 5：确认 materialize 写 candidate targets 和 manifest，不写正式层。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._create_sources(project_root)
            report = build_auto_mode_formal_target_adapter_materialization_execute(
                project_root,
                self._ready_preflight(),
                mode="materialize",
                confirm_materialize=True,
                reviewer="unit_test_reviewer",
                note="Create candidate targets for review.",
                materialization_manifest_path=Path("workspace/formal_target_adapter_materialization/custom/materialization_manifest.json"),
            )
            report_path, review_path, manifest_path = write_auto_mode_formal_target_adapter_materialization_execute_outputs(
                project_root,
                report,
                materialization_manifest_path=Path("workspace/formal_target_adapter_materialization/custom/materialization_manifest.json"),
            )

            self.assertEqual(report["status"], "adapter_materialization_completed")
            self.assertTrue(report["candidate_targets_materialized"])
            self.assertFalse(report["formal_target_adapters_executed"])
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIsNotNone(manifest_path)
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                manifest["schema_version"],
                "p7.auto_mode_formal_target_adapter_materialization_manifest.v1",
            )
            self.assertEqual(len(manifest["materialized_targets"]), 6)
            target = project_root / "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md"
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(encoding="utf-8"), "source::formal_manuscript_sources\n")
            self.assertFalse((project_root / "state/product/auto_mode_formal_target_adapter_materialization_execute.json").exists())

    def test_bdd_p7q_missing_source_or_existing_target_blocks_materialization(self) -> None:
        """行为 6：缺 source 或 target 已存在时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._create_sources(project_root)
            (project_root / "workspace/paper_packages/cgss_social_capital_happiness/formal_bibliography_sources.json").unlink()
            existing_target = project_root / "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md"
            existing_target.parent.mkdir(parents=True, exist_ok=True)
            existing_target.write_text("existing target\n", encoding="utf-8")

            report = build_auto_mode_formal_target_adapter_materialization_execute(
                project_root,
                self._ready_preflight(),
                mode="materialize",
                confirm_materialize=True,
                reviewer="unit_test_reviewer",
                note="Attempt materialization.",
            )

        self.assertEqual(report["status"], "blocked_by_materialization_contract")
        self.assertFalse(report["candidate_targets_materialized"])
        self.assertIn("materialization_source_missing:formal_bibliography_sources", report["blocking_reasons"])
        self.assertIn("materialization_target_already_exists:formal_manuscript_sources", report["blocking_reasons"])

    def test_bdd_p7q_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 7：CLI 默认读取当前 blocked preflight，不创建 candidate target。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_target_adapter_materialization_preflight.json",
                self._blocked_preflight(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_materialization_execute.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_materialization_preflight", result.stdout)
            self.assertIn("candidate_targets_materialized=false", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_target_adapter_materialization_execute.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_target_adapter_materialization_execute.md").exists())
            self.assertFalse(
                (project_root / "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md").exists()
            )

    def _ready_preflight(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_materialization_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "ready_for_adapter_materialization_review",
            "can_request_adapter_materialization": True,
            "requires_explicit_materialize_command": True,
            "candidate_targets_materialized": False,
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "materialization_plan": [
                self._plan_item("01", "formal_manuscript_sources", "formal_manuscript_sources_adapter", "manuscript/paper.md"),
                self._plan_item("02", "formal_bibliography_sources", "formal_bibliography_sources_adapter", "bibliography/literature_review_packet.json"),
                self._plan_item("03", "method_review_records", "method_review_records_adapter", "reviews/method_gate.md"),
                self._plan_item("04", "statistical_result_records", "statistical_result_records_adapter", "evidence/results_evidence_package.json"),
                self._plan_item("05", "reproducibility_records", "reproducibility_records_adapter", "reproducibility/reproducibility_readme.md"),
                self._plan_item("06", "formal_package_records", "formal_package_records_adapter", "manifest.json"),
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_preflight(self) -> dict:
        preflight = self._ready_preflight()
        preflight["status"] = "blocked_by_target_adapter_execution"
        preflight["can_request_adapter_materialization"] = False
        preflight["requires_explicit_materialize_command"] = False
        preflight["blocking_reasons"] = [
            "target_adapter_execution_not_manifest_recorded",
            "target_adapter_execution_manifest_not_recorded",
        ]
        preflight["materialization_plan"] = []
        return preflight

    def _plan_item(self, number: str, group: str, adapter_id: str, target: str) -> dict:
        return {
            "materialization_id": f"materialization::{number}::{group}",
            "execution_id": f"target_adapter::{number}::{group}",
            "operation_id": f"formal_writeback::{number}::{group}",
            "category": group,
            "writeback_target_group": group,
            "adapter_id": adapter_id,
            "source_artifacts": [
                {
                    "path": f"workspace/paper_packages/cgss_social_capital_happiness/{group}.json",
                    "exists": True,
                }
            ],
            "candidate_targets": [
                {
                    "path": f"Submissions/auto_mode/cgss_social_capital_happiness/{target}",
                    "exists": False,
                    "will_be_written_by_this_command": False,
                }
            ],
            "materialization_status": "planned_not_materialized",
            "requires_explicit_materialize_command": True,
            "will_materialize_by_this_command": False,
        }

    def _create_sources(self, project_root: Path) -> None:
        for item in self._ready_preflight()["materialization_plan"]:
            source = project_root / item["source_artifacts"][0]["path"]
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(f"source::{item['writeback_target_group']}\n", encoding="utf-8")

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
            "executed_target_adapters": False,
            "created_candidate_targets": False,
            "materialized_candidate_targets": False,
        }

    def _source_paths(self) -> dict:
        return {
            "materialization_preflight": "Results/json/auto_mode_formal_target_adapter_materialization_preflight.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
