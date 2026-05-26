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


class MethodDiagnosticsCliTests(unittest.TestCase):
    """BDD: ExecutionAgent must turn MethodGate yellow gaps into real diagnostics artifacts."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="method-diagnostics-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_bartik_iv_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_method_diagnostics_writes_real_report_without_formal_writeback(self) -> None:
        """行为 12：真实方法诊断写出报告，并保护正式层不被静默改写。"""
        before = self._protected_snapshots()

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "method_diagnostics.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report_path = self.project_root / "Results" / "json" / "method_diagnostics_report.json"
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(report["schema_version"], "p4.method_diagnostics.v1")
        self.assertEqual(report["method_family"], "iv")
        self.assertEqual(report["method_subtype"], "bartik_shift_share_iv")
        self.assertEqual(report["status"], "completed_with_review_items")
        self.assertEqual(report["variables"]["outcome"], "ln_wage")
        self.assertEqual(report["variables"]["endogenous_treatment"], "ln_robot")
        self.assertEqual(report["variables"]["instrument"], "bartik_iv")
        self.assertGreaterEqual(report["dataset_profile"]["usable_rows"], 20)

        diagnostics = {item["id"]: item for item in report["diagnostics"]}
        self.assertEqual(diagnostics["baseline_iv_2sls_binding"]["status"], "green")
        self.assertEqual(diagnostics["first_stage_relevance"]["status"], "green")
        self.assertEqual(diagnostics["reduced_form"]["status"], "green")
        self.assertEqual(diagnostics["ols_comparison"]["status"], "green")
        self.assertEqual(diagnostics["sample_consistency"]["status"], "yellow")
        self.assertEqual(diagnostics["artifact_binding"]["status"], "green")
        self.assertEqual(diagnostics["shift_share_rotemberg_weights"]["status"], "needs_manual_review")
        self.assertEqual(diagnostics["leave_one_out_or_alternative_shock"]["status"], "needs_manual_review")
        self.assertIn("missing_shift_share_components", diagnostics["shift_share_rotemberg_weights"]["review_items"])

        schedule = report["agent_team_schedule"]
        self.assertEqual(schedule["call_when"], "after_method_gate_yellow_without_red_blockers")
        self.assertEqual(schedule["recall_when"], "after_method_diagnostics_report_written")
        self.assertEqual(schedule["next_call_after_recall"], "method_agent_and_reviewer_agent")
        self.assertIn("ExecutionAgent", [lane["agent"] for lane in schedule["parallel_lanes"]])
        self.assertEqual(report["formal_state_write"]["can_promote"], False)
        self.assertEqual(before, self._protected_snapshots())

    def test_bdd_2_method_gate_reads_method_diagnostics_artifact(self) -> None:
        subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "method_diagnostics.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

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
        report = json.loads((self.project_root / "Results" / "json" / "method_gate_report.json").read_text(encoding="utf-8"))
        diagnostics = {item["id"]: item for item in report["diagnostics"]}

        self.assertEqual(report["gate_status"], "yellow")
        self.assertEqual(report["method_diagnostics_ref"]["path"], "Results/json/method_diagnostics_report.json")
        self.assertEqual(diagnostics["reduced_form"]["status"], "recorded")
        self.assertEqual(diagnostics["robust_first_stage_f_or_kp"]["status"], "recorded")
        self.assertEqual(diagnostics["result_artifact_binding"]["status"], "recorded")
        self.assertNotIn("missing_reduced_form", report["yellow_items"])
        self.assertNotIn("missing_result_artifact_binding", report["yellow_items"])
        self.assertIn("missing_shift_share_rotemberg_weights", report["yellow_items"])

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
                    "expected_sample_size": 40,
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
        lines = ["pid,provcd,urban,ln_wage,female,age,edu_last,year,ln_robot,bartik_iv"]
        pid = 1
        for province in range(1, 7):
            for year in [2020, 2022]:
                for index in range(4):
                    female = (pid + province) % 2
                    urban = (pid + index + province) % 2
                    age = 26 + ((pid * 7) % 19)
                    edu = 8 + ((province + index + pid) % 8)
                    bartik = province * 0.4 + (year - 2020) * 0.15 + index * 0.03 + ((pid * 3) % 7) * 0.01
                    robot = 0.55 * bartik + ((pid * 7) % 11) * 0.025 + province * 0.01
                    wage = 8.0 + 0.25 * robot - 0.08 * female + 0.06 * urban + 0.004 * age + 0.03 * edu + ((pid * 5) % 13) * 0.01
                    lines.append(
                        f"{pid},{province},{urban},{wage:.4f},{female},{age},{edu},{year},{robot:.4f},{bartik:.4f}"
                    )
                    pid += 1
        (project_root / "Data" / "Final" / "cfps_robot_reallocation.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
