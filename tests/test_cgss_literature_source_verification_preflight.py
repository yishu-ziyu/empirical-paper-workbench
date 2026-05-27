import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_literature_seed_package import build_literature_seed_package
from Program.workbench.cgss_literature_source_verification_preflight import (
    build_literature_source_verification_preflight,
    write_literature_source_preflight_outputs,
)


class CgssLiteratureSourceVerificationPreflightTests(unittest.TestCase):
    """BDD: seed literature must become a reviewable source-verification queue before citation use."""

    def test_bdd_55_builds_candidate_bibliography_without_formal_writeback(self) -> None:
        preflight = build_literature_source_verification_preflight(self._seed_package())

        self.assertEqual(preflight["schema_version"], "p6.cgss_literature_source_verification_preflight.v1")
        self.assertEqual(preflight["status"], "needs_source_verification")
        self.assertFalse(preflight["promotion"]["allowed"])
        self.assertFalse(preflight["boundary_flags"]["modified_verified_bibliography"])
        self.assertFalse(preflight["boundary_flags"]["modified_formal_manuscript"])
        self.assertGreaterEqual(len(preflight["candidate_bibliography"]), 8)
        self.assertGreaterEqual(len(preflight["manual_review_queue"]), 3)
        self.assertGreaterEqual(len(preflight["cnki_queue"]), 3)
        self.assertIn("CGSS 项目概况", {item["title"] for item in preflight["candidate_bibliography"]})

    def test_bdd_55_classifies_source_actions_by_evidence_type(self) -> None:
        preflight = build_literature_source_verification_preflight(self._seed_package())

        by_id = {item["id"]: item for item in preflight["candidate_bibliography"]}
        self.assertEqual(by_id["S01"]["verification_actions"], ["open_official_source", "record_access_date"])
        self.assertIn("verify_doi_or_publisher_page", by_id["S05"]["verification_actions"])
        self.assertIn("cnki_or_journal_page_check", by_id["S09"]["verification_actions"])
        self.assertIn("manual_cnki_verification_required", preflight["blocking_reasons"])

    def test_bdd_55_blocks_when_seed_package_is_not_reviewable(self) -> None:
        seed_package = self._seed_package()
        seed_package["status"] = "blocked_missing_variable_role_review"

        preflight = build_literature_source_verification_preflight(seed_package)

        self.assertEqual(preflight["status"], "blocked_missing_literature_seed")
        self.assertEqual(preflight["candidate_bibliography"], [])
        self.assertIn("literature_seed_not_reviewable", preflight["blocking_reasons"])
        self.assertFalse(preflight["promotion"]["allowed"])

    def test_bdd_55_writes_reviewable_source_preflight_files(self) -> None:
        preflight = build_literature_source_verification_preflight(self._seed_package())

        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path = write_literature_source_preflight_outputs(
                Path(tmpdir),
                preflight,
                Path("Results/json/literature_source_preflight.json"),
                Path("Reviews/literature_source_preflight.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(json.loads(result_path.read_text(encoding="utf-8"))["status"], "needs_source_verification")
            self.assertIn("CGSS 文献来源校验预检", review_path.read_text(encoding="utf-8"))

    def _seed_package(self) -> dict:
        return build_literature_seed_package(
            role_review_draft={
                "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
                "status": "needs_human_role_review",
                "proposed_roles": {
                    "outcome": {"canonical_name": "happiness", "source_variable": "a36"},
                    "treatment": {
                        "canonical_name": "social_capital_index",
                        "source_items": ["a33", "a31a", "a31b", "a311"],
                    },
                    "controls": ["female", "age", "education_level", "log_income", "health"],
                },
            },
            evidence_package={
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
                    },
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
