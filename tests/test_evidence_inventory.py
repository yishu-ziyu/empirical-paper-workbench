import shutil
import tempfile
import unittest
from pathlib import Path

from Product.backend.evidence import build_evidence_inventory
from Product.backend.project_adapter import detect_project_profile


class EvidenceInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="evidence-inventory-"))
        self.root = self.temp_dir / "final"
        for rel in ["01_data", "02_code", "03_results", "04_paper/sections_v21", "05_reference", "06_workspace", "literature/core", "state"]:
            (self.root / rel).mkdir(parents=True)
        (self.root / "01_data" / "cfps_panel_v5.dta").write_bytes(b"stata-bytes")
        (self.root / "02_code" / "18_final_results.do").write_text("ivregress 2sls y (x=z)", encoding="utf-8")
        (self.root / "03_results" / "index.json").write_text('{"artifacts": []}', encoding="utf-8")
        (self.root / "literature" / "README.md").write_text("core literature", encoding="utf-8")
        (self.root / "literature" / "core" / "Acemoglu_Restrepo.pdf").write_bytes(b"pdf")
        (self.root / "04_paper" / "sections_v21" / "00_摘要_中文.md").write_text("摘要", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_builds_inventory_without_mutating_sources(self) -> None:
        profile = detect_project_profile(self.root)
        inventory = build_evidence_inventory(self.root, profile)

        self.assertEqual(inventory["project_root"], str(self.root.resolve()))
        self.assertEqual(inventory["datasets"][0]["name"], "cfps_panel_v5.dta")
        self.assertEqual(inventory["code_files"][0]["name"], "18_final_results.do")
        self.assertIn("Acemoglu_Restrepo.pdf", {item["name"] for item in inventory["literature_files"]})
        self.assertEqual(inventory["manuscript_sections"][0]["name"], "00_摘要_中文.md")
        self.assertTrue((self.root / "01_data" / "cfps_panel_v5.dta").exists())


if __name__ == "__main__":
    unittest.main()
