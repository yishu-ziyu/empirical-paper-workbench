from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class GitExperimentLoggerTests(unittest.TestCase):
    """BDD: Stage 完成后自动 git commit，前端可查看实验历史并回退。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="git-experiment-logger-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "git-experiment-project",
                "title": "Git Experiment Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]

        # Ensure git repo exists
        subprocess.run(["git", "init"], cwd=self.project_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=self.project_root, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.project_root, capture_output=True)

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_minimal_project(self, project_root: Path) -> None:
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "Results" / "json").mkdir(parents=True)
        (project_root / "state" / "product").mkdir(parents=True)
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: git-experiment-project\n  title: Git Experiment Project\n"
            "research:\n  question: 培训是否影响工资？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n12,0,14,5\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")

    def test_behavior_1_stage_success_creates_commit(self) -> None:
        """行为1: Stage 成功即 Commit。"""
        from Product.backend import git_experiment_logger

        # Simulate stage output files
        draft_path = self.project_root / "Manuscripts" / "04_identification_draft.md"
        draft_path.write_text("# 识别策略\n\nIV: bartik_iv", encoding="utf-8")

        # Call commit function
        result = git_experiment_logger.commit_stage(
            project_root=self.project_root,
            stage="04_identification",
            agent_name="identification_agent",
            status="succeeded",
        )

        self.assertTrue(result["committed"])
        self.assertIn("04_identification", result["message"])
        self.assertIn("succeeded", result["message"])

        # Verify git log
        log_output = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("experiment:", log_output.stdout)
        self.assertIn("04_identification", log_output.stdout)

    def test_behavior_2_commit_excludes_data_directory(self) -> None:
        """行为2: Commit 范围正确，不包含 Data/。"""
        from Product.backend import git_experiment_logger

        # Create files in all directories
        (self.project_root / "Manuscripts" / "draft.md").write_text("draft")
        (self.project_root / "Results" / "json" / "result.json").write_text('{"beta": 0.2}')
        (self.project_root / "state" / "product" / "run_plan.json").write_text("{}")
        (self.project_root / "Data" / "raw.csv").write_text("a,b,c\n1,2,3")

        result = git_experiment_logger.commit_stage(
            project_root=self.project_root,
            stage="05_modeling",
            agent_name="modeling_agent",
            status="succeeded",
        )

        self.assertTrue(result["committed"])

        # Verify Data/ is not in commit
        diff_output = subprocess.run(
            ["git", "show", "--name-only", "--pretty=format:", result["commit_hash"]],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        committed_files = [f for f in diff_output.stdout.strip().split("\n") if f]
        self.assertIn("Manuscripts/draft.md", committed_files)
        self.assertIn("Results/json/result.json", committed_files)
        self.assertIn("state/product/run_plan.json", committed_files)
        self.assertNotIn("Data/raw.csv", committed_files)

    def test_behavior_3_api_returns_experiment_history(self) -> None:
        """行为3: 前端查看实验历史 API。"""
        from Product.backend import git_experiment_logger

        # Create two commits
        (self.project_root / "Manuscripts" / "03_variables_draft.md").write_text("variables")
        git_experiment_logger.commit_stage(
            project_root=self.project_root,
            stage="03_variables",
            agent_name="variable_agent",
            status="succeeded",
        )

        (self.project_root / "Manuscripts" / "04_identification_draft.md").write_text("identification")
        git_experiment_logger.commit_stage(
            project_root=self.project_root,
            stage="04_identification",
            agent_name="identification_agent",
            status="succeeded",
        )

        # Call API
        response = self.client.get(f"/api/v1/projects/{self.project_id}/experiments")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("experiments", data)
        self.assertEqual(len(data["experiments"]), 2)

        # Verify order (most recent first)
        experiments = data["experiments"]
        self.assertEqual(experiments[0]["stage"], "04_identification")
        self.assertEqual(experiments[1]["stage"], "03_variables")

    def test_behavior_4_revert_to_historical_version(self) -> None:
        """行为4: 回退到历史版本。"""
        from Product.backend import git_experiment_logger

        # Create initial content
        draft_path = self.project_root / "Manuscripts" / "04_identification_draft.md"
        draft_path.write_text("version 1", encoding="utf-8")

        result1 = git_experiment_logger.commit_stage(
            project_root=self.project_root,
            stage="04_identification",
            agent_name="identification_agent",
            status="succeeded",
        )
        commit_hash = result1["commit_hash"]

        # Modify content
        draft_path.write_text("version 2", encoding="utf-8")

        # Revert
        revert_result = git_experiment_logger.revert_to_commit(
            project_root=self.project_root,
            commit_hash=commit_hash,
        )

        self.assertTrue(revert_result["reverted"])
        self.assertEqual(draft_path.read_text(encoding="utf-8"), "version 1")

    def test_behavior_1b_failed_stage_also_commits(self) -> None:
        """边界: 失败 stage 也 commit，记录失败状态。"""
        from Product.backend import git_experiment_logger

        (self.project_root / "Manuscripts" / "04_identification_draft.md").write_text("failed draft")

        result = git_experiment_logger.commit_stage(
            project_root=self.project_root,
            stage="04_identification",
            agent_name="identification_agent",
            status="failed",
        )

        self.assertTrue(result["committed"])
        self.assertIn("failed", result["message"])

        log_output = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("failed", log_output.stdout)
