from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.paper_quality import build_paper_quality_report


class PaperEvidenceIntegrityGateTests(unittest.TestCase):
    """BDD: paper quality must block paper-like conclusions without real evidence."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="paper-evidence-integrity-"))
        self.project_root = self.tmp / "project"
        (self.project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (self.project_root / "Results" / "json").mkdir(parents=True)
        (self.project_root / "Tasks" / "demo").mkdir(parents=True)

    def test_bdd_blocks_placeholder_evidence_ids_and_missing_iv_diagnostics(self) -> None:
        """Given bad paper text, When quality runs, Then it blocks formal conclusions."""
        draft = self.project_root / "Manuscripts" / "generated" / "paper_draft.md"
        draft.write_text(
            "# 父母教育对子女工资的影响研究\n\n"
            "## Abstract\n\n"
            "本文报告父母教育对子女工资的因果影响。\n\n"
            "## Introduction\n\n"
            "父母教育回报在城镇样本中大于农村样本。evidence_id=main_reg_v1。\n\n"
            "## Literature and Contribution\n\n"
            "文献综述仍待 DOI 核验。\n\n"
            "## Institutional Background\n\n"
            "制度背景待补。\n\n"
            "## Data and Measurement\n\n"
            "本文使用 {dataset_name}，最终样本为 {n_obs} 个观测。\n\n"
            "## Empirical Strategy\n\n"
            "本文采用 IV 估计，但工具变量和样本单位仍未定义清楚。\n\n"
            "## Main Results\n\n"
            "2SLS 系数为 0.094，表 main_reg_v1 显示结果显著。\n\n"
            "## Robustness\n\n"
            "稳健性部分继续引用 evidence_id=robust_v1。\n\n"
            "## Conclusion\n\n"
            "本文结论可直接写入正式稿。\n\n"
            "## References\n\n"
            "待补。\n",
            encoding="utf-8",
        )
        (self.project_root / "Results" / "json" / "results.json").write_text(
            json.dumps(
                {
                    "method": "IV",
                    "provenance": {"model": "MiniMax-M3"},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (self.project_root / "Tasks" / "demo" / "design.json").write_text(
            json.dumps({"method": "IV"}, ensure_ascii=False),
            encoding="utf-8",
        )

        report = build_paper_quality_report(self.project_root, draft)
        integrity = report["evidence_integrity_checks"]

        self.assertEqual(integrity["status"], "blocked")
        self.assertFalse(integrity["can_write_formal_conclusions"])
        self.assertIn("evidence_integrity_blocked", report["verdict"])

        rule_ids = {issue["rule_id"] for issue in integrity["issues"]}
        self.assertIn("placeholder_in_manuscript", rule_ids)
        self.assertIn("unresolved_evidence_id", rule_ids)
        self.assertIn("missing_main_result_table", rule_ids)
        self.assertIn("missing_iv_diagnostics", rule_ids)

        task_by_id = {task["id"]: task for task in report["recommended_next_tasks"]}
        self.assertIn("audit_and_repair_evidence_chain", task_by_id)
        self.assertEqual(task_by_id["audit_and_repair_evidence_chain"]["agent"], "VerifierAgent")

    def test_bdd_uses_task_scoped_results_and_design_for_manuscript_slug(self) -> None:
        """Given one manuscript slug, Then evidence audit does not read another task's files."""
        draft_dir = self.project_root / "Manuscripts" / "parent-education-wage"
        draft_dir.mkdir(parents=True)
        draft = draft_dir / "paper_draft.md"
        draft.write_text(
            "# 研究草稿\n\n"
            "## Abstract\n\n摘要。\n\n"
            "## Main Results\n\n"
            "主结果引用 evidence_id=local_main_table。\n",
            encoding="utf-8",
        )
        (self.project_root / "Results" / "other-topic").mkdir(parents=True)
        (self.project_root / "Results" / "other-topic" / "results.json").write_text(
            json.dumps({"tables": [{"evidence_id": "wrong_table"}]}, ensure_ascii=False),
            encoding="utf-8",
        )
        (self.project_root / "Results" / "parent-education-wage").mkdir(parents=True)
        (self.project_root / "Results" / "parent-education-wage" / "results.json").write_text(
            json.dumps({"tables": [{"evidence_id": "local_main_table"}]}, ensure_ascii=False),
            encoding="utf-8",
        )
        (self.project_root / "Tasks" / "parent-education-wage").mkdir(parents=True, exist_ok=True)
        (self.project_root / "Tasks" / "parent-education-wage" / "design.json").write_text(
            json.dumps({"method": "OLS"}, ensure_ascii=False),
            encoding="utf-8",
        )

        report = build_paper_quality_report(self.project_root, draft)
        integrity = report["evidence_integrity_checks"]

        self.assertIn("Results/parent-education-wage/results.json", integrity["results_path"])
        self.assertEqual(integrity["unresolved_evidence_ids"], [])
        self.assertIn("local_main_table", integrity["resolved_evidence_ids"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
