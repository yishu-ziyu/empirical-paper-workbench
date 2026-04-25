import shutil
import tempfile
import unittest
from pathlib import Path

from Product.backend.project_adapter import detect_project_profile


class ProjectAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="project-adapter-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_detects_thesis_layout(self) -> None:
        root = self.temp_dir / "final"
        for rel in ["01_data", "02_code", "03_results", "04_paper/sections_v21", "05_reference", "06_workspace", "literature", "state"]:
            (root / rel).mkdir(parents=True)
        (root / "AI_项目交接文档.md").write_text("industrial robots and labor reallocation", encoding="utf-8")

        profile = detect_project_profile(root)

        self.assertEqual(profile["layout"], "thesis_final")
        self.assertEqual(profile["paths"]["data"], "01_data")
        self.assertEqual(profile["paths"]["code"], "02_code")
        self.assertEqual(profile["paths"]["results"], "03_results")
        self.assertEqual(profile["paths"]["manuscript"], "04_paper")
        self.assertIn("Bartik IV", profile["known_logic"]["identification"])

    def test_detects_generic_aer_layout(self) -> None:
        root = self.temp_dir / "generic"
        for rel in ["Data", "Program", "Results", "Manuscripts", "Reference", "state"]:
            (root / rel).mkdir(parents=True)

        profile = detect_project_profile(root)

        self.assertEqual(profile["layout"], "generic_aer")
        self.assertEqual(profile["paths"]["data"], "Data")
        self.assertEqual(profile["paths"]["code"], "Program")


if __name__ == "__main__":
    unittest.main()

