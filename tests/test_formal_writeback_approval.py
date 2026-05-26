import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalWritebackApprovalCliTests(unittest.TestCase):
    """BDD: P5-A records the human entry decision for formal paper package."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-writeback-approval-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_23_approve_records_formal_package_entry_without_state_changes(self) -> None:
        preflight_path = self.project_root / "Results" / "json" / "formal_writeback_preflight.json"
        preflight_before = preflight_path.read_text(encoding="utf-8")
        protected_before = self._snapshot_protected_state()

        result = self._run_cli("--action", "approve", "--note", "批准进入 P5 正式包。")
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_writeback_approval.json"
        review_path = self.project_root / "Reviews" / "formal_writeback_approval.md"
        approval_path = self.project_root / "state" / "product" / "writeback_approvals.json"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(approval_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p5.formal_writeback_approval.v1")
        self.assertEqual(report["status"], "approved_for_p5")
        self.assertEqual(report["action"], "approve")
        self.assertTrue(report["can_enter_p5"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["approval_path"], "state/product/writeback_approvals.json")
        self.assertEqual(report["source_preflight"], "Results/json/formal_writeback_preflight.json")
        self.assertEqual(report["writeback_scope_categories"], [
            "sections",
            "citations",
            "method_narrative",
            "result_tables",
            "reproducibility",
        ])

        ledger = json.loads(approval_path.read_text(encoding="utf-8"))
        self.assertIn("approvals", ledger)
        self.assertEqual(ledger["approvals"], {"legacy_candidate": {"status": "approved"}})
        entry = ledger["formal_preflight_approvals"]["formal_writeback_preflight"]
        self.assertEqual(entry["status"], "approved")
        self.assertTrue(entry["can_enter_p5"])
        self.assertEqual(entry["note"], "批准进入 P5 正式包。")

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P5-A 正式包入口批准", review_text)
        self.assertIn("approved_for_p5", review_text)

        self.assertEqual(preflight_path.read_text(encoding="utf-8"), preflight_before)
        self.assertEqual(self._snapshot_protected_state(), protected_before)

    def test_bdd_23_needs_revision_records_blocking_decision(self) -> None:
        result = self._run_cli("--action", "needs_revision", "--note", "补充摘要和文献综述后再进 P5。")
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_writeback_approval.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "needs_revision")
        self.assertFalse(report["can_enter_p5"])
        self.assertEqual(report["next_action"]["id"], "revise_formal_writeback_preflight")

        ledger = json.loads(
            (self.project_root / "state" / "product" / "writeback_approvals.json").read_text(
                encoding="utf-8"
            )
        )
        entry = ledger["formal_preflight_approvals"]["formal_writeback_preflight"]
        self.assertEqual(entry["status"], "needs_revision")
        self.assertFalse(entry["can_enter_p5"])

    def test_bdd_23_blocks_approval_when_preflight_is_not_ready(self) -> None:
        preflight_path = self.project_root / "Results" / "json" / "formal_writeback_preflight.json"
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        preflight["status"] = "blocked_by_gate_recompute"
        preflight["blocking_reasons"] = ["uncleared_revision_tasks"]
        preflight_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli("--action", "approve", "--note", "尝试批准。")
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_writeback_approval.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_preflight")
        self.assertFalse(report["can_enter_p5"])
        self.assertEqual(report["blocking_reasons"], ["uncleared_revision_tasks"])

        ledger = json.loads(
            (self.project_root / "state" / "product" / "writeback_approvals.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertNotIn("formal_writeback_preflight", ledger.get("formal_preflight_approvals", {}))

    def _run_cli(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_writeback_approval.py"),
                "--project-root",
                str(self.project_root),
                "--preflight",
                "Results/json/formal_writeback_preflight.json",
                "--output-report",
                "Results/json/formal_writeback_approval.json",
                "--output-review",
                "Reviews/formal_writeback_approval.md",
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
            if path.name != "writeback_approvals.json"
        }

    def _seed_project(self, root: Path) -> None:
        results_dir = root / "Results" / "json"
        reviews_dir = root / "Reviews"
        state_dir = root / "state" / "product"
        preview_dir = root / "Manuscripts" / "generated" / "previews"
        for directory in [results_dir, reviews_dir, state_dir, preview_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        for name in [
            "research_question.json",
            "variable_roles.json",
            "variable_role_set.json",
            "design_spec.json",
            "run_plan.json",
            "supervisor_plan.json",
            "agent_task_queue.json",
        ]:
            (state_dir / name).write_text(json.dumps({"name": name, "formal": True}), encoding="utf-8")

        (state_dir / "writeback_approvals.json").write_text(
            json.dumps(
                {
                    "schema_version": "product.writeback_approvals.v1",
                    "approvals": {"legacy_candidate": {"status": "approved"}},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (preview_dir / "formal_writeback_preflight.md").write_text(
            "# Formal writeback preview\n",
            encoding="utf-8",
        )
        (results_dir / "formal_writeback_preflight.json").write_text(
            json.dumps(
                {
                    "schema_version": "p4.formal_writeback_preflight.v1",
                    "status": "ready_for_human_approval",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                    "requires_human_approval": True,
                    "blocking_reasons": [],
                    "preview_path": "Manuscripts/generated/previews/formal_writeback_preflight.md",
                    "writeback_scope": [
                        {"category": "sections", "approval_status": "pending_human_approval"},
                        {"category": "citations", "approval_status": "pending_human_approval"},
                        {"category": "method_narrative", "approval_status": "pending_human_approval"},
                        {"category": "result_tables", "approval_status": "pending_human_approval"},
                        {"category": "reproducibility", "approval_status": "pending_human_approval"},
                    ],
                    "approval_contract": {
                        "approval_path": "state/product/writeback_approvals.json",
                        "ready_for_approval": True,
                    },
                    "formal_state_guard": {
                        "changed": False,
                        "changed_paths": [],
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
