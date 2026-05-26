from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")
RUN_SCRIPT = REPO_ROOT / "Program" / "run_paper.py"
EXPORT_SCRIPT = REPO_ROOT / "Program" / "export_pdf.py"


class ExportPdfCliTests(unittest.TestCase):
    """BDD: PDF-first 研究包必须从 QMD 源文件可预检、可导出、可追溯。"""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="econ-workbench-pdf-test-"))
        shutil.copytree(REPO_ROOT, self.temp_dir / "project", dirs_exist_ok=True)
        self.project_dir = self.temp_dir / "project"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def run_paper(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(RUN_SCRIPT), "--project-root", str(self.project_dir), "--dry-run"],
            cwd=self.project_dir,
            text=True,
            capture_output=True,
        )

    def run_export_pdf(self, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        command = ["python3", str(EXPORT_SCRIPT), "--project-root", str(self.project_dir)]
        if extra_args:
            command.extend(extra_args)
        return subprocess.run(command, cwd=self.project_dir, text=True, capture_output=True)

    def test_bdd_pdf_preflight_writes_manifest_without_rendering(self) -> None:
        """行为 2：PDF 预检必须记录 QMD、Quarto、LaTeX 引擎和输出路径。"""
        run = self.run_paper()
        self.assertEqual(run.returncode, 0, msg=run.stderr)

        result = self.run_export_pdf(["--preflight-only"])

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        manifest_path = self.project_dir / "Submissions" / "pdf_export_manifest.json"
        pdf_path = self.project_dir / "Submissions" / "paper_draft.pdf"
        self.assertTrue(manifest_path.exists())
        self.assertFalse(pdf_path.exists())

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["export_format"], "pdf")
        self.assertEqual(manifest["source_qmd"], "Manuscripts/generated/paper_draft.qmd")
        self.assertEqual(manifest["output_pdf"], "Submissions/paper_draft.pdf")
        self.assertEqual(manifest["preflight"]["status"], "ready")
        checks = {check["id"]: check for check in manifest["preflight"]["checks"]}
        self.assertEqual(checks["source_qmd_exists"]["status"], "passed")
        self.assertEqual(checks["quarto_available"]["status"], "passed")
        self.assertEqual(checks["xelatex_available"]["status"], "passed")
        self.assertEqual(manifest["review_doc"], "Submissions/pdf_first_review.md")
        self.assertEqual(manifest["reproduce_script"], "Submissions/reproduce_pdf_first.sh")

    def test_bdd_missing_qmd_blocks_pdf_export_and_records_failed_check(self) -> None:
        """行为 4：缺少 QMD 稿源时必须阻断导出，不能伪造 PDF 成功。"""
        result = self.run_export_pdf(["--preflight-only"])

        self.assertEqual(result.returncode, 2)
        manifest_path = self.project_dir / "Submissions" / "pdf_export_manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        checks = {check["id"]: check for check in manifest["preflight"]["checks"]}
        self.assertEqual(manifest["preflight"]["status"], "blocked")
        self.assertEqual(checks["source_qmd_exists"]["status"], "failed")
        self.assertFalse(manifest["pdf_exists"])

    def test_bdd_pdf_export_writes_review_doc_and_reproduce_script(self) -> None:
        """行为 6：PDF-first 包必须包含人工审阅文档和可复跑入口。"""
        run = self.run_paper()
        self.assertEqual(run.returncode, 0, msg=run.stderr)

        result = self.run_export_pdf(["--preflight-only"])

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        review_doc = self.project_dir / "Submissions" / "pdf_first_review.md"
        reproduce_script = self.project_dir / "Submissions" / "reproduce_pdf_first.sh"
        self.assertTrue(review_doc.exists())
        self.assertTrue(reproduce_script.exists())
        self.assertTrue(reproduce_script.stat().st_mode & 0o111)

        review_text = review_doc.read_text(encoding="utf-8")
        script_text = reproduce_script.read_text(encoding="utf-8")
        self.assertIn("PDF-first 探索性研究包", review_text)
        self.assertIn("exploratory / draft / needs_human_review", review_text)
        self.assertIn("Manuscripts/generated/paper_draft.qmd", review_text)
        self.assertIn("python3 Program/export_pdf.py", script_text)
        self.assertIn("--source Manuscripts/generated/paper_draft.qmd", script_text)
        self.assertIn("--review-doc Submissions/pdf_first_review.md", script_text)
        self.assertIn("--reproduce-script Submissions/reproduce_pdf_first.sh", script_text)

    def test_bdd_pdf_package_writes_full_chain_reproduce_script_when_paper_config_is_known(self) -> None:
        """行为 7：PDF-first 包必须能从真实配置重新跑到 PDF，而不只重排 QMD。"""
        run = self.run_paper()
        self.assertEqual(run.returncode, 0, msg=run.stderr)

        result = self.run_export_pdf(
            [
                "--preflight-only",
                "--paper-config",
                "paper.yaml",
                "--full-reproduce-script",
                "Submissions/reproduce_pdf_first_full_chain.sh",
            ]
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        manifest_path = self.project_dir / "Submissions" / "pdf_export_manifest.json"
        review_doc = self.project_dir / "Submissions" / "pdf_first_review.md"
        full_script = self.project_dir / "Submissions" / "reproduce_pdf_first_full_chain.sh"
        self.assertTrue(full_script.exists())
        self.assertTrue(full_script.stat().st_mode & 0o111)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        review_text = review_doc.read_text(encoding="utf-8")
        script_text = full_script.read_text(encoding="utf-8")
        self.assertEqual(
            manifest["full_reproduce_script"],
            "Submissions/reproduce_pdf_first_full_chain.sh",
        )
        self.assertIn("完整链路复跑脚本", review_text)
        self.assertIn("reproduce_pdf_first_full_chain.sh", review_text)
        self.assertIn("python3 Program/run_paper.py", script_text)
        self.assertIn("--paper-config paper.yaml", script_text)
        self.assertIn("python3 Program/export_pdf.py", script_text)
        self.assertIn("--source Manuscripts/generated/paper_draft.qmd", script_text)

    @unittest.skipUnless(shutil.which("quarto") and shutil.which("xelatex"), "requires quarto and xelatex")
    def test_bdd_pdf_export_creates_pdf_log_and_manifest(self) -> None:
        """行为 3：PDF 导出必须生成 PDF、日志和可追溯 manifest。"""
        run = self.run_paper()
        self.assertEqual(run.returncode, 0, msg=run.stderr)

        result = self.run_export_pdf()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        pdf_path = self.project_dir / "Submissions" / "paper_draft.pdf"
        log_path = self.project_dir / "Results" / "logs" / "export_pdf.log"
        manifest_path = self.project_dir / "Submissions" / "pdf_export_manifest.json"
        self.assertTrue(pdf_path.exists())
        self.assertGreater(pdf_path.stat().st_size, 0)
        self.assertTrue(log_path.exists())

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertTrue(manifest["pdf_exists"])
        self.assertEqual(manifest["engine"], "quarto")
        self.assertEqual(manifest["log_path"], "Results/logs/export_pdf.log")
        self.assertIn("quarto", manifest["command"][0])


if __name__ == "__main__":
    unittest.main()
