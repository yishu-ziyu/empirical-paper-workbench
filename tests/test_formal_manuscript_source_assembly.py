import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalManuscriptSourceAssemblyCliTests(unittest.TestCase):
    """BDD: P5-C assembles formal manuscript source placeholders from the P5-B manifest."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-manuscript-sources-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root)

    def test_bdd_25_assembles_section_sources_without_final_outputs(self) -> None:
        manifest_before = (self.project_root / "Results" / "json" / "formal_paper_package_manifest.json").read_text(
            encoding="utf-8"
        )
        protected_before = self._snapshot_protected_state()

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_manuscript_source_map.json"
        review_path = self.project_root / "Reviews" / "formal_manuscript_source_map.md"
        section_sources_path = self.project_root / "Submissions" / "formal_package" / "manuscript" / "section_sources.json"
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(section_sources_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p5.formal_manuscript_source_map.v1")
        self.assertEqual(report["status"], "formal_manuscript_sources_ready")
        self.assertTrue(report["can_prepare_pdf_preflight"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["this_command_wrote_final_outputs"])
        self.assertEqual(report["final_outputs_written"], [])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["source_manifest"], "Results/json/formal_paper_package_manifest.json")
        self.assertEqual(report["section_sources_path"], "Submissions/formal_package/manuscript/section_sources.json")

        expected_sections = [
            "Abstract",
            "Introduction",
            "Literature and Contribution",
            "Institutional Background / Theory / Context",
            "Data and Measurement",
            "Empirical Strategy",
            "Main Results",
            "Robustness / Mechanisms / Heterogeneity",
            "Conclusion",
            "References",
        ]
        self.assertEqual([item["section"] for item in report["section_sources"]], expected_sections)

        for item in report["section_sources"]:
            self.assertEqual(item["status"], "source_placeholder_ready")
            self.assertTrue(item["target_length"])
            self.assertTrue(item["agent"])
            self.assertTrue(item["evidence_requirements"])
            self.assertTrue((self.project_root / item["source_path"]).exists(), item["source_path"])

        section_sources = json.loads(section_sources_path.read_text(encoding="utf-8"))
        self.assertEqual(section_sources["schema_version"], "p5.formal_manuscript_section_sources.v1")
        self.assertEqual(len(section_sources["sections"]), len(expected_sections))

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P5-C 正式稿源装配清单", review_text)
        self.assertIn("formal_manuscript_sources_ready", review_text)
        self.assertIn("最终 PDF/docx：未生成", review_text)

        self.assertEqual(
            (self.project_root / "Results" / "json" / "formal_paper_package_manifest.json").read_text(
                encoding="utf-8"
            ),
            manifest_before,
        )
        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.pdf").exists())
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "manuscript" / "paper.md").exists())

    def test_bdd_25_blocks_when_formal_package_manifest_is_not_ready(self) -> None:
        manifest_path = self.project_root / "Results" / "json" / "formal_paper_package_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "blocked_by_approval"
        manifest["can_build_package"] = False
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_manuscript_source_map.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_manifest")
        self.assertFalse(report["can_prepare_pdf_preflight"])
        self.assertIn("manifest_not_ready_for_source_assembly", report["blocking_reasons"])
        self.assertFalse(
            (self.project_root / "Submissions" / "formal_package" / "manuscript" / "section_sources.json").exists()
        )

    def test_bdd_25_blocks_when_manifest_package_sections_are_incomplete(self) -> None:
        manifest_path = self.project_root / "Results" / "json" / "formal_paper_package_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["package_sections"] = [
            item for item in manifest["package_sections"] if item["category"] != "method_narrative"
        ]
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        result = self._run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_manuscript_source_map.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_manifest")
        self.assertFalse(report["can_prepare_pdf_preflight"])
        self.assertIn("manifest_missing_package_section:method_narrative", report["blocking_reasons"])
        self.assertFalse(
            (self.project_root / "Submissions" / "formal_package" / "manuscript" / "section_sources.json").exists()
        )

    def _run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_manuscript_source_assembly.py"),
                "--project-root",
                str(self.project_root),
                "--source-manifest",
                "Results/json/formal_paper_package_manifest.json",
                "--output-report",
                "Results/json/formal_manuscript_source_map.json",
                "--output-review",
                "Reviews/formal_manuscript_source_map.md",
                "--package-root",
                "Submissions/formal_package",
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
        state_dir = root / "state" / "product"
        package_root = root / "Submissions" / "formal_package"
        for directory in [
            results_dir,
            state_dir,
            package_root / "manuscript",
            package_root / "literature",
            package_root / "methods",
            package_root / "results",
            package_root / "reproducibility",
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

        package_sections = [
            {
                "order": 1,
                "category": "sections",
                "label": "章节扩写",
                "directory": "Submissions/formal_package/manuscript",
                "approved_by_p5a": True,
                "write_status": "skeleton_only",
                "evidence_level": "local_file",
                "expected_artifacts": ["section_drafts", "section_index"],
            },
            {
                "order": 2,
                "category": "citations",
                "label": "引用与文献",
                "directory": "Submissions/formal_package/literature",
                "approved_by_p5a": True,
                "write_status": "skeleton_only",
                "evidence_level": "local_file",
                "expected_artifacts": ["verified_bibliography", "contribution_matrix"],
            },
            {
                "order": 3,
                "category": "method_narrative",
                "label": "方法叙述",
                "directory": "Submissions/formal_package/methods",
                "approved_by_p5a": True,
                "write_status": "skeleton_only",
                "evidence_level": "local_file",
                "expected_artifacts": ["method_gate_report", "method_diagnostics_report"],
            },
            {
                "order": 4,
                "category": "result_tables",
                "label": "结果表与样本说明",
                "directory": "Submissions/formal_package/results",
                "approved_by_p5a": True,
                "write_status": "skeleton_only",
                "evidence_level": "local_file",
                "expected_artifacts": ["regression_tables", "sample_profile"],
            },
            {
                "order": 5,
                "category": "reproducibility",
                "label": "复现说明",
                "directory": "Submissions/formal_package/reproducibility",
                "approved_by_p5a": True,
                "write_status": "skeleton_only",
                "evidence_level": "local_file",
                "expected_artifacts": ["replication_readme", "artifact_manifest"],
            },
        ]
        (results_dir / "formal_paper_package_manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_paper_package_manifest.v1",
                    "source_approval": "Results/json/formal_writeback_approval.json",
                    "approval_state_path": "state/product/writeback_approvals.json",
                    "package_root": "Submissions/formal_package",
                    "status": "formal_package_manifest_ready",
                    "blocking_reasons": [],
                    "can_build_package": True,
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
                    "final_outputs_written": [],
                    "package_sections": package_sections,
                    "formal_state_guard": {"changed": False, "changed_paths": []},
                    "next_action": {"id": "assemble_formal_manuscript_sources"},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
