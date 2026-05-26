import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PaperRevisionEvidencePacketsCliTests(unittest.TestCase):
    """BDD: P4-H turns revision tasks into draft-layer evidence packets."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="paper-revision-evidence-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_revision_round_project(self.project_root)

    def test_bdd_17_revision_tasks_generate_evidence_packets_without_formal_writeback(self) -> None:
        round_path = self.project_root / "Results" / "json" / "paper_revision_round.json"
        round_before = round_path.read_text(encoding="utf-8")
        protected_files = list((self.project_root / "state" / "product").glob("*.json"))
        protected_before = {path: path.read_text(encoding="utf-8") for path in protected_files}

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_evidence_packets.py"),
                "--project-root",
                str(self.project_root),
                "--revision-round",
                "Results/json/paper_revision_round.json",
                "--output-manifest",
                "Results/json/paper_revision_evidence_packets.json",
                "--output-review",
                "Reviews/paper_revision_evidence_packets.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        manifest_path = self.project_root / "Results" / "json" / "paper_revision_evidence_packets.json"
        review_path = self.project_root / "Reviews" / "paper_revision_evidence_packets.md"
        self.assertTrue(manifest_path.exists())
        self.assertTrue(review_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["schema_version"], "p4.paper_revision_evidence_packets.v1")
        self.assertEqual(manifest["source_revision_round"], "Results/json/paper_revision_round.json")
        self.assertTrue(manifest["draft_layer_only"])
        self.assertFalse(manifest["formal_writeback_allowed"])
        self.assertEqual(manifest["agent_team_schedule"]["call_when"], "before_revision_evidence_execution")
        self.assertEqual(manifest["agent_team_schedule"]["recall_when"], "after_revision_evidence_packets_written")
        self.assertEqual(manifest["agent_team_schedule"]["next_call_when"], "before_quality_gate_recompute_or_formal_writeback")
        self.assertFalse(manifest["formal_state_guard"]["changed"])

        records = {record["task_id"]: record for record in manifest["task_results"]}
        self.assertEqual(set(records), {"run_method_gate", "add_weak_iv_robust_interval_or_caveat"})

        ready = records["run_method_gate"]
        self.assertEqual(ready["status"], "evidence_packet_ready")
        self.assertTrue(ready["evidence_items"])
        self.assertEqual(ready["evidence_items"][0]["path"], "Results/json/method_gate_report.json")
        self.assertTrue(ready["evidence_items"][0]["exists"])
        self.assertIn("sha256", ready["evidence_items"][0])
        self.assertEqual(ready["evidence_items"][0]["schema_version"], "p4.method_gate.v1")
        self.assertEqual(ready["evidence_items"][0]["evidence_level"], "structured_local_artifact")

        manual = records["add_weak_iv_robust_interval_or_caveat"]
        self.assertEqual(manual["status"], "needs_manual_review")
        self.assertTrue(manual["evidence_items"])
        self.assertTrue(manual["missing_evidence"])
        self.assertIn("Results/json/method_diagnostics_report.json", manual["missing_evidence"][0]["path"])

        for record in records.values():
            packet_path = self.project_root / record["evidence_packet_path"]
            self.assertTrue(packet_path.exists())
            packet_text = packet_path.read_text(encoding="utf-8")
            self.assertIn("Evidence Packet", packet_text)
            self.assertIn("Source Evidence", packet_text)
            self.assertIn("Verification Evidence", packet_text)
            self.assertIn("Gate Recompute Inputs", packet_text)
            self.assertFalse(record["can_write_product_state"])

        self.assertEqual(round_path.read_text(encoding="utf-8"), round_before)
        for path, content in protected_before.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_bdd_20_literature_short_names_resolve_to_canonical_processed_artifacts(self) -> None:
        """BDD: literature evidence packets must bind processed literature artifacts."""
        self._replace_with_literature_revision_round(self.project_root)
        processed = self.project_root / "Data" / "literature" / "processed"
        processed.mkdir(parents=True)
        verified_path = processed / "verified_bibliography.csv"
        matrix_path = processed / "contribution_matrix.md"
        verified_path.write_text(
            "\n".join(
                [
                    "source_id,citation_key,title,authors,year,venue,verification_status,contribution_role,used_in_section",
                    "lit_001,autor2013,The China Syndrome,Autor Dorn Hanson,2013,AER,doi_verified,closest_evidence,related_work",
                    "lit_002,acemoglu2020,Robots and Jobs,Acemoglu Restrepo,2020,JPE,doi_verified,method_evidence,methodology",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        matrix_path.write_text(
            "\n".join(
                [
                    "| source_id | citation_key | contribution_role | used_in_section | variables_or_method_evidence | difference_from_this_paper | verification_status |",
                    "| --- | --- | --- | --- | --- | --- | --- |",
                    "| lit_001 | autor2013 | closest_evidence | related_work | labor market exposure | China CFPS household evidence | doi_verified |",
                    "| lit_002 | acemoglu2020 | method_evidence | methodology | robot exposure design | city labor market matching focus | doi_verified |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (self.project_root / "Results" / "json" / "literature_package_report.json").write_text(
            json.dumps(
                {
                    "schema_version": "p4.literature_package.v1",
                    "status": "ready_for_human_review",
                    "outputs": {
                        "verified_bibliography": "Data/literature/processed/verified_bibliography.csv",
                        "contribution_matrix": "Data/literature/processed/contribution_matrix.md",
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        protected_files = list((self.project_root / "state" / "product").glob("*.json"))
        protected_before = {path: path.read_text(encoding="utf-8") for path in protected_files}

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_evidence_packets.py"),
                "--project-root",
                str(self.project_root),
                "--revision-round",
                "Results/json/paper_revision_round.json",
                "--output-manifest",
                "Results/json/paper_revision_evidence_packets.json",
                "--output-review",
                "Reviews/paper_revision_evidence_packets.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        manifest = json.loads(
            (self.project_root / "Results" / "json" / "paper_revision_evidence_packets.json").read_text(
                encoding="utf-8"
            )
        )
        records = {record["task_id"]: record for record in manifest["task_results"]}
        literature = records["build_literature_package"]
        self.assertEqual(literature["status"], "evidence_packet_ready")
        self.assertFalse(literature["missing_evidence"])
        paths = {item["path"] for item in literature["evidence_items"]}
        self.assertIn("Data/literature/processed/verified_bibliography.csv", paths)
        self.assertIn("Data/literature/processed/contribution_matrix.md", paths)
        self.assertIn("Results/json/literature_package_report.json", paths)
        self.assertFalse(literature["can_write_product_state"])
        self.assertFalse(manifest["formal_state_guard"]["changed"])
        for path, content in protected_before.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def _seed_revision_round_project(self, root: Path) -> None:
        results_dir = root / "Results" / "json"
        state_dir = root / "state" / "product"
        results_dir.mkdir(parents=True)
        state_dir.mkdir(parents=True)
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

        (results_dir / "method_gate_report.json").write_text(
            json.dumps(
                {
                    "schema_version": "p4.method_gate.v1",
                    "method_family": "iv",
                    "gate_status": "yellow",
                    "required_evidence": ["weak_iv_robust_interval"],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        revision_round = {
            "schema_version": "p4.paper_revision_round.v1",
            "round_id": "paper_revision_round_test",
            "status": "ready_for_human_review",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "agent_packets": [
                {
                    "agent": "MethodAgent",
                    "task_count": 2,
                    "draft_output_dir": "Reviews/agent_packets/methodagent",
                    "tasks": [
                        {
                            "order": 1,
                            "id": "run_method_gate",
                            "agent": "MethodAgent",
                            "source": "paper_quality_report",
                            "source_artifact": "Results/json/method_gate_report.json",
                            "reason": "方法门报告已经存在，需要绑定到下一轮审阅。",
                            "action_item": "把 method gate 结果作为下一轮质量门输入。",
                            "inputs": ["Results/json/method_gate_report.json"],
                            "draft_output_path": "Reviews/agent_packets/methodagent/run-method-gate.md",
                            "verification_evidence_required": ["method_gate_report"],
                            "requires_human_confirmation": True,
                            "can_write_product_state": False,
                            "status": "queued_for_revision",
                        },
                        {
                            "order": 2,
                            "id": "add_weak_iv_robust_interval_or_caveat",
                            "agent": "MethodAgent",
                            "source": "pdf_export_manifest",
                            "source_artifact": "Results/json/method_diagnostics_report.json",
                            "reason": "补充 AR/CLR 稳健区间，见 reviewer 建议。",
                            "action_item": "补充弱工具变量稳健区间或写明 caveat。",
                            "inputs": ["Results/json/method_diagnostics_report.json"],
                            "draft_output_path": "Reviews/agent_packets/methodagent/add-weak-iv-robust-interval-or-caveat.md",
                            "verification_evidence_required": ["weak_iv_robust_interval_or_caveat"],
                            "requires_human_confirmation": True,
                            "can_write_product_state": False,
                            "status": "queued_for_revision",
                        },
                    ],
                }
            ],
        }
        (results_dir / "paper_revision_round.json").write_text(
            json.dumps(revision_round, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _replace_with_literature_revision_round(self, root: Path) -> None:
        revision_round = {
            "schema_version": "p4.paper_revision_round.v1",
            "round_id": "paper_revision_round_literature_test",
            "status": "ready_for_human_review",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "agent_packets": [
                {
                    "agent": "LiteratureAgent",
                    "task_count": 1,
                    "draft_output_dir": "Reviews/agent_packets/literatureagent",
                    "tasks": [
                        {
                            "order": 1,
                            "id": "build_literature_package",
                            "agent": "LiteratureAgent",
                            "source": "paper_quality_report",
                            "source_artifact": "Results/json/literature_package_report.json",
                            "reason": "文献包已写入 processed 路径，需要绑定为下一轮证据。",
                            "action_item": "把 verified bibliography 和 contribution matrix 作为修订证据。",
                            "inputs": ["verified_bibliography.csv", "contribution_matrix.md"],
                            "draft_output_path": "Reviews/agent_packets/literatureagent/build-literature-package.md",
                            "verification_evidence_required": [
                                "verified_bibliography.csv",
                                "contribution_matrix.md",
                            ],
                            "requires_human_confirmation": True,
                            "can_write_product_state": False,
                            "status": "queued_for_revision",
                        }
                    ],
                }
            ],
        }
        (root / "Results" / "json" / "paper_revision_round.json").write_text(
            json.dumps(revision_round, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
