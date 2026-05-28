import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_materialization_preflight import (
    build_auto_mode_formal_target_adapter_materialization_preflight,
    write_auto_mode_formal_target_adapter_materialization_preflight_outputs,
)


class AutoModeFormalTargetAdapterMaterializationPreflightTests(unittest.TestCase):
    """BDD: P7-P checks adapter materialization readiness without creating targets."""

    def test_bdd_p7p_recorded_execution_manifest_supports_materialization_preflight(self) -> None:
        """行为 1：已记录 execution manifest 时生成 materialization 预检计划。"""
        report = build_auto_mode_formal_target_adapter_materialization_preflight(
            self._ready_execution_report(),
            self._execution_manifest(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(
            report["schema_version"],
            "p7.auto_mode_formal_target_adapter_materialization_preflight.v1",
        )
        self.assertEqual(report["status"], "ready_for_adapter_materialization_review")
        self.assertTrue(report["can_request_adapter_materialization"])
        self.assertTrue(report["requires_explicit_materialize_command"])
        self.assertFalse(report["candidate_targets_materialized"])
        self.assertFalse(report["formal_target_adapters_executed"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertEqual(len(report["materialization_plan"]), 6)
        self.assertTrue(
            all(item["materialization_status"] == "planned_not_materialized" for item in report["materialization_plan"])
        )
        self.assertTrue(all(item["will_materialize_by_this_command"] is False for item in report["materialization_plan"]))

    def test_bdd_p7p_current_blocked_execution_report_blocks_preflight(self) -> None:
        """行为 2：当前 P7-O blocked 时不能生成 materialization plan。"""
        report = build_auto_mode_formal_target_adapter_materialization_preflight(
            self._blocked_execution_report(),
            {},
        )

        self.assertEqual(report["status"], "blocked_by_target_adapter_execution")
        self.assertFalse(report["can_request_adapter_materialization"])
        self.assertEqual(report["materialization_plan"], [])
        self.assertIn("target_adapter_execution_not_manifest_recorded", report["blocking_reasons"])
        self.assertIn("target_adapter_execution_manifest_not_recorded", report["blocking_reasons"])

    def test_bdd_p7p_missing_or_invalid_manifest_blocks_preflight(self) -> None:
        """行为 3：execution manifest 缺失或 schema 错误时阻断。"""
        manifest = self._execution_manifest()
        manifest["schema_version"] = "wrong.schema"

        report = build_auto_mode_formal_target_adapter_materialization_preflight(
            self._ready_execution_report(),
            manifest,
        )

        self.assertEqual(report["status"], "blocked_by_execution_manifest")
        self.assertFalse(report["can_request_adapter_materialization"])
        self.assertEqual(report["materialization_plan"], [])
        self.assertIn("execution_manifest_missing_or_invalid_schema", report["blocking_reasons"])

    def test_bdd_p7p_execution_report_must_be_recorded_manifest_state(self) -> None:
        """行为 4：execution report 未进入 manifest recorded 状态时阻断。"""
        execution_report = self._ready_execution_report()
        execution_report["status"] = "target_adapter_execution_dry_run_ready"
        execution_report["execution_manifest_recorded"] = False

        report = build_auto_mode_formal_target_adapter_materialization_preflight(
            execution_report,
            self._execution_manifest(),
        )

        self.assertEqual(report["status"], "blocked_by_target_adapter_execution")
        self.assertIn("target_adapter_execution_not_manifest_recorded", report["blocking_reasons"])
        self.assertIn("target_adapter_execution_manifest_not_recorded", report["blocking_reasons"])

    def test_bdd_p7p_bad_adapter_execution_plan_blocks_materialization(self) -> None:
        """行为 5：adapter plan 不完整时阻断 materialization。"""
        manifest = self._execution_manifest()
        manifest["adapter_execution_plan"][0]["candidate_targets"] = []
        manifest["adapter_execution_plan"][1]["requires_materialization_node"] = False

        report = build_auto_mode_formal_target_adapter_materialization_preflight(
            self._ready_execution_report(),
            manifest,
        )

        self.assertEqual(report["status"], "blocked_by_materialization_contract")
        self.assertFalse(report["can_request_adapter_materialization"])
        self.assertEqual(report["materialization_plan"], [])
        self.assertIn("materialization_candidate_targets_missing:formal_manuscript_sources", report["blocking_reasons"])
        self.assertIn("materialization_node_requirement_missing:formal_bibliography_sources", report["blocking_reasons"])

    def test_bdd_p7p_cli_defaults_to_current_blocked_execution_state(self) -> None:
        """行为 6：CLI 默认读取当前 blocked execution，不创建候选目标。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_target_adapter_execution.json",
                self._blocked_execution_report(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_materialization_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_target_adapter_execution", result.stdout)
            self.assertIn("candidate_targets_materialized=false", result.stdout)
            self.assertIn("formal_target_adapters_executed=false", result.stdout)
            self.assertTrue(
                (project_root / "Results/json/auto_mode_formal_target_adapter_materialization_preflight.json").exists()
            )
            self.assertTrue((project_root / "Reviews/auto_mode_formal_target_adapter_materialization_preflight.md").exists())
            self.assertFalse(
                (project_root / "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md").exists()
            )

    def test_bdd_p7p_writes_report_and_review_without_materializing_targets(self) -> None:
        """行为 1/6：写出预检报告和审阅文件，但不创建 target 文件。"""
        report = build_auto_mode_formal_target_adapter_materialization_preflight(
            self._ready_execution_report(),
            self._execution_manifest(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path = write_auto_mode_formal_target_adapter_materialization_preflight_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "ready_for_adapter_materialization_review")
            self.assertFalse((project_root / "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_target_adapter_materialization.json").exists())

    def _ready_execution_report(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_execution.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "target_adapter_execution_manifest_recorded",
            "mode": "execute",
            "confirm_execution": True,
            "can_execute_with_confirmation": True,
            "execution_manifest_recorded": True,
            "execution_manifest_path": "workspace/formal_target_adapter_execution/auto_mode/formal_target_adapter_execution_manifest.json",
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "adapter_execution_plan": self._adapter_plan(),
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_execution_report(self) -> dict:
        report = self._ready_execution_report()
        report["status"] = "blocked_by_target_adapter_readiness"
        report["mode"] = "dry-run"
        report["confirm_execution"] = False
        report["can_execute_with_confirmation"] = False
        report["execution_manifest_recorded"] = False
        report["execution_manifest_path"] = ""
        report["blocking_reasons"] = [
            "target_adapter_readiness_not_ready",
            "target_adapter_readiness_cannot_request_execution",
            "adapter_mappings_missing",
        ]
        report["adapter_execution_plan"] = []
        return report

    def _execution_manifest(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_target_adapter_execution_manifest.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_execution_report": "Results/json/auto_mode_formal_target_adapter_execution.json",
            "manifest_path": "workspace/formal_target_adapter_execution/auto_mode/formal_target_adapter_execution_manifest.json",
            "reviewer": "unit_test_reviewer",
            "note": "Record manifest for later materialization.",
            "formal_target_adapters_executed": False,
            "formal_writeback_executed": False,
            "candidate_targets_created": False,
            "adapter_execution_plan": self._adapter_plan(),
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _adapter_plan(self) -> list[dict]:
        return [
            self._plan_item("01", "formal_manuscript_sources", "formal_manuscript_sources_adapter", ["manuscript/paper.md"]),
            self._plan_item("02", "formal_bibliography_sources", "formal_bibliography_sources_adapter", ["bibliography/literature_review_packet.json"]),
            self._plan_item("03", "method_review_records", "method_review_records_adapter", ["reviews/method_gate.md"]),
            self._plan_item("04", "statistical_result_records", "statistical_result_records_adapter", ["evidence/results_evidence_package.json"]),
            self._plan_item("05", "reproducibility_records", "reproducibility_records_adapter", ["reproducibility/reproducibility_readme.md"]),
            self._plan_item("06", "formal_package_records", "formal_package_records_adapter", ["manifest.json"]),
        ]

    def _plan_item(self, number: str, group: str, adapter_id: str, targets: list[str]) -> dict:
        return {
            "execution_id": f"target_adapter::{number}::{group}",
            "operation_id": f"formal_writeback::{number}::{group}",
            "category": group,
            "writeback_target_group": group,
            "adapter_id": adapter_id,
            "source_artifacts": [{"path": f"workspace/paper_packages/cgss_social_capital_happiness/{group}.json", "exists": True}],
            "candidate_targets": [
                {
                    "path": f"Submissions/auto_mode/cgss_social_capital_happiness/{target}",
                    "exists": False,
                    "will_be_written_by_this_command": False,
                }
                for target in targets
            ],
            "execution_status": "planned_not_executed",
            "requires_materialization_node": True,
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
            "created_candidate_targets": False,
        }

    def _source_paths(self) -> dict:
        return {
            "target_adapter_execution": "Results/json/auto_mode_formal_target_adapter_execution.json",
            "execution_manifest": "workspace/formal_target_adapter_execution/auto_mode/formal_target_adapter_execution_manifest.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
