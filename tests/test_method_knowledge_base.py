import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Program.workbench.method_knowledge_base import (
    build_method_knowledge_base,
    write_outputs,
)


class MethodKnowledgeBaseTests(unittest.TestCase):
    """BDD: MethodAgent must read method rules as a queryable knowledge base."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="method-kb-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_methodology_sources(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_bdd_p7f_separates_canonical_and_proposal_method_sources(self) -> None:
        """行为 1：canonical 与 proposal 分层索引，proposal 不能阻断正式导出。"""
        kb = build_method_knowledge_base(self.project_root, profile="aer_like")

        self.assertEqual(kb["schema_version"], "p7.method_knowledge_base.v1")
        self.assertEqual(kb["status"], "needs_human_method_kb_review")
        self.assertEqual(kb["source_summary"]["canonical_rule_count"], 1)
        self.assertEqual(kb["source_summary"]["proposal_source_count"], 1)
        self.assertTrue(kb["canonical_rules"][0]["can_block_formal_export"])
        self.assertFalse(kb["proposal_sources"][0]["can_block_formal_export"])
        self.assertEqual(kb["proposal_sources"][0]["review_status"], "proposal_only")
        self.assertFalse(kb["formal_export_policy"]["proposal_rules_can_block"])

    def test_bdd_p7f_returns_relevant_checks_for_cgss_ols_ordered_logit_query(self) -> None:
        """行为 2：CGSS 主观幸福感 + OLS/Ordered Logit 查询返回方法审阅 checks。"""
        kb = build_method_knowledge_base(
            self.project_root,
            query="CGSS 主观幸福感 社会资本 OLS Ordered Logit 横截面",
            profile="aer_like",
        )

        check_ids = {check["id"] for check in kb["recommended_checks"]}
        self.assertIn("ordered_outcome_model_fit", check_ids)
        self.assertIn("ols_association_boundary", check_ids)
        self.assertIn("endogeneity_risk_statement", check_ids)
        self.assertIn("baseline_controls", check_ids)
        self.assertIn("robustness_heterogeneity_mechanism_plan", check_ids)
        self.assertIn("candidate_citation_verification", check_ids)
        self.assertIn("cross_section_ols_ordered_logit", kb["method_families"])

    def test_bdd_p7f_aer_like_profile_recommends_but_does_not_over_enforce(self) -> None:
        """行为 3：AER-like profile 提高建议标准，但 proposal 未 review 前不越权阻断。"""
        kb = build_method_knowledge_base(
            self.project_root,
            query="Bartik IV weak instrument robustness",
            profile="aer_like",
        )

        self.assertEqual(kb["profile_policy"]["requested_profile"], "aer_like")
        self.assertIn("AER-like 顶刊标准", kb["profile_policy"]["recommended_standards"])
        self.assertEqual(
            kb["profile_policy"]["proposal_enforcement_mode"],
            "recommendation_only_until_canonical_review",
        )
        self.assertFalse(kb["formal_export_policy"]["can_export_based_on_method_kb_alone"])

    def test_bdd_p7f_writes_json_and_markdown_without_formal_writeback(self) -> None:
        """行为 4：输出 Method KB JSON 和审阅 Markdown，不写正式层或 canonical。"""
        kb = build_method_knowledge_base(self.project_root, profile="aer_like")

        report_path, review_path = write_outputs(
            self.project_root,
            kb,
            Path("Results/json/method_knowledge_base.json"),
            Path("Reviews/method_knowledge_base.md"),
        )

        self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "needs_human_method_kb_review")
        review = review_path.read_text(encoding="utf-8")
        self.assertIn("Method Knowledge Base", review)
        self.assertIn("proposal 规则阻断正式导出：否", review)
        self.assertFalse((self.project_root / "state/product/method_knowledge_base.json").exists())
        self.assertFalse((self.project_root / "Manuscripts/sections/empirical-strategy.md").exists())
        self.assertFalse((self.project_root / "Program/methodology/canonical/generated.yml").exists())
        self.assertFalse(kb["boundary_flags"]["modified_product_state"])
        self.assertFalse(kb["boundary_flags"]["modified_canonical_rules"])

    def test_bdd_p7f_blocks_when_methodology_sources_are_missing(self) -> None:
        """行为 5：缺少方法库来源时阻断，不伪造知识库 checks。"""
        empty_project = self.temp_dir / "empty-project"
        empty_project.mkdir()

        kb = build_method_knowledge_base(empty_project, query="OLS Ordered Logit")

        self.assertEqual(kb["status"], "blocked_missing_methodology_sources")
        self.assertIn("Program/methodology/README.md", kb["missing_inputs"])
        self.assertIn("Program/methodology/proposals", kb["missing_inputs"])
        self.assertEqual(kb["recommended_checks"], [])

    @staticmethod
    def _seed_methodology_sources(project_root: Path) -> None:
        methodology_root = project_root / "Program" / "methodology"
        proposal_dir = methodology_root / "proposals" / "2026-05-26-aer-skills-import"
        canonical_dir = methodology_root / "canonical" / "journal" / "aer"
        proposal_dir.mkdir(parents=True)
        canonical_dir.mkdir(parents=True)
        (methodology_root / "README.md").write_text(
            "# Methodology Library Boundary\n\n"
            "proposals cannot block formal export; canonical reviewed rules may block.\n",
            encoding="utf-8",
        )
        (proposal_dir / "proposal.yml").write_text(
            "id: 2026-05-26-aer-skills-import\n"
            "status: proposal_only\n"
            "review_status: needs_human_review\n"
            "purpose: AER-like top-journal review standards.\n"
            "initial_scope:\n"
            "  - identification\n"
            "  - robustness\n"
            "rules_boundary:\n"
            "  proposal_cannot:\n"
            "    - block formal export\n",
            encoding="utf-8",
        )
        (canonical_dir / "identification.yml").write_text(
            "rules:\n"
            "  - id: aer_like.iv.weak_instrument_requires_robust_inference\n"
            "    standard: aer_like\n"
            "    method_family: iv\n"
            "    review_status: reviewed\n"
            "    severity: blocking\n"
            "    blocks_formal_export: true\n"
            "    required_evidence:\n"
            "      - weak_iv_robust_inference\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
