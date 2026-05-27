import unittest

from Program.workbench.cgss_topic_variable_discovery import (
    build_candidate_report,
    classify_variable,
)


class CgssTopicVariableDiscoveryTests(unittest.TestCase):
    """BDD: CGSS topic intake must turn metadata into reviewable variable candidates."""

    def test_bdd_49_classifies_happiness_social_capital_and_controls(self) -> None:
        variables = [
            {"name": "a36", "label": "总的来说，您觉得您的生活是否幸福"},
            {"name": "a33", "label": "您是否认为社会大多数人可信任"},
            {"name": "c17a", "label": "您对亲戚的信任程度"},
            {"name": "a2", "label": "受访者性别"},
            {"name": "a7a", "label": "受访者最高教育程度"},
            {"name": "noise", "label": "问卷访问状态"},
        ]

        self.assertEqual(classify_variable(variables[0])["primary_role"], "outcome")
        self.assertEqual(classify_variable(variables[1])["primary_role"], "social_capital")
        self.assertEqual(classify_variable(variables[2])["primary_role"], "social_capital")
        self.assertEqual(classify_variable(variables[3])["primary_role"], "control")
        self.assertEqual(classify_variable(variables[4])["primary_role"], "control")
        self.assertIsNone(classify_variable(variables[5])["primary_role"])

    def test_bdd_49_builds_reviewable_cgss_variable_report_without_formal_writeback(self) -> None:
        datasets = [
            {
                "year": "2023",
                "path": "/data/CGSS2023.dta",
                "variable_count": 6,
                "variables": [
                    {"name": "a36", "label": "总的来说，您觉得您的生活是否幸福"},
                    {"name": "a33", "label": "您是否认为社会大多数人可信任"},
                    {"name": "c17a", "label": "您对亲戚的信任程度"},
                    {"name": "a2", "label": "受访者性别"},
                    {"name": "a7a", "label": "受访者最高教育程度"},
                    {"name": "noise", "label": "问卷访问状态"},
                ],
            }
        ]

        report = build_candidate_report(
            topic="社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            datasets=datasets,
        )

        self.assertEqual(report["schema_version"], "p6.cgss_topic_variable_discovery.v1")
        self.assertEqual(report["status"], "needs_human_review")
        self.assertFalse(report["boundary_flags"]["modified_formal_variable_roles"])
        self.assertEqual(report["recommended_dataset_order"][0]["year"], "2023")
        self.assertEqual(report["role_candidates"]["outcome"][0]["name"], "a36")
        self.assertIn("a33", {item["name"] for item in report["role_candidates"]["social_capital"]})
        self.assertIn("c17a", {item["name"] for item in report["role_candidates"]["social_capital"]})
        self.assertIn("a2", {item["name"] for item in report["role_candidates"]["controls"]})
        self.assertIn("a7a", {item["name"] for item in report["role_candidates"]["controls"]})
        self.assertIn("run_cgss_minimal_model", report["next_tasks"])


if __name__ == "__main__":
    unittest.main()
