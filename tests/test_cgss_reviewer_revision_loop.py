import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_reviewer_revision_loop import (
    build_cgss_reviewer_revision_loop,
    write_cgss_reviewer_revision_outputs,
)


class CgssReviewerRevisionLoopTests(unittest.TestCase):
    """BDD: reviewer-style feedback produces a draft revision loop, not formal writeback."""

    def test_bdd_62_builds_reviewer_report_covering_required_review_areas(self) -> None:
        """行为 62.1：审稿报告覆盖结构、文献、数据、识别、结果、稳健性、规范和人工判断。"""
        loop = build_cgss_reviewer_revision_loop(
            paper_markdown=self._paper_markdown(),
            paper_assembly=self._paper_assembly(),
            method_gate=self._method_gate(),
            results_evidence=self._results_evidence(),
            literature_packet=self._literature_packet(),
        )

        self.assertEqual(loop["schema_version"], "p6.cgss_reviewer_revision_loop.v1")
        self.assertEqual(loop["status"], "needs_human_revision_review")
        self.assertFalse(loop["formal_writeback_allowed"])
        areas = {item["area"] for item in loop["reviewer_report"]["findings"]}
        self.assertEqual(
            areas,
            {
                "paper_structure",
                "literature_review",
                "data_and_variables",
                "identification_strategy",
                "result_interpretation",
                "robustness_gap",
                "submission_standard_gap",
                "human_judgment_required",
            },
        )

    def test_bdd_62_builds_revision_queue_from_method_gate_and_review_findings(self) -> None:
        """行为 62.2：修订任务队列消费方法门风险，并保持草案层。"""
        loop = build_cgss_reviewer_revision_loop(
            paper_markdown=self._paper_markdown(),
            paper_assembly=self._paper_assembly(),
            method_gate=self._method_gate(),
            results_evidence=self._results_evidence(),
            literature_packet=self._literature_packet(),
        )

        queue = loop["revision_task_queue"]
        task_ids = {task["task_id"] for task in queue["tasks"]}
        self.assertIn("method.address_reverse_causality_and_omitted_variables", task_ids)
        self.assertIn("literature.verify_candidate_citations", task_ids)
        self.assertIn("writer.expand_robustness_and_mechanism_plan", task_ids)
        self.assertTrue(all(task["draft_layer_only"] for task in queue["tasks"]))
        self.assertFalse(queue["formal_writeback_allowed"])
        self.assertIn("reverse_causality", queue["source_method_gate_risks"])

    def test_bdd_62_generates_rev1_markdown_without_formal_layer_writeback(self) -> None:
        """行为 62.3：生成 Rev1 草稿，标记人工审阅，不写正式论文层。"""
        loop = build_cgss_reviewer_revision_loop(
            paper_markdown=self._paper_markdown(),
            paper_assembly=self._paper_assembly(),
            method_gate=self._method_gate(),
            results_evidence=self._results_evidence(),
            literature_packet=self._literature_packet(),
        )

        rev1 = loop["paper_rev1_markdown"]
        self.assertIn("Status: `needs_human_revision_review`", rev1)
        self.assertIn("## Rev1 审稿式修订说明", rev1)
        self.assertIn("反向因果", rev1)
        self.assertIn("候选引用仍需人工核验", rev1)
        self.assertIn("OLS 系数 0.1658", rev1)
        self.assertIn("Ordered Logit 系数 0.405", rev1)
        self.assertFalse(loop["boundary_flags"]["modified_formal_manuscript"])

    def test_bdd_62_writes_required_outputs_only(self) -> None:
        """行为 62.4：只写 reviewer report、revision queue 和 Rev1 草稿。"""
        loop = build_cgss_reviewer_revision_loop(
            paper_markdown=self._paper_markdown(),
            paper_assembly=self._paper_assembly(),
            method_gate=self._method_gate(),
            results_evidence=self._results_evidence(),
            literature_packet=self._literature_packet(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = write_cgss_reviewer_revision_outputs(Path(tmpdir), loop)

            self.assertTrue(paths["reviewer_report"].exists())
            self.assertTrue(paths["revision_task_queue"].exists())
            self.assertTrue(paths["paper_rev1"].exists())
            self.assertFalse((Path(tmpdir) / "Manuscripts/sections/introduction.md").exists())
            self.assertFalse((Path(tmpdir) / "state/product/paper.json").exists())
            self.assertIn("审稿式修订报告", paths["reviewer_report"].read_text(encoding="utf-8"))
            self.assertIn("审稿式修订任务队列", paths["revision_task_queue"].read_text(encoding="utf-8"))

    def test_bdd_62_blocks_when_method_gate_is_not_review_ready(self) -> None:
        """行为 62.5：方法门未就绪时，不生成 Rev1 草稿。"""
        method_gate = self._method_gate()
        method_gate["status"] = "blocked_missing_method_gate_inputs"

        loop = build_cgss_reviewer_revision_loop(
            paper_markdown=self._paper_markdown(),
            paper_assembly=self._paper_assembly(),
            method_gate=method_gate,
            results_evidence=self._results_evidence(),
            literature_packet=self._literature_packet(),
        )

        self.assertEqual(loop["status"], "blocked_revision_loop_inputs_not_ready")
        self.assertIn("method_gate_not_review_ready", loop["blocking_reasons"])
        self.assertEqual(loop["paper_rev1_markdown"], "")

    def _paper_markdown(self) -> str:
        return (
            "# 社会资本对居民主观幸福感的影响研究\n\n"
            "- Status: `needs_human_exploratory_paper_review`\n\n"
            "## 摘要\n\n探索性论文草稿。\n\n"
            "## 一、引言\n\n研究社会资本与幸福感。\n\n"
            "## 二、文献综述与研究贡献\n\n候选引用待核验。\n\n"
            "## 三、数据与变量\n\nCGSS2023 与变量定义。\n\n"
            "## 四、实证策略\n\nOLS 和 Ordered Logit。\n\n"
            "## 五、主要实证结果\n\n结果正向。\n\n"
            "## 六、稳健性与进一步检验计划\n\n需要后续检验。\n\n"
            "## 七、结论\n\n结论草稿。\n"
        )

    def _paper_assembly(self) -> dict:
        return {
            "status": "needs_human_exploratory_paper_review",
            "paper_metrics": {"chinese_characters": 5399},
            "formal_writeback_allowed": False,
        }

    def _method_gate(self) -> dict:
        return {
            "schema_version": "p6.cgss_method_gate.v1",
            "status": "needs_human_method_gate_review",
            "gate_status": "yellow",
            "risk_register": ["reverse_causality", "omitted_variables"],
            "checks": [
                {"id": "variable_definitions", "status": "passed"},
                {"id": "social_capital_theory_literature", "status": "needs_human_verification"},
                {"id": "robustness_heterogeneity_mechanism_plan", "status": "needs_followup"},
                {"id": "reverse_causality_and_omitted_variable_risk", "status": "risk_flagged"},
            ],
        }

    def _results_evidence(self) -> dict:
        return {
            "status": "ready_for_paper_draft_input",
            "primary_result": {
                "ols": {"coef": 0.1658, "std_error": 0.0187, "p_value": 0.0, "nobs": 5310},
                "ordered_logit": {"coef": 0.405, "std_error": 0.0424, "p_value": 0.0, "nobs": 5310},
            },
        }

    def _literature_packet(self) -> dict:
        return {
            "status": "needs_human_literature_review_draft_approval",
            "open_dependencies": [{"status": "manual_verification_required"}],
        }


if __name__ == "__main__":
    unittest.main()
