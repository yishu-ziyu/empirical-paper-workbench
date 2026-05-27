import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_run_plan_seed import (
    build_cgss_run_plan_seed,
    write_cgss_run_plan_seed_outputs,
)


class CgssRunPlanSeedTests(unittest.TestCase):
    """BDD: CGSS DesignSpec draft must become a reviewable execution plan before any real run."""

    def test_bdd_56_builds_reviewable_run_plan_seed_without_formal_writeback(self) -> None:
        """行为 56.1：RunPlan seed 只能进入草案层，不能静默写正式 RunPlan。"""
        report = build_cgss_run_plan_seed(self._design_draft())

        self.assertEqual(report["schema_version"], "p6.cgss_run_plan_seed.v1")
        self.assertEqual(report["status"], "needs_human_run_plan_seed_review")
        self.assertFalse(report["boundary_flags"]["modified_formal_run_plan"])
        self.assertFalse(report["boundary_flags"]["modified_formal_design_spec"])
        self.assertFalse(report["boundary_flags"]["wrote_state_product"])
        self.assertFalse(report["boundary_flags"]["ran_models"])
        self.assertFalse(report["promotion"]["allowed"])
        self.assertEqual(report["promotion"]["would_write_if_approved"], "state/product/run_plan.json")

        seed = report["run_plan_seed"]
        self.assertEqual(seed["status"], "draft_needs_human_review")
        self.assertEqual(seed["dataset_path"], "/data/CGSS2023.dta")
        self.assertEqual(seed["design_spec_draft_id"], "cgss_design_spec_draft")

    def test_bdd_56_translates_raw_cgss_fields_to_executable_analysis_variables(self) -> None:
        """行为 56.2：执行前必须说明原始字段如何变成模型变量。"""
        report = build_cgss_run_plan_seed(self._design_draft())

        preflight = report["execution_preflight"]
        self.assertEqual(preflight["status"], "ready_for_human_review")
        for column in ("a36", "a33", "a31a", "a31b", "a311", "a2", "a3a", "a7a", "a8a", "a15", "a18", "s41"):
            self.assertIn(column, preflight["required_source_columns"])
        self.assertIn("happiness", preflight["required_analysis_columns"])
        self.assertIn("social_capital_index", preflight["required_analysis_columns"])
        self.assertEqual(preflight["feature_engineering"]["outcome"]["source"], "a36")
        self.assertEqual(preflight["feature_engineering"]["social_capital_index"]["source_items"], ["a33", "a31a", "a31b", "a311"])
        self.assertEqual(preflight["feature_engineering"]["controls"]["age"], "2023 - a3a")
        self.assertIn("a7b", preflight["deferred_control_source_columns"])
        self.assertIn("a21", preflight["deferred_control_source_columns"])
        self.assertIn("a8b", preflight["deferred_control_source_columns"])

    def test_bdd_56_schedules_ols_and_ordered_logit_cli_tasks(self) -> None:
        """行为 56.3：RunPlan seed 必须给出可执行命令和预期产物。"""
        report = build_cgss_run_plan_seed(self._design_draft())

        tasks = {task["id"]: task for task in report["run_plan_seed"]["tasks"]}
        self.assertIn("run_ols_baseline", tasks)
        self.assertIn("run_ordered_logit_robustness", tasks)
        self.assertEqual(tasks["run_ols_baseline"]["method_id"], "ols")
        self.assertEqual(tasks["run_ordered_logit_robustness"]["method_id"], "ordered_logit")
        self.assertIn("Program/cgss_minimal_model.py", tasks["run_ols_baseline"]["cli"])
        self.assertIn("Program/cgss_ordered_robustness.py", tasks["run_ordered_logit_robustness"]["cli"])
        self.assertIn("social_capital_index", tasks["run_ols_baseline"]["formula"])
        self.assertNotIn("social_capital_index_draft", tasks["run_ols_baseline"]["formula"])
        self.assertIn("Results/json/cgss_social_capital_happiness_minimal_model.json", tasks["run_ols_baseline"]["expected_outputs"])
        self.assertIn(
            "Results/json/cgss_social_capital_happiness_ordered_robustness.json",
            tasks["run_ordered_logit_robustness"]["expected_outputs"],
        )

    def test_bdd_56_blocks_when_design_spec_draft_is_not_reviewable(self) -> None:
        """行为 56.4：DesignSpec 草案没到审阅态时，不能生成执行计划。"""
        design_draft = self._design_draft()
        design_draft["status"] = "blocked_missing_dataset_bound_variable_roles"

        report = build_cgss_run_plan_seed(design_draft)

        self.assertEqual(report["status"], "blocked_missing_reviewable_design_spec_draft")
        self.assertIn("design_spec_draft_not_reviewable", report["blocking_reasons"])
        self.assertEqual(report["run_plan_seed"], {})
        self.assertFalse(report["promotion"]["allowed"])

    def test_bdd_56_writes_reviewable_markdown_without_state_product(self) -> None:
        """行为 56.5：写出审阅文件，但不创建正式 RunPlan。"""
        report = build_cgss_run_plan_seed(self._design_draft())

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_path, review_path = write_cgss_run_plan_seed_outputs(
                project_root,
                report,
                Path("Results/json/cgss_run_plan_seed.json"),
                Path("Reviews/cgss_run_plan_seed.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            saved = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "needs_human_run_plan_seed_review")
            review = review_path.read_text(encoding="utf-8")
            self.assertIn("CGSS RunPlan seed", review)
            self.assertIn("OLS 基准模型", review)
            self.assertIn("Ordered Logit 有序模型", review)
            self.assertIn("不写正式 RunPlan", review)
            self.assertFalse((project_root / "state/product/run_plan.json").exists())

    def _design_draft(self) -> dict:
        return {
            "schema_version": "p6.cgss_design_spec_draft.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            "status": "needs_human_design_spec_review",
            "blocking_reasons": [],
            "design_spec_draft": {
                "id": "cgss_design_spec_draft",
                "status": "draft_needs_human_review",
                "research_question": "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
                "dataset_year": "2023",
                "dataset_path": "/data/CGSS2023.dta",
                "variables": {
                    "outcome": ["happiness"],
                    "treatment": ["social_capital_index_draft"],
                    "controls": ["a2", "a3a", "a7a", "a7b", "a15", "a18", "a21", "a8a", "a8b", "s41"],
                    "fixed_effects": ["s41"],
                    "cluster_by": [],
                },
                "source_variable_bindings": {
                    "outcome": ["a36"],
                    "treatment_items": ["a33", "a31a", "a31b", "a311"],
                    "control_items": ["a2", "a3a", "a7a", "a7b", "a15", "a18", "a21", "a8a", "a8b", "s41"],
                },
                "model_candidates": [
                    {"id": "ols_baseline", "estimator": "ols"},
                    {"id": "ordered_logit", "estimator": "ordered_logit"},
                ],
            },
        }


if __name__ == "__main__":
    unittest.main()
