import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PaperRevisionGateRecomputeCliTests(unittest.TestCase):
    """BDD: P4-I turns evidence packets into gate recompute task statuses."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="paper-revision-gate-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_gate_recompute_project(self.project_root)

    def test_bdd_18_gate_recompute_classifies_revision_tasks_without_formal_writeback(self) -> None:
        manifest_path = self.project_root / "Results" / "json" / "paper_revision_evidence_packets.json"
        manifest_before = manifest_path.read_text(encoding="utf-8")
        protected_files = list((self.project_root / "state" / "product").glob("*.json"))
        protected_before = {path: path.read_text(encoding="utf-8") for path in protected_files}

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_gate_recompute.py"),
                "--project-root",
                str(self.project_root),
                "--evidence-manifest",
                "Results/json/paper_revision_evidence_packets.json",
                "--output-report",
                "Results/json/paper_revision_gate_recompute.json",
                "--output-review",
                "Reviews/paper_revision_gate_recompute.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "paper_revision_gate_recompute.json"
        review_path = self.project_root / "Reviews" / "paper_revision_gate_recompute.md"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(report["schema_version"], "p4.paper_revision_gate_recompute.v1")
        self.assertEqual(report["source_evidence_manifest"], "Results/json/paper_revision_evidence_packets.json")
        self.assertTrue(report["draft_layer_only"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertEqual(report["agent_team_schedule"]["call_when"], "before_revision_gate_recompute")
        self.assertEqual(report["agent_team_schedule"]["recall_when"], "after_revision_gate_recompute_written")
        self.assertEqual(report["agent_team_schedule"]["next_call_when"], "before_formal_writeback_preflight")
        self.assertFalse(report["formal_state_guard"]["changed"])

        records = {record["task_id"]: record for record in report["task_results"]}
        self.assertEqual(set(records), {"expand_working_paper_sections", "run_method_gate", "build_literature_package"})

        cleared = records["expand_working_paper_sections"]
        self.assertEqual(cleared["status"], "cleared")
        self.assertEqual(cleared["blocking_sources"], [])
        self.assertEqual(cleared["missing_gate_inputs"], [])

        blocking = records["run_method_gate"]
        self.assertEqual(blocking["status"], "still_blocking")
        self.assertEqual(blocking["blocking_sources"], ["missing_gate_input"])
        self.assertIn("Results/json/missing_method_gate_dependency.json", blocking["missing_gate_inputs"])

        manual = records["build_literature_package"]
        self.assertEqual(manual["status"], "manual_review_required")
        self.assertTrue(manual["missing_evidence"])
        self.assertIn("verified_bibliography.csv", manual["missing_evidence"][0]["path"])
        self.assertNotIn("reviewer_scorecard_report", manual["blocking_sources"])

        self.assertEqual(report["status_counts"]["cleared"], 1)
        self.assertEqual(report["status_counts"]["still_blocking"], 1)
        self.assertEqual(report["status_counts"]["manual_review_required"], 1)
        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P4-I 质量门复核账本", review_text)
        self.assertIn("expand_working_paper_sections", review_text)
        self.assertIn("run_method_gate", review_text)
        self.assertIn("build_literature_package", review_text)

        self.assertEqual(manifest_path.read_text(encoding="utf-8"), manifest_before)
        for path, content in protected_before.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_bdd_21_ready_evidence_packets_consume_stale_gate_task_references(self) -> None:
        manifest_path = self.project_root / "Results" / "json" / "paper_revision_evidence_packets.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for task in manifest["task_results"]:
            task["status"] = "evidence_packet_ready"
            task["missing_evidence"] = []
            if task["task_id"] == "build_literature_package":
                task["evidence_items"] = [
                    {"path": "Data/literature/processed/verified_bibliography.csv", "exists": True}
                ]
            task["gate_recompute_inputs"] = [
                "Results/json/paper_quality_report.json",
                "Results/json/reviewer_scorecard_report.json",
                "Submissions/cfps_robot_pdf_export_manifest.json",
            ]
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_gate_recompute.py"),
                "--project-root",
                str(self.project_root),
                "--evidence-manifest",
                "Results/json/paper_revision_evidence_packets.json",
                "--output-report",
                "Results/json/paper_revision_gate_recompute.json",
                "--output-review",
                "Reviews/paper_revision_gate_recompute.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "paper_revision_gate_recompute.json").read_text(
                encoding="utf-8"
            )
        )
        records = {record["task_id"]: record for record in report["task_results"]}

        self.assertEqual(report["status"], "ready_for_formal_writeback_preflight")
        self.assertEqual(report["status_counts"]["cleared"], 3)
        self.assertEqual(report["status_counts"]["still_blocking"], 0)
        self.assertEqual(report["status_counts"]["manual_review_required"], 0)
        for record in records.values():
            self.assertEqual(record["status"], "cleared")
            self.assertEqual(record["blocking_sources"], [])
            self.assertEqual(record["gate_matches"], [])

        consumed = records["run_method_gate"]["consumed_gate_matches"]
        self.assertTrue(consumed)
        self.assertIn("reviewer_scorecard_report", {match["source"] for match in consumed})
        self.assertIn("pdf_export_manifest", {match["source"] for match in consumed})
        self.assertEqual(report["next_action"]["id"], "formal_writeback_preflight")

    def _seed_gate_recompute_project(self, root: Path) -> None:
        results_dir = root / "Results" / "json"
        submissions_dir = root / "Submissions"
        state_dir = root / "state" / "product"
        reviews_dir = root / "Reviews" / "agent_packets"
        results_dir.mkdir(parents=True)
        submissions_dir.mkdir(parents=True)
        state_dir.mkdir(parents=True)
        reviews_dir.mkdir(parents=True)

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

        for packet in [
            "manuscriptagent/expand-working-paper-sections.md",
            "methodagent/run-method-gate.md",
            "literatureagent/build-literature-package.md",
        ]:
            packet_path = reviews_dir / packet
            packet_path.parent.mkdir(parents=True, exist_ok=True)
            packet_path.write_text(f"# Evidence Packet\n\n{packet}\n", encoding="utf-8")

        (results_dir / "paper_quality_report.json").write_text(
            json.dumps(
                {
                    "schema_version": "p4.paper_quality.v1",
                    "recommended_next_tasks": [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (results_dir / "method_gate_report.json").write_text(
            json.dumps({"schema_version": "p4.method_gate.v1", "gate_status": "yellow"}, ensure_ascii=False),
            encoding="utf-8",
        )
        (results_dir / "reviewer_scorecard_report.json").write_text(
            json.dumps(
                {
                    "schema_version": "p4.reviewer_scorecard.v1",
                    "revision_tasks": [{"id": "run_method_gate", "reason": "method gate still yellow"}],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (submissions_dir / "cfps_robot_pdf_export_manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": "p4.pdf_export_manifest.v1",
                    "export_gate": {
                        "can_export_pdf": False,
                        "blocking_reasons": ["run_method_gate"],
                    },
                    "next_review_tasks": [{"id": "run_method_gate", "agent": "MethodAgent"}],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        manifest = {
            "schema_version": "p4.paper_revision_evidence_packets.v1",
            "status": "ready_for_gate_recompute",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "task_results": [
                {
                    "task_id": "expand_working_paper_sections",
                    "agent": "ManuscriptAgent",
                    "status": "evidence_packet_ready",
                    "evidence_packet_path": "Reviews/agent_packets/manuscriptagent/expand-working-paper-sections.md",
                    "evidence_items": [{"path": "Results/json/paper_quality_report.json", "exists": True}],
                    "missing_evidence": [],
                    "gate_recompute_inputs": [
                        "Results/json/paper_quality_report.json",
                        "Results/json/reviewer_scorecard_report.json",
                        "Submissions/cfps_robot_pdf_export_manifest.json",
                    ],
                },
                {
                    "task_id": "run_method_gate",
                    "agent": "MethodAgent",
                    "status": "evidence_packet_ready",
                    "evidence_packet_path": "Reviews/agent_packets/methodagent/run-method-gate.md",
                    "evidence_items": [{"path": "Results/json/method_gate_report.json", "exists": True}],
                    "missing_evidence": [],
                    "gate_recompute_inputs": [
                        "Results/json/method_gate_report.json",
                        "Results/json/missing_method_gate_dependency.json",
                        "Results/json/reviewer_scorecard_report.json",
                        "Submissions/cfps_robot_pdf_export_manifest.json",
                    ],
                },
                {
                    "task_id": "build_literature_package",
                    "agent": "LiteratureAgent",
                    "status": "needs_manual_review",
                    "evidence_packet_path": "Reviews/agent_packets/literatureagent/build-literature-package.md",
                    "evidence_items": [],
                    "missing_evidence": [
                        {"path": "verified_bibliography.csv", "review_reason": "required local artifact was not found"}
                    ],
                    "gate_recompute_inputs": [
                        "Results/json/paper_quality_report.json",
                        "Results/json/reviewer_scorecard_report.json",
                        "Submissions/cfps_robot_pdf_export_manifest.json",
                    ],
                },
            ],
        }
        (results_dir / "paper_revision_evidence_packets.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
