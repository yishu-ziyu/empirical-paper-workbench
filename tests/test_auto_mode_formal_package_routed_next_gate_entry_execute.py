import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_routed_next_gate_entry_execute import (
    build_auto_mode_formal_package_routed_next_gate_entry_execute,
    write_auto_mode_formal_package_routed_next_gate_entry_execute_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageRoutedNextGateEntryExecuteTests(unittest.TestCase):
    """BDD: P7-AG records an explicit next-gate entry manifest without running the gate."""

    def test_bdd_p7ag_ready_pdf_entry_preflight_supports_dry_run_without_manifest(self) -> None:
        """行为 1：ready PDF entry 可 dry-run，但不记录 manifest、不进入下一关。"""
        report = build_auto_mode_formal_package_routed_next_gate_entry_execute(
            self._ready_preflight("pdf_export"),
            mode="dry-run",
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_package_routed_next_gate_entry_execute.v1")
        self.assertEqual(report["status"], "routed_next_gate_entry_dry_run_ready")
        self.assertEqual(report["mode"], "dry-run")
        self.assertTrue(report["can_enter_routed_next_gate_with_confirmation"])
        self.assertFalse(report["routed_next_gate_entry_manifest_recorded"])
        self.assertEqual(len(report["routed_next_gate_entry_operations"]), 1)
        operation = report["routed_next_gate_entry_operations"][0]
        self.assertEqual(operation["verified_route_type"], "pdf_export")
        self.assertEqual(operation["gate_id"], "formal_package_export_acceptance_router")
        self.assertEqual(operation["next_command"], "auto_mode_formal_package_export_acceptance_router")
        self.assertFalse(report["next_gate_entered"])
        self.assertFalse(report["this_command_entered_next_gate"])
        self.assertFalse(report["next_gate_command_executed"])
        self.assertFalse(report["export_or_acceptance_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])

    def test_bdd_p7ag_current_blocked_preflight_blocks_entry_execute_gate(self) -> None:
        """行为 2：当前 P7-AF blocked 时不能生成 entry operation。"""
        report = build_auto_mode_formal_package_routed_next_gate_entry_execute(
            self._blocked_preflight(),
            mode="dry-run",
        )

        self.assertEqual(report["status"], "blocked_by_routed_next_gate_entry_preflight")
        self.assertFalse(report["can_enter_routed_next_gate_with_confirmation"])
        self.assertFalse(report["routed_next_gate_entry_manifest_recorded"])
        self.assertEqual(report["routed_next_gate_entry_operations"], [])
        self.assertIn("routed_next_gate_entry_preflight_not_ready", report["blocking_reasons"])

    def test_bdd_p7ag_missing_invalid_or_unready_preflight_blocks_entry_execution(self) -> None:
        """行为 3：preflight 缺失、schema 错误或未 ready 时阻断。"""
        missing = build_auto_mode_formal_package_routed_next_gate_entry_execute({}, mode="dry-run")
        wrong_schema_source = self._ready_preflight("pdf_export")
        wrong_schema_source["schema_version"] = "wrong.schema"
        unready_source = self._ready_preflight("pdf_export")
        unready_source["status"] = "blocked_by_verified_route_next_gate_router"

        wrong_schema = build_auto_mode_formal_package_routed_next_gate_entry_execute(
            wrong_schema_source,
            mode="dry-run",
        )
        unready = build_auto_mode_formal_package_routed_next_gate_entry_execute(
            unready_source,
            mode="dry-run",
        )

        self.assertEqual(missing["status"], "blocked_by_routed_next_gate_entry_preflight")
        self.assertIn("routed_next_gate_entry_preflight_missing_or_invalid_schema", missing["blocking_reasons"])
        self.assertEqual(wrong_schema["status"], "blocked_by_routed_next_gate_entry_preflight")
        self.assertIn("routed_next_gate_entry_preflight_missing_or_invalid_schema", wrong_schema["blocking_reasons"])
        self.assertEqual(unready["status"], "blocked_by_routed_next_gate_entry_preflight")
        self.assertIn("routed_next_gate_entry_preflight_not_ready", unready["blocking_reasons"])

    def test_bdd_p7ag_execute_requires_explicit_confirmation(self) -> None:
        """行为 4：execute 缺 confirm 时阻断。"""
        report = build_auto_mode_formal_package_routed_next_gate_entry_execute(
            self._ready_preflight("pdf_export"),
            mode="execute",
            confirm_entry=False,
            reviewer="unit_test_reviewer",
            note="Record next gate entry.",
        )

        self.assertEqual(report["status"], "blocked_by_missing_routed_next_gate_entry_confirmation")
        self.assertFalse(report["routed_next_gate_entry_manifest_recorded"])
        self.assertIn("confirm_entry_required", report["blocking_reasons"])

    def test_bdd_p7ag_execute_requires_reviewer_and_note(self) -> None:
        """行为 5：execute 缺 reviewer/note 时阻断。"""
        report = build_auto_mode_formal_package_routed_next_gate_entry_execute(
            self._ready_preflight("pdf_export"),
            mode="execute",
            confirm_entry=True,
            reviewer="",
            note="",
        )

        self.assertEqual(report["status"], "blocked_by_routed_next_gate_entry_metadata")
        self.assertFalse(report["routed_next_gate_entry_manifest_recorded"])
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("entry_note_required", report["blocking_reasons"])

    def test_bdd_p7ag_bad_entry_plan_contract_blocks_execution(self) -> None:
        """行为 6：entry plan 不干净时阻断。"""
        unknown_gate = self._ready_preflight("pdf_export")
        unknown_gate["routed_next_gate"] = "unknown_gate"
        unknown_gate["next_gate_entry_plan"][0]["gate_id"] = "unknown_gate"
        duplicated = self._ready_preflight("pdf_export")
        duplicated["next_gate_entry_plan"].append(dict(duplicated["next_gate_entry_plan"][0]))
        already_marked = self._ready_preflight("pdf_export")
        already_marked["next_gate_entry_plan"][0]["will_enter_next_gate_by_this_command"] = True
        no_command = self._ready_preflight("pdf_export")
        no_command["next_gate_entry_plan"][0]["next_command"] = ""

        reports = [
            build_auto_mode_formal_package_routed_next_gate_entry_execute(source, mode="dry-run")
            for source in [unknown_gate, duplicated, already_marked, no_command]
        ]

        self.assertTrue(all(report["status"] == "blocked_by_routed_next_gate_entry_contract" for report in reports))
        self.assertIn("routed_next_gate_unknown:unknown_gate", reports[0]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_plan_not_single", reports[1]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_marked_enter_by_this_command:pdf_export", reports[2]["blocking_reasons"])
        self.assertIn("routed_next_gate_entry_next_command_missing:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7ag_confirmed_manual_acceptance_entry_records_manifest_only(self) -> None:
        """行为 7：确认 manual acceptance entry 只写 manifest，不运行交付完成门。"""
        report = build_auto_mode_formal_package_routed_next_gate_entry_execute(
            self._ready_preflight("manual_acceptance"),
            mode="execute",
            confirm_entry=True,
            reviewer="unit_test_reviewer",
            note="Record delivery completion gate entry manifest.",
            entry_manifest_path=Path("workspace/formal_package_routed_next_gate_entry/custom/entry_manifest.json"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path, manifest_path = (
                write_auto_mode_formal_package_routed_next_gate_entry_execute_outputs(
                    project_root,
                    report,
                    entry_manifest_path=Path(
                        "workspace/formal_package_routed_next_gate_entry/custom/entry_manifest.json"
                    ),
                )
            )

            self.assertEqual(report["status"], "routed_next_gate_entry_manifest_recorded")
            self.assertTrue(report["routed_next_gate_entry_manifest_recorded"])
            self.assertFalse(report["next_gate_entered"])
            self.assertFalse(report["this_command_entered_next_gate"])
            self.assertFalse(report["next_gate_command_executed"])
            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIsNotNone(manifest_path)
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], "p7.auto_mode_formal_package_routed_next_gate_entry_manifest.v1")
            self.assertEqual(len(manifest["routed_next_gate_entry_operations"]), 1)
            self.assertEqual(
                manifest["routed_next_gate_entry_operations"][0]["gate_id"],
                "formal_package_delivery_completion_gate",
            )
            self.assertEqual(
                manifest["routed_next_gate_entry_operations"][0]["next_command"],
                "auto_mode_formal_package_delivery_completion_gate",
            )
            self.assertFalse(manifest["next_gate_entered"])
            self.assertFalse(manifest["next_gate_command_executed"])
            self.assertFalse((project_root / "state/product/auto_mode_formal_package_routed_next_gate_entry_execute.json").exists())

    def test_bdd_p7ag_cli_defaults_to_current_blocked_preflight(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AF，写 blocked execute report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json",
                self._blocked_preflight(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_routed_next_gate_entry_execute.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_routed_next_gate_entry_preflight", result.stdout)
            self.assertIn("can_enter_routed_next_gate_with_confirmation=false", result.stdout)
            self.assertIn("routed_next_gate_entry_manifest_recorded=false", result.stdout)
            self.assertIn("routed_next_gate_entry_operations=0", result.stdout)
            self.assertTrue(
                (
                    project_root / "Results/json/auto_mode_formal_package_routed_next_gate_entry_execute.json"
                ).exists()
            )
            self.assertTrue(
                (project_root / "Reviews/auto_mode_formal_package_routed_next_gate_entry_execute.md").exists()
            )
            self.assertFalse(
                (
                    project_root
                    / "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
                ).exists()
            )
            self.assertFalse(
                (project_root / "state/product/auto_mode_formal_package_routed_next_gate_entry_execute.json").exists()
            )

    def _ready_preflight(self, route_type: str) -> dict:
        gate_id, action, next_command, entry_kind = self._entry_mapping(route_type)
        return {
            "schema_version": "p7.auto_mode_formal_package_routed_next_gate_entry_preflight.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_status": "verified_route_next_gate_route_recorded",
            "status": "ready_for_routed_next_gate_entry_review",
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "can_request_routed_next_gate_entry": True,
            "requires_explicit_next_gate_entry_command": True,
            "next_gate_entered": False,
            "this_command_entered_next_gate": False,
            "export_or_acceptance_executed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "source_router": {"status": "verified_route_next_gate_route_recorded"},
            "next_gate_entry_plan": [
                {
                    "entry_id": f"routed_next_gate_entry::{gate_id}::{route_type}",
                    "source_route_id": f"verified_route_next_gate::{route_type}",
                    "verified_route_type": route_type,
                    "gate_id": gate_id,
                    "entry_kind": entry_kind,
                    "next_gate_action": action,
                    "next_command": next_command,
                    "entry_status": "pending_explicit_next_gate_entry_command",
                    "requires_explicit_next_gate_entry_command": True,
                    "will_enter_next_gate_by_this_command": False,
                    "will_execute_export_or_acceptance_by_this_command": False,
                    "will_write_product_state_by_this_command": False,
                    "handoff_summary": "Ready for explicit next gate entry.",
                }
            ],
            "boundary_flags": self._clean_boundary_flags(),
            "next_action": {"id": next_command},
        }

    def _blocked_preflight(self) -> dict:
        preflight = self._ready_preflight("pdf_export")
        preflight["source_status"] = "blocked_by_verified_route_completion_ledger"
        preflight["status"] = "blocked_by_verified_route_next_gate_router"
        preflight["verified_route_type"] = ""
        preflight["routed_next_gate"] = ""
        preflight["can_request_routed_next_gate_entry"] = False
        preflight["requires_explicit_next_gate_entry_command"] = False
        preflight["blocking_reasons"] = ["verified_route_next_gate_router_not_route_recorded"]
        preflight["next_gate_entry_plan"] = []
        return preflight

    def _entry_mapping(self, route_type: str) -> tuple[str, str, str, str]:
        if route_type == "manual_acceptance":
            return (
                "formal_package_delivery_completion_gate",
                "finalize_formal_package_delivery_review",
                "auto_mode_formal_package_delivery_completion_gate",
                "delivery_completion",
            )
        return (
            "formal_package_export_acceptance_router",
            "continue_formal_package_export_acceptance_cycle",
            "auto_mode_formal_package_export_acceptance_router",
            "continue_export_acceptance_cycle",
        )

    def _clean_boundary_flags(self) -> dict:
        return {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
            "reran_models": False,
            "modified_statistical_execution_artifacts": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "generated_package_manifest": False,
            "performed_manual_acceptance": False,
            "entered_next_gate": False,
            "wrote_formal_state": False,
        }

    def _source_paths(self) -> dict:
        return {
            "routed_next_gate_entry_preflight": (
                "Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
