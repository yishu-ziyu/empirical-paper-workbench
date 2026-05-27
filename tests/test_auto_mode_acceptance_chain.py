import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_acceptance_chain import build_auto_mode_acceptance_chain, write_report


class AutoModeAcceptanceChainTests(unittest.TestCase):
    """BDD: Auto Mode must expose one package readiness and repair queue."""

    def test_bdd_p7d_red_level3_gate_creates_auto_mode_repair_queue(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index=self._dataset_index(),
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="red", ready=False),
            source_paths=self._source_paths(),
        )

        self.assertEqual(chain["schema_version"], "p7.auto_mode_acceptance_chain.v1")
        self.assertEqual(chain["package_readiness"], "needs_auto_mode_repair")
        self.assertEqual(chain["status"], "needs_auto_mode_repair")
        task_ids = {item["task_id"] for item in chain["repair_queue"]}
        self.assertIn("mark_candidate_references_for_human_review", task_ids)
        self.assertFalse(chain["boundary_flags"]["modified_formal_manuscript"])

    def test_bdd_p7d_yellow_ready_gate_enters_human_final_review(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index=self._dataset_index(),
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="yellow", ready=True),
            source_paths=self._source_paths(),
        )

        self.assertEqual(chain["package_readiness"], "needs_human_final_review")
        self.assertEqual(chain["repair_queue"], [])
        self.assertIn("review_level3_quality_gate", chain["human_review_checklist"])
        self.assertIn("review_literature_discovery_seed", chain["human_review_checklist"])

    def test_bdd_p7d_reports_component_statuses_and_artifact_layers(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index=self._dataset_index(),
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="yellow", ready=True),
            source_paths=self._source_paths(),
        )

        statuses = {item["component"]: item["status"] for item in chain["component_statuses"]}
        self.assertEqual(statuses["dataset_motherlode_index"], "needs_human_dataset_index_review")
        self.assertEqual(statuses["literature_discovery_seed"], "needs_human_literature_discovery_review")
        self.assertEqual(statuses["level3_manuscript_quality_gate"], "needs_human_level3_quality_review")
        self.assertIn("results_evidence_package.json", chain["artifact_layers"]["real_run_artifacts"])
        self.assertIn("paper.md", chain["artifact_layers"]["draft_layer_artifacts"])
        self.assertIn("method_gate.md", chain["artifact_layers"]["human_review_required"])

    def test_bdd_p7d_blocks_when_required_inputs_are_missing(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index={},
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="yellow", ready=True),
            source_paths=self._source_paths(),
        )

        self.assertEqual(chain["status"], "blocked_missing_acceptance_inputs")
        self.assertEqual(chain["package_readiness"], "blocked")
        self.assertIn("dataset_motherlode_index", chain["missing_inputs"])

    def test_bdd_p7d_writes_json_and_markdown_review_outputs(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index=self._dataset_index(),
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="red", ready=False),
            source_paths=self._source_paths(),
        )

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            report_path, review_path = write_report(
                project_root,
                chain,
                Path("Results/json/auto_mode_acceptance_chain.json"),
                Path("Reviews/auto_mode_acceptance_chain.md"),
            )

            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "needs_auto_mode_repair")
            review_text = review_path.read_text(encoding="utf-8")
            self.assertIn("Auto Mode Acceptance Chain", review_text)
            self.assertIn("正式论文写回：否", review_text)
            self.assertIn("needs_auto_mode_repair", review_text)

    def _dataset_index(self) -> dict:
        return {
            "schema_version": "p7.dataset_motherlode_index.v1",
            "status": "needs_human_dataset_index_review",
            "candidate_data_bindings": [{"family_name": "外部源数据"}],
        }

    def _literature_seed(self) -> dict:
        return {
            "schema_version": "p7.literature_discovery_seed.v1",
            "status": "needs_human_literature_discovery_review",
            "candidate_search_records": [{"record_id": "LQ001"}],
            "source_registry": [{"source_id": "openalex_metadata"}],
        }

    def _level3_gate(self, gate_status: str, ready: bool) -> dict:
        return {
            "schema_version": "p7.level3_manuscript_quality_gate.v1",
            "status": "needs_human_level3_quality_review",
            "gate_status": gate_status,
            "ready_for_level3_review": ready,
            "required_followup_tasks": [] if ready else ["mark_candidate_references_for_human_review"],
            "artifact_check": {
                "real_run_artifacts": ["results_evidence_package.json", "paper.pdf"],
                "draft_layer_artifacts": ["paper.md", "literature_review_packet.json"],
                "human_review_required": ["method_gate.md", "reviewer_report.md"],
            },
        }

    def _source_paths(self) -> dict:
        return {
            "dataset_index": "Results/json/dataset_motherlode_index.json",
            "literature_seed": "Results/json/literature_discovery_seed.json",
            "level3_gate": "Results/json/level3_manuscript_quality_gate.json",
        }


if __name__ == "__main__":
    unittest.main()
