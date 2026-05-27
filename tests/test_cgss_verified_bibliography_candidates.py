import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_literature_seed_package import build_literature_seed_package
from Program.workbench.cgss_literature_source_verification_preflight import build_literature_source_verification_preflight
from Program.workbench.cgss_verified_bibliography_candidates import (
    build_verified_bibliography_candidates,
    write_verified_bibliography_candidate_outputs,
)


class CgssVerifiedBibliographyCandidatesTests(unittest.TestCase):
    """BDD: source-checked literature can become bibliography candidates, not formal references."""

    def test_bdd_56_builds_source_checked_bibliography_candidates_without_formal_writeback(self) -> None:
        package = build_verified_bibliography_candidates(self._source_preflight())

        self.assertEqual(package["schema_version"], "p6.cgss_verified_bibliography_candidates.v1")
        self.assertEqual(package["status"], "needs_human_bibliography_approval")
        self.assertFalse(package["boundary_flags"]["modified_verified_bibliography"])
        self.assertFalse(package["boundary_flags"]["modified_formal_manuscript"])
        self.assertFalse(package["promotion"]["allowed"])
        self.assertGreaterEqual(len(package["verified_bibliography_candidates"]), 6)
        self.assertGreaterEqual(len(package["citation_bindings"]), 5)
        self.assertIn("S08", {item["source_id"] for item in package["verified_bibliography_candidates"]})
        self.assertIn("S09", {item["source_id"] for item in package["verified_bibliography_candidates"]})

    def test_bdd_56_keeps_unverified_sources_in_manual_queue(self) -> None:
        package = build_verified_bibliography_candidates(self._source_preflight())

        manual_ids = {item["source_id"] for item in package["manual_followup_queue"]}
        self.assertIn("S01", manual_ids)
        self.assertIn("S02", manual_ids)
        self.assertIn("S05", manual_ids)
        self.assertNotIn("S08", manual_ids)
        self.assertIn("browser_or_database_verification_required", package["blocking_reasons"])

    def test_bdd_56_binds_sources_to_specific_paper_sections_and_claims(self) -> None:
        package = build_verified_bibliography_candidates(self._source_preflight())

        bindings_by_source = {item["source_id"]: item for item in package["citation_bindings"]}
        self.assertEqual(bindings_by_source["S03"]["target_section"], "literature_review")
        self.assertEqual(bindings_by_source["S06"]["target_section"], "data_and_measurement")
        self.assertEqual(bindings_by_source["S10"]["target_section"], "empirical_strategy")
        self.assertIn("social capital", bindings_by_source["S03"]["claim_role"])
        self.assertIn("ordered outcome", bindings_by_source["S10"]["claim_role"])

    def test_bdd_56_blocks_when_source_preflight_is_not_ready(self) -> None:
        preflight = self._source_preflight()
        preflight["status"] = "blocked_missing_literature_seed"

        package = build_verified_bibliography_candidates(preflight)

        self.assertEqual(package["status"], "blocked_missing_source_preflight")
        self.assertEqual(package["verified_bibliography_candidates"], [])
        self.assertIn("source_preflight_not_ready", package["blocking_reasons"])
        self.assertFalse(package["promotion"]["allowed"])

    def test_bdd_56_writes_reviewable_candidate_files(self) -> None:
        package = build_verified_bibliography_candidates(self._source_preflight())

        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path = write_verified_bibliography_candidate_outputs(
                Path(tmpdir),
                package,
                Path("Results/json/verified_bibliography_candidates.json"),
                Path("Reviews/verified_bibliography_candidates.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(json.loads(result_path.read_text(encoding="utf-8"))["status"], "needs_human_bibliography_approval")
            self.assertIn("CGSS 可核验参考文献候选", review_path.read_text(encoding="utf-8"))

    def _source_preflight(self) -> dict:
        seed_package = build_literature_seed_package(
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
            },
        )
        return build_literature_source_verification_preflight(seed_package)


if __name__ == "__main__":
    unittest.main()
