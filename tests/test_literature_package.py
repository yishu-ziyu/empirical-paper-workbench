from __future__ import annotations

import csv
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class LiteraturePackageCliTests(unittest.TestCase):
    """BDD: literature package must create a reviewable source loop."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="literature-package-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_bdd_10_builds_literature_package_without_formal_writeback(self) -> None:
        """行为 10：生成候选文献、已校验书目和贡献矩阵，并让 paper_quality 读取通过。"""
        protected_paths = [
            self.project_root / "state" / "product" / "research_question.json",
            self.project_root / "state" / "product" / "design_spec.json",
            self.project_root / "state" / "product" / "run_plan.json",
        ]
        before = {path.name: path.read_text(encoding="utf-8") for path in protected_paths}

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "literature_package.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("literature_package_report=Results/json/literature_package_report.json", result.stdout)

        processed = self.project_root / "Data" / "literature" / "processed"
        candidate_path = processed / "candidate_literature.csv"
        verified_path = processed / "verified_bibliography.csv"
        matrix_path = processed / "contribution_matrix.md"
        report_path = self.project_root / "Results" / "json" / "literature_package_report.json"
        for path in [candidate_path, verified_path, matrix_path, report_path]:
            self.assertTrue(path.exists(), f"missing {path}")

        candidate_rows = self._read_csv(candidate_path)
        verified_rows = self._read_csv(verified_path)
        self.assertGreaterEqual(len(candidate_rows), 8)
        self.assertGreaterEqual(
            len([row for row in verified_rows if row["verification_status"] != "needs_manual_review"]),
            5,
        )
        self.assertGreaterEqual(
            len([row for row in verified_rows if row["contribution_role"] in {"closest_paper", "method_reference"}]),
            3,
        )

        required_columns = {
            "source_id",
            "title",
            "authors",
            "year",
            "venue",
            "doi",
            "publisher_url",
            "verification_status",
            "topic_relevance",
            "method_relevance",
            "contribution_role",
        }
        self.assertTrue(required_columns.issubset(candidate_rows[0].keys()))

        matrix = matrix_path.read_text(encoding="utf-8")
        self.assertIn("| source_id | citation_key | contribution_role | used_in_section |", matrix)
        self.assertIn("robot_wage_closest_us", matrix)
        self.assertIn("shift_share_method_core", matrix)

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p4.literature_package.v1")
        self.assertEqual(report["status"], "needs_human_review")
        self.assertEqual(report["write_policy"]["mode"], "processed_evidence_only")
        self.assertIn("cnki_manual_queue", report)
        self.assertGreaterEqual(len(report["cnki_manual_queue"]), 3)
        self.assertEqual(report["agent_team_schedule"]["call_when"], "after_candidate_literature_written")
        self.assertEqual(report["agent_team_schedule"]["recall_when"], "before_manuscript_citation_writeback")
        self.assertEqual(
            [lane["agent"] for lane in report["agent_team_schedule"]["parallel_lanes"]],
            ["LiteratureAgent", "MethodAgent", "DataAgent"],
        )

        quality = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_quality.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(quality.returncode, 0, quality.stderr)
        quality_report = json.loads(
            (self.project_root / "Results" / "json" / "paper_quality_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(quality_report["citation_checks"]["verified_bibliography"]["status"], "found")
        self.assertEqual(quality_report["citation_checks"]["contribution_matrix"]["status"], "found")
        self.assertNotIn("needs_literature_review", quality_report["verdict"])

        after = {path.name: path.read_text(encoding="utf-8") for path in protected_paths}
        self.assertEqual(before, after)

    def _seed_project(self, root: Path) -> None:
        state_dir = root / "state" / "product"
        manuscript_dir = root / "Manuscripts" / "generated"
        state_dir.mkdir(parents=True)
        manuscript_dir.mkdir(parents=True)
        self._write_json(
            state_dir / "research_question.json",
            {
                "id": "research_question",
                "version": 7,
                "status": "confirmed",
                "question": "工业机器人应用对劳动力市场匹配效率的影响",
                "evidence_level": "local_file",
            },
        )
        self._write_json(
            state_dir / "design_spec.json",
            {
                "id": "design_spec",
                "version": 2,
                "status": "approved",
                "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                "variables": {
                    "outcome": ["ln_wage"],
                    "treatment": ["ln_robot"],
                    "controls": ["female", "age", "edu_last", "urban"],
                    "instruments": ["bartik_iv"],
                    "fixed_effects": ["year"],
                    "cluster_by": ["provcd"],
                },
                "identification_strategy": {
                    "name": "bartik_iv_2sls",
                    "summary": "使用 Bartik IV 处理机器人暴露内生性。",
                },
            },
        )
        self._write_json(
            state_dir / "run_plan.json",
            {
                "id": "run_plan",
                "version": 2,
                "status": "approved",
                "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                "tasks": [
                    {
                        "id": "robot_wage_iv_baseline",
                        "estimator": "iv",
                        "formula": "ln_wage ~ (ln_robot ~ bartik_iv) + female + age + edu_last + urban",
                    }
                ],
            },
        )
        (manuscript_dir / "paper_draft.md").write_text(
            "# Draft\n\n## Abstract\n\nShort draft.\n\n## References\n\nPending.\n",
            encoding="utf-8",
        )

    def _write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_csv(self, path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))


if __name__ == "__main__":
    unittest.main()
