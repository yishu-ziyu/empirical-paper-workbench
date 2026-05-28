import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_final_review_packet import (
    build_auto_mode_final_review_decision,
    build_auto_mode_final_review_packet,
    write_auto_mode_final_review_outputs,
)


class AutoModeFinalReviewPacketTests(unittest.TestCase):
    """BDD: P7-I turns final readiness into a human-review packet and gated route."""

    def test_bdd_p7i_builds_packet_from_ready_chain_and_package_manifest(self) -> None:
        """行为 1：终审 packet 汇总五组件、方法、统计和 package 证据。"""
        packet = build_auto_mode_final_review_packet(
            self._acceptance_chain(),
            self._package_manifest(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(packet["schema_version"], "p7.auto_mode_final_review_packet.v1")
        self.assertEqual(packet["status"], "awaiting_human_final_review")
        self.assertTrue(packet["can_request_final_decision"])
        self.assertEqual(packet["evidence_summary"]["component_count"], 5)
        self.assertEqual(packet["evidence_summary"]["method_recommended_check_count"], 6)
        self.assertEqual(packet["evidence_summary"]["statistical_contract_ready_result_count"], 6)
        self.assertIn("review_method_knowledge_base", packet["required_review_items"])
        self.assertIn("paper.pdf", packet["package_artifacts"]["real_run_artifacts"])
        self.assertFalse(packet["formal_writeback_allowed"])
        self.assertFalse(packet["can_write_product_state"])

    def test_bdd_p7i_blocks_packet_when_acceptance_chain_has_repair_queue(self) -> None:
        """行为 2：有 repair queue 时不能请求人工终审决策。"""
        chain = self._acceptance_chain(package_readiness="needs_auto_mode_repair")
        chain["repair_queue"] = [{"task_id": "repair_statistical_adapter_contract"}]

        packet = build_auto_mode_final_review_packet(chain, self._package_manifest())

        self.assertEqual(packet["status"], "blocked_final_review_packet_inputs")
        self.assertFalse(packet["can_request_final_decision"])
        self.assertIn("acceptance_chain_not_ready_for_final_review", packet["blocking_reasons"])
        self.assertIn("auto_mode_repair_queue_not_empty", packet["blocking_reasons"])

    def test_bdd_p7i_defer_waits_without_formal_or_product_writeback(self) -> None:
        """行为 3：默认 defer 只写审阅记录，不写正式层。"""
        packet = build_auto_mode_final_review_packet(self._acceptance_chain(), self._package_manifest())
        decision = build_auto_mode_final_review_decision(packet, decision="defer", reviewer="", note="")

        self.assertEqual(decision["status"], "waiting_for_human_final_review_decision")
        self.assertEqual(decision["route"], "wait_for_human_confirmation")
        self.assertFalse(decision["approved"])
        self.assertFalse(decision["formal_writeback_allowed"])
        self.assertFalse(decision["can_write_product_state"])

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            packet_path, packet_review, decision_path, decision_review = write_auto_mode_final_review_outputs(
                project_root,
                packet,
                decision,
            )

            self.assertTrue(packet_path.exists())
            self.assertTrue(packet_review.exists())
            self.assertTrue(decision_path.exists())
            self.assertTrue(decision_review.exists())
            self.assertFalse((project_root / "state/product/auto_mode_final_review_decision.json").exists())
            self.assertFalse((project_root / "Manuscripts/sections/introduction.md").exists())

    def test_bdd_p7i_approve_requires_reviewer_and_note(self) -> None:
        """行为 4：approve 缺少审阅人或说明时阻断。"""
        packet = build_auto_mode_final_review_packet(self._acceptance_chain(), self._package_manifest())
        decision = build_auto_mode_final_review_decision(packet, decision="approve", reviewer="", note="")

        self.assertEqual(decision["status"], "blocked_missing_human_final_review_metadata")
        self.assertFalse(decision["approved"])
        self.assertIn("reviewer_required", decision["blocking_reasons"])
        self.assertIn("decision_note_required", decision["blocking_reasons"])

    def test_bdd_p7i_approve_routes_to_preflight_without_formal_writeback(self) -> None:
        """行为 5：approve 只进入正式推广预检，不直接写正式层。"""
        packet = build_auto_mode_final_review_packet(self._acceptance_chain(), self._package_manifest())
        decision = build_auto_mode_final_review_decision(
            packet,
            decision="approve",
            reviewer="unit_test_reviewer",
            note="Five-component packet reviewed.",
        )

        self.assertEqual(decision["status"], "approved_for_formal_promotion_preflight")
        self.assertEqual(decision["route"], "formal_promotion_preflight")
        self.assertTrue(decision["approved"])
        self.assertTrue(decision["promotion"]["allowed"])
        self.assertIn("run_formal_promotion_preflight", decision["next_actions"])
        self.assertFalse(decision["formal_writeback_allowed"])
        self.assertFalse(decision["can_write_product_state"])

    def test_bdd_p7i_revise_and_reject_route_without_promotion(self) -> None:
        """行为 6：revise/reject 只记录返修或重建路线。"""
        packet = build_auto_mode_final_review_packet(self._acceptance_chain(), self._package_manifest())

        revise = build_auto_mode_final_review_decision(packet, decision="revise", reviewer="reviewer", note="Revise.")
        reject = build_auto_mode_final_review_decision(packet, decision="reject", reviewer="reviewer", note="Reject.")

        self.assertEqual(revise["status"], "final_review_requires_auto_mode_repair")
        self.assertEqual(revise["route"], "auto_mode_repair")
        self.assertFalse(revise["promotion"]["allowed"])
        self.assertEqual(reject["status"], "final_review_rejected")
        self.assertEqual(reject["route"], "stop_or_rebuild_package")
        self.assertFalse(reject["promotion"]["allowed"])

    def test_bdd_p7i_cli_defaults_to_defer_and_writes_packet_and_decision_reviews(self) -> None:
        """行为 3：CLI 默认 defer，并写出 packet/router 审阅产物。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_acceptance_chain_method_stat_integrated.json",
                self._acceptance_chain(),
            )
            self._write_json(
                project_root / "workspace/paper_packages/cgss_social_capital_happiness/manifest.json",
                self._package_manifest(),
            )

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_final_review_packet.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("packet_status=awaiting_human_final_review", result.stdout)
            self.assertIn("decision_status=waiting_for_human_final_review_decision", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_final_review_packet.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_final_review_packet.md").exists())
            self.assertTrue((project_root / "Results/json/auto_mode_final_review_decision.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_final_review_decision.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_final_review_decision.json").exists())

    def _acceptance_chain(self, package_readiness: str = "needs_human_final_review") -> dict:
        return {
            "schema_version": "p7.auto_mode_acceptance_chain.v1",
            "status": package_readiness,
            "package_readiness": package_readiness,
            "missing_inputs": [],
            "repair_queue": [],
            "component_statuses": [
                {"component": "dataset_motherlode_index", "status": "needs_human_dataset_index_review"},
                {"component": "literature_discovery_seed", "status": "needs_human_literature_discovery_review"},
                {"component": "level3_manuscript_quality_gate", "status": "needs_human_level3_quality_review"},
                {"component": "method_knowledge_base", "status": "needs_human_method_kb_review"},
                {"component": "statistical_adapter_contract", "status": "needs_human_statistical_adapter_review"},
            ],
            "human_review_checklist": [
                "review_dataset_motherlode_candidates",
                "review_literature_discovery_seed",
                "review_level3_quality_gate",
                "review_method_knowledge_base",
                "review_statistical_adapter_contract",
                "decide_formal_promotion_or_auto_mode_repair",
            ],
            "method_readiness": {
                "recommended_check_count": 6,
                "proposal_source_count": 1,
                "reviewed_canonical_blocking_rule_count": 0,
                "proposal_rules_can_block": False,
                "ready_for_human_review": True,
            },
            "statistical_readiness": {
                "normalized_result_count": 6,
                "contract_ready_result_count": 6,
                "observed_methods": ["iv", "ols", "ordered_logit"],
                "ready_for_human_review": True,
            },
        }

    def _package_manifest(self) -> dict:
        return {
            "schema_version": "p6.cgss_paper_package.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "needs_human_paper_package_review",
            "package_dir": "workspace/paper_packages/cgss_social_capital_happiness",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "files": [
                {"target": "paper.md", "kind": "draft_layer"},
                {"target": "results_evidence_package.json", "kind": "real_run"},
                {"target": "paper.pdf", "kind": "real_run"},
            ],
            "real_run_artifacts": ["results_evidence_package.json", "paper.pdf"],
            "draft_layer_artifacts": ["paper.md", "literature_review_packet.json"],
            "human_review_required": ["method_gate.md", "reviewer_report.md", "revision_task_queue.md"],
            "missing_targets": [],
            "rendered_artifact": "paper.pdf",
            "next_tasks": [
                "human_open_paper_md_and_pdf",
                "human_review_method_gate_reviewer_report_revision_queue",
                "decide_formal_layer_promotion_or_next_revision",
            ],
        }

    def _source_paths(self) -> dict:
        return {
            "acceptance_chain": "Results/json/auto_mode_acceptance_chain_method_stat_integrated.json",
            "package_manifest": "workspace/paper_packages/cgss_social_capital_happiness/manifest.json",
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
