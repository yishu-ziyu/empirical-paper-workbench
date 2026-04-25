import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")
SCRIPT_PATH = REPO_ROOT / "Program" / "run_paper.py"


class RunPaperDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="econ-workbench-test-"))
        shutil.copytree(REPO_ROOT, self.temp_dir / "project", dirs_exist_ok=True)
        self.project_dir = self.temp_dir / "project"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def run_command(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT_PATH), "--project-root", str(self.project_dir), "--dry-run"],
            cwd=self.project_dir,
            text=True,
            capture_output=True,
        )

    def test_dry_run_creates_project_state_and_results_index(self) -> None:
        result = self.run_command()

        self.assertEqual(result.returncode, 0, msg=result.stderr)

        state_path = self.project_dir / "state" / "project_state.json"
        index_path = self.project_dir / "Results" / "index.json"
        snapshot_path = self.project_dir / "Results" / "json" / "project_snapshot.json"

        self.assertTrue(state_path.exists())
        self.assertTrue(index_path.exists())
        self.assertTrue(snapshot_path.exists())

        state = json.loads(state_path.read_text())
        index = json.loads(index_path.read_text())

        self.assertEqual(state["current_stage"], "question-definition")
        self.assertEqual(index["mode"], "dry-run")
        self.assertIn("artifacts", index)
        self.assertGreaterEqual(len(index["artifacts"]), 3)

    def test_dry_run_creates_markdown_and_latex_draft_artifacts(self) -> None:
        result = self.run_command()

        self.assertEqual(result.returncode, 0, msg=result.stderr)

        markdown_path = self.project_dir / "Manuscripts" / "generated" / "paper_draft.md"
        latex_path = self.project_dir / "Manuscripts" / "generated" / "paper_draft.tex"

        self.assertTrue(markdown_path.exists())
        self.assertTrue(latex_path.exists())
        self.assertIn("研究问题", markdown_path.read_text())
        self.assertIn("\\section{研究问题}", latex_path.read_text())


if __name__ == "__main__":
    unittest.main()
