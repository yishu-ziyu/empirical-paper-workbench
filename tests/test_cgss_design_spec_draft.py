import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_design_spec_draft import (
    build_cgss_design_spec_draft,
    write_cgss_design_spec_draft_outputs,
)


class CgssDesignSpecDraftTests(unittest.TestCase):
    """BDD: Dataset-bound CGSS variable roles must become a reviewable design draft before execution."""

    def test_bdd_55_builds_reviewable_design_spec_draft_without_formal_writeback(self) -> None:
        draft = build_cgss_design_spec_draft(self._role_draft())

        self.assertEqual(draft["schema_version"], "p6.cgss_design_spec_draft.v1")
        self.assertEqual(draft["status"], "needs_human_design_spec_review")
        self.assertFalse(draft["boundary_flags"]["modified_formal_design_spec"])
        self.assertFalse(draft["boundary_flags"]["modified_run_plan"])
        self.assertFalse(draft["boundary_flags"]["wrote_state_product"])
        self.assertFalse(draft["promotion"]["allowed"])
        self.assertEqual(draft["promotion"]["would_write_if_approved"], "state/product/design_spec.json")

        design = draft["design_spec_draft"]
        self.assertEqual(design["dataset_path"], "/data/CGSS2023.dta")
        self.assertEqual(design["variables"]["outcome"], ["happiness"])
        self.assertEqual(design["variables"]["treatment"], ["social_capital_index_draft"])
        self.assertIn("a36", design["source_variable_bindings"]["outcome"])
        self.assertIn("a33", design["source_variable_bindings"]["treatment_items"])

    def test_bdd_55_recommends_cross_section_models_and_claim_boundary(self) -> None:
        draft = build_cgss_design_spec_draft(self._role_draft())

        models = {model["id"]: model for model in draft["design_spec_draft"]["model_candidates"]}
        self.assertIn("ols_baseline", models)
        self.assertIn("ordered_logit", models)
        self.assertEqual(models["ols_baseline"]["estimator"], "ols")
        self.assertEqual(models["ordered_logit"]["estimator"], "ordered_logit")
        self.assertIn("social_capital_index_draft", models["ols_baseline"]["formula"])
        self.assertEqual(
            draft["design_spec_draft"]["claim_boundary"]["level"],
            "conditional_association_not_strong_causality",
        )
        self.assertIn("横截面", draft["design_spec_draft"]["identification_strategy"]["summary"])

    def test_bdd_55_explains_blocked_method_families_before_run_plan(self) -> None:
        draft = build_cgss_design_spec_draft(self._role_draft())

        blocked = {item["method"]: item["reason"] for item in draft["method_family_gate"]["blocked_method_families"]}
        self.assertIn("DID", blocked)
        self.assertIn("IV", blocked)
        self.assertIn("RDD", blocked)
        self.assertIn("PSM", blocked)
        self.assertIn("DML", blocked)
        self.assertIn("处理时间", blocked["DID"])
        self.assertIn("工具变量", blocked["IV"])
        self.assertIn("断点", blocked["RDD"])
        self.assertIn("RunPlan", draft["next_tasks"][1])

    def test_bdd_55_blocks_when_dataset_bound_roles_are_not_reviewable(self) -> None:
        role_draft = self._role_draft()
        role_draft["status"] = "blocked_missing_dataset_bound_candidates"

        draft = build_cgss_design_spec_draft(role_draft)

        self.assertEqual(draft["status"], "blocked_missing_dataset_bound_variable_roles")
        self.assertIn("dataset_bound_variable_roles_not_reviewable", draft["blocking_reasons"])
        self.assertEqual(draft["design_spec_draft"], {})
        self.assertFalse(draft["promotion"]["allowed"])

    def test_bdd_55_writes_reviewable_markdown_without_state_product(self) -> None:
        draft = build_cgss_design_spec_draft(self._role_draft())

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result_path, review_path = write_cgss_design_spec_draft_outputs(
                project_root,
                draft,
                Path("Results/json/cgss_design_spec_draft.json"),
                Path("Reviews/cgss_design_spec_draft.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            saved = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "needs_human_design_spec_review")
            review = review_path.read_text(encoding="utf-8")
            self.assertIn("CGSS 研究设计草案", review)
            self.assertIn("OLS", review)
            self.assertIn("Ordered Logit", review)
            self.assertIn("不写正式 DesignSpec", review)
            self.assertFalse((project_root / "state/product/design_spec.json").exists())

    def _role_draft(self) -> dict:
        return {
            "schema_version": "p6.cgss_dataset_bound_variable_role_draft.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            "status": "needs_human_dataset_bound_role_review",
            "dataset_binding": {
                "year": "2023",
                "path": "/data/CGSS2023.dta",
                "row_count": 11326,
                "variable_count": 439,
                "evidence_level": "local_file",
            },
            "proposed_roles": {
                "outcome": {
                    "canonical_name": "happiness",
                    "source_variable": "a36",
                    "source_label": "总的来说，您觉得您的生活是否幸福",
                    "measurement_level": "ordered_happiness_scale_needs_codebook_review",
                },
                "treatment": {
                    "canonical_name": "social_capital_index_draft",
                    "source_items": ["a33", "a31a", "a31b", "a311"],
                    "dimensions": {
                        "general_trust": "a33",
                        "neighborhood_ties": "a31a",
                        "friend_ties": "a31b",
                        "leisure_social_participation": "a311",
                    },
                },
                "controls": {
                    "source_items": ["a2", "a3a", "a7a", "a7b", "a15", "a18", "a21", "a8a", "a8b", "s41"],
                    "role_mapping": {
                        "gender": ["a2"],
                        "age": ["a3a"],
                        "education": ["a7a", "a7b"],
                        "health": ["a15"],
                        "hukou": ["a18", "a21"],
                        "income": ["a8a", "a8b"],
                        "province_fixed_effect": ["s41"],
                    },
                },
            },
            "review_gates": [
                "outcome_coding_and_scale_review",
                "social_capital_index_construction",
                "control_set_completeness",
                "missingness_and_sample_loss_review",
                "literature_support_required",
            ],
        }


if __name__ == "__main__":
    unittest.main()
