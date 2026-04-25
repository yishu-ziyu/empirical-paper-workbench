import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")


class CliWorkbenchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cli-workbench-"))
        self.root = self.temp_dir / "final"
        for rel in ["01_data", "02_code", "03_results", "04_paper/sections_v21", "05_reference", "06_workspace", "literature", "state"]:
            (self.root / rel).mkdir(parents=True)
        (self.root / "01_data" / "cfps_panel_v5.dta").write_bytes(b"stata-bytes")
        (self.root / "04_paper" / "sections_v21" / "00_摘要_中文.md").write_text("摘要", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_cli_runs_workbench_and_prints_manifest_json(self) -> None:
        result = subprocess.run(
            [
                "python3",
                "Product/cli.py",
                "run-workbench",
                "--project-root",
                str(self.root),
                "--mode",
                "dry-run",
                "--user-goal",
                "CLI smoke test",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "completed")
        self.assertTrue(Path(payload["run_root"]).exists())


if __name__ == "__main__":
    unittest.main()

