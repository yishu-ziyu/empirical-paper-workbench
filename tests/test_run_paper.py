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

    def run_command(self, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        command = ["python3", str(SCRIPT_PATH), "--project-root", str(self.project_dir), "--dry-run"]
        if extra_args:
            command.extend(extra_args)
        return subprocess.run(
            command,
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
        qmd_path = self.project_dir / "Manuscripts" / "generated" / "paper_draft.qmd"
        latex_path = self.project_dir / "Manuscripts" / "generated" / "paper_draft.tex"

        self.assertTrue(markdown_path.exists())
        self.assertTrue(qmd_path.exists())
        self.assertTrue(latex_path.exists())
        self.assertIn("研究问题", markdown_path.read_text())
        qmd_content = qmd_path.read_text()
        self.assertIn("format:", qmd_content)
        self.assertIn("pdf-engine: xelatex", qmd_content)
        self.assertIn("## 研究问题", qmd_content)
        self.assertNotIn("✅", qmd_content)
        self.assertNotIn("ℹ️", qmd_content)
        self.assertIn("\\section{研究问题}", latex_path.read_text())

    def test_dry_run_can_use_an_explicit_paper_config_without_overwriting_default(self) -> None:
        config_path = self.project_dir / "Program" / "config" / "paper_real_override.yaml"
        dataset_path = self.project_dir / "Data" / "Final" / "real_override.csv"
        default_state = self.project_dir / "state" / "project_state.json"
        default_snapshot = self.project_dir / "Results" / "json" / "project_snapshot.json"
        default_state_before = default_state.read_text(encoding="utf-8") if default_state.exists() else None
        default_snapshot_before = default_snapshot.read_text(encoding="utf-8") if default_snapshot.exists() else None
        dataset_path.write_text(
            "ln_wage,ln_robot,edu_last,age,female,urban\n"
            "10.0,8.1,3,30,0,1\n"
            "11.0,8.4,4,41,1,0\n",
            encoding="utf-8",
        )
        config_path.write_text(
            """
project:
  slug: real-override
  title: "真实数据覆盖配置测试"
  language: zh
  final_output: docx
  internal_formats:
    - markdown
    - latex
research:
  question: "工业机器人暴露是否影响劳动收入"
  contribution: "验证 run_paper 可以读取独立真实数据配置"
  current_stage: real-data-cli-validation
  target_journey:
    - data-readiness
    - baseline-estimation
data:
  final_dataset: Data/Final/real_override.csv
  unit_of_analysis: "individual-year"
  sample_definition: "minimal real-data override fixture"
  key_variables:
    outcome:
      - ln_wage
    treatment:
      - ln_robot
    controls:
      - edu_last
      - age
      - female
      - urban
    instruments: []
methods:
  baseline:
    family: "ols"
    candidates:
      - ols
  robustness: []
outputs:
  markdown_draft: Manuscripts/generated/real_override_draft.md
  qmd_draft: Manuscripts/generated/real_override_draft.qmd
  latex_draft: Manuscripts/generated/real_override_draft.tex
  results_index: Results/real_override_index.json
  state_file: state/real_override_project_state.json
  project_snapshot: Results/json/real_override_project_snapshot.json
  analysis_result: Results/json/real_override_analysis_result.json
  run_log: Results/logs/real_override_run_paper.log
""".lstrip(),
            encoding="utf-8",
        )

        result = self.run_command(
            ["--paper-config", "Program/config/paper_real_override.yaml", "--run-id", "run_test_real_override"]
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)

        override_state = self.project_dir / "state" / "real_override_project_state.json"
        override_index = self.project_dir / "Results" / "real_override_index.json"
        override_snapshot = self.project_dir / "Results" / "json" / "real_override_project_snapshot.json"
        override_analysis_result = self.project_dir / "Results" / "json" / "real_override_analysis_result.json"
        override_run_log = self.project_dir / "Results" / "logs" / "real_override_run_paper.log"
        override_markdown = self.project_dir / "Manuscripts" / "generated" / "real_override_draft.md"
        override_qmd = self.project_dir / "Manuscripts" / "generated" / "real_override_draft.qmd"
        run_steps = self.project_dir / "state" / "runs" / "run_test_real_override" / "run_steps.json"

        default_state_after = default_state.read_text(encoding="utf-8") if default_state.exists() else None
        default_snapshot_after = default_snapshot.read_text(encoding="utf-8") if default_snapshot.exists() else None
        self.assertEqual(default_state_before, default_state_after)
        self.assertEqual(default_snapshot_before, default_snapshot_after)
        self.assertTrue(override_state.exists())
        self.assertTrue(override_index.exists())
        self.assertTrue(override_snapshot.exists())
        self.assertFalse(override_analysis_result.exists())
        self.assertTrue(override_run_log.exists())
        self.assertTrue(override_markdown.exists())
        self.assertTrue(override_qmd.exists())

        snapshot = json.loads(override_snapshot.read_text())
        index = json.loads(override_index.read_text())
        steps_payload = json.loads(run_steps.read_text())
        steps = steps_payload["items"]

        self.assertEqual(snapshot["project"]["slug"], "real-override")
        self.assertEqual(snapshot["data"]["final_dataset"], "Data/Final/real_override.csv")
        self.assertIn("qmd", {artifact["kind"] for artifact in index["artifacts"]})
        config_step = next(step for step in steps if step["id"] == "config_load")
        self.assertEqual(config_step["metadata"]["paper_config"], "Program/config/paper_real_override.yaml")


if __name__ == "__main__":
    unittest.main()
