import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.cgss_pdf_preflight import (
    build_cgss_pdf_preflight,
    write_cgss_pdf_preflight_outputs,
)


class CgssPdfPreflightTests(unittest.TestCase):
    """BDD: a reviewable CGSS exploratory paper can produce a local PDF preflight artifact."""

    def test_bdd_60_renders_pdf_preflight_from_exploratory_paper(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            paper_path = project_root / "Manuscripts/generated/cgss_social_capital_happiness_paper.md"
            paper_path.parent.mkdir(parents=True)
            paper_path.write_text("# 论文\n\n## 摘要\n\n这是可审阅草稿。" * 200, encoding="utf-8")

            package = build_cgss_pdf_preflight(
                project_root,
                paper_path.relative_to(project_root),
                Path("Submissions/cgss_social_capital_happiness/paper.pdf"),
                renderer=self._fake_pdf_renderer,
            )

            self.assertEqual(package["schema_version"], "p6.cgss_pdf_preflight.v1")
            self.assertEqual(package["status"], "pdf_preflight_ready")
            self.assertTrue(package["draft_layer_only"])
            self.assertFalse(package["formal_writeback_allowed"])
            self.assertTrue(package["pdf"]["exists"])
            self.assertGreater(package["pdf"]["bytes"], 0)
            self.assertFalse(package["boundary_flags"]["modified_formal_manuscript"])
            self.assertIn("human_review_pdf_candidate", package["next_tasks"])

    def test_bdd_60_blocks_when_exploratory_paper_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            package = build_cgss_pdf_preflight(
                project_root,
                Path("Manuscripts/generated/missing.md"),
                Path("Submissions/cgss_social_capital_happiness/paper.pdf"),
                renderer=self._fake_pdf_renderer,
            )

            self.assertEqual(package["status"], "blocked_missing_exploratory_paper")
            self.assertIn("exploratory_paper_missing", package["blocking_reasons"])
            self.assertFalse(package["pdf"]["exists"])
            self.assertFalse(package["formal_writeback_allowed"])

    def test_bdd_60_writes_preflight_review_without_formal_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            paper_path = project_root / "Manuscripts/generated/cgss_social_capital_happiness_paper.md"
            paper_path.parent.mkdir(parents=True)
            paper_path.write_text("# 论文\n\n## 摘要\n\n这是可审阅草稿。" * 200, encoding="utf-8")
            package = build_cgss_pdf_preflight(
                project_root,
                paper_path.relative_to(project_root),
                Path("Submissions/cgss_social_capital_happiness/paper.pdf"),
                renderer=self._fake_pdf_renderer,
            )

            result_path, review_path = write_cgss_pdf_preflight_outputs(project_root, package)

            self.assertTrue(result_path.exists())
            self.assertTrue(review_path.exists())
            self.assertFalse((project_root / "state/product/paper.json").exists())
            saved = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "pdf_preflight_ready")
            self.assertIn("CGSS PDF 预检", review_path.read_text(encoding="utf-8"))

    def _fake_pdf_renderer(self, project_root: Path, paper_path: Path, pdf_path: Path) -> dict:
        absolute_pdf = project_root / pdf_path
        absolute_pdf.parent.mkdir(parents=True, exist_ok=True)
        absolute_pdf.write_bytes(b"%PDF-1.4\n%fake\n")
        return {
            "ok": True,
            "engine": "fake",
            "returncode": 0,
            "stdout": "",
            "stderr": "",
        }


if __name__ == "__main__":
    unittest.main()
