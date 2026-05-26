import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalPdfExportPreflightCliTests(unittest.TestCase):
    """BDD: P5-D checks formal manuscript sources before any PDF render."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-pdf-preflight-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_26_blocks_pdf_when_sections_are_still_placeholders(self) -> None:
        source_map_before = (self.project_root / "Results" / "json" / "formal_manuscript_source_map.json").read_text(
            encoding="utf-8"
        )
        section_sources_before = (
            self.project_root / "Submissions" / "formal_package" / "manuscript" / "section_sources.json"
        ).read_text(encoding="utf-8")
        protected_before = self._snapshot_protected_state()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_pdf_export_preflight.json"
        review_path = self.project_root / "Reviews" / "formal_pdf_export_preflight.md"
        tasks_path = (
            self.project_root
            / "Submissions"
            / "formal_package"
            / "reproducibility"
            / "pdf_export_preflight_tasks.json"
        )
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(tasks_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p5.formal_pdf_export_preflight.v1")
        self.assertEqual(report["status"], "blocked_by_source_gaps")
        self.assertFalse(report["can_export_pdf_candidate"])
        self.assertFalse(report["this_command_wrote_final_outputs"])
        self.assertEqual(report["final_outputs_written"], [])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertIn("section_source_placeholders_remaining", report["blocking_reasons"])
        self.assertTrue(any(task["agent"] == "ManuscriptAgent" for task in report["next_review_tasks"]))

        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
        self.assertEqual(tasks["schema_version"], "p5.pdf_export_preflight_tasks.v1")
        self.assertEqual(tasks["source_preflight"], "Results/json/formal_pdf_export_preflight.json")
        self.assertTrue(tasks["tasks"])

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P5-D PDF 导出预检", review_text)
        self.assertIn("blocked_by_source_gaps", review_text)
        self.assertIn("未生成最终 PDF/docx", review_text)

        self.assertEqual(
            (self.project_root / "Results" / "json" / "formal_manuscript_source_map.json").read_text(
                encoding="utf-8"
            ),
            source_map_before,
        )
        self.assertEqual(
            (
                self.project_root
                / "Submissions"
                / "formal_package"
                / "manuscript"
                / "section_sources.json"
            ).read_text(encoding="utf-8"),
            section_sources_before,
        )
        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.pdf").exists())
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())

    def test_bdd_26_allows_pdf_candidate_when_sources_and_evidence_are_ready(self) -> None:
        self._mark_all_sections_ready()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_pdf_export_preflight.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "ready_for_pdf_export_review")
        self.assertTrue(report["can_export_pdf_candidate"])
        self.assertEqual(report["blocking_reasons"], [])
        self.assertEqual(report["next_action"]["id"], "render_pdf_candidate")
        self.assertTrue(all(item["status"] == "passed" for item in report["section_checks"]))
        self.assertTrue(all(item["status"] == "passed" for item in report["evidence_checks"]))

    def test_bdd_26_blocks_when_source_map_is_not_ready(self) -> None:
        source_map_path = self.project_root / "Results" / "json" / "formal_manuscript_source_map.json"
        source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
        source_map["status"] = "blocked_by_manifest"
        source_map["can_prepare_pdf_preflight"] = False
        source_map_path.write_text(json.dumps(source_map, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_pdf_export_preflight.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_source_map")
        self.assertFalse(report["can_export_pdf_candidate"])
        self.assertIn("source_map_not_ready_for_pdf_preflight", report["blocking_reasons"])

    def _run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_pdf_export_preflight.py"),
                "--project-root",
                str(self.project_root),
                "--source-map",
                "Results/json/formal_manuscript_source_map.json",
                "--output-report",
                "Results/json/formal_pdf_export_preflight.json",
                "--output-review",
                "Reviews/formal_pdf_export_preflight.md",
                "--output-tasks",
                "Submissions/formal_package/reproducibility/pdf_export_preflight_tasks.json",
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

    def _mark_all_sections_ready(self) -> None:
        section_sources_path = self.project_root / "Submissions" / "formal_package" / "manuscript" / "section_sources.json"
        payload = json.loads(section_sources_path.read_text(encoding="utf-8"))
        for section in payload["sections"]:
            section["status"] = "source_draft_ready"
            section_path = self.project_root / section["source_path"]
            section_path.write_text(
                (
                    f"# {section['section']}\n\n"
                    f"Status: source_draft_ready\n\n"
                    "This section contains reviewer-facing draft material supported by the required evidence. "
                    "It is ready for PDF export preflight review but still awaits human paper approval.\n"
                ),
                encoding="utf-8",
            )
        section_sources_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        source_map_path = self.project_root / "Results" / "json" / "formal_manuscript_source_map.json"
        source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
        for section in source_map["section_sources"]:
            section["status"] = "source_draft_ready"
        source_map_path.write_text(json.dumps(source_map, ensure_ascii=False, indent=2), encoding="utf-8")

    def _seed_project(self, root: Path) -> None:
        results_dir = root / "Results" / "json"
        state_dir = root / "state" / "product"
        package_root = root / "Submissions" / "formal_package"
        sections_dir = package_root / "manuscript" / "sections"
        for directory in [
            results_dir,
            state_dir,
            sections_dir,
            package_root / "reproducibility",
            root / "Data" / "literature" / "processed",
            root / "Reviews",
        ]:
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

        evidence_files = {
            "Data/literature/processed/verified_bibliography.csv": "title,doi\nPaper,10.0000/example\n",
            "Data/literature/processed/contribution_matrix.md": "| contribution | evidence |\n| --- | --- |\n",
            "Results/json/method_gate_report.json": '{"schema_version":"p4.method_gate.v1"}',
            "Results/json/method_diagnostics_report.json": '{"schema_version":"p4.method_diagnostics.v1"}',
            "Results/json/method_execution_result.json": '{"schema_version":"p2.method_execution.v1"}',
            "Results/json/project_snapshot.json": '{"schema_version":"project.snapshot.v1"}',
            "Results/json/reviewer_scorecard_report.json": '{"schema_version":"p4.reviewer_scorecard.v1"}',
            "Results/json/paper_quality_report.json": '{"schema_version":"p4.paper_quality.v1"}',
            "Results/json/literature_package_report.json": '{"schema_version":"p4.literature_package.v1"}',
            "Results/json/citation_verification_log.json": '{"schema_version":"citation.verification.v1"}',
            "Results/json/domain_notes.json": '{"schema_version":"domain.notes.v1"}',
            "Results/json/verified_context_sources.json": '{"schema_version":"context.sources.v1"}',
            "Results/json/approved_findings.json": '{"schema_version":"approved.findings.v1"}',
            "Results/json/sample_profile.json": '{"schema_version":"sample.profile.v1"}',
            "Results/json/regression_tables.json": '{"schema_version":"regression.tables.v1"}',
            "Results/json/figure_manifest.json": '{"schema_version":"figure.manifest.v1"}',
            "Results/json/robustness_matrix.json": '{"schema_version":"robustness.matrix.v1"}',
            "Results/json/limitations_register.json": '{"schema_version":"limitations.register.v1"}',
        }
        for path_value, content in evidence_files.items():
            path = root / path_value
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        section_specs = [
            ("Abstract", "100 English words or concise Chinese equivalent", "ManuscriptAgent", ["approved_findings", "method_gate_report", "verified_bibliography"]),
            ("Introduction", "1200-1800 English words / 3-4 pages", "ManuscriptAgent", ["research_question", "contribution_matrix", "approved_findings"]),
            ("Literature and Contribution", "1800-3000 English words / 5-7 pages", "LiteratureAgent", ["verified_bibliography", "contribution_matrix", "citation_verification_log"]),
            ("Institutional Background / Theory / Context", "1200-2500 English words / 3-6 pages", "DomainAgent", ["domain_notes", "verified_context_sources"]),
            ("Data and Measurement", "1500-2500 English words / 4-6 pages", "DataAgent", ["variable_role_set", "data_profile", "sample_profile"]),
            ("Empirical Strategy", "1200-2000 English words / 3-5 pages", "MethodAgent", ["design_spec", "method_gate_report", "method_diagnostics_report"]),
            ("Main Results", "1200-2200 English words / 3-5 pages", "ExecutionAgent", ["method_execution_result", "regression_tables", "figure_manifest"]),
            ("Robustness / Mechanisms / Heterogeneity", "1500-3000 English words / 4-7 pages", "MethodAgent", ["robustness_matrix", "method_diagnostics_report"]),
            ("Conclusion", "800-1400 English words / 2-3 pages", "ManuscriptAgent", ["approved_findings", "limitations_register", "reviewer_scorecard_report"]),
            ("References", "verified bibliography", "LiteratureAgent", ["verified_bibliography", "citation_verification_log"]),
        ]
        sections = []
        for index, (name, target_length, agent, evidence) in enumerate(section_specs, start=1):
            source_path = f"Submissions/formal_package/manuscript/sections/{index:02d}-{self._slug(name)}.md"
            (root / source_path).write_text(
                (
                    f"# {name}\n\n"
                    "- Status: `source_placeholder_ready`\n"
                    f"- Agent: `{agent}`\n"
                    f"- Target length: `{target_length}`\n\n"
                    "本文件是正式论文包的章节源占位。下一轮由对应 Agent 读取证据后填充内容。\n"
                ),
                encoding="utf-8",
            )
            sections.append(
                {
                    "order": index,
                    "section": name,
                    "source_path": source_path,
                    "status": "source_placeholder_ready",
                    "target_length": target_length,
                    "agent": agent,
                    "purpose": "test purpose",
                    "evidence_requirements": evidence,
                    "can_write_final_paper": False,
                }
            )

        section_sources_path = package_root / "manuscript" / "section_sources.json"
        section_sources_path.write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_manuscript_section_sources.v1",
                    "source_manifest": "Results/json/formal_paper_package_manifest.json",
                    "draft_layer_only": True,
                    "formal_paper_write_allowed": False,
                    "sections": sections,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (results_dir / "formal_manuscript_source_map.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_manuscript_source_map.v1",
                    "source_manifest": "Results/json/formal_paper_package_manifest.json",
                    "package_root": "Submissions/formal_package",
                    "section_sources_path": "Submissions/formal_package/manuscript/section_sources.json",
                    "status": "formal_manuscript_sources_ready",
                    "can_prepare_pdf_preflight": True,
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
                    "section_sources": sections,
                    "formal_state_guard": {"changed": False, "changed_paths": []},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _slug(value: str) -> str:
        return (
            value.lower()
            .replace(" / ", "-")
            .replace("/", "-")
            .replace(" ", "-")
        )
