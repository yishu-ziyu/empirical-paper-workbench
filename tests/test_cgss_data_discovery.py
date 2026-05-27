import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_data_discovery import (
    build_cgss_data_discovery_report,
    render_review,
)


class CgssDataDiscoveryTests(unittest.TestCase):
    """BDD: a new CGSS topic must first bind to real local data assets."""

    def test_bdd_50_builds_dataset_binding_draft_without_formal_writeback(self) -> None:
        datasets = [
            {
                "year": "2023",
                "path": "/data/CGSS2023.dta",
                "file_type": "dta",
                "size_bytes": 123456,
                "row_count": 11326,
                "variable_count": 439,
                "readability_status": "readable",
                "evidence_level": "local_file",
                "supporting_documents": ["/data/CGSS2023编码表.xlsx"],
                "variables": [
                    {"name": "a36", "label": "总的来说，您觉得您的生活是否幸福"},
                    {"name": "a33", "label": "您是否认为社会大多数人可信任"},
                    {"name": "a2", "label": "受访者性别"},
                ],
            },
            {
                "year": "2021",
                "path": "/data/CGSS2021.dta",
                "file_type": "dta",
                "size_bytes": 45678,
                "row_count": 8148,
                "variable_count": 512,
                "readability_status": "readable",
                "evidence_level": "local_file",
                "supporting_documents": [],
                "variables": [{"name": "D36", "label": "幸福感"}],
            },
        ]

        report = build_cgss_data_discovery_report(
            topic="社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            data_root=Path("/data"),
            datasets=datasets,
        )

        self.assertEqual(report["schema_version"], "p6.cgss_data_discovery.v1")
        self.assertEqual(report["status"], "needs_human_dataset_binding_review")
        self.assertEqual(report["dataset_binding_draft"]["recommended_dataset"]["year"], "2023")
        self.assertEqual(report["dataset_binding_draft"]["recommended_dataset"]["row_count"], 11326)
        self.assertEqual(report["dataset_binding_draft"]["candidate_count"], 2)
        self.assertEqual(report["dataset_candidates"][0]["evidence_level"], "local_file")
        self.assertEqual(report["field_profile"]["outcome_candidates"], 2)
        self.assertEqual(report["field_profile"]["social_capital_candidates"], 1)
        self.assertFalse(report["boundary_flags"]["modified_formal_variable_roles"])
        self.assertFalse(report["boundary_flags"]["modified_design_spec"])
        self.assertFalse(report["boundary_flags"]["generated_formal_paper"])
        self.assertIn("draft_cgss_variable_roles", report["next_tasks"])

    def test_bdd_50_review_text_tells_human_what_to_check_next(self) -> None:
        report = build_cgss_data_discovery_report(
            topic="社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            data_root=Path("/data"),
            datasets=[
                {
                    "year": "2023",
                    "path": "/data/CGSS2023.dta",
                    "file_type": "dta",
                    "size_bytes": 123456,
                    "row_count": 11326,
                    "variable_count": 439,
                    "readability_status": "readable",
                    "evidence_level": "local_file",
                    "supporting_documents": ["/data/CGSS2023编码表.xlsx"],
                    "variables": [{"name": "a36", "label": "幸福感"}],
                }
            ],
        )

        review = render_review(report)

        self.assertIn("确认是否使用推荐 CGSS 数据", review)
        self.assertIn("CGSS2023.dta", review)
        self.assertIn("11326", review)
        self.assertIn("不自动改变量角色", review)

    def test_bdd_50_blocks_cleanly_when_no_cgss_data_is_found(self) -> None:
        report = build_cgss_data_discovery_report(
            topic="社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            data_root=Path("/missing"),
            datasets=[],
        )

        self.assertEqual(report["status"], "blocked_no_cgss_dataset")
        self.assertIsNone(report["dataset_binding_draft"]["recommended_dataset"])
        self.assertEqual(report["dataset_binding_draft"]["candidate_count"], 0)
        self.assertIn("locate_cgss_dataset", report["next_tasks"])

    def test_bdd_50_writes_machine_and_review_outputs(self) -> None:
        from Program.workbench.cgss_data_discovery import write_report

        report = build_cgss_data_discovery_report(
            topic="社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            data_root=Path("/data"),
            datasets=[
                {
                    "year": "2023",
                    "path": "/data/CGSS2023.dta",
                    "file_type": "dta",
                    "size_bytes": 123456,
                    "row_count": 11326,
                    "variable_count": 439,
                    "readability_status": "readable",
                    "evidence_level": "local_file",
                    "supporting_documents": [],
                    "variables": [{"name": "a36", "label": "幸福感"}],
                }
            ],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path, review_path = write_report(
                Path(tmpdir),
                report,
                Path("Results/json/cgss_data_discovery.json"),
                Path("Reviews/cgss_data_discovery.md"),
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIn("DatasetBinding 草案", review_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
