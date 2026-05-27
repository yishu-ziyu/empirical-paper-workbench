import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_method_structure_gate_packet import (
    build_method_structure_gate_packet,
    write_method_structure_gate_packet_outputs,
)


class CgssMethodStructureGatePacketTests(unittest.TestCase):
    """BDD: method claims and paper length standards are explicit before drafting."""

    def test_bdd_58_builds_method_and_structure_gate_without_formal_writeback(self) -> None:
        packet = build_method_structure_gate_packet(self._evidence_package(), self._literature_packet())

        self.assertEqual(packet["schema_version"], "p6.cgss_method_structure_gate_packet.v1")
        self.assertEqual(packet["status"], "needs_human_method_structure_approval")
        self.assertFalse(packet["boundary_flags"]["modified_formal_manuscript"])
        self.assertFalse(packet["promotion"]["allowed"])
        self.assertGreaterEqual(packet["paper_length_standard"]["total_target_chinese_chars"], 16000)
        self.assertIn("Literature and Contribution", packet["section_standards"])

    def test_bdd_58_separates_supported_association_claims_from_causal_methods(self) -> None:
        packet = build_method_structure_gate_packet(self._evidence_package(), self._literature_packet())

        supported = {item["claim_type"] for item in packet["method_claim_gates"]["supported_claims"]}
        blocked = {item["method"] for item in packet["method_claim_gates"]["blocked_method_families"]}
        self.assertIn("conditional_association", supported)
        self.assertIn("ordered_outcome_robustness", supported)
        self.assertIn("DID", blocked)
        self.assertIn("IV", blocked)
        self.assertIn("RDD", blocked)

    def test_bdd_58_uses_real_result_numbers_for_main_result_gate(self) -> None:
        packet = build_method_structure_gate_packet(self._evidence_package(), self._literature_packet())

        main_result = packet["method_claim_gates"]["main_result_gate"]
        self.assertEqual(main_result["nobs"], 5310)
        self.assertAlmostEqual(main_result["ols_coef"], 0.1658, places=4)
        self.assertAlmostEqual(main_result["ordered_logit_coef"], 0.4050, places=4)
        self.assertEqual(main_result["claim_boundary"], "positive_conditional_association")

    def test_bdd_58_blocks_when_inputs_are_not_ready(self) -> None:
        evidence = self._evidence_package()
        evidence["status"] = "blocked"

        packet = build_method_structure_gate_packet(evidence, self._literature_packet())

        self.assertEqual(packet["status"], "blocked_missing_method_or_literature_inputs")
        self.assertIn("results_evidence_package_not_ready", packet["blocking_reasons"])
        self.assertFalse(packet["promotion"]["allowed"])

    def test_bdd_58_writes_reviewable_method_structure_files(self) -> None:
        packet = build_method_structure_gate_packet(self._evidence_package(), self._literature_packet())

        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path = write_method_structure_gate_packet_outputs(
                Path(tmpdir),
                packet,
                Path("Results/json/method_structure_gate_packet.json"),
                Path("Reviews/method_structure_gate_packet.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(json.loads(result_path.read_text(encoding="utf-8"))["status"], "needs_human_method_structure_approval")
            self.assertIn("CGSS 方法规范与论文结构门禁", review_path.read_text(encoding="utf-8"))

    def _evidence_package(self) -> dict:
        return {
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "ready_for_paper_draft_input",
            "main_results": [
                {
                    "model": "OLS",
                    "variable": "social_capital_index",
                    "coef": 0.1658,
                    "se": 0.0187,
                    "p_value": 0.0,
                    "nobs": 5310,
                },
                {
                    "model": "Ordered Logit",
                    "variable": "social_capital_index",
                    "coef": 0.4050,
                    "se": 0.0424,
                    "p_value": 0.0,
                    "nobs": 5310,
                },
            ],
        }

    def _literature_packet(self) -> dict:
        return {
            "status": "needs_human_literature_review_draft_approval",
            "paragraph_blocks": [
                {"id": "theory_foundation"},
                {"id": "measurement_foundation"},
                {"id": "cgss_empirical_context"},
                {"id": "method_transition"},
            ],
        }


if __name__ == "__main__":
    unittest.main()
