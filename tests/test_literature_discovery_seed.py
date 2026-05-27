import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.literature_discovery_seed import build_literature_discovery_seed, write_report


class LiteratureDiscoverySeedTests(unittest.TestCase):
    """BDD: LiteratureAgent must turn a topic and data context into reviewable discovery tasks."""

    def test_bdd_p7b_expands_custom_topic_into_chinese_and_english_queries(self) -> None:
        packet = build_literature_discovery_seed(
            topic="工业机器人对劳动力市场匹配效率的影响",
            dataset_index=self._dataset_index(),
        )

        self.assertEqual(packet["schema_version"], "p7.literature_discovery_seed.v1")
        self.assertEqual(packet["status"], "needs_human_literature_discovery_review")
        self.assertGreaterEqual(len(packet["query_plan"]["search_queries"]), 8)
        query_text = "\n".join(item["query"] for item in packet["query_plan"]["search_queries"])
        self.assertIn("工业机器人 劳动力市场 匹配效率", query_text)
        self.assertIn("industrial robots labor market matching efficiency", query_text)
        self.assertIn("automation labor market matching China", query_text)

    def test_bdd_p7b_folds_dataset_index_context_into_query_plan(self) -> None:
        packet = build_literature_discovery_seed(
            topic="工业机器人对劳动力市场匹配效率的影响",
            dataset_index=self._dataset_index(),
        )

        data_terms = packet["query_plan"]["dataset_context_terms"]
        self.assertIn("IFR", data_terms)
        self.assertIn("robot", data_terms)
        self.assertIn("CLDS", data_terms)
        self.assertIn("CFPS", data_terms)
        self.assertIn("CMDS", data_terms)
        contextual_queries = [item["query"] for item in packet["query_plan"]["search_queries"] if item["source_context"] == "dataset_index"]
        self.assertTrue(any("IFR" in query for query in contextual_queries))
        self.assertTrue(any("CLDS" in query for query in contextual_queries))

    def test_bdd_p7b_registers_discovery_and_fulltext_sources(self) -> None:
        packet = build_literature_discovery_seed(
            topic="工业机器人对劳动力市场匹配效率的影响",
            dataset_index=self._dataset_index(),
        )

        source_ids = {item["source_id"] for item in packet["source_registry"]}
        self.assertIn("local_pdf_or_zotero_import", source_ids)
        self.assertIn("openalex_metadata", source_ids)
        self.assertIn("crossref_metadata", source_ids)
        self.assertIn("semantic_scholar_metadata", source_ids)
        self.assertIn("open_fulltext_discovery", source_ids)
        self.assertIn("cnki_manual_review_queue", source_ids)
        self.assertIn("google_scholar_manual_queue", source_ids)
        self.assertIn("user_uploaded_fulltext", source_ids)

    def test_bdd_p7b_candidate_records_cannot_support_claims_before_review(self) -> None:
        packet = build_literature_discovery_seed(
            topic="工业机器人对劳动力市场匹配效率的影响",
            dataset_index=self._dataset_index(),
        )

        self.assertEqual(packet["bibliography_state_model"]["states"][0], "candidate")
        self.assertIn("approved_for_project_bibliography", packet["bibliography_state_model"]["states"])
        self.assertGreaterEqual(len(packet["candidate_search_records"]), 8)
        for record in packet["candidate_search_records"]:
            self.assertEqual(record["review_state"], "candidate")
            self.assertFalse(record["can_support_strong_claims"])
            self.assertEqual(record["required_next_state"], "metadata_verified")
        self.assertFalse(packet["promotion"]["allowed"])
        self.assertFalse(packet["boundary_flags"]["modified_formal_bibliography"])

    def test_bdd_p7b_writes_json_and_markdown_review_outputs(self) -> None:
        packet = build_literature_discovery_seed(
            topic="工业机器人对劳动力市场匹配效率的影响",
            dataset_index=self._dataset_index(),
        )

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            report_path, review_path = write_report(
                project_root,
                packet,
                Path("Results/json/literature_discovery_seed.json"),
                Path("Reviews/literature_discovery_seed.md"),
            )

            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "needs_human_literature_discovery_review")
            review_text = review_path.read_text(encoding="utf-8")
            self.assertIn("Literature Discovery Seed Review", review_text)
            self.assertIn("正式 bibliography 写回：否", review_text)
            self.assertIn("needs_human_literature_discovery_review", review_text)

    def _dataset_index(self) -> dict:
        return {
            "schema_version": "p7.dataset_motherlode_index.v1",
            "status": "needs_human_dataset_index_review",
            "candidate_data_bindings": [
                {
                    "family_name": "外部源数据",
                    "match_reasons": ["ifr", "robot", "工业机器人", "机器人"],
                    "year_hints": ["1993", "2023"],
                },
                {
                    "family_name": "A005CLDS中国劳动力动态调查数据",
                    "match_reasons": ["clds", "劳动", "劳动力"],
                    "year_hints": ["2018"],
                },
                {
                    "family_name": "A001CFPS中国家庭追踪调查",
                    "match_reasons": ["cfps"],
                    "year_hints": ["2022"],
                },
                {
                    "family_name": "A019-中国流动人口动态监测CMDS数据2011-2018年",
                    "match_reasons": ["cmds"],
                    "year_hints": ["2018"],
                },
            ],
        }


if __name__ == "__main__":
    unittest.main()
