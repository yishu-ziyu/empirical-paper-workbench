import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_writeback_execution_preflight import (
    build_auto_mode_formal_writeback_execution_preflight,
    write_auto_mode_formal_writeback_execution_preflight_outputs,
)


class AutoModeFormalWritebackExecutionPreflightTests(unittest.TestCase):
    """BDD: P7-L turns effective approval into a reviewed execution plan only."""

    def test_bdd_p7l_effective_approval_creates_execution_preflight_plan(self) -> None:
        """行为 1：生效审批生成执行预检计划，但不执行写回。"""
        report = build_auto_mode_formal_writeback_execution_preflight(
            self._approved_ledger(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_writeback_execution_preflight.v1")
        self.assertEqual(report["status"], "ready_for_formal_writeback_execution_review")
        self.assertTrue(report["can_request_formal_writeback_execution"])
        self.assertTrue(report["requires_explicit_execute_command"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["can_write_product_state"])
        categories = {item["category"] for item in report["execution_plan"]}
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
        for item in report["execution_plan"]:
            self.assertEqual(item["execution_status"], "pending_explicit_execute_command")
            self.assertFalse(item["executed_by_this_command"])

    def test_bdd_p7l_blocks_when_approval_ledger_is_not_effective(self) -> None:
        """行为 2：P7-K 未生效时不能请求正式写回执行。"""
        report = build_auto_mode_formal_writeback_execution_preflight(self._blocked_ledger())

        self.assertEqual(report["status"], "blocked_by_formal_writeback_approval")
        self.assertFalse(report["can_request_formal_writeback_execution"])
        self.assertFalse(report["formal_writeback_executed"])
        self.assertIn("formal_writeback_approval_not_effective", report["blocking_reasons"])
        self.assertEqual(report["execution_plan"], [])

    def test_bdd_p7l_blocks_approved_ledger_without_scope(self) -> None:
        """行为 3：审批账本缺少 approved_scope 时不能生成执行计划。"""
        ledger = self._approved_ledger()
        ledger["approved_scope"] = []
        report = build_auto_mode_formal_writeback_execution_preflight(ledger)

        self.assertEqual(report["status"], "blocked_by_formal_writeback_scope")
        self.assertFalse(report["can_request_formal_writeback_execution"])
        self.assertIn("approved_scope_missing", report["blocking_reasons"])

    def test_bdd_p7l_boundary_violation_blocks_execution_preflight(self) -> None:
        """行为 4：上游账本出现正式层或 product 写入标记时阻断。"""
        ledger = self._approved_ledger()
        ledger["this_command_wrote_formal_state"] = True
        ledger["can_write_product_state"] = True
        ledger["boundary_flags"]["modified_formal_manuscript"] = True
        report = build_auto_mode_formal_writeback_execution_preflight(ledger)

        self.assertEqual(report["status"], "blocked_by_approval_boundary_violation")
        self.assertIn("approval_ledger_already_wrote_formal_state", report["blocking_reasons"])
        self.assertIn("approval_ledger_allows_product_state_write", report["blocking_reasons"])
        self.assertIn("approval_ledger_boundary_violation:modified_formal_manuscript", report["blocking_reasons"])

    def test_bdd_p7l_writes_json_and_markdown_without_formal_state(self) -> None:
        """行为 5：只写 execution preflight JSON/Markdown，不写正式层。"""
        report = build_auto_mode_formal_writeback_execution_preflight(self._approved_ledger())

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path = write_auto_mode_formal_writeback_execution_preflight_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIn("Auto Mode Formal Writeback Execution Preflight", review_path.read_text(encoding="utf-8"))
            self.assertFalse((project_root / "state/product/auto_mode_formal_writeback_execution_preflight.json").exists())
            self.assertFalse((project_root / "Manuscripts/sections/introduction.md").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())

    def test_bdd_p7l_cli_defaults_to_current_blocked_approval(self) -> None:
        """行为 6：CLI 默认读取当前 blocked approval，继续不执行写回。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_writeback_approval.json",
                self._blocked_ledger(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_writeback_execution_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_formal_writeback_approval", result.stdout)
            self.assertIn("formal_writeback_executed=false", result.stdout)
            self.assertIn("this_command_wrote_formal_state=false", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_writeback_execution_preflight.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_writeback_execution_preflight.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_writeback_execution_preflight.json").exists())

    def _approved_ledger(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_writeback_approval.v1",
            "status": "approved_for_formal_writeback_execution_preflight",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "approved": True,
            "formal_writeback_allowed": True,
            "can_enter_formal_writeback_execution_preflight": True,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "approval": {
                "decision": "approve",
                "reviewer": "unit_test_reviewer",
                "note": "Approved for execution preflight.",
                "approved": True,
                "metadata_complete": True,
            },
            "approved_scope": [
                self._approved_scope_item("manuscript"),
                self._approved_scope_item("bibliography"),
                self._approved_scope_item("method_review"),
                self._approved_scope_item("statistical_results"),
                self._approved_scope_item("reproducibility"),
                self._approved_scope_item("package_artifacts"),
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_ledger(self) -> dict:
        ledger = self._approved_ledger()
        ledger["status"] = "blocked_by_formal_promotion_preflight"
        ledger["approved"] = False
        ledger["formal_writeback_allowed"] = False
        ledger["can_enter_formal_writeback_execution_preflight"] = False
        ledger["blocking_reasons"] = ["formal_promotion_preflight_not_ready"]
        ledger["approval"]["decision"] = "defer"
        ledger["approval"]["approved"] = False
        ledger["approved_scope"] = []
        return ledger

    def _approved_scope_item(self, category: str) -> dict:
        return {
            "category": category,
            "label": category.replace("_", " ").title(),
            "evidence_refs": [{"target": f"{category}.md", "kind": "unit_test"}],
            "approval_status": "approved_for_formal_writeback_execution_preflight",
            "requires_execution_preflight": True,
            "this_command_wrote_formal_state": False,
            "next_gates": ["formal_writeback_execution"],
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
            "formal_writeback_approval": "Results/json/auto_mode_formal_writeback_approval.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
