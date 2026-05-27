import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_variable_role_review_draft import build_variable_role_review_draft, write_review_draft_outputs


class CgssVariableRoleReviewDraftTests(unittest.TestCase):
    """BDD: variable roles must be reviewable before they become canonical."""

    def test_bdd_53_builds_reviewable_variable_role_draft_without_formal_writeback(self) -> None:
        draft = build_variable_role_review_draft(
            evidence_package=self._evidence_package(),
            variable_candidates=self._variable_candidates(),
        )

        self.assertEqual(draft["schema_version"], "p6.cgss_variable_role_review_draft.v1")
        self.assertEqual(draft["status"], "needs_human_role_review")
        self.assertEqual(draft["topic"], "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析")
        self.assertEqual(draft["proposed_roles"]["outcome"]["canonical_name"], "happiness")
        self.assertEqual(draft["proposed_roles"]["treatment"]["canonical_name"], "social_capital_index")
        self.assertIn("a33", draft["proposed_roles"]["treatment"]["source_items"])
        self.assertIn("health", draft["proposed_roles"]["controls"])
        self.assertIn("outcome_measurement", draft["review_gates"])
        self.assertFalse(draft["boundary_flags"]["modified_formal_variable_roles"])
        self.assertFalse(draft["boundary_flags"]["modified_formal_package"])
        self.assertFalse(draft["boundary_flags"]["modified_design_spec"])
        self.assertFalse(draft["boundary_flags"]["modified_run_plan"])
        self.assertEqual(draft["proposed_roles"]["outcome"]["ordered_levels"], [1, 2, 3, 4, 5])
        self.assertIn("a15", draft["proposed_roles"]["control_source_candidates"]["health"])
        self.assertEqual(draft["result_evidence"]["primary_result"]["ols"]["nobs"], 5310)
        self.assertEqual(draft["result_evidence"]["evidence_consistency"]["social_capital_direction"], "consistent_positive")
        self.assertEqual(draft["review_decisions"]["outcome"]["decision"], "pending")
        self.assertEqual(draft["promotion"]["allowed"], False)

    def test_bdd_53_blocks_when_evidence_package_is_not_ready(self) -> None:
        evidence = self._evidence_package()
        evidence["status"] = "blocked_missing_model_evidence"

        draft = build_variable_role_review_draft(
            evidence_package=evidence,
            variable_candidates=self._variable_candidates(),
        )

        self.assertEqual(draft["status"], "blocked_missing_evidence_package")
        self.assertIn("evidence_package_not_ready", draft["blocking_reasons"])
        self.assertEqual(draft["proposed_roles"], {})
        self.assertFalse(draft["boundary_flags"]["modified_formal_variable_roles"])

    def test_bdd_53_writes_reviewable_draft_files(self) -> None:
        draft = build_variable_role_review_draft(
            evidence_package=self._evidence_package(),
            variable_candidates=self._variable_candidates(),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path = write_review_draft_outputs(
                Path(tmpdir),
                draft,
                Path("Results/json/draft.json"),
                Path("Reviews/draft.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(json.loads(result_path.read_text(encoding="utf-8"))["status"], "needs_human_role_review")
            self.assertIn("变量角色审阅草案", review_path.read_text(encoding="utf-8"))

    def _evidence_package(self) -> dict:
        return {
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "ready_for_paper_draft_input",
            "dataset": {"path": "/data/CGSS2023.dta", "year": "2023"},
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
                    "p_value": 7.78e-19,
                    "nobs": 5310,
                },
                "ordered_logit": {
                    "model": "ordered_logit_index",
                    "variable": "social_capital_index",
                    "coef": 0.4050,
                    "std_error": 0.0424,
                    "p_value": 1.25e-21,
                    "nobs": 5310,
                    "outcome_levels": [1, 2, 3, 4, 5],
                },
            },
            "evidence_consistency": {
                "sample_nobs_match": True,
                "ordered_method_gate": "passed",
                "social_capital_direction": "consistent_positive",
            },
            "source_artifacts": {
                "minimal_model": {
                    "path": "Results/json/cgss_social_capital_happiness_minimal_model.json",
                    "schema_version": "p6.cgss_minimal_model.v1",
                    "status": "completed_needs_human_review",
                },
                "ordered_robustness": {
                    "path": "Results/json/cgss_social_capital_happiness_ordered_robustness.json",
                    "schema_version": "p6.cgss_ordered_robustness.v1",
                    "status": "completed_needs_human_review",
                },
            },
            "human_review_checklist": ["outcome_measurement", "social_capital_index_construction", "control_variable_set"],
        }

    def _variable_candidates(self) -> dict:
        return {
            "status": "needs_human_review",
            "role_candidates": {
                "outcome": [
                    {"name": "a36", "label": "总的来说，您觉得您的生活是否幸福", "year": "2023"},
                ],
                "social_capital": [
                    {"name": "a33", "label": "一般而言，您同不同意在这个社会上，绝大多数人都是可以信任的", "year": "2023"},
                    {"name": "a31a", "label": "您与邻居进行社交娱乐活动的频繁程度", "year": "2023"},
                    {"name": "a31b", "label": "您与其他朋友进行社交娱乐活动的频繁程度", "year": "2023"},
                    {"name": "a311", "label": "空闲时间社交", "year": "2023"},
                ],
                "controls": [
                    {"name": "a15", "label": "身体健康状况", "year": "2023"},
                    {"name": "a18", "label": "户口登记状况", "year": "2023"},
                ],
            },
        }


if __name__ == "__main__":
    unittest.main()
