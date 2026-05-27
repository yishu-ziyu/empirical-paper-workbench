import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_paper_package_builder import (
    build_cgss_paper_package,
    write_cgss_paper_package,
)


class CgssPaperPackageBuilderTests(unittest.TestCase):
    """BDD: CGSS paper package collects draft paper, evidence, gates, and review artifacts."""

    def test_bdd_63_builds_manifest_for_reviewable_paper_package_with_pdf(self) -> None:
        """行为 63.1：输入齐全时，生成可验收 paper package manifest。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._seed_project(root, include_pdf=True)

            package = build_cgss_paper_package(root)

            self.assertEqual(package["schema_version"], "p6.cgss_paper_package.v1")
            self.assertEqual(package["status"], "needs_human_paper_package_review")
            self.assertFalse(package["formal_writeback_allowed"])
            self.assertEqual(package["rendered_artifact"], "paper.pdf")
            package_files = {item["target"] for item in package["files"]}
            for expected in [
                "paper.md",
                "paper.pdf",
                "results_evidence_package.json",
                "literature_review_packet.json",
                "method_gate.md",
                "reviewer_report.md",
                "revision_task_queue.md",
                "reproducibility_readme.md",
                "manifest.json",
            ]:
                self.assertIn(expected, package_files)

    def test_bdd_63_writes_package_files_without_formal_state(self) -> None:
        """行为 63.2：写入 workspace package，不写正式论文层或 state/product。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._seed_project(root, include_pdf=True)
            package = build_cgss_paper_package(root)

            package_dir = write_cgss_paper_package(root, package)

            self.assertTrue((package_dir / "paper.md").exists())
            self.assertTrue((package_dir / "paper.pdf").exists())
            self.assertTrue((package_dir / "manifest.json").exists())
            self.assertTrue((package_dir / "reproducibility_readme.md").exists())
            self.assertFalse((root / "Manuscripts/sections/paper.md").exists())
            self.assertFalse((root / "state/product/paper_package.json").exists())
            manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "needs_human_paper_package_review")

    def test_bdd_63_uses_preview_html_when_pdf_is_missing(self) -> None:
        """行为 63.3：PDF 缺失但 HTML 存在时，生成 preview.html 替代物。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._seed_project(root, include_pdf=False, include_html=True)

            package = build_cgss_paper_package(root)

            self.assertEqual(package["status"], "needs_human_paper_package_review")
            self.assertEqual(package["rendered_artifact"], "preview.html")
            self.assertIn("pdf_missing_html_preview_used", package["warnings"])

    def test_bdd_63_blocks_when_required_review_artifacts_are_missing(self) -> None:
        """行为 63.4：关键审阅产物缺失时，不生成可验收 package。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._seed_project(root, include_pdf=True)
            (root / "Reviews/cgss_social_capital_happiness_method_gate.md").unlink()

            package = build_cgss_paper_package(root)

            self.assertEqual(package["status"], "blocked_missing_package_inputs")
            self.assertIn("method_gate.md", package["missing_targets"])

    def test_bdd_63_manifest_marks_real_runs_drafts_and_human_review_items(self) -> None:
        """行为 63.5：manifest 明确哪些是真实运行、草稿层、需要人工审阅。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._seed_project(root, include_pdf=True)

            package = build_cgss_paper_package(root)

            self.assertIn("results_evidence_package.json", package["real_run_artifacts"])
            self.assertIn("paper.md", package["draft_layer_artifacts"])
            self.assertIn("method_gate.md", package["human_review_required"])
            self.assertIn("reviewer_report.md", package["human_review_required"])
            self.assertIn("revision_task_queue.md", package["human_review_required"])

    def _seed_project(self, root: Path, *, include_pdf: bool, include_html: bool = False) -> None:
        files = {
            "Manuscripts/generated/cgss_social_capital_happiness_paper_rev1.md": "# Rev1\n\nDraft.",
            "Results/json/cgss_social_capital_happiness_results_evidence_package.json": '{"status":"ready_for_paper_draft_input"}',
            "Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json": '{"status":"needs_human_literature_review_draft_approval"}',
            "Reviews/cgss_social_capital_happiness_method_gate.md": "# Method gate\n",
            "Reviews/cgss_social_capital_happiness_reviewer_report.md": "# Reviewer report\n",
            "Reviews/cgss_social_capital_happiness_revision_task_queue.md": "# Revision queue\n",
        }
        if include_pdf:
            files["Submissions/cgss_social_capital_happiness/paper.pdf"] = "%PDF-1.7\n"
        if include_html:
            files["Submissions/cgss_social_capital_happiness/paper.html"] = "<html><body>Preview</body></html>"
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
