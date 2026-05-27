import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_literature_review_draft_packet import (
    build_literature_review_draft_packet,
    write_literature_review_draft_packet_outputs,
)
from Program.workbench.cgss_literature_seed_package import build_literature_seed_package
from Program.workbench.cgss_literature_source_verification_preflight import build_literature_source_verification_preflight
from Program.workbench.cgss_verified_bibliography_candidates import build_verified_bibliography_candidates


class CgssLiteratureReviewDraftPacketTests(unittest.TestCase):
    """BDD: bibliography candidates can drive a reviewable literature draft packet."""

    def test_bdd_57_builds_pending_literature_review_draft_without_formal_writeback(self) -> None:
        packet = build_literature_review_draft_packet(self._bibliography_candidates())

        self.assertEqual(packet["schema_version"], "p6.cgss_literature_review_draft_packet.v1")
        self.assertEqual(packet["status"], "needs_human_literature_review_draft_approval")
        self.assertEqual(packet["draft_mode"], "pending_bibliography_approval")
        self.assertFalse(packet["boundary_flags"]["modified_formal_manuscript"])
        self.assertFalse(packet["boundary_flags"]["modified_verified_bibliography"])
        self.assertFalse(packet["promotion"]["allowed"])
        self.assertGreaterEqual(len(packet["paragraph_blocks"]), 4)
        self.assertGreaterEqual(packet["length_plan"]["target_chinese_characters"], 1200)

    def test_bdd_57_maps_each_paragraph_to_candidate_sources_and_claims(self) -> None:
        packet = build_literature_review_draft_packet(self._bibliography_candidates())

        blocks = {item["id"]: item for item in packet["paragraph_blocks"]}
        self.assertIn("S03", blocks["theory_foundation"]["source_ids"])
        self.assertIn("S07", blocks["measurement_foundation"]["source_ids"])
        self.assertIn("S08", blocks["cgss_empirical_context"]["source_ids"])
        self.assertIn("S10", blocks["method_transition"]["source_ids"])
        self.assertIn("社会资本", blocks["theory_foundation"]["draft_claim"])
        self.assertIn("有序", blocks["method_transition"]["draft_claim"])

    def test_bdd_57_keeps_unapproved_sources_as_open_dependencies(self) -> None:
        packet = build_literature_review_draft_packet(self._bibliography_candidates())

        dependency_ids = {item["source_id"] for item in packet["open_dependencies"]}
        self.assertIn("S01", dependency_ids)
        self.assertIn("S02", dependency_ids)
        self.assertIn("S05", dependency_ids)
        self.assertIn("manual_or_database_verification_required", packet["blocking_reasons"])

    def test_bdd_57_blocks_when_bibliography_candidates_are_not_reviewable(self) -> None:
        candidates = self._bibliography_candidates()
        candidates["status"] = "blocked_missing_source_preflight"

        packet = build_literature_review_draft_packet(candidates)

        self.assertEqual(packet["status"], "blocked_missing_bibliography_candidates")
        self.assertEqual(packet["paragraph_blocks"], [])
        self.assertIn("bibliography_candidates_not_reviewable", packet["blocking_reasons"])
        self.assertFalse(packet["promotion"]["allowed"])

    def test_bdd_57_writes_reviewable_draft_packet_files(self) -> None:
        packet = build_literature_review_draft_packet(self._bibliography_candidates())

        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path = write_literature_review_draft_packet_outputs(
                Path(tmpdir),
                packet,
                Path("Results/json/literature_review_draft_packet.json"),
                Path("Reviews/literature_review_draft_packet.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(json.loads(result_path.read_text(encoding="utf-8"))["status"], "needs_human_literature_review_draft_approval")
            self.assertIn("CGSS 文献综述草稿包", review_path.read_text(encoding="utf-8"))

    def _bibliography_candidates(self) -> dict:
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
        source_preflight = build_literature_source_verification_preflight(seed_package)
        return build_verified_bibliography_candidates(source_preflight)


if __name__ == "__main__":
    unittest.main()
