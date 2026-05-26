import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalEvidenceRegistryResolverCliTests(unittest.TestCase):
    """BDD: P5-E1 maps existing artifacts before asking agents to recreate evidence."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-evidence-registry-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_27_maps_existing_aliases_and_derivable_artifacts(self) -> None:
        preflight_before = (self.project_root / "Results" / "json" / "formal_pdf_export_preflight.json").read_text(
            encoding="utf-8"
        )
        protected_before = self._snapshot_protected_state()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_evidence_registry_resolution.json"
        review_path = self.project_root / "Reviews" / "formal_evidence_registry_resolution.md"
        proposal_path = (
            self.project_root
            / "Submissions"
            / "formal_package"
            / "reproducibility"
            / "evidence_registry_patch_proposal.json"
        )
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(proposal_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p5.formal_evidence_registry_resolution.v1")
        self.assertEqual(report["status"], "evidence_registry_patch_proposed")
        self.assertFalse(report["this_command_mutated_preflight"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])

        by_id = {item["id"]: item for item in report["evidence_resolutions"]}
        self.assertEqual(by_id["variable_role_set"]["resolution"], "direct_alias_available")
        self.assertIn("state/product/variable_roles.json", by_id["variable_role_set"]["selected_paths"])
        self.assertEqual(by_id["approved_findings"]["resolution"], "derivable_from_existing_artifact")
        self.assertIn("state/product/finding_reviews.json", by_id["approved_findings"]["selected_paths"])
        self.assertEqual(by_id["sample_profile"]["resolution"], "derivable_from_existing_artifact")
        self.assertIn("Results/json/method_execution_result.json", by_id["sample_profile"]["selected_paths"])
        self.assertEqual(by_id["regression_tables"]["resolution"], "derivable_from_existing_artifact")
        self.assertEqual(by_id["verified_context_sources"]["resolution"], "missing_after_scan")

        proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
        self.assertEqual(proposal["schema_version"], "p5.evidence_registry_patch_proposal.v1")
        self.assertFalse(proposal["can_apply_without_human_review"])
        self.assertTrue(any(item["id"] == "variable_role_set" for item in proposal["patch_items"]))
        self.assertTrue(any(item["requires_human_confirmation"] for item in proposal["patch_items"]))

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P5-E1 证据注册表解析", review_text)
        self.assertIn("direct_alias_available", review_text)
        self.assertIn("missing_after_scan", review_text)

        self.assertEqual(
            (self.project_root / "Results" / "json" / "formal_pdf_export_preflight.json").read_text(
                encoding="utf-8"
            ),
            preflight_before,
        )
        self.assertEqual(self._snapshot_protected_state(), protected_before)

    def test_bdd_27_noops_when_preflight_has_no_missing_evidence(self) -> None:
        preflight_path = self.project_root / "Results" / "json" / "formal_pdf_export_preflight.json"
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        preflight["status"] = "ready_for_pdf_export_review"
        preflight["blocking_reasons"] = []
        for check in preflight["evidence_checks"]:
            check["status"] = "passed"
            check["issues"] = []
        preflight_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_evidence_registry_resolution.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "no_missing_evidence")
        self.assertEqual(report["evidence_resolutions"], [])
        self.assertEqual(report["patch_summary"]["total"], 0)

    def test_bdd_27_blocks_when_preflight_report_is_missing(self) -> None:
        (self.project_root / "Results" / "json" / "formal_pdf_export_preflight.json").unlink()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_evidence_registry_resolution.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_preflight_report")
        self.assertIn("preflight_report_missing", report["blocking_reasons"])

    def _run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_evidence_registry_resolver.py"),
                "--project-root",
                str(self.project_root),
                "--preflight-report",
                "Results/json/formal_pdf_export_preflight.json",
                "--output-report",
                "Results/json/formal_evidence_registry_resolution.json",
                "--output-review",
                "Reviews/formal_evidence_registry_resolution.md",
                "--output-proposal",
                "Submissions/formal_package/reproducibility/evidence_registry_patch_proposal.json",
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
            "variable_roles.json",
            "design_spec.json",
            "run_plan.json",
            "supervisor_plan.json",
            "agent_task_queue.json",
        ]:
            payload = {"name": name, "status": "approved" if name != "variable_roles.json" else "approved"}
            if name == "variable_roles.json":
                payload.update({"id": "variable_role_set", "roles": {"outcome": ["ln_wage"]}})
            (root / "state" / "product" / name).write_text(json.dumps(payload), encoding="utf-8")

        (root / "state" / "product" / "finding_reviews.json").write_text(
            json.dumps(
                {
                    "reviews": {
                        "finding_robot_wage": {
                            "review_status": "approved",
                            "finding_id": "finding_robot_wage",
                            "artifact_path": "Results/json/method_execution_result.json",
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        (root / "Results" / "json" / "method_execution_result.json").write_text(
            json.dumps(
                {
                    "schema_version": "p2.method_execution.v1",
                    "methods": [
                        {
                            "task_id": "robot_wage_iv_baseline",
                            "nobs": 34315,
                            "dependent_var": "ln_wage",
                            "treatment": "ln_robot",
                            "coefficients": {"ln_robot": 0.1994},
                            "standard_errors": {"ln_robot": 0.0793},
                            "data_preflight": {
                                "dataset_path": "Data/Final/cfps_robot_reallocation.csv",
                                "rows_read": 34315,
                                "usable_numeric_rows": 34315,
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (root / "Results" / "json" / "method_diagnostics_report.json").write_text(
            json.dumps({"schema_version": "p4.method_diagnostics.v1", "diagnostics": []}),
            encoding="utf-8",
        )

        evidence_checks = []
        for evidence_id in [
            "variable_role_set",
            "approved_findings",
            "sample_profile",
            "regression_tables",
            "verified_context_sources",
        ]:
            evidence_checks.append(
                {
                    "id": evidence_id,
                    "status": "failed",
                    "candidate_paths": [f"Results/json/{evidence_id}.json"],
                    "existing_paths": [],
                    "required_by_sections": ["Example Section"],
                    "issues": ["required_evidence_missing"],
                }
            )
        (root / "Results" / "json" / "formal_pdf_export_preflight.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_pdf_export_preflight.v1",
                    "status": "blocked_by_source_gaps",
                    "blocking_reasons": ["required_evidence_missing"],
                    "evidence_checks": evidence_checks,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
