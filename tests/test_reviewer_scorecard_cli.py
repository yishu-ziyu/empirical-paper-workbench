import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReviewerScorecardCliTests(unittest.TestCase):
    """BDD: method diagnostics must become reviewer scorecard and revision tasks."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="reviewer-scorecard-cli-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def run_scorecard(self, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        args = [
            "python3",
            str(REPO_ROOT / "Program" / "reviewer_scorecard.py"),
            "--project-root",
            str(self.project_root),
        ]
        if extra_args:
            args.extend(extra_args)
        return subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True)

    def test_bdd_1_reviewer_scorecard_reads_method_diagnostics_without_formal_writeback(self) -> None:
        result = self.run_scorecard()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "reviewer_scorecard_report.json"
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(report["schema_version"], "p4.reviewer_scorecard.v1")
        self.assertEqual(report["source_refs"]["method_diagnostics_report"]["path"], "Results/json/method_diagnostics_report.json")
        self.assertEqual(report["source_refs"]["method_gate_report"]["path"], "Results/json/method_gate_report.json")
        self.assertEqual(report["overall_verdict"], "draft_allowed_with_causal_caveat")
        self.assertFalse(report["blocks_draft"])
        self.assertTrue(report["blocks_export_or_formal_claims"])
        self.assertEqual(report["formal_state_write"]["status"], "not_written")
        self.assertFalse((self.project_root / "state" / "product" / "reviewer_scorecard.json").exists())
        self.assertFalse((self.project_root / "state" / "product" / "agent_task_queue.json").exists())

        dimension_ids = {dimension["id"] for dimension in report["dimensions"]}
        self.assertEqual(
            dimension_ids,
            {
                "execution_binding",
                "instrument_relevance",
                "weak_iv_and_inference_robustness",
                "bartik_identification_credibility",
                "sample_and_reporting_transparency",
            },
        )
        self.assertGreaterEqual(report["overall_score"], 0)
        self.assertLessEqual(report["overall_score"], 100)
        self.assertEqual(report["agent_team_schedule"]["recall_when"], "after_reviewer_scorecard_report_written")
        self.assertEqual(report["agent_team_schedule"]["next_call_after_recall"], "manuscript_or_export_review")

    def test_bdd_2_scorecard_turns_yellow_diagnostics_into_revision_tasks_not_missing_green_items(self) -> None:
        result = self.run_scorecard()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.project_root / "Results" / "json" / "reviewer_scorecard_report.json").read_text(encoding="utf-8"))

        task_ids = {task["id"] for task in report["revision_tasks"]}
        self.assertIn("add_weak_iv_robust_interval_or_caveat", task_ids)
        self.assertIn("recover_bartik_share_shock_components", task_ids)
        self.assertIn("add_rotemberg_weights_review", task_ids)
        self.assertIn("add_leave_one_out_or_alternative_shock_check", task_ids)
        self.assertIn("write_exclusion_and_shock_exogeneity_review", task_ids)
        self.assertIn("explain_missing_drop_and_analysis_sample", task_ids)

        task_text = json.dumps(report["revision_tasks"], ensure_ascii=False)
        self.assertNotIn("missing_reduced_form", task_text)
        self.assertNotIn("missing_first_stage_relevance", task_text)
        self.assertNotIn("missing_artifact_binding", task_text)

        blocking_scopes = {task["id"]: task["blocking_scope"] for task in report["revision_tasks"]}
        self.assertEqual(blocking_scopes["add_weak_iv_robust_interval_or_caveat"], "formal_claims")
        self.assertEqual(blocking_scopes["recover_bartik_share_shock_components"], "formal_claims_and_export")
        self.assertEqual(blocking_scopes["explain_missing_drop_and_analysis_sample"], "transparency_only")

    def test_bdd_3_paper_quality_detects_reviewer_scorecard_report(self) -> None:
        scorecard = self.run_scorecard()
        self.assertEqual(scorecard.returncode, 0, scorecard.stderr)

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
        quality_report = json.loads((self.project_root / "Results" / "json" / "paper_quality_report.json").read_text(encoding="utf-8"))

        self.assertEqual(quality_report["revision_checks"]["reviewer_scorecard"]["status"], "found")
        self.assertEqual(
            quality_report["revision_checks"]["reviewer_scorecard"]["path"],
            "Results/json/reviewer_scorecard_report.json",
        )
        self.assertEqual(quality_report["revision_checks"]["reviewer_scorecard"]["overall_verdict"], "draft_allowed_with_causal_caveat")

    def _seed_project(self, root: Path) -> None:
        results_dir = root / "Results" / "json"
        results_dir.mkdir(parents=True)
        (root / "state" / "product").mkdir(parents=True)
        diagnostics = {
            "schema_version": "p4.method_diagnostics.v1",
            "status": "completed_with_review_items",
            "method_family": "iv",
            "method_subtype": "bartik_shift_share_iv",
            "dataset_profile": {
                "path": "Data/Final/cfps_robot_reallocation.csv",
                "row_count": 34315,
                "usable_rows": 15697,
                "dropped_rows": 18618,
                "cluster_count": 30,
            },
            "diagnostics": [
                {
                    "id": "baseline_iv_2sls_binding",
                    "status": "green",
                    "outputs": {"coef": 0.1994, "std_error": 0.0780, "nobs": 15697, "cluster_by": ["provcd"]},
                    "review_items": [],
                },
                {
                    "id": "first_stage_relevance",
                    "status": "green",
                    "outputs": {"first_stage_f": 14.52, "partial_r_squared": 0.4834},
                    "review_items": [],
                },
                {
                    "id": "robust_first_stage_f_or_kp",
                    "status": "green",
                    "outputs": {"statistic": 14.52},
                    "review_items": [],
                },
                {
                    "id": "weak_iv_robust_inference_ar_or_clr",
                    "status": "yellow",
                    "outputs": {"note": "exactly_identified_model_ar_overidentification_test_not_available"},
                    "review_items": ["weak_iv_robust_ci_follow_up"],
                },
                {
                    "id": "reduced_form",
                    "status": "green",
                    "outputs": {"coef": 0.14, "std_error": 0.0246, "nobs": 15697},
                    "review_items": [],
                },
                {
                    "id": "ols_comparison",
                    "status": "green",
                    "outputs": {"coef": 0.0975, "std_error": 0.0178, "nobs": 15697},
                    "review_items": [],
                },
                {
                    "id": "sample_consistency",
                    "status": "yellow",
                    "outputs": {"raw_rows": 34315, "usable_rows": 15697, "dropped_rows": 18618},
                    "review_items": ["raw_rows_differ_from_usable_rows_after_missing_drop"],
                },
                {
                    "id": "shift_share_identification_diagnostics",
                    "status": "yellow",
                    "outputs": {"available_components": []},
                    "review_items": ["missing_shift_share_components"],
                },
                {
                    "id": "shift_share_rotemberg_weights",
                    "status": "needs_manual_review",
                    "outputs": {},
                    "review_items": ["missing_shift_share_components"],
                },
                {
                    "id": "leave_one_out_or_alternative_shock",
                    "status": "needs_manual_review",
                    "outputs": {},
                    "review_items": ["missing_shift_share_components"],
                },
                {
                    "id": "artifact_binding",
                    "status": "green",
                    "outputs": {"diagnostics_artifact_path": "Results/json/method_diagnostics_report.json"},
                    "review_items": [],
                },
            ],
        }
        method_gate = {
            "schema_version": "p4.method_gate.v1",
            "gate_status": "yellow",
            "method_family": "iv",
            "method_subtype": "bartik_shift_share_iv",
            "yellow_items": [
                "missing_weak_iv_robust_inference_ar_or_clr",
                "missing_shift_share_identification_diagnostics",
                "missing_shift_share_rotemberg_weights",
                "missing_leave_one_out_or_alternative_shock",
                "review_exclusion_restriction_argument",
                "review_share_or_shock_exogeneity_position",
            ],
            "blocking_items": [],
        }
        (results_dir / "method_diagnostics_report.json").write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")
        (results_dir / "method_gate_report.json").write_text(json.dumps(method_gate, ensure_ascii=False, indent=2), encoding="utf-8")
        draft_dir = root / "Manuscripts" / "generated"
        draft_dir.mkdir(parents=True)
        (draft_dir / "paper_draft.md").write_text("# Draft\n\n## Abstract\n\nShort.\n", encoding="utf-8")
