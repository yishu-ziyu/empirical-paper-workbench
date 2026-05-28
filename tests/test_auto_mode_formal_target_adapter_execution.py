import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_execution import (
    build_auto_mode_formal_target_adapter_execution,
    write_auto_mode_formal_target_adapter_execution_outputs,
)


class AutoModeFormalTargetAdapterExecutionTests(unittest.TestCase):
    """BDD: P7-O gates formal target adapter execution without materializing targets."""

    def test_bdd_p7o_ready_readiness_supports_dry_run_execution_planning(self) -> None:
        """行为 1：ready readiness 可 dry-run adapter execution plan。"""
        report = build_auto_mode_formal_target_adapter_execution(
            self._ready_readiness(),
            mode="dry-run",
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_target_adapter_execution.v1")
        self.assertEqual(report["status"], "target_adapter_execution_dry_run_ready")
        self.assertEqual(report["mode"], "dry-run")
        self.assertTrue(report["can_execute_with_confirmation"])
        self.assertFalse(report["execution_manifest_recorded"])
        self.assertFalse(report["formal_target_adapters_executed"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertEqual(len(report["adapter_execution_plan"]), 6)
        self.assertTrue(all(item["execution_status"] == "planned_not_executed" for item in report["adapter_execution_plan"]))

    def test_bdd_p7o_blocks_when_readiness_is_not_ready(self) -> None:
        """行为 2：当前 P7-N blocked 时不能生成 execution plan。"""
        report = build_auto_mode_formal_target_adapter_execution(
            self._blocked_readiness(),
            mode="dry-run",
        )

        self.assertEqual(report["status"], "blocked_by_target_adapter_readiness")
        self.assertFalse(report["can_execute_with_confirmation"])
        self.assertFalse(report["formal_target_adapters_executed"])
        self.assertEqual(report["adapter_execution_plan"], [])
        self.assertIn("target_adapter_readiness_not_ready", report["blocking_reasons"])

    def test_bdd_p7o_execute_requires_explicit_confirmation(self) -> None:
        """行为 3：execute 缺 confirm 时阻断。"""
        report = build_auto_mode_formal_target_adapter_execution(
            self._ready_readiness(),
            mode="execute",
            confirm_execution=False,
            reviewer="unit_test_reviewer",
            note="Execute manifest request.",
        )

        self.assertEqual(report["status"], "blocked_by_missing_execution_confirmation")
        self.assertFalse(report["execution_manifest_recorded"])
        self.assertIn("confirm_execution_required", report["blocking_reasons"])

    def test_bdd_p7o_execute_requires_reviewer_and_note(self) -> None:
        """行为 4：execute 缺 reviewer/note 时阻断。"""
        report = build_auto_mode_formal_target_adapter_execution(
            self._ready_readiness(),
            mode="execute",
            confirm_execution=True,
            reviewer="",
            note="",
        )

        self.assertEqual(report["status"], "blocked_by_execution_metadata")
        self.assertFalse(report["execution_manifest_recorded"])
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("execution_note_required", report["blocking_reasons"])

    def test_bdd_p7o_confirmed_execute_records_manifest_only(self) -> None:
        """行为 5：确认 execute 只写 execution manifest，不创建 candidate target。"""
        report = build_auto_mode_formal_target_adapter_execution(
            self._ready_readiness(),
            mode="execute",
            confirm_execution=True,
            reviewer="unit_test_reviewer",
            note="Record target adapter execution manifest for later materialization.",
            execution_manifest_path=Path("workspace/formal_target_adapter_execution/custom/execution_manifest.json"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path, manifest_path = write_auto_mode_formal_target_adapter_execution_outputs(
                project_root,
                report,
                execution_manifest_path=Path("workspace/formal_target_adapter_execution/custom/execution_manifest.json"),
            )

            self.assertEqual(report["status"], "target_adapter_execution_manifest_recorded")
            self.assertTrue(report["execution_manifest_recorded"])
            self.assertEqual(
                report["execution_manifest_path"],
                "workspace/formal_target_adapter_execution/custom/execution_manifest.json",
            )
            self.assertFalse(report["formal_target_adapters_executed"])
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIsNotNone(manifest_path)
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], "p7.auto_mode_formal_target_adapter_execution_manifest.v1")
            self.assertEqual(len(manifest["adapter_execution_plan"]), 6)
            self.assertFalse((project_root / "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_target_adapter_execution.json").exists())

    def test_bdd_p7o_bad_adapter_mapping_blocks_execution(self) -> None:
        """行为 6：readiness 内部 mapping 非 ready 时阻断。"""
        readiness = self._ready_readiness()
        readiness["adapter_mappings"][0]["mapping_status"] = "blocked_by_unit_test"

        report = build_auto_mode_formal_target_adapter_execution(readiness, mode="dry-run")

        self.assertEqual(report["status"], "blocked_by_target_adapter_readiness")
        self.assertFalse(report["can_execute_with_confirmation"])
        self.assertIn(
            "adapter_mapping_not_ready:formal_manuscript_sources",
            report["blocking_reasons"],
        )

    def test_bdd_p7o_cli_defaults_to_current_blocked_readiness(self) -> None:
        """行为 7：CLI 默认读取当前 blocked readiness，写 blocked execution gate。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_target_adapter_readiness.json",
                self._blocked_readiness(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_execution.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_target_adapter_readiness", result.stdout)
            self.assertIn("formal_target_adapters_executed=false", result.stdout)
            self.assertIn("execution_manifest_recorded=false", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_target_adapter_execution.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_target_adapter_execution.md").exists())
            self.assertFalse((project_root / "workspace/formal_target_adapter_execution/auto_mode/formal_target_adapter_execution_manifest.json").exists())

    def _ready_readiness(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_readiness.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "ready_for_formal_target_adapter_review",
            "can_request_target_adapter_execution": True,
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "adapter_mappings": [
                self._adapter_mapping("formal_writeback::01::manuscript", "formal_manuscript_sources", "formal_manuscript_sources_adapter", ["manuscript/paper.md"]),
                self._adapter_mapping("formal_writeback::02::bibliography", "formal_bibliography_sources", "formal_bibliography_sources_adapter", ["bibliography/literature_review_packet.json"]),
                self._adapter_mapping("formal_writeback::03::method_review", "method_review_records", "method_review_records_adapter", ["reviews/method_gate.md"]),
                self._adapter_mapping("formal_writeback::04::statistical_results", "statistical_result_records", "statistical_result_records_adapter", ["evidence/results_evidence_package.json"]),
                self._adapter_mapping("formal_writeback::05::reproducibility", "reproducibility_records", "reproducibility_records_adapter", ["reproducibility/reproducibility_readme.md"]),
                self._adapter_mapping("formal_writeback::06::package_artifacts", "formal_package_records", "formal_package_records_adapter", ["manifest.json", "paper.pdf"]),
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_readiness(self) -> dict:
        readiness = self._ready_readiness()
        readiness["status"] = "blocked_by_apply_manifest"
        readiness["can_request_target_adapter_execution"] = False
        readiness["blocking_reasons"] = ["apply_manifest_missing_or_invalid_schema", "apply_manifest_operations_missing"]
        readiness["adapter_mappings"] = []
        return readiness

    def _adapter_mapping(
        self,
        operation_id: str,
        group: str,
        adapter_id: str,
        candidate_targets: list[str],
    ) -> dict:
        return {
            "operation_id": operation_id,
            "category": operation_id.rsplit("::", 1)[-1],
            "writeback_target_group": group,
            "adapter_id": adapter_id,
            "adapter_label": adapter_id.replace("_", " ").title(),
            "source_artifacts": [{"path": f"workspace/paper_packages/cgss_social_capital_happiness/{group}.json", "exists": True}],
            "candidate_targets": [
                {
                    "path": f"Submissions/auto_mode/cgss_social_capital_happiness/{target}",
                    "exists": False,
                    "will_be_written_by_this_command": False,
                }
                for target in candidate_targets
            ],
            "mapping_status": "ready_for_target_adapter",
            "requires_target_adapter_execution": True,
            "executed_by_this_command": False,
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
            "executed_target_adapters": False,
        }

    def _source_paths(self) -> dict:
        return {
            "target_adapter_readiness": "Results/json/auto_mode_formal_target_adapter_readiness.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
