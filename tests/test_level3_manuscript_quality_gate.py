import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.level3_manuscript_quality_gate import build_level3_quality_gate, write_report


class Level3ManuscriptQualityGateTests(unittest.TestCase):
    """BDD: Auto Mode paper packages must be complete enough for human Level 3 review."""

    def test_bdd_p7c_complete_paper_passes_level3_structure_and_length_minimum(self) -> None:
        gate = build_level3_quality_gate(
            paper_text=self._complete_paper(),
            package_manifest=self._package_manifest(),
            source_paths={"paper": "paper.md", "package_manifest": "manifest.json"},
        )

        self.assertEqual(gate["schema_version"], "p7.level3_manuscript_quality_gate.v1")
        self.assertEqual(gate["status"], "needs_human_level3_quality_review")
        self.assertEqual(gate["gate_status"], "yellow")
        self.assertTrue(gate["ready_for_level3_review"])
        self.assertEqual(gate["structure_check"]["missing_sections"], [])
        self.assertEqual(gate["length_check"]["status"], "passed_minimum")
        self.assertGreaterEqual(gate["length_check"]["chinese_characters"], 5000)
        self.assertFalse(gate["boundary_flags"]["modified_formal_manuscript"])

    def test_bdd_p7c_short_or_incomplete_paper_is_not_ready_for_level3_review(self) -> None:
        paper = "# Test\n\n## 摘要\n\n太短。\n\n## 引言\n\n还没有完成。"

        gate = build_level3_quality_gate(paper_text=paper, package_manifest={})

        self.assertFalse(gate["ready_for_level3_review"])
        self.assertEqual(gate["length_check"]["status"], "too_short")
        self.assertIn("literature_review", gate["structure_check"]["missing_sections"])
        self.assertIn("robustness_and_further_tests", gate["structure_check"]["missing_sections"])
        self.assertIn("human_review_checklist", gate["structure_check"]["missing_sections"])

    def test_bdd_p7c_candidate_references_must_be_marked_for_human_review(self) -> None:
        paper = self._complete_paper().replace("（候选，待人工核验）", "")

        gate = build_level3_quality_gate(paper_text=paper, package_manifest=self._package_manifest())

        self.assertEqual(gate["citation_policy_check"]["status"], "needs_human_review_markers")
        self.assertFalse(gate["citation_policy_check"]["candidate_references_can_support_claims"])
        self.assertIn("mark_candidate_references_for_human_review", gate["required_followup_tasks"])

    def test_bdd_p7c_package_manifest_distinguishes_artifact_trust_layers(self) -> None:
        gate = build_level3_quality_gate(
            paper_text=self._complete_paper(),
            package_manifest=self._package_manifest(),
        )

        artifacts = gate["artifact_check"]
        self.assertEqual(artifacts["status"], "needs_human_review")
        self.assertIn("results_evidence_package.json", artifacts["real_run_artifacts"])
        self.assertIn("paper.md", artifacts["draft_layer_artifacts"])
        self.assertIn("method_gate.md", artifacts["human_review_required"])
        self.assertFalse(gate["boundary_flags"]["modified_product_state"])

    def test_bdd_p7c_writes_json_and_markdown_review_outputs(self) -> None:
        gate = build_level3_quality_gate(
            paper_text=self._complete_paper(),
            package_manifest=self._package_manifest(),
        )

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            report_path, review_path = write_report(
                project_root,
                gate,
                Path("Results/json/level3_manuscript_quality_gate.json"),
                Path("Reviews/level3_manuscript_quality_gate.md"),
            )

            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "needs_human_level3_quality_review")
            review_text = review_path.read_text(encoding="utf-8")
            self.assertIn("Level 3 Manuscript Quality Gate", review_text)
            self.assertIn("正式论文写回：否", review_text)
            self.assertIn("needs_human_level3_quality_review", review_text)

    def _complete_paper(self) -> str:
        filler = "这是用于质量门测试的正文材料，强调变量定义、数据来源、方法边界、结果解释和人工审阅要求。"
        long_body = "\n\n".join([filler * 18 for _ in range(8)])
        return (
            "# 工业机器人对劳动力市场匹配效率的影响研究\n\n"
            "## 摘要\n\n"
            f"{filler * 6}\n\n"
            "## 引言\n\n"
            f"{long_body}\n\n"
            "## 文献综述与研究贡献\n\n"
            f"{long_body}\n\n"
            "## 数据与变量\n\n"
            f"{long_body}\n\n"
            "## 实证策略\n\n"
            f"{long_body}\n\n"
            "## 主要实证结果\n\n"
            f"{long_body}\n\n"
            "## 稳健性与进一步检验计划\n\n"
            f"{long_body}\n\n"
            "## 结论\n\n"
            f"{filler * 10}\n\n"
            "## 参考文献候选\n\n"
            "- Acemoglu and Restrepo 2020（候选，待人工核验）\n"
            "- IFR robot data paper（候选，待人工核验）\n\n"
            "## 人工审阅清单\n\n"
            "- 参考文献是否已经人工核验？\n"
            "- 方法门是否允许进入正式层？\n"
        )

    def _package_manifest(self) -> dict:
        return {
            "schema_version": "p6.cgss_paper_package.v1",
            "status": "needs_human_paper_package_review",
            "real_run_artifacts": ["results_evidence_package.json", "paper.pdf"],
            "draft_layer_artifacts": ["paper.md", "literature_review_packet.json"],
            "human_review_required": ["method_gate.md", "reviewer_report.md", "revision_task_queue.md"],
            "boundary_flags": {
                "modified_formal_manuscript": False,
                "modified_verified_bibliography": False,
                "modified_product_state": False,
            },
        }


if __name__ == "__main__":
    unittest.main()
