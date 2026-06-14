import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Product.backend.orchestrator import run_workbench
from Product.backend.workbench_paths import stage_dir


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
        user_goal = "父母的教育水平对子女工资水平的影响。使用 Data/Final/charls_did_analysis_sample.csv。"
        manifest = run_workbench(self.root, mode="dry-run", user_goal=user_goal)
        run_root = Path(manifest["run_root"])

        required = [
            f"{stage_dir('00_intake')}/project_profile.json",
            f"{stage_dir('00_intake')}/user_goal.md",
            f"{stage_dir('01_sources')}/source_inventory.json",
            f"{stage_dir('01_sources')}/dataset_inventory.json",
            f"{stage_dir('01_sources')}/literature_inventory.json",
            f"{stage_dir('02_literature')}/literature_clusters.json",
            f"{stage_dir('02_literature')}/core_literature_brief.md",
            f"{stage_dir('02_literature')}/claim_evidence_map.json",
            f"{stage_dir('03_strategy')}/research_plan.md",
            f"{stage_dir('03_strategy')}/identification_plan.md",
            f"{stage_dir('03_strategy')}/empirical_plan.md",
            f"{stage_dir('04_modeling')}/modeling_report.json",
            f"{stage_dir('04_modeling')}/diagnostics_report.md",
            f"{stage_dir('05_results')}/results_index.json",
            f"{stage_dir('06_writing')}/paper_draft.md",
            f"{stage_dir('07_review')}/review_report.md",
            f"{stage_dir('07_review')}/revision_plan.md",
            f"{stage_dir('07_review')}/reviewer_decision.json",
            f"{stage_dir('08_final')}/paper_draft.tex",
            f"{stage_dir('08_final')}/paper_draft.docx",
            f"{stage_dir('08_final')}/formatting_report.md",
            "run_manifest.json",
        ]
        for rel in required:
            self.assertTrue((run_root / rel).exists(), rel)
        self.assertFalse((run_root / "00_intake").exists())

        run_profile = json.loads((run_root / stage_dir("00_intake") / "project_profile.json").read_text(encoding="utf-8"))
        self.assertEqual(run_profile["research_question"], user_goal)
        self.assertEqual(run_profile["title"], user_goal)
        self.assertEqual(run_profile["final_dataset"], "Data/Final/charls_did_analysis_sample.csv")

        draft_text = (run_root / stage_dir("06_writing") / "paper_draft.md").read_text(encoding="utf-8")
        self.assertIn(user_goal, draft_text)
        self.assertIn("旧稿不会自动并入正文", draft_text)
        self.assertNotIn("# 论文v2.1", draft_text)
        self.assertNotIn("Source Snapshot", draft_text)

        review = json.loads((run_root / stage_dir("07_review") / "reviewer_decision.json").read_text(encoding="utf-8"))
        self.assertNotEqual(review["reviewer"], "WritingAgent")
        self.assertIn(review["decision"], ["approve", "revise_minor", "revise_major", "block"])


if __name__ == "__main__":
    unittest.main()
