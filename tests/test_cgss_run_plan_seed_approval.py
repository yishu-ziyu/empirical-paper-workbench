import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_run_plan_seed_approval import (
    build_cgss_run_plan_seed_approval,
    write_cgss_run_plan_seed_approval_outputs,
)


class CgssRunPlanSeedApprovalTests(unittest.TestCase):
    """BDD: real CGSS execution needs an explicit RunPlan seed decision first."""

    def test_bdd_57_defer_records_pending_decision_without_approved_seed(self) -> None:
        """行为 57.1：默认只记录待审阅，不生成可执行批准版。"""
        record = build_cgss_run_plan_seed_approval(
            self._run_plan_seed(),
            decision="defer",
            reviewer="",
            note="",
        )

        self.assertEqual(record["schema_version"], "p6.cgss_run_plan_seed_approval.v1")
        self.assertEqual(record["status"], "pending_human_run_plan_seed_decision")
        self.assertEqual(record["decision"], "defer")
        self.assertFalse(record["approved"])
        self.assertFalse(record["formal_writeback_allowed"])
        self.assertFalse(record["can_write_product_state"])
        self.assertEqual(record["approved_run_plan_seed"], {})

    def test_bdd_57_approve_requires_reviewer_and_note(self) -> None:
        """行为 57.2：批准执行前必须留下审阅人和审阅说明。"""
        record = build_cgss_run_plan_seed_approval(
            self._run_plan_seed(),
            decision="approve",
            reviewer="",
            note="",
        )

        self.assertEqual(record["status"], "blocked_missing_human_approval_metadata")
        self.assertFalse(record["approved"])
        self.assertIn("reviewer_required", record["blocking_reasons"])
        self.assertIn("approval_note_required", record["blocking_reasons"])
        self.assertEqual(record["approved_run_plan_seed"], {})

    def test_bdd_57_approve_creates_draft_execution_seed_only(self) -> None:
        """行为 57.3：批准只生成草案执行版，不写正式 RunPlan。"""
        record = build_cgss_run_plan_seed_approval(
            self._run_plan_seed(),
            decision="approve",
            reviewer="mahaoxuan",
            note="批准先跑 OLS 和 Ordered Logit，结果仍进入草案证据包。",
        )

        self.assertEqual(record["status"], "run_plan_seed_approved_for_draft_execution")
        self.assertTrue(record["approved"])
        approved_seed = record["approved_run_plan_seed"]
        self.assertEqual(approved_seed["status"], "approved_for_draft_execution")
        self.assertTrue(approved_seed["promotion"]["allowed"])
        self.assertEqual(approved_seed["human_approval"]["decision"], "human_approve_cgss_run_plan_seed")
        self.assertFalse(approved_seed["formal_writeback_allowed"])
        self.assertEqual(record["promotion"]["would_enable"], ["execute_cgss_run_plan_seed"])

        with tempfile.TemporaryDirectory() as tmpdir:
            _, _, approved_seed_path = write_cgss_run_plan_seed_approval_outputs(
                Path(tmpdir),
                record,
                Path("Results/json/cgss_social_capital_happiness_run_plan_seed_approval.json"),
                Path("Reviews/cgss_social_capital_happiness_run_plan_seed_approval.md"),
                Path("Results/json/cgss_social_capital_happiness_run_plan_seed_approved.json"),
            )

            self.assertIsNotNone(approved_seed_path)
            payload = json.loads(approved_seed_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "approved_for_draft_execution")
            self.assertEqual(payload["human_approval"]["approved_by"], "mahaoxuan")
            self.assertFalse((Path(tmpdir) / "state/product/run_plan.json").exists())

    def test_bdd_57_revise_and_reject_do_not_create_approved_seed(self) -> None:
        """行为 57.4：要求修订或否决时，不能继续展开执行。"""
        for decision in ("revise", "reject"):
            with self.subTest(decision=decision):
                record = build_cgss_run_plan_seed_approval(
                    self._run_plan_seed(),
                    decision=decision,
                    reviewer="mahaoxuan",
                    note="需要先调整模型任务或变量构造。",
                )

                self.assertFalse(record["approved"])
                self.assertEqual(record["approved_run_plan_seed"], {})
                self.assertIn(record["status"], {"run_plan_seed_needs_changes", "run_plan_seed_rejected"})
                self.assertFalse(record["promotion"]["allowed"])

    def test_bdd_57_cli_defaults_to_defer_without_product_state(self) -> None:
        """行为 57.5：CLI 默认只生成审阅记录，不写正式层。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(project_root / "Results/json/run_plan_seed.json", self._run_plan_seed())

            result = subprocess.run(
                [
                    "python3",
                    "Program/cgss_run_plan_seed_approval.py",
                    "--project-root",
                    str(project_root),
                    "--run-plan-seed",
                    "Results/json/run_plan_seed.json",
                    "--output-result",
                    "Results/json/cgss_social_capital_happiness_run_plan_seed_approval.json",
                    "--output-review",
                    "Reviews/cgss_social_capital_happiness_run_plan_seed_approval.md",
                    "--output-approved-seed",
                    "Results/json/cgss_social_capital_happiness_run_plan_seed_approved.json",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=pending_human_run_plan_seed_decision", result.stdout)
            self.assertIn("approved=false", result.stdout)
            self.assertIn("approved_seed=none", result.stdout)
            self.assertTrue((project_root / "Reviews/cgss_social_capital_happiness_run_plan_seed_approval.md").exists())
            self.assertFalse((project_root / "Results/json/cgss_social_capital_happiness_run_plan_seed_approved.json").exists())
            self.assertFalse((project_root / "state/product/run_plan.json").exists())

    def _run_plan_seed(self) -> dict:
        return {
            "schema_version": "p6.cgss_run_plan_seed.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析",
            "status": "needs_human_run_plan_seed_review",
            "boundary_flags": {
                "modified_formal_run_plan": False,
                "wrote_state_product": False,
                "ran_models": False,
            },
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_cgss_run_plan_seed",
                "would_write_if_approved": "state/product/run_plan.json",
            },
            "run_plan_seed": {
                "id": "cgss_run_plan_seed",
                "status": "draft_needs_human_review",
                "dataset_path": "/data/CGSS2023.dta",
                "tasks": [
                    {
                        "id": "run_ols_baseline",
                        "label": "OLS 基准模型",
                        "method_id": "ols",
                        "status": "planned",
                        "cli": "python3 Program/cgss_minimal_model.py --project-root .",
                    },
                    {
                        "id": "run_ordered_logit_robustness",
                        "label": "Ordered Logit 有序模型",
                        "method_id": "ordered_logit",
                        "status": "planned",
                        "cli": "python3 Program/cgss_ordered_robustness.py --project-root .",
                    },
                ],
            },
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
