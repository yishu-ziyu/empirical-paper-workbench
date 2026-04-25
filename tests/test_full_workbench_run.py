import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Product.backend.orchestrator import run_workbench


class FullWorkbenchRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="full-workbench-"))
        self.root = self.temp_dir / "final"
        for rel in ["01_data", "02_code", "03_results", "04_paper/sections_v21", "05_reference", "06_workspace", "literature/core", "state"]:
            (self.root / rel).mkdir(parents=True)
        (self.root / "01_data" / "cfps_panel_v5.dta").write_bytes(b"stata-bytes")
        (self.root / "02_code" / "18_final_results.do").write_text("ivregress 2sls y (x=z)", encoding="utf-8")
        (self.root / "03_results" / "index.json").write_text('{"artifacts": [{"path": "03_results/table.md", "exists": true}]}', encoding="utf-8")
        (self.root / "literature" / "core" / "Acemoglu_Restrepo.pdf").write_bytes(b"pdf")
        (self.root / "04_paper" / "sections_v21" / "00_摘要_中文.md").write_text("摘要", encoding="utf-8")
        (self.root / "04_paper" / "论文v2.1_完整版.md").write_text("# 论文v2.1", encoding="utf-8")
        (self.root / "05_reference" / "匹配效率概念与可测代理对照表.md").write_text("strict matching efficiency", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_full_dry_run_writes_required_artifacts(self) -> None:
        manifest = run_workbench(self.root, mode="dry-run", user_goal="推进毕业论文")
        run_root = Path(manifest["run_root"])

        required = [
            "00_intake/project_profile.json",
            "00_intake/user_goal.md",
            "01_sources/source_inventory.json",
            "01_sources/dataset_inventory.json",
            "01_sources/literature_inventory.json",
            "02_literature/literature_clusters.json",
            "02_literature/core_literature_brief.md",
            "02_literature/claim_evidence_map.json",
            "03_strategy/research_plan.md",
            "03_strategy/identification_plan.md",
            "03_strategy/empirical_plan.md",
            "04_modeling/modeling_report.json",
            "04_modeling/diagnostics_report.md",
            "05_results/results_index.json",
            "06_writing/paper_draft.md",
            "07_review/review_report.md",
            "07_review/revision_plan.md",
            "07_review/reviewer_decision.json",
            "08_final/paper_draft.tex",
            "08_final/paper_draft.docx",
            "08_final/formatting_report.md",
            "run_manifest.json",
        ]
        for rel in required:
            self.assertTrue((run_root / rel).exists(), rel)

        review = json.loads((run_root / "07_review" / "reviewer_decision.json").read_text(encoding="utf-8"))
        self.assertNotEqual(review["reviewer"], "WritingAgent")
        self.assertIn(review["decision"], ["approve", "revise_minor", "revise_major", "block"])


if __name__ == "__main__":
    unittest.main()

