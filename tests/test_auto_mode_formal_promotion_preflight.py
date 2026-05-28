import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_promotion_preflight import (
    build_auto_mode_formal_promotion_preflight,
    write_auto_mode_formal_promotion_preflight_outputs,
)


class AutoModeFormalPromotionPreflightTests(unittest.TestCase):
    """BDD: P7-J gates formal promotion behind explicit final review approval."""

    def test_bdd_p7j_ready_after_explicit_final_review_approval(self) -> None:
        """行为 1：终审 approve 后只进入正式写回审批预检。"""
        report = build_auto_mode_formal_promotion_preflight(
            self._approved_decision(),
            self._final_review_packet(),
            self._package_manifest(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(report["schema_version"], "p7.auto_mode_formal_promotion_preflight.v1")
        self.assertEqual(report["status"], "ready_for_formal_writeback_approval")
        self.assertTrue(report["can_request_formal_writeback_approval"])
        self.assertTrue(report["requires_separate_formal_writeback_approval"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertFalse(report["can_write_product_state"])
        categories = {item["category"] for item in report["promotion_scope"]}
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
        for item in report["promotion_scope"]:
            self.assertEqual(item["approval_status"], "pending_formal_writeback_approval")
            self.assertFalse(item["can_write_formal_state"])

    def test_bdd_p7j_blocks_while_final_review_is_deferred(self) -> None:
        """行为 2：当前 defer 决策不能进入正式写回审批。"""
        report = build_auto_mode_formal_promotion_preflight(
            self._deferred_decision(),
            self._final_review_packet(),
            self._package_manifest(),
        )

        self.assertEqual(report["status"], "blocked_by_final_review_decision")
        self.assertFalse(report["can_request_formal_writeback_approval"])
        self.assertIn("final_review_decision_not_approved_for_preflight", report["blocking_reasons"])
        self.assertEqual(report["promotion_scope"], [])

    def test_bdd_p7j_blocks_approval_without_reviewer_or_note(self) -> None:
        """行为 3：伪 approve 缺少 reviewer/note 时仍阻断。"""
        decision = self._approved_decision()
        decision["reviewer"] = ""
        decision["note"] = ""
        report = build_auto_mode_formal_promotion_preflight(
            decision,
            self._final_review_packet(),
            self._package_manifest(),
        )

        self.assertEqual(report["status"], "blocked_by_final_review_decision")
        self.assertIn("reviewer_required", report["blocking_reasons"])
        self.assertIn("decision_note_required", report["blocking_reasons"])

    def test_bdd_p7j_package_manifest_gaps_block_preflight(self) -> None:
        """行为 4：package manifest 有缺口时不能请求正式写回审批。"""
        manifest = self._package_manifest()
        manifest["missing_targets"] = ["paper.pdf"]
        report = build_auto_mode_formal_promotion_preflight(
            self._approved_decision(),
            self._final_review_packet(),
            manifest,
        )

        self.assertEqual(report["status"], "blocked_by_package_manifest")
        self.assertFalse(report["can_request_formal_writeback_approval"])
        self.assertIn("paper_package_manifest_has_missing_targets", report["blocking_reasons"])

    def test_bdd_p7j_writes_json_and_markdown_without_formal_state(self) -> None:
        """行为 5：只写 preflight JSON/Markdown，不写正式层。"""
        report = build_auto_mode_formal_promotion_preflight(
            self._approved_decision(),
            self._final_review_packet(),
            self._package_manifest(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_path, review_path = write_auto_mode_formal_promotion_preflight_outputs(
                project_root,
                report,
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIn("Auto Mode Formal Promotion Preflight", review_path.read_text(encoding="utf-8"))
            self.assertFalse((project_root / "state/product/auto_mode_formal_promotion_preflight.json").exists())
            self.assertFalse((project_root / "Manuscripts/sections/introduction.md").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())

    def test_bdd_p7j_cli_defaults_to_current_defer_state_and_writes_blocked_preflight(self) -> None:
        """行为 6：CLI 默认读取当前决策，defer 时写 blocked preflight。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(project_root / "Results/json/auto_mode_final_review_decision.json", self._deferred_decision())
            self._write_json(project_root / "Results/json/auto_mode_final_review_packet.json", self._final_review_packet())
            self._write_json(
                project_root / "workspace/paper_packages/cgss_social_capital_happiness/manifest.json",
                self._package_manifest(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_promotion_preflight.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_final_review_decision", result.stdout)
            self.assertIn("formal_writeback_allowed=false", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_promotion_preflight.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_promotion_preflight.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_promotion_preflight.json").exists())

    def _approved_decision(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_final_review_decision.v1",
            "status": "approved_for_formal_promotion_preflight",
            "decision": "approve",
            "route": "formal_promotion_preflight",
            "approved": True,
            "reviewer": "unit_test_reviewer",
            "note": "Ready for preflight.",
            "formal_writeback_allowed": False,
            "can_write_product_state": False,
            "promotion": {"allowed": True, "would_enable": ["formal_promotion_preflight"]},
        }

    def _deferred_decision(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_final_review_decision.v1",
            "status": "waiting_for_human_final_review_decision",
            "decision": "defer",
            "route": "wait_for_human_confirmation",
            "approved": False,
            "reviewer": "",
            "note": "",
            "formal_writeback_allowed": False,
            "can_write_product_state": False,
            "promotion": {"allowed": False},
        }

    def _final_review_packet(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_final_review_packet.v1",
            "status": "awaiting_human_final_review",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "can_request_final_decision": True,
            "evidence_summary": {
                "component_count": 5,
                "method_recommended_check_count": 6,
                "statistical_contract_ready_result_count": 6,
                "package_file_count": 9,
            },
            "required_review_items": ["review_method_knowledge_base", "review_statistical_adapter_contract"],
        }

    def _package_manifest(self) -> dict:
        return {
            "schema_version": "p6.cgss_paper_package.v1",
            "status": "needs_human_paper_package_review",
            "package_dir": "workspace/paper_packages/cgss_social_capital_happiness",
            "missing_targets": [],
            "files": [
                {"target": "paper.md", "kind": "draft_layer"},
                {"target": "paper.pdf", "kind": "real_run"},
                {"target": "results_evidence_package.json", "kind": "real_run"},
                {"target": "literature_review_packet.json", "kind": "draft_layer"},
                {"target": "method_gate.md", "kind": "human_review_required"},
                {"target": "reviewer_report.md", "kind": "human_review_required"},
                {"target": "revision_task_queue.md", "kind": "human_review_required"},
                {"target": "reproducibility_readme.md", "kind": "generated_package_metadata"},
                {"target": "manifest.json", "kind": "generated_package_metadata"},
            ],
        }

    def _source_paths(self) -> dict:
        return {
            "final_review_decision": "Results/json/auto_mode_final_review_decision.json",
            "final_review_packet": "Results/json/auto_mode_final_review_packet.json",
            "package_manifest": "workspace/paper_packages/cgss_social_capital_happiness/manifest.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
