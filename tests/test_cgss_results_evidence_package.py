import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_results_evidence_package import build_results_evidence_package, write_evidence_outputs


class CgssResultsEvidencePackageTests(unittest.TestCase):
    """BDD: CGSS model outputs must be merged into a writing-ready evidence package."""

    def test_bdd_52_merges_ols_and_ordered_results_without_formal_writeback(self) -> None:
        package = build_results_evidence_package(
            minimal_model=self._minimal_model(),
            ordered_robustness=self._ordered_robustness(),
        )

        self.assertEqual(package["schema_version"], "p6.cgss_results_evidence_package.v1")
        self.assertEqual(package["status"], "ready_for_paper_draft_input")
        self.assertEqual(package["topic"], "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析")
        self.assertEqual(package["evidence_consistency"]["social_capital_direction"], "consistent_positive")
        self.assertEqual(package["primary_result"]["ols"]["variable"], "social_capital_index")
        self.assertEqual(package["primary_result"]["ordered_logit"]["variable"], "social_capital_index")
        self.assertEqual(package["source_artifacts"]["minimal_model"]["schema_version"], "p6.cgss_minimal_model.v1")
        self.assertEqual(package["source_artifacts"]["ordered_robustness"]["schema_version"], "p6.cgss_ordered_robustness.v1")
        self.assertEqual(package["variables"]["social_capital"]["index"], "social_capital_index")
        self.assertIn("社会资本指数", package["writing_inputs"]["result_sentence_seed"])
        self.assertIn("outcome_measurement", package["human_review_checklist"])
        self.assertFalse(package["boundary_flags"]["modified_formal_package"])
        self.assertFalse(package["boundary_flags"]["modified_formal_variable_roles"])

    def test_bdd_52_blocks_when_required_model_output_is_missing(self) -> None:
        package = build_results_evidence_package(
            minimal_model={},
            ordered_robustness=self._ordered_robustness(),
        )

        self.assertEqual(package["status"], "blocked_missing_model_evidence")
        self.assertIn("missing_minimal_model", package["blocking_reasons"])
        self.assertEqual(package["primary_result"], {})
        self.assertFalse(package["boundary_flags"]["modified_formal_package"])

    def test_bdd_52_blocks_when_ordered_method_gate_did_not_pass(self) -> None:
        ordered = self._ordered_robustness()
        ordered["method_gate"] = {"status": "blocked", "blocking_reasons": ["outcome_has_too_few_ordered_levels"]}

        package = build_results_evidence_package(
            minimal_model=self._minimal_model(),
            ordered_robustness=ordered,
        )

        self.assertEqual(package["status"], "blocked_missing_model_evidence")
        self.assertIn("ordered_model_gate_not_passed", package["blocking_reasons"])
        self.assertEqual(package["primary_result"], {})

    def test_bdd_52_writes_reviewable_package_files(self) -> None:
        package = build_results_evidence_package(
            minimal_model=self._minimal_model(),
            ordered_robustness=self._ordered_robustness(),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path = write_evidence_outputs(
                Path(tmpdir),
                package,
                Path("Results/json/package.json"),
                Path("Reviews/package.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(json.loads(result_path.read_text(encoding="utf-8"))["status"], "ready_for_paper_draft_input")
            self.assertIn("结果证据包", review_path.read_text(encoding="utf-8"))

    def _minimal_model(self) -> dict:
        return {
            "schema_version": "p6.cgss_minimal_model.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "completed_needs_human_review",
            "dataset": {"path": "/data/CGSS2023.dta", "year": "2023"},
            "sample": {"nobs": 5310},
            "variables": {
                "outcome": "happiness <- a36",
                "social_capital_index": ["a33 trust", "a31a neighbor_social"],
                "controls": ["female", "age"],
            },
            "models": {
                "baseline_index": {
                    "coefficients": {
                        "social_capital_index": {"coef": 0.1658, "std_error_hc1": 0.0187, "p_value": 0.0000}
                    }
                }
            },
        }

    def _ordered_robustness(self) -> dict:
        return {
            "schema_version": "p6.cgss_ordered_robustness.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "completed_needs_human_review",
            "sample": {"nobs": 5310, "outcome_levels": [1, 2, 3, 4, 5]},
            "method_gate": {"status": "passed", "blocking_reasons": []},
            "models": {
                "ordered_logit_index": {
                    "coefficients": {
                        "social_capital_index": {"coef": 0.4050, "std_error": 0.0424, "p_value": 0.0000}
                    }
                }
            },
        }


if __name__ == "__main__":
    unittest.main()
