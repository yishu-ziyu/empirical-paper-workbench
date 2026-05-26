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
