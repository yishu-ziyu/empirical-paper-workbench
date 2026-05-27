import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_literature_seed_package import build_literature_seed_package, write_literature_seed_outputs


class CgssLiteratureSeedPackageTests(unittest.TestCase):
    """BDD: literature support must enter the CGSS paper path as reviewable evidence."""

    def test_bdd_54_builds_reviewable_literature_seed_without_formal_writeback(self) -> None:
        package = build_literature_seed_package(
            role_review_draft=self._role_review_draft(),
            evidence_package=self._evidence_package(),
        )

        self.assertEqual(package["schema_version"], "p6.cgss_literature_seed_package.v1")
        self.assertEqual(package["status"], "needs_human_literature_review")
        self.assertEqual(package["topic"], "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析")
        self.assertGreaterEqual(len(package["seed_sources"]), 8)
        self.assertIn("social_capital_theory", package["coverage"])
        self.assertIn("subjective_wellbeing_measurement", package["coverage"])
        self.assertIn("cgss_empirical_context", package["coverage"])
        self.assertIn("ordinal_outcome_method", package["coverage"])
        self.assertIn("a36", package["variable_support"]["outcome"]["source_variables"])
        self.assertIn("a33", package["variable_support"]["treatment"]["source_items"])
        self.assertIn("social_trust_mechanism", package["mechanism_map"])
        self.assertIn("ordered_logit", package["method_support"])
        self.assertGreaterEqual(len(package["cnki_manual_queue"]), 3)
        self.assertFalse(package["boundary_flags"]["modified_formal_bibliography"])
        self.assertFalse(package["boundary_flags"]["modified_formal_manuscript"])
        self.assertFalse(package["promotion"]["allowed"])

    def test_bdd_54_blocks_when_variable_roles_are_not_reviewable(self) -> None:
        draft = self._role_review_draft()
        draft["status"] = "blocked_missing_evidence_package"

        package = build_literature_seed_package(
            role_review_draft=draft,
            evidence_package=self._evidence_package(),
        )

        self.assertEqual(package["status"], "blocked_missing_variable_role_review")
        self.assertIn("variable_role_review_not_ready", package["blocking_reasons"])
        self.assertEqual(package["seed_sources"], [])
        self.assertFalse(package["promotion"]["allowed"])

    def test_bdd_54_writes_reviewable_literature_seed_files(self) -> None:
        package = build_literature_seed_package(
            role_review_draft=self._role_review_draft(),
            evidence_package=self._evidence_package(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path = write_literature_seed_outputs(
                Path(tmpdir),
                package,
                Path("Results/json/literature_seed.json"),
                Path("Reviews/literature_seed.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(json.loads(result_path.read_text(encoding="utf-8"))["status"], "needs_human_literature_review")
            self.assertIn("CGSS 文献综述种子包", review_path.read_text(encoding="utf-8"))

    def _role_review_draft(self) -> dict:
        return {
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "needs_human_role_review",
            "dataset": {"path": "/data/CGSS2023.dta", "year": "2023", "source": "CGSS2023.dta"},
            "proposed_roles": {
                "outcome": {
                    "canonical_name": "happiness",
                    "source_variable": "a36",
                    "source_label": "总的来说，您觉得您的生活是否幸福",
                    "ordered_levels": [1, 2, 3, 4, 5],
                },
                "treatment": {
                    "canonical_name": "social_capital_index",
                    "source_items": ["a33", "a31a", "a31b", "a311"],
                    "construction": "standardized_mean_index",
                },
                "controls": ["female", "age", "education_level", "log_income", "health", "urban_hukou", "province fixed effects"],
            },
            "boundary_flags": {
                "modified_formal_variable_roles": False,
                "modified_formal_package": False,
                "modified_design_spec": False,
                "modified_run_plan": False,
            },
        }

    def _evidence_package(self) -> dict:
        return {
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "ready_for_paper_draft_input",
            "primary_result": {
                "ols": {"variable": "social_capital_index", "coef": 0.1658, "std_error": 0.0187, "p_value": 7.78e-19, "nobs": 5310},
                "ordered_logit": {
                    "variable": "social_capital_index",
                    "coef": 0.4050,
                    "std_error": 0.0424,
                    "p_value": 1.25e-21,
                    "nobs": 5310,
                    "outcome_levels": [1, 2, 3, 4, 5],
                },
            },
            "evidence_consistency": {
                "sample_nobs_match": True,
                "ordered_method_gate": "passed",
                "social_capital_direction": "consistent_positive",
            },
        }


if __name__ == "__main__":
    unittest.main()
