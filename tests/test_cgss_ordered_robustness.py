import unittest

import numpy as np
import pandas as pd

from Program.workbench.cgss_ordered_robustness import run_cgss_ordered_robustness


class CgssOrderedRobustnessTests(unittest.TestCase):
    """BDD: ordinal happiness outcomes need an ordered-model robustness gate."""

    def test_bdd_51_runs_ordered_logit_without_formal_writeback(self) -> None:
        frame = self._analysis_frame()

        report = run_cgss_ordered_robustness(
            frame,
            topic="社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            dataset_path="/data/CGSS2023.dta",
        )

        self.assertEqual(report["schema_version"], "p6.cgss_ordered_robustness.v1")
        self.assertEqual(report["status"], "completed_needs_human_review")
        self.assertEqual(report["method_gate"]["status"], "passed")
        self.assertEqual(report["models"]["ordered_logit_index"]["method"], "ordered_logit")
        self.assertIn("social_capital_index", report["models"]["ordered_logit_index"]["coefficients"])
        self.assertFalse(report["boundary_flags"]["modified_formal_package"])
        self.assertFalse(report["boundary_flags"]["modified_formal_variable_roles"])
        self.assertIn("draft_cgss_paper_from_ordered_robustness", report["next_tasks"])

    def test_bdd_51_blocks_when_happiness_has_too_few_ordered_levels(self) -> None:
        frame = self._analysis_frame()
        frame["happiness"] = 4

        report = run_cgss_ordered_robustness(
            frame,
            topic="社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            dataset_path="/data/CGSS2023.dta",
        )

        self.assertEqual(report["status"], "blocked_by_method_gate")
        self.assertEqual(report["method_gate"]["status"], "blocked")
        self.assertIn("outcome_has_too_few_ordered_levels", report["method_gate"]["blocking_reasons"])
        self.assertEqual(report["models"], {})
        self.assertFalse(report["boundary_flags"]["modified_formal_package"])

    def _analysis_frame(self) -> pd.DataFrame:
        rng = np.random.default_rng(20260527)
        n = 80
        social = rng.normal(0, 1, n)
        latent = social * 0.7 + rng.normal(0, 1, n)
        happiness = pd.cut(latent, bins=[-np.inf, -0.8, -0.2, 0.3, 0.9, np.inf], labels=[1, 2, 3, 4, 5])
        return pd.DataFrame(
            {
                "happiness": happiness.astype(int),
                "social_capital_index": social,
                "trust": social + rng.normal(0, 0.2, n),
                "female": rng.integers(0, 2, n).astype(float),
                "age": rng.integers(18, 78, n).astype(float),
                "education_level": rng.integers(1, 16, n).astype(float),
                "log_income": rng.normal(10.5, 0.5, n),
                "health": rng.integers(1, 6, n).astype(float),
                "urban_hukou": rng.integers(0, 2, n).astype(float),
                "province": [str(value) for value in rng.integers(1, 5, n)],
            }
        )


if __name__ == "__main__":
    unittest.main()
