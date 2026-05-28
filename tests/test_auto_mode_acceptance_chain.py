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
            method_knowledge_base=self._method_knowledge_base(),
            statistical_adapter_contract=self._statistical_adapter_contract(),
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
            method_knowledge_base=self._method_knowledge_base(),
            statistical_adapter_contract=self._statistical_adapter_contract(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(chain["package_readiness"], "needs_human_final_review")
        self.assertEqual(chain["repair_queue"], [])
        self.assertIn("review_level3_quality_gate", chain["human_review_checklist"])
        self.assertIn("review_literature_discovery_seed", chain["human_review_checklist"])
        self.assertIn("review_method_knowledge_base", chain["human_review_checklist"])
        self.assertIn("review_statistical_adapter_contract", chain["human_review_checklist"])

    def test_bdd_p7h_reports_five_component_statuses_and_artifact_layers(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index=self._dataset_index(),
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="yellow", ready=True),
            method_knowledge_base=self._method_knowledge_base(),
            statistical_adapter_contract=self._statistical_adapter_contract(),
            source_paths=self._source_paths(),
        )

        statuses = {item["component"]: item["status"] for item in chain["component_statuses"]}
        self.assertEqual(statuses["dataset_motherlode_index"], "needs_human_dataset_index_review")
        self.assertEqual(statuses["literature_discovery_seed"], "needs_human_literature_discovery_review")
        self.assertEqual(statuses["level3_manuscript_quality_gate"], "needs_human_level3_quality_review")
        self.assertEqual(statuses["method_knowledge_base"], "needs_human_method_kb_review")
        self.assertEqual(statuses["statistical_adapter_contract"], "needs_human_statistical_adapter_review")
        self.assertIn("results_evidence_package.json", chain["artifact_layers"]["real_run_artifacts"])
        self.assertIn("statistical_adapter_contract.json", chain["artifact_layers"]["real_run_artifacts"])
        self.assertIn("paper.md", chain["artifact_layers"]["draft_layer_artifacts"])
        self.assertIn("method_knowledge_base.json", chain["artifact_layers"]["draft_layer_artifacts"])
        self.assertIn("method_gate.md", chain["artifact_layers"]["human_review_required"])
        self.assertIn("method_knowledge_base.md", chain["artifact_layers"]["human_review_required"])
        self.assertIn("statistical_adapter_contract.md", chain["artifact_layers"]["human_review_required"])

    def test_bdd_p7d_blocks_when_required_inputs_are_missing(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index={},
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="yellow", ready=True),
            method_knowledge_base=self._method_knowledge_base(),
            statistical_adapter_contract=self._statistical_adapter_contract(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(chain["status"], "blocked_missing_acceptance_inputs")
        self.assertEqual(chain["package_readiness"], "blocked")
        self.assertIn("dataset_motherlode_index", chain["missing_inputs"])

    def test_bdd_p7h_blocks_and_routes_missing_method_or_stat_contracts(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index=self._dataset_index(),
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="yellow", ready=True),
            method_knowledge_base={},
            statistical_adapter_contract={},
            source_paths=self._source_paths(),
        )

        self.assertEqual(chain["status"], "blocked_missing_acceptance_inputs")
        self.assertIn("method_knowledge_base", chain["missing_inputs"])
        self.assertIn("statistical_adapter_contract", chain["missing_inputs"])
        task_ids = {item["task_id"] for item in chain["repair_queue"]}
        self.assertIn("build_method_knowledge_base", task_ids)
        self.assertIn("build_statistical_adapter_contract", task_ids)

    def test_bdd_p7h_repairs_incomplete_statistical_contract(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index=self._dataset_index(),
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="yellow", ready=True),
            method_knowledge_base=self._method_knowledge_base(),
            statistical_adapter_contract=self._statistical_adapter_contract(contract_ready_count=0),
            source_paths=self._source_paths(),
        )

        self.assertEqual(chain["package_readiness"], "needs_auto_mode_repair")
        task_ids = {item["task_id"] for item in chain["repair_queue"]}
        self.assertIn("repair_statistical_adapter_contract", task_ids)
        self.assertEqual(chain["statistical_readiness"]["contract_ready_result_count"], 0)

    def test_bdd_p7h_exposes_method_and_statistical_readiness_summaries(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index=self._dataset_index(),
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="yellow", ready=True),
            method_knowledge_base=self._method_knowledge_base(),
            statistical_adapter_contract=self._statistical_adapter_contract(),
            source_paths=self._source_paths(),
        )

        self.assertEqual(chain["method_readiness"]["recommended_check_count"], 2)
        self.assertFalse(chain["method_readiness"]["proposal_rules_can_block"])
        self.assertEqual(chain["statistical_readiness"]["normalized_result_count"], 2)
        self.assertEqual(chain["statistical_readiness"]["contract_ready_result_count"], 2)
        self.assertEqual(chain["statistical_readiness"]["observed_methods"], ["ols", "ordered_logit"])

    def test_bdd_p7d_writes_json_and_markdown_review_outputs(self) -> None:
        chain = build_auto_mode_acceptance_chain(
            dataset_index=self._dataset_index(),
            literature_seed=self._literature_seed(),
            level3_gate=self._level3_gate(gate_status="red", ready=False),
            method_knowledge_base=self._method_knowledge_base(),
            statistical_adapter_contract=self._statistical_adapter_contract(),
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
            self.assertIn("Method Knowledge Base", review_text)
            self.assertIn("Statistical Adapter Contract", review_text)

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

    def _method_knowledge_base(self) -> dict:
        return {
            "schema_version": "p7.method_knowledge_base.v1",
            "status": "needs_human_method_kb_review",
            "source_summary": {
                "proposal_source_count": 1,
                "canonical_rule_count": 0,
                "reviewed_canonical_blocking_rule_count": 0,
            },
            "formal_export_policy": {
                "proposal_rules_can_block": False,
                "reviewed_canonical_blocking_rule_count": 0,
                "canonical_rules_can_block_after_human_review": False,
            },
            "recommended_checks": [
                {"check_id": "ordered_outcome_model_fit", "requires_human_review": True},
                {"check_id": "ols_association_boundary", "requires_human_review": True},
            ],
        }

    def _statistical_adapter_contract(self, contract_ready_count: int = 2) -> dict:
        normalized_results = [
            {"result_id": "ols_baseline", "method_id": "ols", "status": "contract_ready"},
            {"result_id": "ordered_logit", "method_id": "ordered_logit", "status": "contract_ready"},
        ][:contract_ready_count]
        return {
            "schema_version": "p7.statistical_adapter_contract.v1",
            "status": "needs_human_statistical_adapter_review",
            "normalized_results": normalized_results,
            "capability_matrix": {
                "ols": {
                    "method_id": "ols",
                    "status": "contract_ready" if contract_ready_count else "incomplete",
                    "result_count": 1 if contract_ready_count else 0,
                    "contract_ready_count": 1 if contract_ready_count else 0,
                },
                "ordered_logit": {
                    "method_id": "ordered_logit",
                    "status": "contract_ready" if contract_ready_count > 1 else "not_observed",
                    "result_count": 1 if contract_ready_count > 1 else 0,
                    "contract_ready_count": 1 if contract_ready_count > 1 else 0,
                },
            },
        }

    def _source_paths(self) -> dict:
        return {
            "dataset_index": "Results/json/dataset_motherlode_index.json",
            "literature_seed": "Results/json/literature_discovery_seed.json",
            "level3_gate": "Results/json/level3_manuscript_quality_gate.json",
            "method_knowledge_base": "Results/json/method_knowledge_base.json",
            "statistical_adapter_contract": "Results/json/statistical_adapter_contract.json",
        }


if __name__ == "__main__":
    unittest.main()
