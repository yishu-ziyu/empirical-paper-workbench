import tempfile
import unittest
from pathlib import Path

from Program.workbench.dataset_motherlode_index import build_dataset_motherlode_index, write_report


class DatasetMotherlodeIndexTests(unittest.TestCase):
    """BDD: DataAgent must turn a local dataset motherlode into reviewable data leads."""

    def test_bdd_p7a_indexes_local_motherlode_as_read_only_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp) / "motherlode"
            family = data_root / "IFR industrial robots 1993-2023"
            family.mkdir(parents=True)
            (family / "ifr_robot_2020.csv").write_text("year,value\n2020,1\n", encoding="utf-8")

            report = build_dataset_motherlode_index(data_root, topic="工业机器人对劳动力市场匹配效率的影响")

            self.assertEqual(report["schema_version"], "p7.dataset_motherlode_index.v1")
            self.assertEqual(report["status"], "needs_human_dataset_index_review")
            self.assertEqual(report["data_source"]["status"], "read_only")
            self.assertEqual(report["data_source"]["scope"], "local_only")
            self.assertEqual(report["data_source"]["source_type"], "user_provided_public_dataset_pool")
            self.assertFalse(report["boundary_flags"]["modified_raw_dataset"])
            self.assertFalse(report["boundary_flags"]["modified_formal_manuscript"])
            self.assertFalse(report["boundary_flags"]["modified_formal_bibliography"])
            self.assertFalse(report["boundary_flags"]["modified_run_plan"])
            self.assertFalse(report["boundary_flags"]["generated_formal_paper"])

    def test_bdd_p7a_groups_nested_files_into_dataset_families(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp) / "motherlode"
            family = data_root / "CLDS 2018 labor survey"
            nested = family / "stata"
            nested.mkdir(parents=True)
            (nested / "clds2018.dta").write_bytes(b"demo")
            (family / "dictionary_2018.xlsx").write_bytes(b"demo")

            report = build_dataset_motherlode_index(data_root, topic="劳动力市场匹配效率")
            clds = report["dataset_families"][0]

            self.assertEqual(clds["family_name"], "CLDS 2018 labor survey")
            self.assertEqual(clds["file_count"], 2)
            self.assertEqual(clds["total_bytes"], 8)
            self.assertEqual(clds["extensions"], [".dta", ".xlsx"])
            self.assertEqual(clds["year_hints"], ["2018"])
            self.assertEqual(clds["field_profile_status"], "not_profiled_metadata_index_only")
            self.assertEqual(len(clds["sample_paths"]), 2)

    def test_bdd_p7a_skips_hidden_system_and_unsupported_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp) / "motherlode"
            family = data_root / "CFPS 2022"
            family.mkdir(parents=True)
            (family / ".DS_Store").write_bytes(b"noise")
            (family / "README").write_text("no extension", encoding="utf-8")
            (family / "cfps2022.dta").write_bytes(b"demo")

            report = build_dataset_motherlode_index(data_root, topic="居民幸福感")
            cfps = report["dataset_families"][0]

            self.assertEqual(cfps["file_count"], 1)
            self.assertEqual(cfps["sample_paths"], ["CFPS 2022/cfps2022.dta"])
            self.assertEqual(cfps["extensions"], [".dta"])

    def test_bdd_p7a_ranks_robot_labor_topic_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp) / "motherlode"
            for family_name in [
                "IFR industrial robots 1993-2023",
                "CLDS 中国劳动力动态调查 2018",
                "CGSS 中国综合社会调查 2021",
                "provincial labor market segmentation 2000-2024",
                "unrelated_weather_data",
            ]:
                family = data_root / family_name
                family.mkdir(parents=True)
                (family / "data_2020.csv").write_text("x\n1\n", encoding="utf-8")

            report = build_dataset_motherlode_index(data_root, topic="工业机器人对劳动力市场匹配效率的影响")
            top_names = [item["family_name"] for item in report["candidate_data_bindings"][:4]]

            self.assertIn("IFR industrial robots 1993-2023", top_names)
            self.assertIn("CLDS 中国劳动力动态调查 2018", top_names)
            self.assertIn("provincial labor market segmentation 2000-2024", top_names)
            self.assertNotEqual(report["candidate_data_bindings"][0]["family_name"], "unrelated_weather_data")
            self.assertTrue(report["candidate_data_bindings"][0]["match_reasons"])

    def test_bdd_p7a_uses_nested_path_hints_beyond_sample_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp) / "motherlode"
            family = data_root / "外部源数据"
            family.mkdir(parents=True)
            for index in range(10):
                (family / f"aaa_archive_{index}_2020.csv").write_text("x\n1\n", encoding="utf-8")
            robot_dir = family / "zzz_IFR industrial robots 1993-2023"
            robot_dir.mkdir()
            (robot_dir / "robot_installation_density_2023.csv").write_text("x\n1\n", encoding="utf-8")

            report = build_dataset_motherlode_index(data_root, topic="工业机器人对劳动力市场匹配效率的影响")
            external = report["candidate_data_bindings"][0]

            self.assertEqual(external["family_name"], "外部源数据")
            self.assertIn("robot", external["match_reasons"])
            self.assertIn("ifr", external["match_reasons"])

    def test_bdd_p7a_writes_json_and_markdown_review_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            data_root = Path(tmp) / "motherlode"
            (data_root / "CFPS 2022").mkdir(parents=True)
            (data_root / "CFPS 2022" / "cfps2022.csv").write_text("x\n1\n", encoding="utf-8")

            report = build_dataset_motherlode_index(data_root, topic="居民幸福感")
            report_path, review_path = write_report(
                project_root,
                report,
                Path("Results/json/dataset_motherlode_index.json"),
                Path("Reviews/dataset_motherlode_index.md"),
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertIn("needs_human_dataset_index_review", report_path.read_text(encoding="utf-8"))
            review_text = review_path.read_text(encoding="utf-8")
            self.assertIn("needs_human_dataset_index_review", review_text)
            self.assertIn("正式层写回：否", review_text)


if __name__ == "__main__":
    unittest.main()
