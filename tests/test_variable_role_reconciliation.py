from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class VariableRoleReconciliationCliTests(unittest.TestCase):
    """BDD: variable role reconciliation writes reviewable proposals only."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="variable-role-reconcile-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_bdd_9_reconciles_legacy_variable_roles_as_proposal_without_formal_writeback(self) -> None:
        """行为 9：旧变量角色与真实设计冲突时，只能生成 needs_human_review proposal。"""
        protected_paths = [
            self.project_root / "state" / "product" / "variable_roles.json",
            self.project_root / "state" / "product" / "design_spec.json",
            self.project_root / "state" / "product" / "run_plan.json",
        ]
        before = {path.name: path.read_text(encoding="utf-8") for path in protected_paths}

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "variable_role_reconcile.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("variable_role_reconciliation=state/proposals/variable_role_reconciliation.json", result.stdout)

        proposal_path = self.project_root / "state" / "proposals" / "variable_role_reconciliation.json"
        report_path = self.project_root / "Results" / "json" / "variable_role_reconciliation_report.json"
        self.assertTrue(proposal_path.exists())
        self.assertTrue(report_path.exists())

        proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
        self.assertEqual(proposal["schema_version"], "p4.variable_role_reconciliation.v1")
        self.assertEqual(proposal["status"], "needs_human_review")
        self.assertFalse(proposal["formal_state_write"]["can_promote"])
        self.assertTrue(proposal["formal_state_write"]["requires_human_review"])
        self.assertEqual(proposal["write_policy"]["mode"], "proposal_only")
        self.assertIn("state/product/variable_roles.json", proposal["formal_state_write"]["protected_paths"])

        conflict_ids = {conflict["id"] for conflict in proposal["detected_conflicts"]}
        self.assertIn("formal_variable_roles_use_legacy_dataset", conflict_ids)
        self.assertIn("formal_variable_roles_disagree_with_design_spec", conflict_ids)

        roles = proposal["recommended_variable_roles"]["roles"]
        self.assertEqual(roles["outcome"], ["ln_wage"])
        self.assertEqual(roles["treatment"], ["ln_robot"])
        self.assertEqual(roles["controls"], ["female", "age", "edu_last", "urban"])
        self.assertEqual(roles["instruments"], ["bartik_iv"])
        self.assertEqual(roles["fixed_effects"], ["year"])
        self.assertEqual(roles["cluster_by"], ["provcd"])

        profile = proposal["dataset_profile"]
        self.assertEqual(profile["path"], "Data/Final/cfps_robot_reallocation.csv")
        self.assertEqual(profile["row_count"], 2)
        self.assertIn("ln_wage", profile["columns"])
        self.assertIn("bartik_iv", profile["columns"])
        self.assertEqual(proposal["missing_dataset_fields"], [])

        risk_ids = {risk["id"] for risk in proposal["risk_flags"]}
        self.assertIn("instrument_requires_exclusion_restriction_review", risk_ids)
        self.assertIn("research_question_scope_needs_alignment", risk_ids)

        role_reviews = {review["role"]: review for review in proposal["role_evidence_matrix"]}
        self.assertEqual(role_reviews["outcome"]["status"], "exploratory_draft_needs_human_review")
        self.assertIn("codebook_definition", role_reviews["outcome"]["evidence_requirements"])
        self.assertIn("construction_formula_or_raw_field", role_reviews["outcome"]["evidence_requirements"])
        self.assertEqual(role_reviews["instruments"]["status"], "exploratory_draft_needs_human_review")
        self.assertIn("instrument_exclusion_untestable", role_reviews["instruments"]["risk_flags"])
        self.assertIn("instrument_weak_first_stage_risk", role_reviews["instruments"]["risk_flags"])

        agent_team = proposal["agent_team_schedule"]
        self.assertEqual(agent_team["call_when"], "after_proposal_written")
        self.assertEqual(agent_team["recall_when"], "before_formal_writeback")
        self.assertEqual(
            [lane["agent"] for lane in agent_team["parallel_lanes"]],
            ["DataAgent", "MethodAgent", "LiteratureAgent"],
        )

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["proposal_path"], "state/proposals/variable_role_reconciliation.json")
        self.assertEqual(report["status"], "needs_human_review")
        self.assertIn("review_variable_role_reconciliation", report["recommended_next_tasks"])

        after = {path.name: path.read_text(encoding="utf-8") for path in protected_paths}
        self.assertEqual(before, after)

    def _seed_project(self, root: Path) -> None:
        state_dir = root / "state" / "product"
        data_dir = root / "Data" / "Final"
        state_dir.mkdir(parents=True)
        data_dir.mkdir(parents=True)
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
            state_dir / "variable_roles.json",
            {
                "id": "variable_role_set",
                "version": 2,
                "status": "approved",
                "evidence_level": "local_file",
                "dataset_path": "Data/Final/analysis_sample.csv",
                "roles": {
                    "outcome": ["wage"],
                    "treatment": ["trained"],
                    "controls": ["edu", "experience"],
                    "instruments": [],
                    "fixed_effects": [],
                    "cluster_by": [],
                },
            },
        )
        self._write_json(
            state_dir / "design_spec.json",
            {
                "id": "design_spec",
                "version": 2,
                "status": "approved",
                "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                "research_question": "工业机器人暴露是否改变劳动者工资回报？",
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
                        "instrument_formula": "ln_robot ~ bartik_iv + female + age + edu_last + urban",
                    }
                ],
            },
        )
        (data_dir / "cfps_robot_reallocation.csv").write_text(
            "\n".join(
                [
                    "pid,provcd,urban,ln_wage,manu_dummy,ISEI_score,part_time,female,age,edu_last,year,ln_robot,bartik_iv",
                    "1,11,1,10.1,0,45,0,1,32,12,2020,9.2,8.7",
                    "2,31,0,10.9,1,52,0,0,41,16,2022,9.8,9.1",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
