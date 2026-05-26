import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTECTED_STATE_PATHS = [
    "state/product/research_question.json",
    "state/product/variable_roles.json",
    "state/product/design_spec.json",
    "state/product/run_plan.json",
]


class MethodGateCliTests(unittest.TestCase):
    """BDD: MethodAgent must expose IV/Bartik method gates as reviewable reports."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="method-gate-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_bartik_iv_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_bartik_iv_method_gate_writes_review_report_without_formal_writeback(self) -> None:
        """行为 11：Bartik IV 方法门写出 yellow 报告，并保护正式层不被静默改写。"""
        before = self._protected_snapshots()

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "method_gate.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report_path = self.project_root / "Results" / "json" / "method_gate_report.json"
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(report["schema_version"], "p4.method_gate.v1")
        self.assertEqual(report["method_family"], "iv")
        self.assertEqual(report["method_subtype"], "bartik_shift_share_iv")
        self.assertEqual(report["gate_status"], "yellow")
        self.assertEqual(report["status"], "needs_human_review")
        self.assertEqual(report["variables"]["outcome"], "ln_wage")
        self.assertEqual(report["variables"]["endogenous_treatment"], "ln_robot")
        self.assertEqual(report["variables"]["instrument"], "bartik_iv")
        self.assertIn("reduced_form", report["required_evidence"])
        self.assertIn("weak_iv_robust_inference_ar_or_clr", report["required_evidence"])
        self.assertIn("shift_share_identification_diagnostics", report["required_evidence"])
        self.assertIn("missing_reduced_form", report["yellow_items"])
        self.assertIn("missing_weak_iv_robust_inference", report["yellow_items"])
        self.assertIn("missing_shift_share_identification_diagnostics", report["yellow_items"])
        self.assertEqual(report["blocking_items"], [])

        diagnostics = {item["id"]: item for item in report["diagnostics"]}
        self.assertEqual(diagnostics["first_stage_f"]["status"], "passed")
        self.assertEqual(diagnostics["first_stage_f"]["observed"], 14.03)
        self.assertEqual(diagnostics["partial_r_squared"]["observed"], 0.4834)

        schedule = report["agent_team_schedule"]
        self.assertEqual(schedule["call_when"], "after_design_spec_and_run_plan_approved")
        self.assertEqual(schedule["recall_when"], "after_method_gate_report_written")
        self.assertEqual(schedule["next_call_after_integration"], "after_method_diagnostics_execution")
        self.assertIn("MethodAgent", [lane["agent"] for lane in schedule["parallel_lanes"]])
        self.assertEqual(before, self._protected_snapshots())

    def test_bdd_2_paper_quality_detects_generated_method_gate(self) -> None:
        subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "method_gate.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        quality = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_quality.py"),
                "--project-root",
                str(self.project_root),
                "--profile",
                "aer_like",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(quality.returncode, 0, quality.stderr)
        report = json.loads((self.project_root / "Results" / "json" / "paper_quality_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["method_gate_checks"]["status"], "found")
        self.assertEqual(report["method_gate_checks"]["method_family"], "iv")
        self.assertEqual(report["method_gate_checks"]["gate_status"], "yellow")
        self.assertNotIn("method_gate_required", report["verdict"])

    def _protected_snapshots(self) -> dict[str, str]:
        snapshots: dict[str, str] = {}
        for relative_path in PROTECTED_STATE_PATHS:
            path = self.project_root / relative_path
            snapshots[relative_path] = path.read_text(encoding="utf-8")
        return snapshots

    @staticmethod
    def _seed_bartik_iv_project(project_root: Path) -> None:
        (project_root / "state" / "product").mkdir(parents=True)
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "state" / "product" / "research_question.json").write_text(
            json.dumps(
                {
                    "version": 7,
                    "status": "confirmed",
                    "question": "工业机器人应用对劳动力市场匹配效率的影响",
                    "evidence_level": "human_confirmed",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (project_root / "state" / "product" / "variable_roles.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "status": "approved",
                    "dataset_path": "Data/Final/legacy_sample.csv",
                    "roles": {
                        "outcome": ["wage"],
                        "treatment": ["trained"],
                        "controls": ["edu", "experience"],
                        "instruments": [],
                        "fixed_effects": [],
                        "cluster_by": [],
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (project_root / "state" / "product" / "design_spec.json").write_text(
            json.dumps(
                {
                    "version": 2,
                    "status": "approved",
                    "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                    "research_question": "工业机器人应用对劳动力市场匹配效率的影响",
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
                        "summary": "使用省份产业结构和行业机器人冲击构造 Bartik 工具变量。",
                        "assumptions": [
                            "Bartik 工具变量与本地机器人暴露相关。",
                            "历史产业结构和外部行业机器人冲击不直接影响个体工资，除非通过机器人暴露。",
                        ],
                        "threats": [
                            "产业结构可能直接影响工资趋势，需要排除限制审阅。",
                            "需要 reduced form 和弱工具稳健推断。",
                        ],
                    },
                    "model": {
                        "estimator": "iv",
                        "formula": "ln_wage ~ (ln_robot ~ bartik_iv) + female + age + edu_last + urban",
                        "instrument_formula": "ln_robot ~ bartik_iv + female + age + edu_last + urban",
                        "fixed_effects": ["year"],
                        "cluster_by": ["provcd"],
                        "sample_filter": "all",
                    },
                    "diagnostics": {
                        "first_stage": {
                            "f_statistic": 14.03,
                            "partial_r_squared": 0.4834,
                        },
                        "dwh": {
                            "f_statistic": 14.27,
                            "p_value": 0.0007,
                        },
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (project_root / "state" / "product" / "run_plan.json").write_text(
            json.dumps(
                {
                    "version": 3,
                    "status": "approved",
                    "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                    "tasks": [
                        {
                            "id": "robot_wage_iv_baseline",
                            "method_id": "iv",
                            "estimator": "iv",
                            "formula": "ln_wage ~ (ln_robot ~ bartik_iv) + female + age + edu_last + urban",
                            "instrument_formula": "ln_robot ~ bartik_iv + female + age + edu_last + urban",
                            "fixed_effects": ["year"],
                            "cluster_by": ["provcd"],
                            "diagnostics": {
                                "first_stage_f": 14.03,
                                "partial_r_squared": 0.4834,
                            },
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "cfps_robot_reallocation.csv").write_text(
            "pid,provcd,urban,ln_wage,manu_dummy,ISEI_score,part_time,female,age,edu_last,year,ln_robot,bartik_iv\n"
            "1,11,1,9.1,1,52,0,0,35,12,2014,0.2,0.3\n"
            "2,11,0,8.7,0,42,0,1,41,9,2016,0.5,0.7\n",
            encoding="utf-8",
        )
        (project_root / "Manuscripts" / "generated" / "paper_draft.md").write_text(
            "# Draft\n\n## Abstract\n\nDraft.\n\n## Introduction\n\nDraft.\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
