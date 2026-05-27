import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_run_plan_seed_executor import (
    build_blocked_execution_report,
    execute_approved_cgss_run_plan_seed,
    write_cgss_run_plan_seed_execution_outputs,
)


class CgssRunPlanSeedExecutorTests(unittest.TestCase):
    """BDD: approved CGSS RunPlan seeds can drive draft-layer model execution."""

    def test_bdd_58_blocks_when_seed_is_not_approved(self) -> None:
        """行为 58.1：没有批准版 RunPlan seed 时，不能启动模型执行。"""
        report = build_blocked_execution_report(
            approved_seed={},
            topic="社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            reason="missing_approved_run_plan_seed",
        )

        self.assertEqual(report["schema_version"], "p6.cgss_run_plan_seed_execution.v1")
        self.assertEqual(report["status"], "blocked_run_plan_seed_not_approved")
        self.assertIn("missing_approved_run_plan_seed", report["blocking_reasons"])
        self.assertFalse(report["ran_models"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertEqual(report["model_artifacts"], {})

    def test_bdd_58_executes_ols_ordered_and_evidence_package_after_approval(self) -> None:
        """行为 58.2：批准后按 seed 执行 OLS、Ordered Logit，并生成结果证据包。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report = execute_approved_cgss_run_plan_seed(
                project_root=project_root,
                approved_seed=self._approved_seed(),
                topic="社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
                model_runner=self._fake_model_runner,
            )

            self.assertEqual(report["status"], "completed_needs_human_result_review")
            self.assertTrue(report["ran_models"])
            self.assertFalse(report["formal_writeback_allowed"])
            self.assertEqual(report["executed_tasks"], ["run_ols_baseline", "run_ordered_logit_robustness"])
            self.assertEqual(report["model_artifacts"]["minimal_model"]["status"], "completed_needs_human_review")
            self.assertEqual(report["model_artifacts"]["ordered_robustness"]["method_gate"], "passed")
            self.assertEqual(report["evidence_package"]["status"], "ready_for_paper_draft_input")
            self.assertFalse((project_root / "state/product/run_plan.json").exists())

    def test_bdd_58_writes_execution_record_and_review_without_formal_state(self) -> None:
        """行为 58.3：执行记录只进入草案证据层，不写正式产品状态。"""
        report = {
            "schema_version": "p6.cgss_run_plan_seed_execution.v1",
            "status": "completed_needs_human_result_review",
            "topic": "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            "ran_models": True,
            "formal_writeback_allowed": False,
            "blocking_reasons": [],
            "executed_tasks": ["run_ols_baseline", "run_ordered_logit_robustness"],
            "model_artifacts": {},
            "evidence_package": {"status": "ready_for_paper_draft_input"},
            "next_tasks": ["human_review_cgss_results_evidence_package"],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_path, review_path = write_cgss_run_plan_seed_execution_outputs(
                project_root,
                report,
                Path("Results/json/cgss_social_capital_happiness_run_plan_seed_execution.json"),
                Path("Reviews/cgss_social_capital_happiness_run_plan_seed_execution.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "completed_needs_human_result_review")
            self.assertIn("RunPlan seed 执行记录", review_path.read_text(encoding="utf-8"))
            self.assertFalse((project_root / "state/product/run_plan.json").exists())

    def _approved_seed(self) -> dict:
        return {
            "id": "cgss_run_plan_seed",
            "status": "approved_for_draft_execution",
            "dataset_path": "/data/CGSS2023.dta",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "human_approval": {
                "status": "approved",
                "approved_by": "mahaoxuan",
                "note": "批准进入草案层执行。",
            },
            "tasks": [
                {"id": "run_ols_baseline", "method_id": "ols"},
                {"id": "run_ordered_logit_robustness", "method_id": "ordered_logit"},
            ],
        }

    def _fake_model_runner(self, project_root: Path, approved_seed: dict, topic: str) -> tuple[dict, dict, dict]:
        minimal_model = {
            "schema_version": "p6.cgss_minimal_model.v1",
            "topic": topic,
            "status": "completed_needs_human_review",
            "dataset": {"path": approved_seed["dataset_path"], "year": "2023"},
            "sample": {"nobs": 5310},
            "variables": {
                "outcome": "happiness <- a36",
                "social_capital_index": ["a33 trust", "a31a neighbor_social"],
                "controls": ["female", "age"],
            },
            "models": {
                "baseline_index": {
                    "coefficients": {
                        "social_capital_index": {
                            "coef": 0.1658,
                            "std_error_hc1": 0.0187,
                            "p_value": 0.0,
                        }
                    }
                }
            },
        }
        ordered_robustness = {
            "schema_version": "p6.cgss_ordered_robustness.v1",
            "topic": topic,
            "status": "completed_needs_human_review",
            "sample": {"nobs": 5310, "outcome_levels": [1, 2, 3, 4, 5]},
            "method_gate": {"status": "passed", "blocking_reasons": []},
            "models": {
                "ordered_logit_index": {
                    "coefficients": {
                        "social_capital_index": {
                            "coef": 0.405,
                            "std_error": 0.0424,
                            "p_value": 0.0,
                        }
                    }
                }
            },
        }
        evidence_package = {
            "schema_version": "p6.cgss_results_evidence_package.v1",
            "status": "ready_for_paper_draft_input",
            "topic": topic,
        }
        return minimal_model, ordered_robustness, evidence_package


if __name__ == "__main__":
    unittest.main()
