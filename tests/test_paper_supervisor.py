from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PaperSupervisorCliTests(unittest.TestCase):
    """BDD: local Codex Supervisor execution is explicit, durable, and review-gated."""

    def setUp(self) -> None:
        self.original_exec_env = os.environ.get("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC")
        self.original_path = os.environ.get("PATH", "")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="paper-supervisor-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir(parents=True)
        self._seed_supervisor_context(self.project_root)

    def tearDown(self) -> None:
        if self.original_exec_env is None:
            os.environ.pop("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC", None)
        else:
            os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = self.original_exec_env
        os.environ["PATH"] = self.original_path
        shutil.rmtree(self.temp_dir)

    def test_bdd_8_blocks_when_local_codex_execution_is_disabled(self) -> None:
        """行为 8：未显式启用本地 Codex 时，不能伪装生成 Supervisor run。"""
        os.environ.pop("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC", None)

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_supervisor.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("local_codex_execution_not_enabled", result.stderr)
        self.assertFalse((self.project_root / "Results" / "json" / "paper_supervisor_run.json").exists())

    def test_bdd_8_enabled_local_codex_writes_review_gated_supervisor_run(self) -> None:
        """行为 8：启用本地 Codex 后，Supervisor run 必须落盘且不得改写正式层状态。"""
        self._install_fake_codex()
        os.environ["EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"] = "1"
        protected_paths = self._seed_formal_state_files(self.project_root)
        before = {path.name: path.read_text(encoding="utf-8") for path in protected_paths}

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "Program" / "paper_supervisor.py"),
                "--project-root",
                str(self.project_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("paper_supervisor_run=Results/json/paper_supervisor_run.json", result.stdout)

        run_path = self.project_root / "Results" / "json" / "paper_supervisor_run.json"
        raw_path = self.project_root / "docs" / "workflows" / "paper_package_supervisor" / "supervisor_round.md"
        self.assertTrue(run_path.exists())
        self.assertTrue(raw_path.exists())
        self.assertIn("Supervisor route", raw_path.read_text(encoding="utf-8"))

        run = json.loads(run_path.read_text(encoding="utf-8"))
        self.assertEqual(run["schema_version"], "p4.paper_supervisor_run.v1")
        self.assertEqual(run["status"], "needs_human_review")
        self.assertEqual(run["evidence_level"], "local_execution")
        self.assertEqual(run["provider"]["provider"], "local_codex")
        self.assertEqual(run["provider"]["returncode"], 0)
        self.assertEqual(run["input_context_path"], "Results/json/paper_supervisor_context.json")
        self.assertEqual(run["raw_output_path"], "docs/workflows/paper_package_supervisor/supervisor_round.md")
        self.assertFalse(run["formal_state_write"]["can_promote"])
        self.assertTrue(run["formal_state_write"]["requires_human_review"])
        self.assertEqual(run["next_action"]["id"], "review_supervisor_run")
        self.assertEqual(run["agent_task_queue"][0]["agent"], "LiteratureAgent")

        after = {path.name: path.read_text(encoding="utf-8") for path in protected_paths}
        self.assertEqual(before, after)

    def _seed_supervisor_context(self, root: Path) -> None:
        context_path = root / "Results" / "json" / "paper_supervisor_context.json"
        context_path.parent.mkdir(parents=True)
        context_path.write_text(
            json.dumps(
                {
                    "schema_version": "p4.paper_supervisor_context.v1",
                    "supervisor_role": "research_orchestrator",
                    "profile": "aer_like",
                    "context_sources": [
                        "Results/json/paper_quality_report.json",
                        "Results/json/paper_expansion_plan.json",
                    ],
                    "current_verdict": ["too_thin", "needs_literature_review"],
                    "agent_task_queue": [
                        {
                            "order": 1,
                            "id": "build_literature_package",
                            "agent": "LiteratureAgent",
                            "reason": "补齐 verified bibliography and contribution matrix",
                            "inputs": ["paper_quality_report.json"],
                            "status": "ready",
                        }
                    ],
                    "release_gate": {
                        "required_before_review": [
                            "verified_bibliography_and_contribution_matrix",
                            "method_gate_report",
                        ]
                    },
                    "write_boundary": "草案层和 proposal 层；正式层人工确认后写回。",
                    "task_prompt": "请生成下一轮研究路线和 Agent Task Queue。",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def _seed_formal_state_files(self, root: Path) -> list[Path]:
        state_dir = root / "state" / "product"
        state_dir.mkdir(parents=True)
        payloads = {
            "research_question.json": {"status": "confirmed", "question": "机器人是否影响劳动力匹配效率？"},
            "variable_roles.json": {"status": "approved", "outcome": ["wage"], "treatment": ["robot"]},
            "design_spec.json": {"status": "approved", "method": "ols"},
            "run_plan.json": {"status": "approved", "backend": "python"},
        }
        paths = []
        for filename, payload in payloads.items():
            path = state_dir / filename
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            paths.append(path)
        return paths

    def _install_fake_codex(self) -> None:
        bin_dir = self.temp_dir / "bin"
        bin_dir.mkdir()
        script = bin_dir / "codex"
        script.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env python3
                import pathlib
                import sys

                if "--version" in sys.argv:
                    print("codex-fake 1.0")
                    raise SystemExit(0)

                output_path = None
                if "--output-last-message" in sys.argv:
                    index = sys.argv.index("--output-last-message")
                    output_path = pathlib.Path(sys.argv[index + 1])

                if output_path is not None:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(
                        "# Supervisor route\\n\\n"
                        "- LiteratureAgent: build verified bibliography.\\n"
                        "- MethodAgent: run method gate before manuscript promotion.\\n",
                        encoding="utf-8",
                    )
                print("fake codex supervisor completed")
                """
            ),
            encoding="utf-8",
        )
        script.chmod(0o755)
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{self.original_path}"


if __name__ == "__main__":
    unittest.main()
