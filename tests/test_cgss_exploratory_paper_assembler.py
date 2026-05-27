import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_exploratory_paper_assembler import (
    build_cgss_exploratory_paper_package,
    write_cgss_exploratory_paper_outputs,
)


class CgssExploratoryPaperAssemblerTests(unittest.TestCase):
    """BDD: reviewable CGSS section drafts assemble into a complete exploratory paper package."""

    def test_bdd_59_assembles_complete_exploratory_paper_without_formal_writeback(self) -> None:
        package = build_cgss_exploratory_paper_package(
            self._section_package(),
            self._results_evidence_package(),
            self._literature_review_packet(),
        )

        self.assertEqual(package["schema_version"], "p6.cgss_exploratory_paper_assembler.v1")
        self.assertEqual(package["status"], "needs_human_exploratory_paper_review")
        self.assertTrue(package["draft_layer_only"])
        self.assertFalse(package["formal_writeback_allowed"])
        self.assertFalse(package["boundary_flags"]["modified_formal_manuscript"])
        self.assertGreaterEqual(package["paper_metrics"]["chinese_characters"], 5000)

        paper = package["paper_markdown"]
        for heading in [
            "# 社会资本对居民主观幸福感的影响研究",
            "## 摘要",
            "## 一、引言",
            "## 二、文献综述与研究贡献",
            "## 三、数据与变量",
            "## 四、实证策略",
            "## 五、主要实证结果",
            "## 六、稳健性与进一步检验计划",
            "## 七、结论",
            "## 参考文献候选",
            "## 人工审阅清单",
        ]:
            self.assertIn(heading, paper)

        self.assertIn("cgss_results_evidence_package", package["evidence_ledger"])
        self.assertIn("cgss_literature_review_draft_packet", package["evidence_ledger"])
        self.assertIn("03-literature-and-contribution.md", package["assembled_sections"][0]["source_path"])
        self.assertIn("run_pdf_export_preflight", package["next_tasks"])

    def test_bdd_59_blocks_when_section_package_is_not_review_ready(self) -> None:
        section_package = self._section_package()
        section_package["status"] = "blocked_section_quality_gate"
        section_package["sections"][0]["status"] = "blocked_section_too_short"

        package = build_cgss_exploratory_paper_package(
            section_package,
            self._results_evidence_package(),
            self._literature_review_packet(),
        )

        self.assertEqual(package["status"], "blocked_manuscript_sections_not_ready")
        self.assertIn("manuscript_sections_not_review_ready", package["blocking_reasons"])
        self.assertEqual(package["paper_markdown"], "")
        self.assertFalse(package["formal_writeback_allowed"])

    def test_bdd_59_writes_paper_review_and_manifest_without_formal_state(self) -> None:
        package = build_cgss_exploratory_paper_package(
            self._section_package(),
            self._results_evidence_package(),
            self._literature_review_packet(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            paper_path, result_path, review_path = write_cgss_exploratory_paper_outputs(project_root, package)

            self.assertTrue(paper_path.exists())
            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertFalse((project_root / "Manuscripts/sections/introduction.md").exists())
            self.assertFalse((project_root / "state/product/paper.json").exists())

            saved = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "needs_human_exploratory_paper_review")
            self.assertIn("完整探索性论文草稿", review_path.read_text(encoding="utf-8"))
            self.assertIn("## 摘要", paper_path.read_text(encoding="utf-8"))

    def _section_package(self) -> dict:
        base_text = (
            "社会资本通过信任、互惠、关系网络和社会参与影响居民生活评价。"
            "本节绑定本地 CGSS 运行证据、候选文献和人工审阅问题，只进入草案层。"
        )
        section_ids = [
            ("literature_and_contribution", "文献综述与研究贡献", "03-literature-and-contribution.md"),
            ("data_and_measurement", "数据与变量", "04-data-and-measurement.md"),
            ("empirical_strategy", "实证策略", "05-empirical-strategy.md"),
            ("main_results", "主要实证结果", "06-main-results.md"),
        ]
        return {
            "schema_version": "p6.cgss_manuscript_section_router.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            "status": "needs_human_manuscript_section_review",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "sections": [
                {
                    "section_id": section_id,
                    "title": title,
                    "status": "section_draft_ready_for_review",
                    "path": f"Manuscripts/generated/cgss_social_capital_happiness_sections/{filename}",
                    "actual_chinese_characters": 700,
                    "minimum_chinese_characters": 500,
                    "evidence_bindings": ["cgss_results_evidence_package"],
                    "citation_keys": ["putnam_2000"],
                    "draft_markdown": f"# {title}\n\n## 草案正文\n\n{base_text * 12}\n",
                }
                for section_id, title, filename in section_ids
            ],
        }

    def _results_evidence_package(self) -> dict:
        return {
            "schema_version": "p6.cgss_results_evidence_package.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            "status": "ready_for_paper_draft_input",
            "dataset": {"year": "2023", "source": "CGSS2023.dta", "path": "/tmp/CGSS2023.dta"},
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

    def _literature_review_packet(self) -> dict:
        return {
            "schema_version": "p6.cgss_literature_review_draft_packet.v1",
            "status": "needs_human_literature_review_draft_approval",
            "candidate_citations": ["putnam_2000", "bourdieu_1986", "ferrer_i_carbonell_frijters_2004"],
            "open_dependencies": [{"source_id": "CNKI01", "title": "社会资本与居民幸福感中文研究", "status": "manual_verification_required"}],
        }


if __name__ == "__main__":
    unittest.main()
