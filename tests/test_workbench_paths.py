import shutil
import tempfile
import unittest
from pathlib import Path

from Product.backend.workbench_paths import create_run_workspace, required_run_relative_paths


class WorkbenchPathsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="workbench-paths-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_create_run_workspace_prefers_06_workspace(self) -> None:
        (self.project_root / "06_workspace").mkdir()
        run = create_run_workspace(self.project_root, run_id="run_test")

        self.assertEqual(run.run_id, "run_test")
        self.assertEqual(run.root, self.project_root / "06_workspace" / "runs" / "run_test")
        for rel in required_run_relative_paths():
            self.assertTrue((run.root / rel).exists(), rel)

    def test_create_run_workspace_uses_workspace_fallback(self) -> None:
        run = create_run_workspace(self.project_root, run_id="run_fallback")

        self.assertEqual(run.root, self.project_root / "workspace" / "runs" / "run_fallback")
        self.assertTrue((run.root / "run_manifest.json").parent.exists())


if __name__ == "__main__":
    unittest.main()

