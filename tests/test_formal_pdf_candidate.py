import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FormalPdfCandidateCliTests(unittest.TestCase):
    """BDD: P5-E3 renders a review-layer PDF candidate from ready formal sources."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="formal-pdf-candidate-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_project(self.project_root, preflight_ready=True)

    def test_bdd_32_writes_qmd_candidate_and_review_report_without_formal_writeback(self) -> None:
        protected_before = self._snapshot_protected_state()

        result = self._run_cli("--render-mode", "source-only")
        self.assertEqual(result.returncode, 0, result.stderr)

        report_path = self.project_root / "Results" / "json" / "formal_pdf_candidate_report.json"
        review_path = self.project_root / "Reviews" / "formal_pdf_candidate.md"
        qmd_path = self.project_root / "Submissions" / "formal_package" / "manuscript" / "paper_candidate.qmd"
        script_path = (
            self.project_root
            / "Submissions"
            / "formal_package"
            / "reproducibility"
            / "render_pdf_candidate.sh"
        )
        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertTrue(qmd_path.exists())
        self.assertTrue(script_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], "p5.formal_pdf_candidate.v1")
        self.assertEqual(report["status"], "candidate_source_ready")
        self.assertTrue(report["candidate_layer_only"])
        self.assertFalse(report["this_command_wrote_formal_state"])
        self.assertFalse(report["this_command_wrote_final_outputs"])
        self.assertFalse(report["final_pdf_approved"])
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(report["render_mode"], "source-only")
        self.assertEqual(report["section_count"], 2)

        qmd_text = qmd_path.read_text(encoding="utf-8")
        self.assertIn("format:", qmd_text)
        self.assertIn("# Abstract", qmd_text)
        self.assertIn("# Introduction", qmd_text)
        self.assertIn("evidence-bound abstract draft", qmd_text)
        self.assertNotIn("source_placeholder_ready", qmd_text)
        self.assertNotIn("章节源占位", qmd_text)

        review_text = review_path.read_text(encoding="utf-8")
        self.assertIn("P5-E3 PDF 候选稿", review_text)
        self.assertIn("candidate_source_ready", review_text)
        self.assertIn("人工审阅", review_text)
        self.assertEqual(self._snapshot_protected_state(), protected_before)
        self.assertFalse((self.project_root / "Submissions" / "formal_package" / "paper.docx").exists())

    def test_bdd_32_blocks_when_pdf_preflight_is_not_ready(self) -> None:
        preflight_path = self.project_root / "Results" / "json" / "formal_pdf_export_preflight.json"
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        preflight["can_export_pdf_candidate"] = False
        preflight["status"] = "blocked_by_source_gaps"
        preflight["blocking_reasons"] = ["section_source_placeholders_remaining"]
        preflight_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
        protected_before = self._snapshot_protected_state()

        result = self._run_cli("--render-mode", "source-only")
        self.assertEqual(result.returncode, 2, result.stderr)

        report = json.loads(
            (self.project_root / "Results" / "json" / "formal_pdf_candidate_report.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["status"], "blocked_by_pdf_preflight")
        self.assertFalse(report["can_render_pdf_candidate"])
        self.assertIn("section_source_placeholders_remaining", report["blocking_reasons"])
        self.assertFalse(
            (self.project_root / "Submissions" / "formal_package" / "manuscript" / "paper_candidate.qmd").exists()
        )
        self.assertFalse(report["formal_state_guard"]["changed"])
        self.assertEqual(self._snapshot_protected_state(), protected_before)

    def _run_cli(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "formal_pdf_candidate.py"),
                "--project-root",
                str(self.project_root),
                "--preflight-report",
                "Results/json/formal_pdf_export_preflight.json",
                "--source-map",
                "Results/json/formal_manuscript_source_map.json",
                "--output-report",
                "Results/json/formal_pdf_candidate_report.json",
                "--output-review",
                "Reviews/formal_pdf_candidate.md",
                "--output-qmd",
                "Submissions/formal_package/manuscript/paper_candidate.qmd",
                "--output-pdf",
                "Submissions/formal_package/paper_candidate.pdf",
                "--reproduce-script",
                "Submissions/formal_package/reproducibility/render_pdf_candidate.sh",
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

    def _seed_project(self, root: Path, *, preflight_ready: bool) -> None:
        state_dir = root / "state" / "product"
        results_dir = root / "Results" / "json"
        sections_dir = root / "Submissions" / "formal_package" / "manuscript" / "sections"
        for directory in [
            state_dir,
            results_dir,
            sections_dir,
            root / "Reviews",
            root / "Submissions" / "formal_package" / "reproducibility",
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

        sections = [
            {
                "order": 1,
                "section": "Abstract",
                "source_path": "Submissions/formal_package/manuscript/sections/01-abstract.md",
                "status": "source_draft_ready",
                "target_length": "100 English words or concise Chinese equivalent",
                "agent": "ManuscriptAgent",
                "evidence_requirements": ["approved_findings", "method_gate_report"],
            },
            {
                "order": 2,
                "section": "Introduction",
                "source_path": "Submissions/formal_package/manuscript/sections/02-introduction.md",
                "status": "source_draft_ready",
                "target_length": "1200-1800 English words / 3-4 pages",
                "agent": "ManuscriptAgent",
                "evidence_requirements": ["research_question", "contribution_matrix"],
            },
        ]
        (sections_dir / "01-abstract.md").write_text(
            "# Abstract\n\nThis is an evidence-bound abstract draft for PDF candidate review.\n",
            encoding="utf-8",
        )
        (sections_dir / "02-introduction.md").write_text(
            "# Introduction\n\nThis introduction is sourced from the formal manuscript draft layer.\n",
            encoding="utf-8",
        )
        section_sources_path = root / "Submissions" / "formal_package" / "manuscript" / "section_sources.json"
        section_sources_path.write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_manuscript_section_sources.v1",
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
                    "section_sources_path": "Submissions/formal_package/manuscript/section_sources.json",
                    "status": "formal_manuscript_sources_ready",
                    "can_prepare_pdf_preflight": True,
                    "section_sources": sections,
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (results_dir / "formal_pdf_export_preflight.json").write_text(
            json.dumps(
                {
                    "schema_version": "p5.formal_pdf_export_preflight.v1",
                    "status": "ready_for_pdf_export_review" if preflight_ready else "blocked_by_source_gaps",
                    "can_export_pdf_candidate": preflight_ready,
                    "blocking_reasons": [] if preflight_ready else ["section_source_placeholders_remaining"],
                    "source_map": "Results/json/formal_manuscript_source_map.json",
                    "section_sources_path": "Submissions/formal_package/manuscript/section_sources.json",
                    "this_command_wrote_formal_state": False,
                    "this_command_wrote_final_outputs": False,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
