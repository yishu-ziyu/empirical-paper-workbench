import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalEvidenceMaterializerCliTests(unittest.TestCase):
    """BDD: P5-E2a materializes high-confidence formal evidence files."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-evidence-materializer-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_28_materializes_target_evidence_without_formal_state_mutation(self) -> None:
        protected_before = self._snapshot_protected_state()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_evidence_materialization_report.json"
        review_path = self.project_root / "Reviews" / "formal_evidence_materialization.md"
        variable_role_path = self.project_root / "Submissions" / "formal_package" / "evidence" / "variable_role_set.json"
        sample_profile_path = self.project_root / "Results" / "json" / "sample_profile.json"
        regression_tables_path = self.project_root / "Results" / "json" / "regression_tables.json"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(variable_role_path.exists())
        self.assertTrue(sample_profile_path.exists())
        self.assertTrue(regression_tables_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p5.formal_evidence_materialization.v1")
        self.assertEqual(report["status"], "evidence_materialized")
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["this_command_wrote_final_outputs"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(
            [item["id"] for item in report["materialized"]],
            ["variable_role_set", "sample_profile", "regression_tables"],
        )
        self.assertIn("variable_role_dataset_mismatch", report["warnings"])

        variable_role_evidence = json.loads(variable_role_path.read_text(encoding="utf-8"))
        self.assertEqual(variable_role_evidence["evidence_id"], "variable_role_set")
        self.assertEqual(variable_role_evidence["review_status"], "needs_human_review")
        self.assertFalse(variable_role_evidence["canonical_write_allowed"])
        self.assertIn("state/product/variable_roles.json", variable_role_evidence["source_paths"])
        self.assertIn("variable_role_dataset_mismatch", variable_role_evidence["warnings"])

        sample_profile = json.loads(sample_profile_path.read_text(encoding="utf-8"))
        self.assertEqual(sample_profile["evidence_id"], "sample_profile")
        self.assertEqual(sample_profile["dataset_path"], "Data/Final/cfps_robot_reallocation.csv")
        self.assertEqual(sample_profile["nobs"], 34315)
        self.assertEqual(sample_profile["rows_read"], 34315)
        self.assertEqual(sample_profile["usable_numeric_rows"], 34315)

        regression_tables = json.loads(regression_tables_path.read_text(encoding="utf-8"))
        self.assertEqual(regression_tables["evidence_id"], "regression_tables")
        self.assertEqual(regression_tables["tables"][0]["method_id"], "iv")
        coefficients = {row["term"]: row for row in regression_tables["tables"][0]["coefficient_rows"]}
        self.assertAlmostEqual(coefficients["ln_robot"]["coefficient"], 0.1994)
        self.assertAlmostEqual(coefficients["ln_robot"]["standard_error"], 0.0793)

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P5-E2a 正式包证据材料化", review_text)
        self.assertIn("variable_role_dataset_mismatch", review_text)

        self.assertEqual(self._snapshot_protected_state(), protected_before)

    def test_bdd_28_blocks_when_patch_proposal_is_missing(self) -> None:
        (
            self.project_root
            / "Submissions"
            / "formal_package"
            / "reproducibility"
            / "evidence_registry_patch_proposal.json"
        ).unlink()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_evidence_materialization_report.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_patch_proposal")
        self.assertIn("patch_proposal_missing", report["blocking_reasons"])
        self.assertEqual(report["materialized"], [])

    def test_bdd_28_skips_unrequested_evidence_ids(self) -> None:
        result = self._run_cli("--evidence-ids", "sample_profile")
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_evidence_materialization_report.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "evidence_materialized")
        self.assertEqual([item["id"] for item in report["materialized"]], ["sample_profile"])
        self.assertFalse(
            (self.project_root / "Submissions" / "formal_package" / "evidence" / "variable_role_set.json").exists()
        )
        self.assertFalse((self.project_root / "Results" / "json" / "regression_tables.json").exists())

    def _run_cli(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_evidence_materializer.py"),
                "--project-root",
                str(self.project_root),
                *extra_args,
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def _snapshot_protected_state(self) -> dict[str, str]:
        state_dir = self.project_root / "state" / "product"
        return {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(state_dir.glob("*.json"))
        }

    def _seed_project(self, root: Path) -> None:
        for directory in [
            root / "Results" / "json",
            root / "Reviews",
            root / "Submissions" / "formal_package" / "reproducibility",
            root / "state" / "product",
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        for name in [
            "research_question.json",
            "design_spec.json",
            "run_plan.json",
            "supervisor_plan.json",
            "agent_task_queue.json",
            "variable_role_set.json",
        ]:
            (root / "state" / "product" / name).write_text(
                json.dumps({"name": name, "formal": True}, ensure_ascii=False),
                encoding="utf-8",
            )

        (root / "state" / "product" / "variable_roles.json").write_text(
            json.dumps(
                {
                    "id": "variable_role_set",
                    "status": "approved",
                    "version": 2,
                    "dataset_path": "Data/Final/analysis_sample.csv",
                    "roles": {
                        "outcome": ["wage"],
                        "treatment": ["trained"],
                        "controls": ["edu", "experience"],
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        (root / "Results" / "json" / "method_execution_result.json").write_text(
            json.dumps(
                {
                    "schema_version": "p2.method_execution.v1",
                    "methods": [
                        {
                            "run_id": "run_612f02a059d1",
                            "task_id": "robot_wage_iv_baseline",
                            "method_id": "iv",
                            "estimator": "iv",
                            "formula": "ln_wage ~ (ln_robot ~ bartik_iv) + female + age + edu_last + urban",
                            "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                            "nobs": 34315,
                            "dependent_var": "ln_wage",
                            "treatment": "ln_robot",
                            "coefficients": {"ln_robot": 0.1994, "female": -0.12},
                            "standard_errors": {"ln_robot": 0.0793, "female": 0.01},
                            "t_statistics": {"ln_robot": 2.51, "female": -12.0},
                            "p_values": {"ln_robot": 0.012, "female": 0.0},
                            "diagnostics": {"first_stage_F": 18.4, "partial_r2": 0.11},
                            "summary_text": "IV baseline completed.",
                            "data_preflight": {
                                "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                                "rows_read": 34315,
                                "usable_numeric_rows": 34315,
                                "dropped_rows": 0,
                                "required_fields": ["ln_wage", "ln_robot", "bartik_iv"],
                                "checks": [{"id": "required_fields", "status": "passed"}],
                            },
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        proposal_path = root / "Submissions" / "formal_package" / "reproducibility" / "evidence_registry_patch_proposal.json"
        proposal_path.write_text(
            json.dumps(
                {
                    "schema_version": "p5.evidence_registry_patch_proposal.v1",
                    "can_apply_without_human_review": False,
                    "patch_items": [
                        {"id": "variable_role_set", "resolution": "direct_alias_available"},
                        {"id": "sample_profile", "resolution": "derivable_from_existing_artifact"},
                        {"id": "regression_tables", "resolution": "derivable_from_existing_artifact"},
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
