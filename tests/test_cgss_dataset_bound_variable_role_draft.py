import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_dataset_bound_variable_role_draft import (
    build_dataset_bound_variable_role_draft,
    write_dataset_bound_role_draft_outputs,
)


class CgssDatasetBoundVariableRoleDraftTests(unittest.TestCase):
    """BDD: DatasetBinding must constrain variable-role draft generation."""

    def test_bdd_54_filters_candidates_to_recommended_dataset_before_role_draft(self) -> None:
        draft = build_dataset_bound_variable_role_draft(
            data_discovery=self._data_discovery(),
            variable_candidates=self._variable_candidates(),
        )

        self.assertEqual(draft["schema_version"], "p6.cgss_dataset_bound_variable_role_draft.v1")
        self.assertEqual(draft["status"], "needs_human_dataset_bound_role_review")
        self.assertEqual(draft["dataset_binding"]["year"], "2023")
        self.assertEqual(draft["dataset_binding"]["path"], "/data/CGSS2023.dta")
        self.assertEqual(draft["proposed_roles"]["outcome"]["source_variable"], "a36")
        self.assertEqual(
            draft["proposed_roles"]["treatment"]["canonical_name"],
            "social_capital_index_draft",
        )
        self.assertIn("a33", draft["proposed_roles"]["treatment"]["source_items"])
        self.assertIn("a31a", draft["proposed_roles"]["treatment"]["source_items"])
        self.assertIn("a31b", draft["proposed_roles"]["treatment"]["source_items"])
        self.assertIn("a311", draft["proposed_roles"]["treatment"]["source_items"])
        self.assertNotIn("D36", draft["selected_source_variables"])
        self.assertNotIn("a36_2018", draft["selected_source_variables"])
        self.assertFalse(draft["boundary_flags"]["modified_formal_variable_roles"])
        self.assertFalse(draft["boundary_flags"]["modified_design_spec"])
        self.assertFalse(draft["boundary_flags"]["modified_run_plan"])
        self.assertFalse(draft["boundary_flags"]["wrote_state_product"])
        self.assertFalse(draft["promotion"]["allowed"])

    def test_bdd_54_explains_why_each_role_is_selected(self) -> None:
        draft = build_dataset_bound_variable_role_draft(
            data_discovery=self._data_discovery(),
            variable_candidates=self._variable_candidates(),
        )

        outcome_reason = draft["proposed_roles"]["outcome"]["why_selected"]
        treatment_reason = draft["proposed_roles"]["treatment"]["why_selected"]
        controls_reason = draft["proposed_roles"]["controls"]["why_selected"]
        self.assertIn("直接测量", outcome_reason)
        self.assertIn("主观幸福感", outcome_reason)
        self.assertIn("信任", treatment_reason)
        self.assertIn("社交", treatment_reason)
        self.assertIn("多维", treatment_reason)
        self.assertIn("混杂因素", controls_reason)
        self.assertIn("literature_support_required", draft["review_gates"])
        self.assertIn("social_capital_index_construction", draft["review_gates"])

    def test_bdd_54_blocks_without_reviewable_dataset_binding(self) -> None:
        data_discovery = self._data_discovery()
        data_discovery["status"] = "blocked_no_cgss_assets"

        draft = build_dataset_bound_variable_role_draft(
            data_discovery=data_discovery,
            variable_candidates=self._variable_candidates(),
        )

        self.assertEqual(draft["status"], "blocked_missing_dataset_binding")
        self.assertIn("dataset_binding_not_reviewable", draft["blocking_reasons"])
        self.assertEqual(draft["proposed_roles"], {})
        self.assertFalse(draft["boundary_flags"]["modified_formal_variable_roles"])

    def test_bdd_54_writes_reviewable_markdown_without_formal_writeback(self) -> None:
        draft = build_dataset_bound_variable_role_draft(
            data_discovery=self._data_discovery(),
            variable_candidates=self._variable_candidates(),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path = write_dataset_bound_role_draft_outputs(
                Path(tmpdir),
                draft,
                Path("Results/json/dataset_bound_role_draft.json"),
                Path("Reviews/dataset_bound_role_draft.md"),
            )

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(
                json.loads(result_path.read_text(encoding="utf-8"))["status"],
                "needs_human_dataset_bound_role_review",
            )
            review_text = review_path.read_text(encoding="utf-8")
            self.assertIn("CGSS2023", review_text)
            self.assertIn("a36", review_text)
            self.assertIn("a33", review_text)
            self.assertIn("不写正式变量角色", review_text)

    def _data_discovery(self) -> dict:
        return {
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "needs_human_dataset_binding_review",
            "dataset_binding_draft": {
                "recommended_dataset": {
                    "year": "2023",
                    "path": "/data/CGSS2023.dta",
                    "row_count": 11326,
                    "variable_count": 439,
                }
            },
            "field_profile": {
                "examples": {
                    "control": [
                        {"name": "s41", "label": "省份"},
                    ]
                }
            },
        }

    def _variable_candidates(self) -> dict:
        return {
            "status": "needs_human_review",
            "role_candidates": {
                "outcome": [
                    {
                        "name": "a36",
                        "label": "总的来说，您觉得您的生活是否幸福",
                        "year": "2023",
                        "dataset_path": "/data/CGSS2023.dta",
                    },
                    {
                        "name": "D36",
                        "label": "生活满意度",
                        "year": "2021",
                        "dataset_path": "/data/CGSS2021.dta",
                    },
                    {
                        "name": "a36_2018",
                        "label": "生活幸福感",
                        "year": "2018",
                        "dataset_path": "/data/CGSS2018.dta",
                    },
                ],
                "social_capital": [
                    {
                        "name": "a33",
                        "label": "绝大多数人都是可以信任的",
                        "year": "2023",
                        "dataset_path": "/data/CGSS2023.dta",
                    },
                    {
                        "name": "a31a",
                        "label": "您与邻居进行社交娱乐活动的频繁程度",
                        "year": "2023",
                        "dataset_path": "/data/CGSS2023.dta",
                    },
                    {
                        "name": "a31b",
                        "label": "您与其他朋友进行社交娱乐活动的频繁程度",
                        "year": "2023",
                        "dataset_path": "/data/CGSS2023.dta",
                    },
                    {
                        "name": "a311",
                        "label": "空闲时间社交",
                        "year": "2023",
                        "dataset_path": "/data/CGSS2023.dta",
                    },
                    {
                        "name": "D40",
                        "label": "其他年份社会交往",
                        "year": "2021",
                        "dataset_path": "/data/CGSS2021.dta",
                    },
                ],
                "controls": [
                    {"name": "a2", "label": "性别", "year": "2023", "dataset_path": "/data/CGSS2023.dta"},
                    {"name": "a7a", "label": "教育程度", "year": "2023", "dataset_path": "/data/CGSS2023.dta"},
                    {"name": "a15", "label": "身体健康状况", "year": "2023", "dataset_path": "/data/CGSS2023.dta"},
                    {"name": "a18", "label": "户口登记状况", "year": "2023", "dataset_path": "/data/CGSS2023.dta"},
                    {"name": "D2", "label": "其他年份性别", "year": "2021", "dataset_path": "/data/CGSS2021.dta"},
                ],
            },
        }


if __name__ == "__main__":
    unittest.main()
