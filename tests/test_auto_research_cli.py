import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")


class AutoResearchCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="auto-research-cli-"))
        self.root = self.temp_dir / "paper"
        for rel in ["Data", "Program", "Results", "Manuscripts", "Reference", "state"]:
            (self.root / rel).mkdir(parents=True)
        (self.root / "Data" / "sample.csv").write_text("wage,ai,age\n10,1,30\n8,0,45\n", encoding="utf-8")
        (self.root / "Reference" / "seed.md").write_text("# 人工智能与劳动收入\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_auto_research_cli_creates_best_available_run_artifacts(self) -> None:
        """BDD: 题目优先 CLI 必须创建 best-available run，并把外部能力状态写成可审计证据。"""
        result = subprocess.run(
            [
                "python3",
                "Product/cli.py",
                "auto-research",
                "--project-root",
                str(self.root),
                "--topic",
                "人工智能是否影响劳动收入差距",
                "--max-depth",
                "2",
                "--max-iterations",
                "5",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["mode"], "auto")
        self.assertEqual(payload["execution_policy"], "best_available")
        self.assertEqual(payload["research_intent"]["topic"], "人工智能是否影响劳动收入差距")

        run_root = Path(payload["run_root"])
        self.assertTrue(run_root.exists())
        expected_paths = [
            "00_intake/research_intent.json",
            "01_sources/recursive_search_plan.json",
            "01_sources/literature_inventory.json",
            "02_literature/literature_clues.jsonl",
            "03_strategy/variable_candidates.json",
            "03_strategy/method_candidates.json",
            "03_strategy/evidence_gaps.json",
            "06_writing/research_report.md",
            "06_writing/paper_draft_exploratory.md",
            "run_manifest.json",
        ]
        for rel in expected_paths:
            self.assertTrue((run_root / rel).exists(), rel)

        manifest = json.loads((run_root / "run_manifest.json").read_text(encoding="utf-8"))
        capability_ids = {item["id"] for item in manifest["capability_status"]}
        self.assertGreaterEqual(
            capability_ids,
            {"local_data", "statspai", "cnki", "web_search", "agentmemory", "llm_supervisor"},
        )
        self.assertTrue(all(item["can_promote"] is False for item in manifest["capability_status"]))
        self.assertEqual(manifest["artifact_policy"]["status"], "needs_human_review")
        self.assertEqual(manifest["artifact_policy"]["can_promote"], False)

        global_clues = self.root / "state" / "orchestration" / "literature_clues.jsonl"
        self.assertTrue(global_clues.exists())
        first_clue = json.loads(global_clues.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(first_clue["evidence_level"], "local_file")
        self.assertEqual(first_clue["can_promote"], False)


if __name__ == "__main__":
    unittest.main()
