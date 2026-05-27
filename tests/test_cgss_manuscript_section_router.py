import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_manuscript_section_router import (
    build_cgss_manuscript_section_package,
    write_cgss_manuscript_section_outputs,
)


class CgssManuscriptSectionRouterTests(unittest.TestCase):
    """BDD: CGSS evidence packages become reviewable manuscript sections, not formal paper edits."""

    def test_bdd_58_routes_ready_evidence_into_reviewable_manuscript_sections(self) -> None:
        package = build_cgss_manuscript_section_package(
            self._results_evidence_package(),
            self._literature_review_draft_packet(),
        )

        self.assertEqual(package["schema_version"], "p6.cgss_manuscript_section_router.v1")
        self.assertEqual(package["status"], "needs_human_manuscript_section_review")
        self.assertTrue(package["draft_layer_only"])
        self.assertFalse(package["formal_writeback_allowed"])
        self.assertFalse(package["boundary_flags"]["modified_formal_manuscript"])
        self.assertFalse(package["boundary_flags"]["modified_verified_bibliography"])

        sections_by_id = {section["section_id"]: section for section in package["sections"]}
        self.assertEqual(
            set(sections_by_id),
            {"literature_and_contribution", "data_and_measurement", "empirical_strategy", "main_results"},
        )
        for section in sections_by_id.values():
            self.assertEqual(section["status"], "section_draft_ready_for_review")
            self.assertGreaterEqual(section["actual_chinese_characters"], section["minimum_chinese_characters"])
            self.assertTrue(section["evidence_bindings"])
            self.assertTrue(section["human_review_questions"])

        self.assertIn("putnam_2000", sections_by_id["literature_and_contribution"]["citation_keys"])
        self.assertIn("cgss_results_evidence_package", sections_by_id["data_and_measurement"]["evidence_bindings"])
        self.assertIn("cgss_results_evidence_package", sections_by_id["main_results"]["evidence_bindings"])
        self.assertIn("Ordered Logit", sections_by_id["main_results"]["draft_markdown"])

    def test_bdd_58_blocks_when_results_evidence_is_not_ready(self) -> None:
        evidence = self._results_evidence_package()
        evidence["status"] = "blocked_missing_model_evidence"

        package = build_cgss_manuscript_section_package(
            evidence,
            self._literature_review_draft_packet(),
        )

        self.assertEqual(package["status"], "blocked_missing_results_evidence_package")
        self.assertIn("results_evidence_package_not_ready", package["blocking_reasons"])
        self.assertEqual(package["sections"], [])
        self.assertFalse(package["formal_writeback_allowed"])

    def test_bdd_58_writes_draft_sections_and_review_without_formal_writeback(self) -> None:
        package = build_cgss_manuscript_section_package(
            self._results_evidence_package(),
            self._literature_review_draft_packet(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_path, review_path, section_paths = write_cgss_manuscript_section_outputs(
                project_root,
                package,
                Path("Results/json/cgss_manuscript_sections.json"),
                Path("Reviews/cgss_manuscript_sections.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(len(section_paths), 4)
            self.assertFalse((project_root / "state/product/paper.json").exists())
            self.assertFalse((project_root / "Data/literature/processed/verified_bibliography.csv").exists())

            saved = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "needs_human_manuscript_section_review")
            self.assertIn("CGSS 论文分节草案包", review_path.read_text(encoding="utf-8"))
            for section_path in section_paths:
                text = section_path.read_text(encoding="utf-8")
                self.assertIn("## 证据绑定", text)
                self.assertIn("## 人工审阅问题", text)

    def _results_evidence_package(self) -> dict:
        return {
            "schema_version": "p6.cgss_results_evidence_package.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            "status": "ready_for_paper_draft_input",
            "dataset": {
                "path": "/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A004CGSS中国综合社会调查/中国综合社会调查2023/CGSS2023.dta",
                "year": "2023",
                "source": "CGSS2023.dta",
            },
            "variables": {
                "outcome": "happiness <- a36",
                "social_capital": {
                    "index": "social_capital_index",
                    "source_items": ["a33 trust", "a31a neighbor_social", "a31b friend_social", "a311 leisure_social"],
                },
                "controls": ["female", "age", "education_level", "log_income", "health", "urban_hukou", "province fixed effects"],
                "ordered_outcome_levels": [1, 2, 3, 4, 5],
            },
            "primary_result": {
                "ols": {
                    "model": "baseline_index",
                    "variable": "social_capital_index",
                    "coef": 0.1658,
                    "std_error": 0.0187,
                    "p_value": 0.0,
                    "nobs": 5310,
                },
                "ordered_logit": {
                    "model": "ordered_logit_index",
                    "variable": "social_capital_index",
                    "coef": 0.4050,
                    "std_error": 0.0424,
                    "p_value": 0.0,
                    "nobs": 5310,
                    "outcome_levels": [1, 2, 3, 4, 5],
                },
            },
            "evidence_consistency": {
                "sample_nobs_match": True,
                "ordered_method_gate": "passed",
                "social_capital_direction": "consistent_positive",
            },
            "writing_inputs": {
                "result_sentence_seed": "在 CGSS2023 样本中，社会资本指数与居民主观幸福感呈正向相关；OLS 系数约为 0.1658，Ordered Logit 系数约为 0.4050。",
                "table_title_seed": "社会资本与居民主观幸福感：OLS 与 Ordered Logit 结果",
            },
            "human_review_checklist": [
                "outcome_measurement",
                "social_capital_index_construction",
                "control_variable_set",
                "ordered_model_interpretation",
                "literature_support_for_mechanism",
            ],
        }

    def _literature_review_draft_packet(self) -> dict:
        return {
            "schema_version": "p6.cgss_literature_review_draft_packet.v1",
            "status": "needs_human_literature_review_draft_approval",
            "length_plan": {
                "minimum_chinese_characters": 450,
                "target_chinese_characters": 900,
            },
            "paragraph_blocks": [
                {
                    "heading": "社会资本理论基础",
                    "citation_keys": ["putnam_2000", "bourdieu_1986"],
                    "draft_paragraph": "社会资本理论强调，个体的生活评价并不只来自收入和个人特征，也来自信任、互惠规范、关系网络和可动员资源。Putnam 的讨论强调信任与公共参与如何降低社会互动成本，Bourdieu 的框架则提醒我们，关系网络本身可能转化为资源。用于解释居民主观幸福感时，社会资本可以理解为一种嵌入日常关系的支持系统：它既可能通过信息、互助和安全感提高生活满意度，也可能通过更稳定的社会连接降低孤立感。",
                },
                {
                    "heading": "变量测量与 CGSS 题项口径",
                    "citation_keys": ["oecd_2025", "world_bank_2004"],
                    "draft_paragraph": "在测量层面，CGSS 的幸福感题项更接近生活评价意义上的主观幸福感代理变量。社会资本指数则需要说明其操作化边界：本文基于 CGSS2023 中可用的信任、邻里交往、朋友交往和休闲社会参与题项构造综合指标，因此它不是完整社会资本量表，而是围绕可观察社会连接形成的经验指标。这个边界需要在正文中直接交代。",
                },
            ],
            "open_dependencies": [
                {"source_id": "S01", "title": "CGSS 项目概况", "status": "manual_verification_required"}
            ],
        }


if __name__ == "__main__":
    unittest.main()
