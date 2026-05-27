import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PaperPackageQualityCliTests(unittest.TestCase):
    """BDD: paper package must expose quality gates beyond PDF generation."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="paper-quality-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def run_quality(self, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        args = [
            "python3",
            str(REPO_ROOT / "Program" / "paper_quality.py"),
            "--project-root",
            str(self.project_root),
        ]
        if extra_args:
            args.extend(extra_args)
        return subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True)

    def test_bdd_1_cli_writes_paper_quality_report(self) -> None:
        result = self.run_quality()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "paper_quality_report.json"
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(report["schema_version"], "p4.paper_quality.v1")
        self.assertEqual(report["profile"], "general_working_paper")
        for key in [
            "word_count",
            "format_checks",
            "section_checks",
            "section_length_checks",
            "citation_checks",
            "method_gate_checks",
            "revision_checks",
            "verdict",
            "recommended_next_tasks",
        ]:
            self.assertIn(key, report)

    def test_bdd_2_short_draft_is_flagged_for_expansion(self) -> None:
        result = self.run_quality()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self._read_report()

        self.assertIn("too_thin", report["verdict"])
        self.assertLess(report["word_count"]["main_text_words"], 7000)
        task_ids = {task["id"] for task in report["recommended_next_tasks"]}
        self.assertIn("expand_working_paper_sections", task_ids)
        self.assertIn("Introduction", report["section_checks"]["required_sections"])

    def test_bdd_2_1_present_but_thin_sections_enter_length_gate(self) -> None:
        """行为 2.1：总字数够长也不能掩盖核心章节过薄。"""
        draft = self.project_root / "Manuscripts" / "generated" / "paper_draft.md"
        long_intro = " ".join(["market"] * 7200)
        draft.write_text(
            "# Industrial Robot Adoption and Labor Market Matching\n\n"
            "## Abstract\n\n"
            "This paper studies industrial robot adoption and labor market matching.\n\n"
            "## Introduction\n\n"
            f"{long_intro}\n\n"
            "## Literature and Contribution\n\n"
            "A short placeholder.\n\n"
            "## Institutional Background\n\n"
            "Context is briefly noted.\n\n"
            "## Data and Measurement\n\n"
            "CFPS and robot exposure are mentioned.\n\n"
            "## Empirical Strategy\n\n"
            "The model is stated.\n\n"
            "## Main Results\n\n"
            "Results are summarized.\n\n"
            "## Robustness\n\n"
            "Robustness is pending.\n\n"
            "## Conclusion\n\n"
            "The paper concludes.\n\n"
            "## References\n\n"
            "Acemoglu and Restrepo.\n",
            encoding="utf-8",
        )

        result = self.run_quality()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self._read_report()

        self.assertGreater(report["word_count"]["main_text_words"], 7000)
        self.assertIn("section_length_gate_required", report["verdict"])
        length_checks = report["section_length_checks"]
        self.assertEqual(length_checks["status"], "needs_expansion")
        self.assertIn("Literature and Contribution", length_checks["summary"]["too_short_sections"])
        self.assertIn("Main Results", length_checks["summary"]["too_short_sections"])
        self.assertEqual(length_checks["sections"]["Literature and Contribution"]["status"], "too_short")
        self.assertEqual(length_checks["sections"]["Main Results"]["status"], "too_short")
        task_by_id = {task["id"]: task for task in report["recommended_next_tasks"]}
        self.assertIn("expand_underdeveloped_sections", task_by_id)
        expansion_task = task_by_id["expand_underdeveloped_sections"]
        task_sections = {item["section"] for item in expansion_task["inputs"]}
        self.assertIn("Literature and Contribution", task_sections)
        self.assertIn("Main Results", task_sections)
        packet = expansion_task["section_expansion_packet"]
        self.assertEqual(packet["source"], "section_length_checks")
        self.assertTrue(packet["draft_layer_only"])
        self.assertFalse(packet["formal_writeback_allowed"])
        self.assertEqual(packet["owner_agent"], "ManuscriptAgent")
        self.assertEqual(packet["source_quality_report"], "Results/json/paper_quality_report.json")
        packet_by_section = {item["section"]: item for item in packet["sections"]}
        literature_packet = packet_by_section["Literature and Contribution"]
        self.assertEqual(literature_packet["output_path"], "Manuscripts/sections/literature-and-contribution.md")
        self.assertIn("verified_bibliography.csv", literature_packet["required_evidence"])
        results_packet = packet_by_section["Main Results"]
        self.assertIn("main_regression_table", results_packet["required_evidence"])
        self.assertIn("section_length_checks.status=passed", packet["verification"]["required_before_completion"])
        self.assertIn("no_state_product_writeback", packet["verification"]["required_before_completion"])

    def test_bdd_3_missing_bibliography_becomes_literature_task(self) -> None:
        result = self.run_quality()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self._read_report()

        self.assertIn("needs_literature_review", report["verdict"])
        self.assertEqual(report["citation_checks"]["verified_bibliography"]["status"], "missing")
        task_ids = {task["id"] for task in report["recommended_next_tasks"]}
        self.assertIn("build_literature_package", task_ids)

    def test_bdd_4_method_gate_report_is_required(self) -> None:
        result = self.run_quality()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self._read_report()

        self.assertIn("method_gate_required", report["verdict"])
        self.assertEqual(report["method_gate_checks"]["status"], "missing")
        task_ids = {task["id"] for task in report["recommended_next_tasks"]}
        self.assertIn("run_method_gate", task_ids)

    def test_bdd_5_existing_literature_and_method_gate_are_detected(self) -> None:
        literature_dir = self.project_root / "workspace" / "runs" / "run_test" / "02_literature"
        literature_dir.mkdir(parents=True)
        (literature_dir / "verified_bibliography.csv").write_text(
            "source_id,title,authors,year,venue,verification_status,contribution_role\n"
            "lit1,Robot adoption,Acemoglu,2020,AER,doi_verified,closest_paper\n"
            "lit2,Automation and labor,Autor,2015,JEP,doi_verified,method_reference\n",
            encoding="utf-8",
        )
        (literature_dir / "contribution_matrix.md").write_text(
            "# Contribution Matrix\n\n- lit1: closest paper.\n- lit2: method reference.\n",
            encoding="utf-8",
        )
        method_report = self.project_root / "Results" / "json" / "method_gate_report.json"
        method_report.parent.mkdir(parents=True, exist_ok=True)
        method_report.write_text(
            json.dumps(
                {
                    "schema_version": "p4.method_gate.v1",
                    "method_family": "ols",
                    "gate_status": "yellow",
                    "pre_checks": [{"id": "cluster_level", "status": "missing"}],
                    "diagnostics": [],
                    "required_evidence": ["cluster_standard_errors"],
                    "blocking_items": [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        result = self.run_quality()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self._read_report()

        self.assertEqual(report["citation_checks"]["verified_bibliography"]["status"], "found")
        self.assertEqual(report["citation_checks"]["contribution_matrix"]["status"], "found")
        self.assertEqual(report["method_gate_checks"]["status"], "found")
        self.assertEqual(report["method_gate_checks"]["gate_status"], "yellow")

    def test_bdd_6_pdf_export_manifest_links_paper_quality_report(self) -> None:
        result = self.run_quality()
        self.assertEqual(result.returncode, 0, result.stderr)
        qmd = self.project_root / "Manuscripts" / "generated" / "paper_draft.qmd"
        qmd.write_text("---\ntitle: Test\n---\n\n# Test\n", encoding="utf-8")

        export = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "export_pdf.py"),
                "--project-root",
                str(self.project_root),
                "--source",
                "Manuscripts/generated/paper_draft.qmd",
                "--preflight-only",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        manifest = json.loads((self.project_root / "Submissions" / "pdf_export_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("paper_quality_report", manifest)
        self.assertEqual(manifest["paper_quality_report"]["path"], "Results/json/paper_quality_report.json")
        self.assertIn("too_thin", manifest["paper_quality_report"]["verdict"])
        script = (self.project_root / "Submissions" / "reproduce_pdf_first.sh").read_text(encoding="utf-8")
        self.assertIn("python3 Program/paper_quality.py", script)

    def test_bdd_7_aer_like_profile_blocks_missing_submission_metadata(self) -> None:
        abstract = " ".join(["evidence"] * 101)
        draft = self.project_root / "Manuscripts" / "generated" / "paper_draft.md"
        draft.write_text(
            "# Test Paper\n\n"
            "## Abstract\n\n"
            f"{abstract}\n\n"
            "## Introduction\n\nThis paper studies a research question.\n\n"
            "## Literature and Contribution\n\nThe literature section is being assembled.\n\n"
            "## Institutional Background\n\nThe background section describes context.\n\n"
            "## Data and Measurement\n\nThe data section describes variables.\n\n"
            "## Empirical Strategy\n\nThe strategy section defines the coefficient.\n\n"
            "## Main Results\n\nThe results section explains estimates.\n\n"
            "## Robustness\n\nThe robustness section records checks.\n\n"
            "## Conclusion\n\nThe conclusion summarizes evidence.\n\n"
            "## References\n\nReferences are listed here.\n",
            encoding="utf-8",
        )

        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self._read_report()

        self.assertEqual(report["profile"], "aer_like")
        self.assertIn("format_gate_required", report["verdict"])
        self.assertEqual(report["format_checks"]["abstract"]["status"], "too_long")
        self.assertIn("abstract_over_100_words", report["format_checks"]["hard_errors"])
        self.assertIn("missing_jel", report["format_checks"]["hard_errors"])
        self.assertIn("missing_keywords", report["format_checks"]["hard_errors"])
        self.assertIn("missing_data_availability_statement", report["format_checks"]["hard_errors"])
        task_ids = {task["id"] for task in report["recommended_next_tasks"]}
        self.assertIn("fix_submission_metadata", task_ids)

    def test_bdd_8_builds_expansion_plan_and_structured_manuscript(self) -> None:
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)

        package = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(package.returncode, 0, package.stderr)

        plan_path = self.project_root / "Results" / "json" / "paper_expansion_plan.json"
        manuscript_path = self.project_root / "Manuscripts" / "generated" / "paper_package_draft.md"
        self.assertTrue(plan_path.exists())
        self.assertTrue(manuscript_path.exists())

        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        self.assertEqual(plan["schema_version"], "p4.paper_expansion_plan.v1")
        self.assertEqual(plan["profile"], "aer_like")
        self.assertIn("agent_task_queue", plan)
        self.assertIn("section_expansion_plan", plan)
        task_ids = {task["id"] for task in plan["agent_task_queue"]}
        self.assertIn("build_literature_package", task_ids)
        self.assertIn("run_method_gate", task_ids)
        task_by_id = {task["id"]: task for task in plan["agent_task_queue"]}
        expansion_task = task_by_id["expand_underdeveloped_sections"]
        self.assertIn("section_expansion_packet", expansion_task)
        packet = expansion_task["section_expansion_packet"]
        self.assertEqual(packet["owner_agent"], "ManuscriptAgent")
        self.assertTrue(packet["draft_layer_only"])
        self.assertFalse(packet["formal_writeback_allowed"])
        self.assertIn("no_state_product_writeback", packet["verification"]["required_before_completion"])
        manuscript_section_tasks = plan["manuscript_section_task_packets"]
        self.assertTrue(manuscript_section_tasks)
        packet_by_section = {item["section"]: item for item in manuscript_section_tasks}
        self.assertIn("Main Results", packet_by_section)
        self.assertEqual(packet_by_section["Main Results"]["owner_agent"], "ManuscriptAgent")
        self.assertEqual(packet_by_section["Main Results"]["output_path"], "Manuscripts/sections/main-results.md")
        self.assertIn("main_regression_table", packet_by_section["Main Results"]["required_evidence"])

        manuscript = manuscript_path.read_text(encoding="utf-8")
        for section in [
            "## Abstract",
            "JEL:",
            "Keywords:",
            "## Introduction",
            "## Literature and Contribution",
            "## Institutional Background / Theory / Context",
            "## Data and Measurement",
            "## Empirical Strategy",
            "## Main Results",
            "## Robustness / Mechanisms / Heterogeneity",
            "## Conclusion",
            "## Data and Code Availability",
            "## References",
        ]:
            self.assertIn(section, manuscript)

        quality_on_package = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_quality.py"),
                "--project-root",
                str(self.project_root),
                "--draft",
                "Manuscripts/generated/paper_package_draft.md",
                "--profile",
                "aer_like",
                "--output",
                "Results/json/paper_quality_after_expansion.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(quality_on_package.returncode, 0, quality_on_package.stderr)
        expanded_report = json.loads(
            (self.project_root / "Results" / "json" / "paper_quality_after_expansion.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("missing_sections", expanded_report["verdict"])
        self.assertNotIn("format_gate_required", expanded_report["verdict"])

    def test_bdd_9_builds_llm_supervisor_context_bundle(self) -> None:
        """BDD: paper package CLI must hand research judgment to the LLM Supervisor path."""
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)

        package = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
                "--output-supervisor-context",
                "Results/json/paper_supervisor_context.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(package.returncode, 0, package.stderr)

        context_path = self.project_root / "Results" / "json" / "paper_supervisor_context.json"
        self.assertTrue(context_path.exists())
        context = json.loads(context_path.read_text(encoding="utf-8"))

        self.assertEqual(context["schema_version"], "p4.paper_supervisor_context.v1")
        self.assertEqual(context["supervisor_role"], "research_orchestrator")
        self.assertIn("草案层", context["write_boundary"])
        backend_ids = {backend["id"] for backend in context["execution_backends"]}
        self.assertIn("statspai", backend_ids)
        self.assertIn("python", backend_ids)
        self.assertIn("stata_mcp", backend_ids)
        self.assertTrue(any(source.endswith("paper_quality_report.json") for source in context["context_sources"]))
        self.assertTrue(any(source.endswith("paper_expansion_plan.json") for source in context["context_sources"]))
        self.assertIn("Agent Task Queue", context["task_prompt"])

    def test_bdd_10_export_manifest_next_tasks_enter_supervisor_agent_queue(self) -> None:
        """行为 15：PDF 预检下一轮任务必须进入 Supervisor / Agent 队列。"""
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest_path = self.project_root / "Submissions" / "cfps_robot_pdf_export_manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": "p4.pdf_export_manifest.v1",
                    "export_gate": {
                        "status": "needs_review",
                        "can_export_pdf": False,
                        "blocking_reasons": ["reviewer_scorecard:blocks_export_or_formal_claims"],
                    },
                    "next_review_tasks": [
                        {
                            "id": "add_weak_iv_robust_interval_or_caveat",
                            "source": "reviewer_scorecard",
                            "agent": "MethodAgent",
                            "reason": "弱工具变量稳健推断仍需补证。",
                            "recommended_action": "补充 Anderson-Rubin 置信区间或写明弱工具限制。",
                            "inputs": ["reviewer_scorecard_report.json", "method_diagnostics_report.json"],
                        },
                        {
                            "id": "expand_empirical_strategy",
                            "source": "paper_quality_report",
                            "agent": "ManuscriptAgent",
                            "reason": "Empirical Strategy 仍需扩写。",
                            "inputs": ["paper_quality_report.json"],
                        },
                    ],
                    "agent_team_schedule": {
                        "call_when": "before_pdf_export_preflight",
                        "called_agents": ["ExportAgent", "ReviewerAgent", "VerifierAgent"],
                        "recall_when": "after_pdf_export_manifest_written",
                        "next_call_when": "before_formal_writeback_or_final_export",
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        package = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--source-manifest",
                "Submissions/cfps_robot_pdf_export_manifest.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
                "--output-supervisor-context",
                "Results/json/paper_supervisor_context.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(package.returncode, 0, package.stderr)

        plan = json.loads((self.project_root / "Results" / "json" / "paper_expansion_plan.json").read_text(encoding="utf-8"))
        task_by_id = {task["id"]: task for task in plan["agent_task_queue"]}
        self.assertIn("add_weak_iv_robust_interval_or_caveat", task_by_id)
        weak_iv_task = task_by_id["add_weak_iv_robust_interval_or_caveat"]
        self.assertEqual(weak_iv_task["source"], "pdf_export_manifest")
        self.assertEqual(weak_iv_task["source_artifact"], "Submissions/cfps_robot_pdf_export_manifest.json")
        self.assertEqual(weak_iv_task["agent"], "MethodAgent")
        self.assertEqual(weak_iv_task["status"], "ready_for_supervisor_review")
        self.assertIn("Anderson-Rubin", weak_iv_task["action"])
        self.assertEqual(plan["source_export_manifest"], "Submissions/cfps_robot_pdf_export_manifest.json")
        self.assertEqual(plan["agent_team_schedule"]["call_when"], "before_paper_package_task_merge")
        self.assertIn("ReviewerAgent", plan["agent_team_schedule"]["called_agents"])
        self.assertEqual(plan["agent_team_schedule"]["recall_when"], "after_paper_expansion_plan_and_supervisor_context_written")

        context = json.loads((self.project_root / "Results" / "json" / "paper_supervisor_context.json").read_text(encoding="utf-8"))
        self.assertIn("Submissions/cfps_robot_pdf_export_manifest.json", context["context_sources"])
        context_task_ids = {task["id"] for task in context["agent_task_queue"]}
        self.assertIn("add_weak_iv_robust_interval_or_caveat", context_task_ids)
        self.assertEqual(context["agent_team_schedule"]["next_call_when"], "before_formal_writeback")

    def test_bdd_11_revision_round_consumes_agent_queue_without_formal_writeback(self) -> None:
        """行为 16：Agent 队列必须生成审稿式修订轮次，但不改写正式层。"""
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest_path = self.project_root / "Submissions" / "cfps_robot_pdf_export_manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": "p4.pdf_export_manifest.v1",
                    "export_gate": {"status": "needs_review", "can_export_pdf": False},
                    "next_review_tasks": [
                        {
                            "id": "add_weak_iv_robust_interval_or_caveat",
                            "source": "reviewer_scorecard",
                            "agent": "MethodAgent",
                            "reason": "弱工具变量稳健推断仍需补证。",
                            "recommended_action": "补充 Anderson-Rubin 置信区间或写明弱工具限制。",
                            "inputs": ["reviewer_scorecard_report.json", "method_diagnostics_report.json"],
                        },
                        {
                            "id": "explain_missing_drop_and_analysis_sample",
                            "source": "reviewer_scorecard",
                            "agent": "DataAgent",
                            "reason": "样本流失和分析样本口径需要解释。",
                            "recommended_action": "补充样本筛选流程和 missing drop 说明。",
                            "inputs": ["reviewer_scorecard_report.json", "Results/json/method_diagnostics_report.json"],
                        },
                    ],
                    "agent_team_schedule": {
                        "call_when": "before_pdf_export_preflight",
                        "called_agents": ["ExportAgent", "ReviewerAgent", "VerifierAgent"],
                        "recall_when": "after_pdf_export_manifest_written",
                        "next_call_when": "before_formal_writeback_or_final_export",
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_files = [
            state_dir / "research_question.json",
            state_dir / "variable_roles.json",
            state_dir / "variable_role_set.json",
            state_dir / "design_spec.json",
            state_dir / "run_plan.json",
            state_dir / "supervisor_plan.json",
            state_dir / "agent_task_queue.json",
        ]
        for path in protected_files:
            path.write_text(json.dumps({"path": str(path.relative_to(self.project_root)), "formal": True}), encoding="utf-8")
        protected_before = {path: path.read_text(encoding="utf-8") for path in protected_files}

        package = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--source-manifest",
                "Submissions/cfps_robot_pdf_export_manifest.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
                "--output-supervisor-context",
                "Results/json/paper_supervisor_context.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(package.returncode, 0, package.stderr)

        revision = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_round.py"),
                "--project-root",
                str(self.project_root),
                "--expansion-plan",
                "Results/json/paper_expansion_plan.json",
                "--supervisor-context",
                "Results/json/paper_supervisor_context.json",
                "--output-round",
                "Results/json/paper_revision_round.json",
                "--output-review",
                "Reviews/paper_revision_round.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(revision.returncode, 0, revision.stderr)

        round_path = self.project_root / "Results" / "json" / "paper_revision_round.json"
        review_path = self.project_root / "Reviews" / "paper_revision_round.md"
        self.assertTrue(round_path.exists())
        self.assertTrue(review_path.exists())
        round_doc = json.loads(round_path.read_text(encoding="utf-8"))

        self.assertEqual(round_doc["schema_version"], "p4.paper_revision_round.v1")
        self.assertTrue(round_doc["draft_layer_only"])
        self.assertFalse(round_doc["formal_writeback_allowed"])
        self.assertEqual(round_doc["status"], "ready_for_human_review")
        self.assertEqual(round_doc["agent_team_schedule"]["call_when"], "before_revision_round_build")
        self.assertEqual(round_doc["agent_team_schedule"]["recall_when"], "after_revision_round_manifest_written")
        self.assertEqual(round_doc["agent_team_schedule"]["next_call_when"], "before_revision_task_execution_or_formal_writeback")
        packet_by_agent = {packet["agent"]: packet for packet in round_doc["agent_packets"]}
        self.assertIn("MethodAgent", packet_by_agent)
        self.assertIn("DataAgent", packet_by_agent)
        weak_iv_task = next(
            task
            for task in packet_by_agent["MethodAgent"]["tasks"]
            if task["id"] == "add_weak_iv_robust_interval_or_caveat"
        )
        self.assertEqual(weak_iv_task["status"], "queued_for_revision")
        self.assertEqual(weak_iv_task["source"], "pdf_export_manifest")
        self.assertEqual(weak_iv_task["source_artifact"], "Submissions/cfps_robot_pdf_export_manifest.json")
        self.assertIn("updated_section_or_diagnostic_artifact", weak_iv_task["verification_evidence_required"])
        self.assertFalse(round_doc["formal_state_guard"]["changed"])

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("审稿式修订轮次", review_text)
        self.assertIn("正式层写回：关闭", review_text)
        self.assertIn("MethodAgent", review_text)
        for path, content in protected_before.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_bdd_11_1_revision_round_materializes_manuscript_section_work_orders(self) -> None:
        """行为 16.1：薄弱章节必须变成可打开的 ManuscriptAgent 工单。"""
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        package = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
                "--output-supervisor-context",
                "Results/json/paper_supervisor_context.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(package.returncode, 0, package.stderr)

        revision = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_round.py"),
                "--project-root",
                str(self.project_root),
                "--expansion-plan",
                "Results/json/paper_expansion_plan.json",
                "--supervisor-context",
                "Results/json/paper_supervisor_context.json",
                "--output-round",
                "Results/json/paper_revision_round.json",
                "--output-review",
                "Reviews/paper_revision_round.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(revision.returncode, 0, revision.stderr)

        round_doc = json.loads((self.project_root / "Results" / "json" / "paper_revision_round.json").read_text(encoding="utf-8"))
        work_orders = round_doc["manuscript_section_work_orders"]
        order_by_section = {item["section"]: item for item in work_orders}
        self.assertIn("Main Results", order_by_section)
        main_results = order_by_section["Main Results"]
        self.assertEqual(main_results["agent"], "ManuscriptAgent")
        self.assertTrue(main_results["draft_layer_only"])
        self.assertFalse(main_results["formal_writeback_allowed"])
        self.assertFalse(main_results["can_write_product_state"])
        self.assertEqual(main_results["status"], "ready_for_section_drafting")
        self.assertEqual(main_results["draft_output_path"], "Manuscripts/sections/main-results.md")
        self.assertEqual(
            main_results["work_order_path"],
            "Reviews/agent_packets/manuscriptagent/sections/main-results.md",
        )
        self.assertIn("main_regression_table", main_results["required_evidence"])

        work_order_path = self.project_root / main_results["work_order_path"]
        self.assertTrue(work_order_path.exists())
        work_order = work_order_path.read_text(encoding="utf-8")
        self.assertIn("# Main Results", work_order)
        self.assertIn("Agent: ManuscriptAgent", work_order)
        self.assertIn("Final paper write: false", work_order)
        self.assertIn("main_regression_table", work_order)
        self.assertFalse(round_doc["formal_state_guard"]["changed"])
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)

    def test_bdd_11_2_section_work_orders_create_draft_section_scaffolds(self) -> None:
        """行为 16.2：章节工单必须落成草案层章节入口。"""
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        package = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
                "--output-supervisor-context",
                "Results/json/paper_supervisor_context.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(package.returncode, 0, package.stderr)

        revision = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_round.py"),
                "--project-root",
                str(self.project_root),
                "--expansion-plan",
                "Results/json/paper_expansion_plan.json",
                "--supervisor-context",
                "Results/json/paper_supervisor_context.json",
                "--output-round",
                "Results/json/paper_revision_round.json",
                "--output-review",
                "Reviews/paper_revision_round.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(revision.returncode, 0, revision.stderr)

        scaffold = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_scaffold.py"),
                "--project-root",
                str(self.project_root),
                "--revision-round",
                "Results/json/paper_revision_round.json",
                "--output-report",
                "Results/json/manuscript_section_scaffold_report.json",
                "--output-review",
                "Reviews/manuscript_section_scaffold.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(scaffold.returncode, 0, scaffold.stderr)

        report_path = self.project_root / "Results" / "json" / "manuscript_section_scaffold_report.json"
        review_path = self.project_root / "Reviews" / "manuscript_section_scaffold.md"
        main_results_path = self.project_root / "Manuscripts" / "sections" / "main-results.md"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(main_results_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.manuscript_section_scaffold.v1")
        self.assertEqual(report["status"], "section_scaffolds_ready")
        self.assertTrue(report["draft_layer_only"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertGreaterEqual(report["section_count"], 1)
        scaffold_by_section = {item["section"]: item for item in report["section_scaffolds"]}
        self.assertIn("Main Results", scaffold_by_section)
        self.assertEqual(scaffold_by_section["Main Results"]["path"], "Manuscripts/sections/main-results.md")
        self.assertEqual(scaffold_by_section["Main Results"]["status"], "section_scaffold_ready")

        main_results = main_results_path.read_text(encoding="utf-8")
        self.assertIn("# Main Results", main_results)
        self.assertIn("Status: `section_scaffold_ready`", main_results)
        self.assertIn("Agent: `ManuscriptAgent`", main_results)
        self.assertIn("Final paper write: `false`", main_results)
        self.assertIn("main_regression_table", main_results)
        self.assertIn("## 草案正文", main_results)
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)

    def test_bdd_11_3_section_scaffolds_bind_real_evidence_or_explicit_gaps(self) -> None:
        """行为 16.3：章节入口必须绑定到真实证据或显式缺口。"""
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        results_dir = self.project_root / "Results" / "json"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "regression_tables.json").write_text(
            json.dumps({"tables": [{"id": "baseline", "coefficient": 0.12}]}, ensure_ascii=False),
            encoding="utf-8",
        )
        (results_dir / "approved_findings.json").write_text(
            json.dumps({"findings": [{"id": "f1", "status": "approved", "claim": "机器人暴露影响匹配效率。"}]}, ensure_ascii=False),
            encoding="utf-8",
        )
        (results_dir / "method_execution_result.json").write_text(
            json.dumps({"coefficients": [{"term": "robot_exposure", "estimate": 0.12}]}, ensure_ascii=False),
            encoding="utf-8",
        )

        package = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
                "--output-supervisor-context",
                "Results/json/paper_supervisor_context.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(package.returncode, 0, package.stderr)

        revision = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_round.py"),
                "--project-root",
                str(self.project_root),
                "--expansion-plan",
                "Results/json/paper_expansion_plan.json",
                "--supervisor-context",
                "Results/json/paper_supervisor_context.json",
                "--output-round",
                "Results/json/paper_revision_round.json",
                "--output-review",
                "Reviews/paper_revision_round.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(revision.returncode, 0, revision.stderr)

        scaffold = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_scaffold.py"),
                "--project-root",
                str(self.project_root),
                "--revision-round",
                "Results/json/paper_revision_round.json",
                "--output-report",
                "Results/json/manuscript_section_scaffold_report.json",
                "--output-review",
                "Reviews/manuscript_section_scaffold.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(scaffold.returncode, 0, scaffold.stderr)

        bindings = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_evidence_bindings.py"),
                "--project-root",
                str(self.project_root),
                "--revision-round",
                "Results/json/paper_revision_round.json",
                "--scaffold-report",
                "Results/json/manuscript_section_scaffold_report.json",
                "--output-report",
                "Results/json/manuscript_section_evidence_bindings.json",
                "--output-review",
                "Reviews/manuscript_section_evidence_bindings.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(bindings.returncode, 0, bindings.stderr)

        report_path = self.project_root / "Results" / "json" / "manuscript_section_evidence_bindings.json"
        review_path = self.project_root / "Reviews" / "manuscript_section_evidence_bindings.md"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.manuscript_section_evidence_bindings.v1")
        self.assertTrue(report["draft_layer_only"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertIn(report["status"], ["section_evidence_bindings_ready", "section_evidence_bindings_with_gaps"])

        section_by_name = {item["section"]: item for item in report["sections"]}
        self.assertIn("Main Results", section_by_name)
        main_results = section_by_name["Main Results"]
        self.assertEqual(main_results["status"], "evidence_bound")
        binding_by_id = {item["evidence_id"]: item for item in main_results["bindings"]}
        for evidence_id in ["main_regression_table", "approved_findings", "coefficient_interpretation"]:
            self.assertEqual(binding_by_id[evidence_id]["status"], "bound")
            self.assertTrue(binding_by_id[evidence_id]["primary_path"])
            self.assertEqual(binding_by_id[evidence_id]["evidence_level"], "local_artifact")
            self.assertIn("sha256", binding_by_id[evidence_id])

        self.assertGreaterEqual(report["summary"]["bound"], 3)
        self.assertIn("missing_evidence", report["summary"])
        self.assertEqual(report["agent_team_schedule"]["call_when"], "after_evidence_binding_report_written")
        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("章节证据绑定索引", review_text)
        self.assertIn("Main Results", review_text)
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)

    def test_bdd_11_4_main_results_expansion_consumes_bound_evidence_only(self) -> None:
        """行为 16.4：Main Results 草案扩写只能消费已绑定证据。"""
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        results_dir = self.project_root / "Results" / "json"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "regression_tables.json").write_text(
            json.dumps(
                {
                    "tables": [
                        {
                            "id": "baseline",
                            "dependent_variable": "labor_market_matching",
                            "key_regressor": "robot_exposure",
                            "coefficient": 0.12,
                            "standard_error": 0.04,
                            "p_value": 0.01,
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (results_dir / "approved_findings.json").write_text(
            json.dumps(
                {
                    "findings": [
                        {
                            "id": "f1",
                            "status": "approved",
                            "claim": "机器人暴露提高劳动力市场匹配效率。",
                            "evidence_level": "local_execution",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (results_dir / "method_execution_result.json").write_text(
            json.dumps(
                {
                    "coefficients": [
                        {
                            "term": "robot_exposure",
                            "estimate": 0.12,
                            "standard_error": 0.04,
                            "p_value": 0.01,
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        for command in [
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
                "--output-supervisor-context",
                "Results/json/paper_supervisor_context.json",
            ],
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_round.py"),
                "--project-root",
                str(self.project_root),
                "--expansion-plan",
                "Results/json/paper_expansion_plan.json",
                "--supervisor-context",
                "Results/json/paper_supervisor_context.json",
                "--output-round",
                "Results/json/paper_revision_round.json",
                "--output-review",
                "Reviews/paper_revision_round.md",
            ],
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_scaffold.py"),
                "--project-root",
                str(self.project_root),
                "--revision-round",
                "Results/json/paper_revision_round.json",
                "--output-report",
                "Results/json/manuscript_section_scaffold_report.json",
                "--output-review",
                "Reviews/manuscript_section_scaffold.md",
            ],
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_evidence_bindings.py"),
                "--project-root",
                str(self.project_root),
                "--revision-round",
                "Results/json/paper_revision_round.json",
                "--scaffold-report",
                "Results/json/manuscript_section_scaffold_report.json",
                "--output-report",
                "Results/json/manuscript_section_evidence_bindings.json",
                "--output-review",
                "Reviews/manuscript_section_evidence_bindings.md",
            ],
        ]:
            completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)

        expansion = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_draft_expansion.py"),
                "--project-root",
                str(self.project_root),
                "--evidence-bindings",
                "Results/json/manuscript_section_evidence_bindings.json",
                "--section",
                "Main Results",
                "--output-report",
                "Results/json/manuscript_section_draft_expansion_report.json",
                "--output-review",
                "Reviews/manuscript_section_draft_expansion.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(expansion.returncode, 0, expansion.stderr)

        report_path = self.project_root / "Results" / "json" / "manuscript_section_draft_expansion_report.json"
        review_path = self.project_root / "Reviews" / "manuscript_section_draft_expansion.md"
        main_results_path = self.project_root / "Manuscripts" / "sections" / "main-results.md"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(main_results_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.manuscript_section_draft_expansion.v1")
        self.assertEqual(report["status"], "section_drafts_expanded")
        self.assertTrue(report["draft_layer_only"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["summary"]["expanded"], 1)
        self.assertEqual(report["summary"]["blocked"], 0)
        section_report = report["sections"][0]
        self.assertEqual(section_report["section"], "Main Results")
        self.assertEqual(section_report["status"], "section_draft_expanded")
        self.assertEqual(section_report["path"], "Manuscripts/sections/main-results.md")
        self.assertEqual(
            {item["evidence_id"] for item in section_report["consumed_evidence"]},
            {"main_regression_table", "approved_findings", "coefficient_interpretation"},
        )
        self.assertTrue(all(item.get("sha256") for item in section_report["consumed_evidence"]))
        self.assertEqual(report["agent_team_schedule"]["recall_when"], "after_target_section_draft_expanded")

        main_results = main_results_path.read_text(encoding="utf-8")
        self.assertIn("Status: `section_draft_expanded`", main_results)
        self.assertIn("## 已消费证据", main_results)
        self.assertIn("main_regression_table", main_results)
        self.assertIn("Results/json/regression_tables.json", main_results)
        self.assertIn("机器人暴露提高劳动力市场匹配效率", main_results)
        self.assertIn("sha256", main_results)
        self.assertNotIn("ManuscriptAgent 在这里写入", main_results)
        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("章节草案扩写报告", review_text)
        self.assertIn("Main Results", review_text)
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)

    def test_bdd_11_5_main_results_semantic_review_verifies_bound_claims(self) -> None:
        """行为 16.5：Main Results 语义核验必须反查草案论断和已消费证据。"""
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        results_dir = self.project_root / "Results" / "json"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "regression_tables.json").write_text(
            json.dumps(
                {
                    "tables": [
                        {
                            "id": "baseline",
                            "dependent_variable": "labor_market_matching",
                            "key_regressor": "robot_exposure",
                            "coefficient": 0.12,
                            "standard_error": 0.04,
                            "p_value": 0.01,
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (results_dir / "approved_findings.json").write_text(
            json.dumps(
                {
                    "findings": [
                        {
                            "id": "f1",
                            "status": "approved",
                            "claim": "机器人暴露提高劳动力市场匹配效率。",
                            "evidence_level": "local_execution",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (results_dir / "method_execution_result.json").write_text(
            json.dumps(
                {
                    "coefficients": [
                        {
                            "term": "robot_exposure",
                            "estimate": 0.12,
                            "standard_error": 0.04,
                            "p_value": 0.01,
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        for command in [
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
                "--output-supervisor-context",
                "Results/json/paper_supervisor_context.json",
            ],
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_revision_round.py"),
                "--project-root",
                str(self.project_root),
                "--expansion-plan",
                "Results/json/paper_expansion_plan.json",
                "--supervisor-context",
                "Results/json/paper_supervisor_context.json",
                "--output-round",
                "Results/json/paper_revision_round.json",
                "--output-review",
                "Reviews/paper_revision_round.md",
            ],
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_scaffold.py"),
                "--project-root",
                str(self.project_root),
                "--revision-round",
                "Results/json/paper_revision_round.json",
                "--output-report",
                "Results/json/manuscript_section_scaffold_report.json",
                "--output-review",
                "Reviews/manuscript_section_scaffold.md",
            ],
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_evidence_bindings.py"),
                "--project-root",
                str(self.project_root),
                "--revision-round",
                "Results/json/paper_revision_round.json",
                "--scaffold-report",
                "Results/json/manuscript_section_scaffold_report.json",
                "--output-report",
                "Results/json/manuscript_section_evidence_bindings.json",
                "--output-review",
                "Reviews/manuscript_section_evidence_bindings.md",
            ],
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_draft_expansion.py"),
                "--project-root",
                str(self.project_root),
                "--evidence-bindings",
                "Results/json/manuscript_section_evidence_bindings.json",
                "--section",
                "Main Results",
                "--output-report",
                "Results/json/manuscript_section_draft_expansion_report.json",
                "--output-review",
                "Reviews/manuscript_section_draft_expansion.md",
            ],
        ]:
            completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)

        main_results_path = self.project_root / "Manuscripts" / "sections" / "main-results.md"
        section_before_review = main_results_path.read_text(encoding="utf-8")
        review = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_semantic_review.py"),
                "--project-root",
                str(self.project_root),
                "--draft-expansion-report",
                "Results/json/manuscript_section_draft_expansion_report.json",
                "--section",
                "Main Results",
                "--output-report",
                "Results/json/manuscript_section_semantic_review.json",
                "--output-review",
                "Reviews/manuscript_section_semantic_review.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(review.returncode, 0, review.stderr)

        report_path = self.project_root / "Results" / "json" / "manuscript_section_semantic_review.json"
        review_path = self.project_root / "Reviews" / "manuscript_section_semantic_review.md"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p6.manuscript_section_semantic_review.v1")
        self.assertEqual(report["status"], "semantic_review_passed")
        self.assertTrue(report["draft_layer_only"])
        self.assertFalse(report["formal_writeback_allowed"])
        self.assertFalse(report["formal_state_guard"]["changed"])

        section_review = report["sections"][0]
        self.assertEqual(section_review["section"], "Main Results")
        self.assertEqual(section_review["verdict"], "passed")
        self.assertEqual(section_review["path"], "Manuscripts/sections/main-results.md")
        self.assertEqual(
            {check["id"] for check in section_review["checks"] if check["status"] == "passed"},
            {
                "section_file_exists",
                "section_declares_draft_layer",
                "section_blocks_formal_writeback",
                "consumed_evidence_declared",
                "core_claim_grounded",
            },
        )
        self.assertEqual(section_review["next_action"]["id"], "continue_section_review_or_expand_next_section")
        self.assertEqual(report["agent_team_schedule"]["called_agents"], ["VerifierAgent", "ManuscriptAgent"])
        self.assertEqual(report["agent_team_schedule"]["recall_when"], "after_semantic_review_written")

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("章节语义核验报告", review_text)
        self.assertIn("Main Results", review_text)
        self.assertIn("core_claim_grounded", review_text)
        self.assertEqual(main_results_path.read_text(encoding="utf-8"), section_before_review)
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)

    def test_bdd_11_6_passed_section_review_creates_reviewable_claim_ledger(self) -> None:
        """行为 16.6：通过语义核验的章节必须生成可审阅论断账本。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        section_path = self.project_root / "Manuscripts" / "sections" / "main-results.md"
        section_path.parent.mkdir(parents=True)
        section_path.write_text(
            "\n".join(
                [
                    "# Main Results",
                    "",
                    "- Draft layer: `true`",
                    "- Final paper write: `false`",
                    "",
                    "## 已消费证据",
                    "",
                    "- `main_regression_table` -> `Results/json/regression_tables.json`",
                    "- `approved_findings` -> `Results/json/approved_findings.json`",
                    "- `coefficient_interpretation` -> `Results/json/method_execution_result.json`",
                    "",
                    "## 草案正文",
                    "",
                    "机器人暴露提高劳动力市场匹配效率。",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        results_dir = self.project_root / "Results" / "json"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "approved_findings.json").write_text(
            json.dumps(
                {
                    "findings": [
                        {
                            "id": "f1",
                            "status": "approved",
                            "claim": "机器人暴露提高劳动力市场匹配效率。",
                            "evidence_level": "local_execution",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (results_dir / "manuscript_section_semantic_review.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.manuscript_section_semantic_review.v1",
                    "status": "semantic_review_passed",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                    "sections": [
                        {
                            "section": "Main Results",
                            "path": "Manuscripts/sections/main-results.md",
                            "verdict": "passed",
                            "checks": [{"id": "core_claim_grounded", "status": "passed"}],
                            "consumed_evidence": [
                                {"evidence_id": "main_regression_table", "path": "Results/json/regression_tables.json"},
                                {"evidence_id": "approved_findings", "path": "Results/json/approved_findings.json"},
                                {
                                    "evidence_id": "coefficient_interpretation",
                                    "path": "Results/json/method_execution_result.json",
                                },
                            ],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_claim_ledger.py"),
                "--project-root",
                str(self.project_root),
                "--semantic-review",
                "Results/json/manuscript_section_semantic_review.json",
                "--section",
                "Main Results",
                "--output-ledger",
                "Results/json/manuscript_section_claim_ledger.json",
                "--output-review",
                "Reviews/manuscript_section_claim_ledger.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

        ledger_path = results_dir / "manuscript_section_claim_ledger.json"
        review_path = self.project_root / "Reviews" / "manuscript_section_claim_ledger.md"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(ledger["schema_version"], "p6.manuscript_section_claim_ledger.v1")
        self.assertEqual(ledger["status"], "claim_ledger_ready")
        self.assertTrue(ledger["draft_layer_only"])
        self.assertFalse(ledger["formal_writeback_allowed"])
        self.assertFalse(ledger["formal_state_guard"]["changed"])
        self.assertEqual(ledger["summary"], {"sections": 1, "claims": 1, "needs_revision": 0})

        claim = ledger["sections"][0]["claims"][0]
        self.assertEqual(claim["claim_text"], "机器人暴露提高劳动力市场匹配效率。")
        self.assertEqual(claim["section"], "Main Results")
        self.assertEqual(claim["source_finding_id"], "f1")
        self.assertEqual(
            claim["bound_evidence_ids"],
            ["approved_findings", "coefficient_interpretation", "main_regression_table"],
        )
        self.assertEqual(claim["review_status"], "ready_for_next_review")
        self.assertEqual(claim["next_action"]["id"], "keep_claim_in_draft_review_queue")
        self.assertEqual(ledger["agent_team_schedule"]["called_agents"], ["VerifierAgent", "ManuscriptAgent"])

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("章节论断账本", review_text)
        self.assertIn("机器人暴露提高劳动力市场匹配效率", review_text)
        self.assertEqual(section_path.read_text(encoding="utf-8").count("机器人暴露"), 1)
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)

    def test_bdd_11_7_claim_ledger_never_fabricates_missing_approved_claim_text(self) -> None:
        """行为 16.7：缺少已审批论断文本时不得编造 claim。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        section_path = self.project_root / "Manuscripts" / "sections" / "main-results.md"
        section_path.parent.mkdir(parents=True)
        section_path.write_text(
            "\n".join(
                [
                    "# Main Results",
                    "",
                    "- Draft layer: `true`",
                    "- Final paper write: `false`",
                    "",
                    "## 已消费证据",
                    "",
                    "- `main_regression_table` -> `Results/json/regression_tables.json`",
                    "- `approved_findings` -> `Results/json/approved_findings.json`",
                    "- `coefficient_interpretation` -> `Results/json/method_execution_result.json`",
                    "",
                    "## 草案正文",
                    "",
                    "主表结果显示机器人暴露和工资之间存在正向关系。",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        section_before = section_path.read_text(encoding="utf-8")

        results_dir = self.project_root / "Results" / "json"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "approved_findings.json").write_text(
            json.dumps(
                {
                    "findings": [
                        {
                            "finding_id": "finding_without_claim",
                            "review_status": "approved",
                            "claim": None,
                            "evidence_level": "local_file",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (results_dir / "manuscript_section_semantic_review.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.manuscript_section_semantic_review.v1",
                    "status": "semantic_review_passed",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                    "sections": [
                        {
                            "section": "Main Results",
                            "path": "Manuscripts/sections/main-results.md",
                            "verdict": "passed",
                            "checks": [{"id": "core_claim_grounded", "status": "passed"}],
                            "consumed_evidence": [
                                {"evidence_id": "main_regression_table", "path": "Results/json/regression_tables.json"},
                                {"evidence_id": "approved_findings", "path": "Results/json/approved_findings.json"},
                                {
                                    "evidence_id": "coefficient_interpretation",
                                    "path": "Results/json/method_execution_result.json",
                                },
                            ],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_claim_ledger.py"),
                "--project-root",
                str(self.project_root),
                "--semantic-review",
                "Results/json/manuscript_section_semantic_review.json",
                "--section",
                "Main Results",
                "--output-ledger",
                "Results/json/manuscript_section_claim_ledger.json",
                "--output-review",
                "Reviews/manuscript_section_claim_ledger.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

        ledger = json.loads((results_dir / "manuscript_section_claim_ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["status"], "claim_ledger_needs_revision")
        self.assertEqual(ledger["summary"], {"sections": 1, "claims": 0, "needs_revision": 1})
        section = ledger["sections"][0]
        self.assertEqual(section["claims"], [])
        self.assertEqual(section["missing_reasons"], ["no_approved_finding_claim_detected_in_section"])
        self.assertFalse(ledger["formal_writeback_allowed"])
        self.assertFalse(ledger["formal_state_guard"]["changed"])
        self.assertEqual(section_path.read_text(encoding="utf-8"), section_before)
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)

    def test_bdd_11_8_missing_claim_text_generates_reviewable_claim_proposal(self) -> None:
        """行为 16.8：缺少已审批论断文本时必须生成草案论断提案。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        section_path = self.project_root / "Manuscripts" / "sections" / "main-results.md"
        section_path.parent.mkdir(parents=True)
        section_path.write_text(
            "\n".join(
                [
                    "# Main Results",
                    "",
                    "- Draft layer: `true`",
                    "- Final paper write: `false`",
                    "",
                    "## 已消费证据",
                    "",
                    "- `main_regression_table` -> `Results/json/regression_tables.json`",
                    "- `approved_findings` -> `Results/json/approved_findings.json`",
                    "- `coefficient_interpretation` -> `Results/json/method_execution_result.json`",
                    "",
                    "## 草案正文",
                    "",
                    "主表结果显示机器人暴露和工资之间存在正向关系。",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        section_before = section_path.read_text(encoding="utf-8")

        results_dir = self.project_root / "Results" / "json"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "approved_findings.json").write_text(
            json.dumps(
                {
                    "findings": [
                        {
                            "finding_id": "finding_without_claim",
                            "review_status": "approved",
                            "claim": None,
                            "evidence_level": "local_file",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (results_dir / "regression_tables.json").write_text(
            json.dumps(
                {
                    "tables": [
                        {
                            "table_id": "regression_table_1",
                            "task_id": "robot_wage_iv_baseline",
                            "method_id": "iv",
                            "estimator": "iv",
                            "dependent_var": "ln_wage",
                            "treatment": "ln_robot",
                            "nobs": 34315,
                            "coefficient_rows": [
                                {
                                    "term": "ln_robot",
                                    "coefficient": 0.199384322747,
                                    "standard_error": 0.0793435494782,
                                    "p_value": 0.0119807291718,
                                }
                            ],
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (results_dir / "manuscript_section_semantic_review.json").write_text(
            json.dumps(
                {
                    "schema_version": "p6.manuscript_section_semantic_review.v1",
                    "status": "semantic_review_passed",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                    "sections": [
                        {
                            "section": "Main Results",
                            "path": "Manuscripts/sections/main-results.md",
                            "verdict": "passed",
                            "checks": [{"id": "core_claim_grounded", "status": "passed"}],
                            "consumed_evidence": [
                                {
                                    "evidence_id": "main_regression_table",
                                    "path": "Results/json/regression_tables.json",
                                },
                                {"evidence_id": "approved_findings", "path": "Results/json/approved_findings.json"},
                                {
                                    "evidence_id": "coefficient_interpretation",
                                    "path": "Results/json/method_execution_result.json",
                                },
                            ],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_section_claim_ledger.py"),
                "--project-root",
                str(self.project_root),
                "--semantic-review",
                "Results/json/manuscript_section_semantic_review.json",
                "--section",
                "Main Results",
                "--output-ledger",
                "Results/json/manuscript_section_claim_ledger.json",
                "--output-review",
                "Reviews/manuscript_section_claim_ledger.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

        ledger = json.loads((results_dir / "manuscript_section_claim_ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["status"], "claim_ledger_needs_revision")
        self.assertEqual(ledger["summary"], {"sections": 1, "claims": 0, "claim_proposals": 1, "needs_revision": 1})
        section = ledger["sections"][0]
        self.assertEqual(section["claims"], [])
        proposal = section["claim_proposals"][0]
        self.assertEqual(proposal["review_status"], "needs_human_review")
        self.assertEqual(proposal["source_finding_id"], "finding_without_claim")
        self.assertEqual(proposal["source_table_id"], "regression_table_1")
        self.assertEqual(proposal["coefficient"], 0.199384322747)
        self.assertEqual(proposal["standard_error"], 0.0793435494782)
        self.assertEqual(proposal["p_value"], 0.0119807291718)
        self.assertEqual(proposal["nobs"], 34315)
        self.assertIn("ln_robot", proposal["proposed_claim_text"])
        self.assertIn("ln_wage", proposal["proposed_claim_text"])
        self.assertEqual(
            proposal["bound_evidence_ids"],
            ["approved_findings", "coefficient_interpretation", "main_regression_table"],
        )
        self.assertEqual(proposal["next_action"]["id"], "review_claim_proposal_before_promotion")
        self.assertFalse(ledger["formal_writeback_allowed"])
        self.assertFalse(ledger["formal_state_guard"]["changed"])
        self.assertEqual(section_path.read_text(encoding="utf-8"), section_before)
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)

    def test_bdd_11_9_claim_proposal_review_records_human_decision_without_promotion(self) -> None:
        """行为 16.9：草案论断提案必须经过显式人工审阅才能进入下一步。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        section_path = self.project_root / "Manuscripts" / "sections" / "main-results.md"
        section_path.parent.mkdir(parents=True)
        section_path.write_text("# Main Results\n\n草案正文。\n", encoding="utf-8")
        section_before = section_path.read_text(encoding="utf-8")

        results_dir = self.project_root / "Results" / "json"
        results_dir.mkdir(parents=True, exist_ok=True)
        approved_findings_path = results_dir / "approved_findings.json"
        approved_findings_path.write_text(
            json.dumps({"findings": [{"finding_id": "finding_without_claim", "review_status": "approved"}]}),
            encoding="utf-8",
        )
        approved_findings_before = approved_findings_path.read_text(encoding="utf-8")

        proposal_id = "main-results::finding_without_claim::claim_proposal"
        claim_ledger_path = results_dir / "manuscript_section_claim_ledger.json"
        claim_ledger_path.write_text(
            json.dumps(
                {
                    "schema_version": "p6.manuscript_section_claim_ledger.v1",
                    "status": "claim_ledger_needs_revision",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                    "summary": {"sections": 1, "claims": 0, "claim_proposals": 1, "needs_revision": 1},
                    "sections": [
                        {
                            "section": "Main Results",
                            "path": "Manuscripts/sections/main-results.md",
                            "status": "needs_revision",
                            "claims": [],
                            "claim_proposals": [
                                {
                                    "proposal_id": proposal_id,
                                    "section": "Main Results",
                                    "proposed_claim_text": "草案提案：在 iv 规格中，ln_robot 对 ln_wage 的估计系数为 0.199。",
                                    "source_finding_id": "finding_without_claim",
                                    "source_table_id": "regression_table_1",
                                    "coefficient": 0.199384322747,
                                    "standard_error": 0.0793435494782,
                                    "p_value": 0.0119807291718,
                                    "nobs": 34315,
                                    "bound_evidence_ids": [
                                        "approved_findings",
                                        "coefficient_interpretation",
                                        "main_regression_table",
                                    ],
                                    "review_status": "needs_human_review",
                                }
                            ],
                            "missing_reasons": ["no_approved_finding_claim_detected_in_section"],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_claim_proposal_review.py"),
                "--project-root",
                str(self.project_root),
                "--claim-ledger",
                "Results/json/manuscript_section_claim_ledger.json",
                "--proposal-id",
                proposal_id,
                "--action",
                "approve",
                "--reviewer",
                "mahaoxuan",
                "--note",
                "同意作为下一步正式论断写回候选。",
                "--output-report",
                "Results/json/manuscript_claim_proposal_review.json",
                "--output-review",
                "Reviews/manuscript_claim_proposal_review.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

        review = json.loads((results_dir / "manuscript_claim_proposal_review.json").read_text(encoding="utf-8"))
        self.assertEqual(review["status"], "claim_proposal_approved_for_promotion")
        self.assertTrue(review["promotion_allowed"])
        self.assertFalse(review["promoted_to_claims"])
        self.assertFalse(review["formal_writeback_allowed"])
        decision = review["human_review"]
        self.assertEqual(decision["action"], "approve")
        self.assertEqual(decision["reviewer"], "mahaoxuan")
        self.assertEqual(decision["note"], "同意作为下一步正式论断写回候选。")
        self.assertEqual(decision["proposal_id"], proposal_id)
        self.assertEqual(review["proposal"]["source_finding_id"], "finding_without_claim")
        self.assertEqual(review["proposal"]["source_table_id"], "regression_table_1")
        self.assertIn("ln_robot", review["proposal"]["proposed_claim_text"])
        self.assertEqual(review["next_action"]["id"], "promote_reviewed_proposal_in_separate_node")
        self.assertFalse(review["formal_state_guard"]["changed"])
        self.assertEqual(section_path.read_text(encoding="utf-8"), section_before)
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)
        self.assertEqual(approved_findings_path.read_text(encoding="utf-8"), approved_findings_before)

    def test_bdd_11_10_approved_claim_proposal_creates_patch_without_formal_writeback(self) -> None:
        """行为 16.10：已批准草案论断只能先生成正式层补丁提案。"""
        state_dir = self.project_root / "state" / "product"
        state_dir.mkdir(parents=True)
        protected_path = state_dir / "agent_task_queue.json"
        protected_path.write_text(json.dumps({"formal": True, "queue": []}), encoding="utf-8")
        protected_before = protected_path.read_text(encoding="utf-8")

        section_path = self.project_root / "Manuscripts" / "sections" / "main-results.md"
        section_path.parent.mkdir(parents=True)
        section_path.write_text("# Main Results\n\n草案正文。\n", encoding="utf-8")
        section_before = section_path.read_text(encoding="utf-8")

        results_dir = self.project_root / "Results" / "json"
        results_dir.mkdir(parents=True, exist_ok=True)
        approved_findings_path = results_dir / "approved_findings.json"
        approved_findings_path.write_text(
            json.dumps({"findings": [{"finding_id": "finding_without_claim", "review_status": "approved"}]}),
            encoding="utf-8",
        )
        approved_findings_before = approved_findings_path.read_text(encoding="utf-8")

        proposal_id = "main-results::finding_without_claim::claim_proposal"
        review_path = results_dir / "manuscript_claim_proposal_review.json"
        review_path.write_text(
            json.dumps(
                {
                    "schema_version": "p6.manuscript_claim_proposal_review.v1",
                    "status": "claim_proposal_approved_for_promotion",
                    "promotion_allowed": True,
                    "promoted_to_claims": False,
                    "formal_writeback_allowed": False,
                    "source_claim_ledger": "Results/json/manuscript_section_claim_ledger.json",
                    "proposal": {
                        "proposal_id": proposal_id,
                        "section": "Main Results",
                        "proposed_claim_text": "草案提案：在 iv 规格中，ln_robot 对 ln_wage 的估计系数为 0.199。",
                        "source_finding_id": "finding_without_claim",
                        "source_table_id": "regression_table_1",
                        "coefficient": 0.199384322747,
                        "standard_error": 0.0793435494782,
                        "p_value": 0.0119807291718,
                        "nobs": 34315,
                        "review_status": "needs_human_review",
                    },
                    "human_review": {
                        "proposal_id": proposal_id,
                        "action": "approve",
                        "reviewer": "mahaoxuan",
                        "note": "同意作为下一步正式论断写回候选。",
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "manuscript_claim_promotion_patch.py"),
                "--project-root",
                str(self.project_root),
                "--review-report",
                "Results/json/manuscript_claim_proposal_review.json",
                "--target-approved-findings",
                "Results/json/approved_findings.json",
                "--output-report",
                "Results/json/manuscript_claim_promotion_patch.json",
                "--output-review",
                "Reviews/manuscript_claim_promotion_patch.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

        patch = json.loads((results_dir / "manuscript_claim_promotion_patch.json").read_text(encoding="utf-8"))
        self.assertEqual(patch["status"], "claim_promotion_patch_ready")
        self.assertTrue(patch["ready_for_apply"])
        self.assertFalse(patch["applied"])
        self.assertFalse(patch["formal_writeback_allowed"])
        operation = patch["patch_operations"][0]
        self.assertEqual(operation["type"], "add_claim_to_approved_finding")
        self.assertEqual(operation["target_path"], "Results/json/approved_findings.json")
        self.assertEqual(operation["source_finding_id"], "finding_without_claim")
        self.assertEqual(operation["source_table_id"], "regression_table_1")
        self.assertEqual(operation["proposal_id"], proposal_id)
        self.assertIn("ln_robot", operation["claim_text"])
        self.assertEqual(patch["human_review_evidence"]["action"], "approve")
        self.assertFalse(patch["formal_state_guard"]["changed"])
        self.assertEqual(patch["next_action"]["id"], "apply_claim_promotion_patch_after_human_confirm")
        self.assertEqual(section_path.read_text(encoding="utf-8"), section_before)
        self.assertEqual(protected_path.read_text(encoding="utf-8"), protected_before)
        self.assertEqual(approved_findings_path.read_text(encoding="utf-8"), approved_findings_before)

    def test_bdd_19_gate_producer_consumes_recompute_without_requeueing_evidence_ready_tasks(self) -> None:
        """行为 19：下一轮任务生产器必须消费质量门复核账本。"""
        result = self.run_quality(["--profile", "aer_like"])
        self.assertEqual(result.returncode, 0, result.stderr)

        manifest_path = self.project_root / "Submissions" / "cfps_robot_pdf_export_manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": "p4.pdf_export_manifest.v1",
                    "export_gate": {"status": "needs_review", "can_export_pdf": False},
                    "next_review_tasks": [
                        {
                            "id": "run_method_gate",
                            "source": "paper_quality_report",
                            "agent": "MethodAgent",
                            "reason": "方法门仍被旧 manifest 引用。",
                            "recommended_action": "重跑方法门。",
                            "inputs": ["paper_quality_report.json"],
                        },
                        {
                            "id": "build_literature_package",
                            "source": "paper_quality_report",
                            "agent": "LiteratureAgent",
                            "reason": "文献包仍需人工补证。",
                            "recommended_action": "补齐 verified bibliography 和 contribution matrix。",
                            "inputs": ["paper_quality_report.json"],
                        },
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        recompute_path = self.project_root / "Results" / "json" / "paper_revision_gate_recompute.json"
        recompute_path.parent.mkdir(parents=True, exist_ok=True)
        recompute_path.write_text(
            json.dumps(
                {
                    "schema_version": "p4.paper_revision_gate_recompute.v1",
                    "draft_layer_only": True,
                    "formal_writeback_allowed": False,
                    "status": "needs_revision_work",
                    "summary": {"cleared": 0, "still_blocking": 1, "manual_review_required": 1},
                    "task_results": [
                        {
                            "task_id": "run_method_gate",
                            "previous_status": "evidence_packet_ready",
                            "status": "still_blocking",
                            "blocking_sources": ["paper_quality_report", "pdf_export_manifest"],
                            "missing_evidence": [],
                        },
                        {
                            "task_id": "build_literature_package",
                            "previous_status": "needs_manual_review",
                            "status": "manual_review_required",
                            "blocking_sources": ["paper_quality_report", "pdf_export_manifest"],
                            "missing_evidence": ["verified_bibliography.csv", "contribution_matrix.md"],
                        },
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        recompute_before = recompute_path.read_text(encoding="utf-8")

        package = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_package.py"),
                "--project-root",
                str(self.project_root),
                "--quality-report",
                "Results/json/paper_quality_report.json",
                "--source-manifest",
                "Submissions/cfps_robot_pdf_export_manifest.json",
                "--output-plan",
                "Results/json/paper_expansion_plan.json",
                "--output-manuscript",
                "Manuscripts/generated/paper_package_draft.md",
                "--output-supervisor-context",
                "Results/json/paper_supervisor_context.json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(package.returncode, 0, package.stderr)

        plan = json.loads((self.project_root / "Results" / "json" / "paper_expansion_plan.json").read_text(encoding="utf-8"))
        task_by_id = {task["id"]: task for task in plan["agent_task_queue"]}
        self.assertNotIn("run_method_gate", task_by_id)
        self.assertIn("build_literature_package", task_by_id)
        self.assertEqual(task_by_id["build_literature_package"]["source"], "paper_revision_gate_recompute")
        self.assertEqual(task_by_id["build_literature_package"]["status"], "manual_review_required")

        context = json.loads((self.project_root / "Results" / "json" / "paper_supervisor_context.json").read_text(encoding="utf-8"))
        self.assertIn("Results/json/paper_revision_gate_recompute.json", context["context_sources"])
        self.assertEqual(recompute_path.read_text(encoding="utf-8"), recompute_before)

    def _read_report(self) -> dict:
        return json.loads((self.project_root / "Results" / "json" / "paper_quality_report.json").read_text(encoding="utf-8"))

    def _seed_project(self, root: Path) -> None:
        draft_dir = root / "Manuscripts" / "generated"
        draft_dir.mkdir(parents=True)
        (draft_dir / "paper_draft.md").write_text(
            "# Industrial Robot Adoption and Labor Market Matching\n\n"
            "## Abstract\n\nThis paper studies industrial robot adoption and labor market matching.\n\n"
            "## Introduction\n\nRobots may change matching efficiency in local labor markets.\n\n"
            "## Data and Measurement\n\nWe use a local CFPS robot dataset and define wages, robot exposure, education, and experience.\n\n"
            "## Empirical Strategy\n\nThe baseline specification uses OLS with controls.\n\n"
            "## Main Results\n\nThe first run produces baseline estimates.\n\n"
            "## Conclusion\n\nThe next version expands literature, method diagnostics, and robustness.\n",
            encoding="utf-8",
        )
        (root / "Results" / "json").mkdir(parents=True)
        (root / "Results" / "index.json").write_text(
            json.dumps({"artifacts": [{"path": "Manuscripts/generated/paper_draft.md", "exists": True}]}),
            encoding="utf-8",
        )
