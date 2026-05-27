import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_revision_task_queue import (
    build_cgss_revision_task_queue,
    write_revision_task_queue_outputs,
    write_revision_task_queue_review,
)


class CgssRevisionTaskQueueTests(unittest.TestCase):
    """BDD: CGSS draft inputs become a human-approved reviewer-style revision queue."""

    def test_bdd_59_builds_four_agent_draft_layer_revision_queue(self) -> None:
        queue = build_cgss_revision_task_queue(
            self._literature_seed_package(),
            self._literature_review_packet(),
            self._method_structure_gate_packet(),
        )

        self.assertEqual(queue["schema_version"], "p6.cgss_revision_task_queue.v1")
        self.assertEqual(queue["status"], "needs_human_revision_queue_approval")
        self.assertTrue(queue["draft_layer_only"])
        self.assertFalse(queue["formal_writeback_allowed"])
        self.assertFalse(queue["boundary_flags"]["wrote_state_product"])
        self.assertFalse(queue["boundary_flags"]["modified_design_spec"])
        self.assertFalse(queue["boundary_flags"]["modified_run_plan"])
        self.assertFalse(queue["boundary_flags"]["wrote_formal_manuscript"])
        self.assertEqual(
            {packet["agent"] for packet in queue["agent_packets"]},
            {"LiteratureAgent", "MethodAgent", "WriterAgent", "ReviewerAgent"},
        )
        self.assertEqual({task["status"] for task in queue["agent_task_queue"]}, {"queued_for_human_approved_revision"})

    def test_bdd_59_literature_agent_receives_seed_sources_and_draft_blocks(self) -> None:
        queue = build_cgss_revision_task_queue(
            self._literature_seed_package(),
            self._literature_review_packet(),
            self._method_structure_gate_packet(),
        )

        literature_packet = self._agent_packet(queue, "LiteratureAgent")
        task_ids = {task["task_id"] for task in literature_packet["tasks"]}
        self.assertIn("literature.verify_open_seed_sources", task_ids)
        self.assertIn("literature.revise_review_blocks", task_ids)
        self.assertIn("S01", literature_packet["input_summary"]["open_source_ids"])
        self.assertIn("theory_foundation", literature_packet["input_summary"]["paragraph_block_ids"])
        for task in literature_packet["tasks"]:
            self.assertTrue(task["draft_layer_only"])
            self.assertFalse(task["formal_writeback_allowed"])

    def test_bdd_59_method_agent_receives_claim_gates_without_updating_designspec_or_runplan(self) -> None:
        queue = build_cgss_revision_task_queue(
            self._literature_seed_package(),
            self._literature_review_packet(),
            self._method_structure_gate_packet(),
        )

        method_packet = self._agent_packet(queue, "MethodAgent")
        task_ids = {task["task_id"] for task in method_packet["tasks"]}
        self.assertIn("method.decide_primary_ordered_outcome_model", task_ids)
        self.assertIn("method.review_blocked_causal_methods", task_ids)
        self.assertIn("IV", method_packet["input_summary"]["blocked_method_families"])
        self.assertEqual(method_packet["write_boundary"]["must_not_write"], ["DesignSpec", "RunPlan", "state/product"])

    def test_bdd_59_writer_and_reviewer_tasks_are_review_queue_items_not_formal_paper_writes(self) -> None:
        queue = build_cgss_revision_task_queue(
            self._literature_seed_package(),
            self._literature_review_packet(),
            self._method_structure_gate_packet(),
        )

        writer_packet = self._agent_packet(queue, "WriterAgent")
        reviewer_packet = self._agent_packet(queue, "ReviewerAgent")
        self.assertIn("writer.prepare_section_revision_briefs", {task["task_id"] for task in writer_packet["tasks"]})
        self.assertIn("reviewer.audit_revision_queue", {task["task_id"] for task in reviewer_packet["tasks"]})
        self.assertIn("Literature and Contribution", writer_packet["input_summary"]["target_sections"])
        self.assertIn("human_approval_required", reviewer_packet["acceptance_checks"])
        for task in writer_packet["tasks"] + reviewer_packet["tasks"]:
            self.assertTrue(task["draft_layer_only"])
            self.assertFalse(task["formal_writeback_allowed"])
            self.assertTrue(task["output_target"].startswith("Reviews/"))

    def test_bdd_59_blocks_when_required_revision_inputs_are_missing(self) -> None:
        literature_packet = self._literature_review_packet()
        literature_packet["status"] = "blocked_missing_bibliography_candidates"

        queue = build_cgss_revision_task_queue(
            self._literature_seed_package(),
            literature_packet,
            self._method_structure_gate_packet(),
        )

        self.assertEqual(queue["status"], "blocked_missing_revision_inputs")
        self.assertEqual(queue["agent_task_queue"], [])
        self.assertIn("literature_review_draft_packet_not_ready", queue["blocking_reasons"])
        self.assertFalse(queue["formal_writeback_allowed"])

    def test_bdd_59_writes_review_file_with_embedded_queue_json(self) -> None:
        queue = build_cgss_revision_task_queue(
            self._literature_seed_package(),
            self._literature_review_packet(),
            self._method_structure_gate_packet(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            review_path = write_revision_task_queue_review(
                Path(tmpdir),
                queue,
                Path("Reviews/cgss_social_capital_happiness_revision_task_queue.md"),
            )

            text = review_path.read_text(encoding="utf-8")
            self.assertIn("CGSS 审稿式修订任务队列", text)
            self.assertIn("p6.cgss_revision_task_queue.v1", text)
            self.assertIn("LiteratureAgent", text)
            self.assertIn('"status": "needs_human_revision_queue_approval"', text)
            self.assertFalse((Path(tmpdir) / "state/product/agent_task_queue.json").exists())

    def test_bdd_59_writes_machine_queue_json_without_product_state(self) -> None:
        queue = build_cgss_revision_task_queue(
            self._literature_seed_package(),
            self._literature_review_packet(),
            self._method_structure_gate_packet(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            result_path, review_path = write_revision_task_queue_outputs(
                Path(tmpdir),
                queue,
                Path("Results/json/cgss_social_capital_happiness_revision_task_queue.json"),
                Path("Reviews/cgss_social_capital_happiness_revision_task_queue.md"),
            )

            payload = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "p6.cgss_revision_task_queue.v1")
            self.assertEqual(payload["status"], "needs_human_revision_queue_approval")
            self.assertEqual(len(payload["agent_task_queue"]), 8)
            self.assertTrue(review_path.exists())
            self.assertFalse((Path(tmpdir) / "state/product/agent_task_queue.json").exists())

    def test_bdd_59_cli_reads_existing_packets_and_writes_review_and_machine_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(project_root / "Results/json/seed.json", self._literature_seed_package())
            self._write_json(project_root / "Results/json/literature.json", self._literature_review_packet())
            self._write_json(project_root / "Results/json/method.json", self._method_structure_gate_packet())

            result = subprocess.run(
                [
                    "python3",
                    "Program/cgss_revision_task_queue.py",
                    "--project-root",
                    str(project_root),
                    "--literature-seed-package",
                    "Results/json/seed.json",
                    "--literature-review-packet",
                    "Results/json/literature.json",
                    "--method-structure-gate-packet",
                    "Results/json/method.json",
                    "--output-result",
                    "Results/json/cgss_social_capital_happiness_revision_task_queue.json",
                    "--output-review",
                    "Reviews/cgss_social_capital_happiness_revision_task_queue.md",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=needs_human_revision_queue_approval", result.stdout)
            self.assertIn("cgss_revision_task_queue=Results/json", result.stdout)
            self.assertTrue((project_root / "Reviews/cgss_social_capital_happiness_revision_task_queue.md").exists())
            self.assertTrue((project_root / "Results/json/cgss_social_capital_happiness_revision_task_queue.json").exists())
            self.assertFalse((project_root / "state/product/agent_task_queue.json").exists())

    def _agent_packet(self, queue: dict, agent: str) -> dict:
        return next(packet for packet in queue["agent_packets"] if packet["agent"] == agent)

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _literature_seed_package(self) -> dict:
        return {
            "schema_version": "p6.cgss_literature_seed_package.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "needs_human_literature_review",
            "coverage": [
                "social_capital_theory",
                "subjective_wellbeing_measurement",
                "cgss_empirical_context",
                "ordinal_outcome_method",
            ],
            "seed_sources": [
                {"id": "S01", "title": "CGSS 项目概况", "evidence_role": ["data_source_description"]},
                {"id": "S03", "title": "Bowling Alone", "evidence_role": ["social_capital_theory"]},
                {"id": "S10", "title": "How Important is Methodology", "evidence_role": ["ordinal_outcome_method"]},
            ],
        }

    def _literature_review_packet(self) -> dict:
        return {
            "schema_version": "p6.cgss_literature_review_draft_packet.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "needs_human_literature_review_draft_approval",
            "paragraph_blocks": [
                {"id": "theory_foundation", "heading": "社会资本理论基础", "source_ids": ["S03"]},
                {"id": "method_transition", "heading": "有序因变量与实证策略衔接", "source_ids": ["S10"]},
            ],
            "open_dependencies": [
                {
                    "source_id": "S01",
                    "title": "CGSS 项目概况",
                    "required_action": "open_official_source_and_record_access_date",
                }
            ],
            "promotion": {"allowed": False},
        }

    def _method_structure_gate_packet(self) -> dict:
        return {
            "schema_version": "p6.cgss_method_structure_gate_packet.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "needs_human_method_structure_approval",
            "section_standards": {
                "Literature and Contribution": {
                    "required_evidence": ["verified_bibliography_candidates", "citation_bindings"],
                },
                "Empirical Strategy": {
                    "required_evidence": ["model_formula", "claim_boundary", "method_gate"],
                },
                "Main Results": {
                    "required_evidence": ["OLS_result", "Ordered_Logit_result"],
                },
            },
            "method_claim_gates": {
                "main_result_gate": {
                    "nobs": 5310,
                    "ols_coef": 0.1658,
                    "ordered_logit_coef": 0.405,
                    "claim_boundary": "positive_conditional_association",
                },
                "supported_claims": [
                    {"claim_type": "conditional_association"},
                    {"claim_type": "ordered_outcome_robustness"},
                ],
                "blocked_method_families": [
                    {"method": "IV", "reason": "当前没有通过相关性与排除性讨论的工具变量。"},
                    {"method": "DID", "reason": "当前没有政策冲击。"},
                ],
                "human_decisions": [
                    "OLS 作为主模型还是 Ordered Logit 作为主模型",
                    "是否把社会资本指数拆成三个分维度",
                ],
            },
            "promotion": {"allowed": False},
        }


if __name__ == "__main__":
    unittest.main()
