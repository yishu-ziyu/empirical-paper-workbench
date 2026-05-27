import unittest

import pandas as pd

from Program.workbench.cgss_minimal_model import build_analysis_frame, run_cgss_minimal_model


class CgssMinimalModelTests(unittest.TestCase):
    """BDD: CGSS topic reproduction must run a real first-pass model before writing."""

    def test_bdd_50_runs_reviewable_minimal_model_without_formal_writeback(self) -> None:
        raw = pd.DataFrame(
            {
                "a36": [3, 4, 5, 4, 2, 5, 4, 3, 5, 4, 3, 5],
                "a33": [2, 4, 5, 4, 1, 5, 4, 3, 5, 4, 3, 5],
                "a31a": [7, 3, 1, 2, 7, 1, 2, 4, 1, 3, 4, 1],
                "a31b": [7, 3, 1, 2, 6, 1, 2, 4, 1, 3, 4, 1],
                "a311": [1, 3, 5, 4, 2, 5, 4, 3, 5, 4, 3, 5],
                "a2": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                "a3a": [1980, 1990, 1975, 1988, 1960, 1995, 1982, 1970, 1999, 1985, 1968, 1991],
                "a7a": [4, 12, 13, 10, 3, 12, 9, 6, 13, 12, 4, 11],
                "a8a": [30000, 60000, 100000, 80000, 10000, 120000, 50000, 20000, 150000, 70000, 40000, 90000],
                "a15": [3, 4, 5, 4, 2, 5, 4, 3, 5, 4, 3, 5],
                "a18": [1, 2, 4, 2, 1, 4, 2, 1, 4, 2, 1, 4],
                "s41": [1, 1, 2, 2, 3, 3, 1, 2, 3, 1, 2, 3],
            }
        )

        frame = build_analysis_frame(raw)
        report = run_cgss_minimal_model(
            frame,
            topic="社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            dataset_path="/data/CGSS2023.dta",
        )

        self.assertEqual(report["schema_version"], "p6.cgss_minimal_model.v1")
        self.assertEqual(report["status"], "completed_needs_human_review")
        self.assertFalse(report["boundary_flags"]["modified_formal_package"])
        self.assertGreaterEqual(report["sample"]["nobs"], 10)
        self.assertIn("social_capital_index", report["models"]["baseline_index"]["coefficients"])
        self.assertIn("trust", report["models"]["trust_only"]["coefficients"])
        self.assertIn("log_income", report["models"]["baseline_index"]["coefficients"])
        self.assertFalse(
            any(name.startswith("log_income[T.") for name in report["models"]["baseline_index"]["coefficients"])
        )
        self.assertIn("draft_cgss_paper_from_results", report["next_tasks"])


if __name__ == "__main__":
    unittest.main()
