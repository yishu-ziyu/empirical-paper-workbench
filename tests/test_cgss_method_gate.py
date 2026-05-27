import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_method_gate import (
    build_cgss_method_gate,
    write_cgss_method_gate_outputs,
)


class CgssMethodGateTests(unittest.TestCase):
    """BDD: CGSS method standards are gated before formal paper promotion."""

    def test_bdd_61_builds_aer_like_gate_without_formal_writeback(self) -> None:
        """行为 61.1：选择 AER-like 后，方法规范门强制进入人工审阅。"""
        gate = build_cgss_method_gate(
            self._evidence_package(),
            self._literature_packet(),
            self._paper_assembly(),
            profile="aer_like",
        )

        self.assertEqual(gate["schema_version"], "p6.cgss_method_gate.v1")
        self.assertEqual(gate["status"], "needs_human_method_gate_review")
        self.assertTrue(gate["gate_enforcement"]["required"])
        self.assertEqual(gate["gate_enforcement"]["profile"], "aer_like")
        self.assertFalse(gate["formal_writeback_allowed"])
        self.assertFalse(gate["boundary_flags"]["modified_formal_manuscript"])
        self.assertFalse(gate["boundary_flags"]["modified_product_state"])
        self.assertEqual(gate["method_family"], "cross_section_ols_ordered_logit")

    def test_bdd_61_default_profile_suggests_gate_but_does_not_force_it(self) -> None:
        """行为 61.2：默认工作论文 profile 只建议开启方法门，不强制阻断。"""
        gate = build_cgss_method_gate(
            self._evidence_package(),
            self._literature_packet(),
            self._paper_assembly(),
        )

        self.assertEqual(gate["status"], "method_gate_suggested_needs_human_review")
        self.assertFalse(gate["gate_enforcement"]["required"])
        self.assertEqual(gate["gate_enforcement"]["mode"], "suggested")
        self.assertIn("aer_like", gate["gate_enforcement"]["recommended_profiles"])

    def test_bdd_61_checks_required_method_standards_and_risk_register(self) -> None:
        """行为 61.3：门禁逐项检查变量、模型、文献、控制、稳健性和内生性风险。"""
        gate = build_cgss_method_gate(
            self._evidence_package(),
            self._literature_packet(),
            self._paper_assembly(),
            profile="aer_like",
        )

        checks = {item["id"]: item for item in gate["checks"]}
        for check_id in [
            "variable_definitions",
            "ordered_outcome_model_fit",
            "social_capital_theory_literature",
            "baseline_controls",
            "robustness_heterogeneity_mechanism_plan",
            "reverse_causality_and_omitted_variable_risk",
        ]:
            self.assertIn(check_id, checks)

        self.assertEqual(checks["variable_definitions"]["status"], "passed")
        self.assertEqual(checks["ordered_outcome_model_fit"]["status"], "passed")
        self.assertEqual(checks["social_capital_theory_literature"]["status"], "needs_human_verification")
        self.assertEqual(checks["robustness_heterogeneity_mechanism_plan"]["status"], "needs_followup")
        self.assertEqual(checks["reverse_causality_and_omitted_variable_risk"]["status"], "risk_flagged")
        self.assertIn("reverse_causality", gate["risk_register"])
        self.assertIn("omitted_variables", gate["risk_register"])

    def test_bdd_61_uses_result_numbers_from_evidence_package_only(self) -> None:
        """行为 61.4：方法门里的结果数字必须来自结果证据包。"""
        gate = build_cgss_method_gate(
            self._evidence_package(),
            self._literature_packet(),
            self._paper_assembly(),
            profile="aer_like",
        )

        numbers = gate["result_number_bindings"]
        self.assertEqual(numbers["source"], "cgss_results_evidence_package")
        self.assertEqual(numbers["ols"]["coef"], 0.1658)
        self.assertEqual(numbers["ordered_logit"]["coef"], 0.405)
        self.assertEqual(numbers["ols"]["nobs"], 5310)
        self.assertEqual(numbers["ordered_logit"]["nobs"], 5310)
        self.assertIn("do_not_invent_numbers", gate["evidence_rules"])

    def test_bdd_61_writes_review_files_without_formal_state(self) -> None:
        """行为 61.5：输出 JSON 和人工审阅报告，不写正式层。"""
        gate = build_cgss_method_gate(
            self._evidence_package(),
            self._literature_packet(),
            self._paper_assembly(),
            profile="aer_like",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_path, review_path = write_cgss_method_gate_outputs(project_root, gate)

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertFalse((project_root / "state/product/method_gate.json").exists())
            self.assertFalse((project_root / "Manuscripts/sections/empirical-strategy.md").exists())
            saved = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "needs_human_method_gate_review")
            review = review_path.read_text(encoding="utf-8")
            self.assertIn("CGSS AER-like 方法规范门", review)
            self.assertIn("反向因果", review)

    def test_bdd_61_blocks_when_core_inputs_are_not_ready(self) -> None:
        """行为 61.6：证据包或论文草稿未就绪时，不生成可审阅方法门。"""
        evidence = self._evidence_package()
        evidence["status"] = "blocked"

        gate = build_cgss_method_gate(
            evidence,
            self._literature_packet(),
            self._paper_assembly(),
            profile="aer_like",
        )

        self.assertEqual(gate["status"], "blocked_missing_method_gate_inputs")
        self.assertIn("results_evidence_package_not_ready", gate["blocking_reasons"])
        self.assertFalse(gate["gate_enforcement"]["required"])
        self.assertFalse(gate["formal_writeback_allowed"])

    def _evidence_package(self) -> dict:
        return {
            "schema_version": "p6.cgss_results_evidence_package.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "ready_for_paper_draft_input",
            "dataset": {"year": "2023", "source": "CGSS2023.dta"},
            "variables": {
                "outcome": "happiness <- a36",
                "social_capital": {"index": "social_capital_index", "source_items": ["a33", "a31a", "a31b", "a311"]},
                "controls": ["female", "age", "education_level", "log_income", "health", "urban_hukou"],
            },
            "primary_result": {
                "ols": {"coef": 0.1658, "std_error": 0.0187, "p_value": 0.0, "nobs": 5310},
                "ordered_logit": {"coef": 0.4050, "std_error": 0.0424, "p_value": 0.0, "nobs": 5310},
            },
            "evidence_consistency": {
                "sample_nobs_match": True,
                "ordered_method_gate": "passed",
                "social_capital_direction": "consistent_positive",
            },
        }

    def _literature_packet(self) -> dict:
        return {
            "schema_version": "p6.cgss_literature_review_draft_packet.v1",
            "status": "needs_human_literature_review_draft_approval",
            "paragraph_blocks": [
                {"id": "theory_foundation", "citation_keys": ["putnam_2000", "bourdieu_1986"]},
                {"id": "measurement_foundation", "citation_keys": ["ferrer_i_carbonell_frijters_2004"]},
                {"id": "cgss_empirical_context", "citation_keys": ["cnki_social_capital_happiness_candidate"]},
                {"id": "method_transition", "citation_keys": ["ordered_outcome_candidate"]},
            ],
            "open_dependencies": [{"status": "manual_verification_required"}],
        }

    def _paper_assembly(self) -> dict:
        return {
            "schema_version": "p6.cgss_exploratory_paper_assembler.v1",
            "status": "needs_human_exploratory_paper_review",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "paper_metrics": {"chinese_characters": 5399, "minimum_chinese_characters": 5000},
            "assembled_sections": [
                {"section_id": "literature_and_contribution", "evidence_bindings": ["cgss_literature_review_draft_packet"]},
                {"section_id": "data_and_measurement", "evidence_bindings": ["cgss_results_evidence_package"]},
                {"section_id": "empirical_strategy", "evidence_bindings": ["cgss_results_evidence_package"]},
                {"section_id": "main_results", "evidence_bindings": ["cgss_results_evidence_package"]},
            ],
        }


if __name__ == "__main__":
    unittest.main()
