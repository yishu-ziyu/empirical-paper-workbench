"""Program/dod_check.py BDD tests.

行为契约 (Phase 8 Task 8.2):
- 9 个 DoD 项 (spec §9)
- 每项返回: {item: int, name: str, status: "PASS"|"FAIL"|"MANUAL", detail: str}
- 整体函数 check_dod() 返回 {"items": [...], "summary": {...}}
- 退出码: 全 pass/manual → 0; 任一 fail → 1

测试约定: 用 unittest.TestCase + setUp/TemporaryDirectory 构造 fixtures (不真实跑 pytest 整个 suite).
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Program import dod_check


# ── 行为 1: DoDItem 数据结构 + 整体结构 ──────────────────────────────────────


class DoDItemStructureTests(unittest.TestCase):
    """行为 1: DoDItem 是 dataclass, 含 item/name/status/detail 字段."""

    def test_bdd_dod_item_has_required_fields(self) -> None:
        """行为 1a: DoDItem 4 个字段 (item, name, status, detail)."""
        item = dod_check.DoDItem(item=1, name="x", status="PASS", detail="ok")
        self.assertEqual(item.item, 1)
        self.assertEqual(item.name, "x")
        self.assertEqual(item.status, "PASS")
        self.assertEqual(item.detail, "ok")

    def test_bdd_dod_status_enum(self) -> None:
        """行为 1b: status 只接受 PASS / FAIL / MANUAL."""
        for status in ("PASS", "FAIL", "MANUAL"):
            item = dod_check.DoDItem(item=1, name="x", status=status, detail="d")
            self.assertEqual(item.status, status)

    def test_bdd_dod_check_returns_9_items(self) -> None:
        """行为 1c: check_dod()["items"] 长度为 9."""
        result = dod_check.check_dod(
            repo_root=Path("/fake/root"),
            changelog_path=Path("/fake/CHANGELOG.md"),
        )
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 9, f"expected 9 DoD items, got {len(result['items'])}")

    def test_bdd_dod_check_items_have_unique_numbers(self) -> None:
        """行为 1d: 9 个 item 编号 1-9 各出现 1 次."""
        result = dod_check.check_dod(
            repo_root=Path("/fake/root"),
            changelog_path=Path("/fake/CHANGELOG.md"),
        )
        nums = sorted(it["item"] for it in result["items"])
        self.assertEqual(nums, [1, 2, 3, 4, 5, 6, 7, 8, 9])

    def test_bdd_dod_check_summary_counts(self) -> None:
        """行为 1e: summary 4 个数字字段."""
        result = dod_check.check_dod(
            repo_root=Path("/fake/root"),
            changelog_path=Path("/fake/CHANGELOG.md"),
        )
        s = result["summary"]
        for k in ("pass", "fail", "manual", "total"):
            self.assertIn(k, s)
        self.assertEqual(s["total"], 9)
        self.assertEqual(s["pass"] + s["fail"] + s["manual"], s["total"])


# ── 行为 2: 5 tab BDD all green ──────────────────────────────────────────────


class BddAllGreenTests(unittest.TestCase):
    """行为 2: item 1 - 5 个 wrapper BDD 测试都 pass."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_bdd_check_5_tab_bdd_passes_when_all_5_pass(self) -> None:
        """行为 2a: 5 个 wrapper 测试文件全 pass → PASS."""
        # 模拟 5 个测试文件
        for name in ("brief", "search", "variables", "design", "execute"):
            (self.tmp_path / f"test_{name}_service.py").write_text(
                "def test_x(): assert 1 == 1\n"
            )

        # patch subprocess.run 让它报告 pytest 全 pass
        fake_completed = subprocess.CompletedProcess(
            ["pytest"], 0, "5 passed in 0.1s", ""
        )
        with patch("subprocess.run", return_value=fake_completed):
            result = dod_check.check_5_tab_bdd(tests_dir=self.tmp_path)
        self.assertEqual(result.status, "PASS")
        self.assertIn("5", result.detail)

    def test_bdd_check_5_tab_bdd_fails_when_missing_files(self) -> None:
        """行为 2b: 缺测试文件 → FAIL."""
        # 只放 3 个文件
        for name in ("brief", "search", "variables"):
            (self.tmp_path / f"test_{name}_service.py").write_text("# empty\n")

        result = dod_check.check_5_tab_bdd(tests_dir=self.tmp_path)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("missing", result.detail.lower())

    def test_bdd_check_5_tab_bdd_fails_when_pytest_fails(self) -> None:
        """行为 2c: 文件齐但 pytest 跑失败 → FAIL."""
        for name in ("brief", "search", "variables", "design", "execute"):
            (self.tmp_path / f"test_{name}_service.py").write_text("# empty\n")

        # pytest 失败
        fake_completed = subprocess.CompletedProcess(
            ["pytest"], 1, "FAILED tests/test_brief.py::test_x - AssertionError", ""
        )
        with patch("subprocess.run", return_value=fake_completed):
            result = dod_check.check_5_tab_bdd(tests_dir=self.tmp_path)
        self.assertEqual(result.status, "FAIL")


# ── 行为 3: 60-min e2e ───────────────────────────────────────────────────────


class SixtyMinE2eTests(unittest.TestCase):
    """行为 3: item 2 - 60-min e2e 检查 (e2e/end-to-end.spec.ts)."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_bdd_check_e2e_passes_when_spec_exists(self) -> None:
        """行为 3a: e2e/end-to-end.spec.ts 存在 → PASS."""
        e2e_dir = self.tmp_path / "Product" / "web-react" / "e2e"
        e2e_dir.mkdir(parents=True)
        (e2e_dir / "end-to-end.spec.ts").write_text("// placeholder\n")

        result = dod_check.check_e2e_60min(repo_root=self.tmp_path)
        self.assertEqual(result.status, "PASS")
        self.assertIn("end-to-end", result.detail.lower())

    def test_bdd_check_e2e_fails_when_no_spec(self) -> None:
        """行为 3b: e2e 文件缺 → FAIL (spec §6.2 明确要求 60min 端到端)."""
        result = dod_check.check_e2e_60min(repo_root=self.tmp_path)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("e2e", result.detail.lower())


# ── 行为 4: 失败模式 5 handled ───────────────────────────────────────────────


class FailureModeTests(unittest.TestCase):
    """行为 4: item 3 - 5 种失败模式被 endpoint 兜底处理 (try/except 存在)."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_endpoint(self, name: str, with_handler: bool = True) -> None:
        """构造一个 endpoint 文件."""
        if with_handler:
            (self.tmp_path / f"{name}.py").write_text(
                "from fastapi import APIRouter, HTTPException\n"
                "router = APIRouter()\n\n"
                f"@router.post('/api/{name}')\n"
                "def post():\n"
                "    try:\n"
                "        return {}\n"
                "    except Exception as e:\n"
                "        raise HTTPException(status_code=500, detail=str(e))\n"
            )
        else:
            (self.tmp_path / f"{name}.py").write_text("# no handler\n")

    def test_bdd_check_failure_modes_passes_when_all_5_have_handlers(self) -> None:
        """行为 4a: 5 个 endpoint 文件都含 try/except + HTTPException → PASS."""
        for name in ("brief", "search", "variables", "design", "execute"):
            self._write_endpoint(name, with_handler=True)

        result = dod_check.check_failure_modes(api_dir=self.tmp_path)
        self.assertEqual(result.status, "PASS")
        self.assertIn("5", result.detail)

    def test_bdd_check_failure_modes_fails_when_endpoint_missing(self) -> None:
        """行为 4b: 缺某个 endpoint → FAIL."""
        for name in ("brief", "search", "variables", "design"):
            self._write_endpoint(name)
        # 缺 execute.py

        result = dod_check.check_failure_modes(api_dir=self.tmp_path)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("execute", result.detail.lower())

    def test_bdd_check_failure_modes_fails_when_handler_missing(self) -> None:
        """行为 4c: execute.py 存在但没有 try/except → FAIL."""
        for name in ("brief", "search", "variables", "design"):
            self._write_endpoint(name, with_handler=True)
        self._write_endpoint("execute", with_handler=False)

        result = dod_check.check_failure_modes(api_dir=self.tmp_path)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("execute", result.detail.lower())


# ── 行为 5: 产物入库 ─────────────────────────────────────────────────────────


class ArtifactsTests(unittest.TestCase):
    """行为 5: item 4 - Tasks/ Manuscripts/ Results/ 目录存在 + 至少 1 个 topic slug."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_bdd_check_artifacts_passes_when_dirs_have_topics(self) -> None:
        """行为 5a: 3 个目录都存在 + 至少有 1 个 topic → PASS."""
        for d in ("Tasks", "Manuscripts", "Results"):
            (self.tmp_path / d / "foo-topic").mkdir(parents=True)
            (self.tmp_path / d / "foo-topic" / "evidence.md").write_text("x")

        result = dod_check.check_artifacts(repo_root=self.tmp_path)
        self.assertEqual(result.status, "PASS")
        self.assertIn("3", result.detail)

    def test_bdd_check_artifacts_fails_when_dir_missing(self) -> None:
        """行为 5b: 缺某个目录 → FAIL."""
        (self.tmp_path / "Tasks" / "foo").mkdir(parents=True)
        (self.tmp_path / "Manuscripts" / "foo").mkdir(parents=True)
        # 缺 Results/

        result = dod_check.check_artifacts(repo_root=self.tmp_path)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("results", result.detail.lower())

    def test_bdd_check_artifacts_fails_when_dir_empty(self) -> None:
        """行为 5c: 目录存在但空 (无 topic slug) → FAIL."""
        (self.tmp_path / "Tasks").mkdir()
        (self.tmp_path / "Manuscripts").mkdir()
        (self.tmp_path / "Results").mkdir()

        result = dod_check.check_artifacts(repo_root=self.tmp_path)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("empty", result.detail.lower())


# ── 行为 6: Re-run equivalence ──────────────────────────────────────────────


class RerunTests(unittest.TestCase):
    """行为 6: item 5 - spec_runner.py 存在."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_bdd_check_rerun_passes_when_spec_runner_exists(self) -> None:
        """行为 6a: Program/spec_runner.py 存在 → PASS."""
        (self.tmp_path / "Program" / "spec_runner.py").parent.mkdir(parents=True)
        (self.tmp_path / "Program" / "spec_runner.py").write_text("# stub\n")

        result = dod_check.check_rerun_equivalence(repo_root=self.tmp_path)
        self.assertEqual(result.status, "PASS")
        self.assertIn("spec_runner", result.detail)

    def test_bdd_check_rerun_fails_when_spec_runner_missing(self) -> None:
        """行为 6b: spec_runner.py 缺 → FAIL."""
        result = dod_check.check_rerun_equivalence(repo_root=self.tmp_path)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("spec_runner", result.detail.lower())


# ── 行为 7: Prompt 迭代轮数 ──────────────────────────────────────────────────


class PromptIterationTests(unittest.TestCase):
    """行为 7: item 6 - CHANGELOG.md 里每个 tab 满足 §4.6 最低轮数.

    spec §4.6 最低轮数:
    - brief: 2, search: 2, variables: 3, design: 3, execution: 4
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_changelog(
        self, brief_v: int, search_v: int, variables_v: int, design_v: int, exec_v: int
    ) -> Path:
        """构造一个 CHANGELOG.md 满足给定 v 数."""
        cl = self.tmp_path / "CHANGELOG.md"
        lines = ["# Prompt 调优 CHANGELOG\n"]
        for tab, n in (
            ("brief", brief_v),
            ("search", search_v),
            ("variables", variables_v),
            ("design", design_v),
        ):
            lines.append(f"## {tab}\n")
            for i in range(1, n + 1):
                lines.append(f"- v{i} (2026-06-04): stub\n")
            lines.append("")
        lines.append("## execution (9 节)\n")
        for i in range(1, exec_v + 1):
            lines.append(f"- v{i} (2026-06-04): stub\n")
        cl.write_text("\n".join(lines), encoding="utf-8")
        return cl

    def test_bdd_check_prompts_passes_when_all_meet_minimums(self) -> None:
        """行为 7a: 5 tab 都满足最低轮数 → PASS."""
        cl = self._write_changelog(
            brief_v=2, search_v=2, variables_v=3, design_v=3, exec_v=4
        )
        result = dod_check.check_prompt_iterations(changelog_path=cl)
        self.assertEqual(result.status, "PASS")
        for tab in ("brief", "search", "variables", "design", "execution"):
            self.assertIn(tab, result.detail.lower())

    def test_bdd_check_prompts_fails_when_brief_below_minimum(self) -> None:
        """行为 7b: brief 只有 v1, 低于 2 → FAIL."""
        cl = self._write_changelog(
            brief_v=1, search_v=2, variables_v=3, design_v=3, exec_v=4
        )
        result = dod_check.check_prompt_iterations(changelog_path=cl)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("brief", result.detail.lower())

    def test_bdd_check_prompts_fails_when_execution_below_minimum(self) -> None:
        """行为 7c: execution 只有 v3, 低于 4 → FAIL."""
        cl = self._write_changelog(
            brief_v=2, search_v=2, variables_v=3, design_v=3, exec_v=3
        )
        result = dod_check.check_prompt_iterations(changelog_path=cl)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("execution", result.detail.lower())

    def test_bdd_check_prompts_handles_missing_file(self) -> None:
        """行为 7d: CHANGELOG 缺 → FAIL."""
        cl = self.tmp_path / "missing_CHANGELOG.md"
        result = dod_check.check_prompt_iterations(changelog_path=cl)
        self.assertEqual(result.status, "FAIL")

    def test_bdd_check_prompts_counts_max_v_per_tab(self) -> None:
        """行为 7e: v{N} 编号取最大值 (避免 v1+2+3 误算成 6)."""
        cl = self.tmp_path / "CHANGELOG.md"
        cl.write_text(
            "## brief\n"
            "- v1 (2026-06-04): a\n"
            "- v1 (2026-06-04): b\n"  # 重复
            "- v2 (2026-06-04): c\n"
            "## search\n- v1\n- v2\n"
            "## variables\n- v1\n- v2\n- v3\n"
            "## design\n- v1\n- v2\n- v3\n"
            "## execution (9 节)\n- v1\n- v2\n- v3\n- v4\n",
            encoding="utf-8",
        )
        result = dod_check.check_prompt_iterations(changelog_path=cl)
        self.assertEqual(result.status, "PASS")


# ── 行为 8: Token 成本 (NO CAP per L8 spec) ─────────────────────────────────


class TokenCostTests(unittest.TestCase):
    """行为 8: item 7 - token 成本 NO CAP, 仅 report (M3 via Token Plan)."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_bdd_check_token_cost_returns_pass_with_n_a_placeholder(self) -> None:
        """行为 8a: 无 LLM log file → 报告 'N/A' → PASS (M3 Token Plan 模式)."""
        result = dod_check.check_token_cost(repo_root=self.tmp_path)
        self.assertEqual(result.status, "PASS")
        self.assertIn("N/A", result.detail)
        self.assertIn("M3", result.detail)
        self.assertIn("Token Plan", result.detail)

    def test_bdd_check_token_cost_reports_spend_no_cap(self) -> None:
        """行为 8b: log file 含 cost_usd=30 → 报告 spend (NOT cap, 永远 PASS)."""
        log_dir = self.tmp_path / "logs" / "llm"
        log_dir.mkdir(parents=True)
        (log_dir / "session_001.jsonl").write_text(
            json.dumps({"cost_usd": 30.0, "prompt_tokens": 1000, "completion_tokens": 2000}) + "\n"
        )

        result = dod_check.check_token_cost(repo_root=self.tmp_path)
        # NO CAP → 即使 30 USD > 25 (旧上限), 仍 PASS
        self.assertEqual(result.status, "PASS")
        self.assertIn("30.00", result.detail)
        self.assertIn("NO CAP", result.detail)

    def test_bdd_check_token_cost_reports_small_spend(self) -> None:
        """行为 8c: log file 含 cost_usd=15 → 报告 15 USD → PASS."""
        log_dir = self.tmp_path / "logs" / "llm"
        log_dir.mkdir(parents=True)
        (log_dir / "session_001.jsonl").write_text(
            json.dumps({"cost_usd": 15.0, "prompt_tokens": 100, "completion_tokens": 200}) + "\n"
        )

        result = dod_check.check_token_cost(repo_root=self.tmp_path)
        self.assertEqual(result.status, "PASS")
        self.assertIn("15.00", result.detail)

    def test_bdd_check_token_cost_sums_multiple_files(self) -> None:
        """行为 8d: 多个 log file cost_usd 求和."""
        log_dir = self.tmp_path / "logs" / "llm"
        log_dir.mkdir(parents=True)
        (log_dir / "s1.jsonl").write_text(
            json.dumps({"cost_usd": 10.0}) + "\n" + json.dumps({"cost_usd": 5.0}) + "\n"
        )
        (log_dir / "s2.jsonl").write_text(json.dumps({"cost_usd": 3.0}) + "\n")

        result = dod_check.check_token_cost(repo_root=self.tmp_path)
        # 10 + 5 + 3 = 18 USD, 求和后报告
        self.assertEqual(result.status, "PASS")
        self.assertIn("18.00", result.detail)

    def test_bdd_check_token_cost_skips_malformed_lines(self) -> None:
        """行为 8e: 损坏的 JSON 行跳过."""
        log_dir = self.tmp_path / "logs" / "llm"
        log_dir.mkdir(parents=True)
        (log_dir / "s1.jsonl").write_text(
            "not-json\n"
            + json.dumps({"cost_usd": 5.0}) + "\n"
            + json.dumps({"wrong_key": 100}) + "\n"
        )

        result = dod_check.check_token_cost(repo_root=self.tmp_path)
        self.assertEqual(result.status, "PASS")
        self.assertIn("5.00", result.detail)


# ── 行为 8b: M3 model path (item 9) ──────────────────────────────────────────


class M3ModelPathTests(unittest.TestCase):
    """行为 8b: item 9 - 5 个 wrapper service 全部用 provider_id="minimax"."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_wrapper(self, name: str, provider: str = "minimax") -> None:
        """构造一个 wrapper service 文件, 注入指定 provider_id (literal string)."""
        path = self.tmp_path / f"{name}_service.py"
        # 必须写 literal provider_id="..." 才能被 check_m3_model_path 命中
        path.write_text(
            f'"""Mock wrapper."""\n'
            f'_PROVIDER_ID = "{provider}"\n'
            f'chat_completion(provider_id="{provider}", model="MiniMax-M3")\n'
        )

    def test_bdd_check_m3_model_path_passes_when_all_5_use_minimax(self) -> None:
        """行为 8b-a: 5 个 wrapper 全用 minimax → PASS."""
        for name in ("brief", "search", "variables", "design", "execute"):
            self._write_wrapper(name, provider="minimax")

        result = dod_check.check_m3_model_path(wrapper_dir=self.tmp_path)
        self.assertEqual(result.status, "PASS")
        self.assertIn("5 wrapper services", result.detail)
        self.assertIn("minimax", result.detail)

    def test_bdd_check_m3_model_path_fails_when_one_uses_openrouter(self) -> None:
        """行为 8b-b: 任一 wrapper 还在 openrouter → FAIL."""
        for name in ("brief", "search", "variables", "design"):
            self._write_wrapper(name, provider="minimax")
        # execute 还在 openrouter
        self._write_wrapper("execute", provider="openrouter")

        result = dod_check.check_m3_model_path(wrapper_dir=self.tmp_path)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("execute", result.detail)

    def test_bdd_check_m3_model_path_fails_when_one_uses_anthropic(self) -> None:
        """行为 8b-c: 任一 wrapper 还在 anthropic → FAIL."""
        for name in ("brief", "search", "variables", "design"):
            self._write_wrapper(name, provider="minimax")
        self._write_wrapper("execute", provider="anthropic")

        result = dod_check.check_m3_model_path(wrapper_dir=self.tmp_path)
        self.assertEqual(result.status, "FAIL")

    def test_bdd_check_m3_model_path_fails_when_wrapper_missing(self) -> None:
        """行为 8b-d: 缺某个 wrapper service → FAIL."""
        for name in ("brief", "search", "variables", "design"):
            self._write_wrapper(name)
        # 缺 execute_service.py

        result = dod_check.check_m3_model_path(wrapper_dir=self.tmp_path)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("missing", result.detail.lower())

    def test_bdd_check_m3_model_path_handles_single_quote_provider_id(self) -> None:
        """行为 8b-e: provider_id='minimax' (单引号) 也算 PASS."""
        path = self.tmp_path / "brief_service.py"
        path.write_text(
            "provider_id='minimax'\n"
        )
        for name in ("search", "variables", "design", "execute"):
            self._write_wrapper(name)
        result = dod_check.check_m3_model_path(wrapper_dir=self.tmp_path)
        self.assertEqual(result.status, "PASS")


# ── 行为 9: PM 验收 (manual) ─────────────────────────────────────────────────


class PmAcceptanceTests(unittest.TestCase):
    """行为 9: item 8 - PM 验收 manual flag."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_bdd_check_pm_acceptance_returns_manual_by_default(self) -> None:
        """行为 9a: 无 Program/dod_pm_accepted.txt → MANUAL."""
        result = dod_check.check_pm_acceptance(repo_root=self.tmp_path)
        self.assertEqual(result.status, "MANUAL")
        self.assertIn("PM", result.detail)

    def test_bdd_check_pm_acceptance_returns_pass_when_flag_exists(self) -> None:
        """行为 9b: dod_pm_accepted.txt 存在 → PASS."""
        flag = self.tmp_path / "Program" / "dod_pm_accepted.txt"
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text("PM 已手动验收 5 tab + paper.pdf\n")

        result = dod_check.check_pm_acceptance(repo_root=self.tmp_path)
        self.assertEqual(result.status, "PASS")


# ── 行为 10: 整体 check_dod + 退出码 + 报告 ──────────────────────────────────


class CheckDodIntegrationTests(unittest.TestCase):
    """行为 10: check_dod() 整体 + run_check() 退出码."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _build_compliant_fixture(self) -> None:
        """构造一个基本合规的 fixture repo (所有 9 项都能 PASS)."""
        # spec_runner.py
        (self.tmp_path / "Program" / "spec_runner.py").parent.mkdir(parents=True, exist_ok=True)
        (self.tmp_path / "Program" / "spec_runner.py").write_text("# stub\n")
        # CHANGELOG.md
        cl = self.tmp_path / "Program" / "prompts" / "CHANGELOG.md"
        cl.parent.mkdir(parents=True, exist_ok=True)
        cl.write_text(
            "## brief\n- v1\n- v2\n\n## search\n- v1\n- v2\n\n"
            "## variables\n- v1\n- v2\n- v3\n\n## design\n- v1\n- v2\n- v3\n\n"
            "## execution (9 节)\n- v1\n- v2\n- v3\n- v4\n"
        )
        # 5 wrapper 测试
        (self.tmp_path / "tests" / "wrapper").mkdir(parents=True)
        for name in ("brief", "search", "variables", "design", "execute"):
            (self.tmp_path / "tests" / "wrapper" / f"test_{name}_service.py").write_text(
                "def test_x(): pass\n"
            )
        # 5 endpoints
        (self.tmp_path / "Product" / "api").mkdir(parents=True)
        for name in ("brief", "search", "variables", "design", "execute"):
            (self.tmp_path / "Product" / "api" / f"{name}.py").write_text(
                "from fastapi import APIRouter, HTTPException\n"
                "router = APIRouter()\n"
                f"@router.post('/api/{name}')\n"
                "def p():\n    try:\n        return {}\n"
                "    except Exception as e:\n        raise HTTPException(500, str(e))\n"
            )
        # 5 wrapper services (M3 path) — Item 9
        (self.tmp_path / "Product" / "backend" / "wrapper").mkdir(parents=True)
        for name in ("brief", "search", "variables", "design", "execute"):
            (self.tmp_path / "Product" / "backend" / "wrapper" / f"{name}_service.py").write_text(
                '_PROVIDER_ID = "minimax"\n'
                'chat_completion(provider_id="minimax", model="MiniMax-M3")\n'
            )
        # artifacts
        for d in ("Tasks", "Manuscripts", "Results"):
            (self.tmp_path / d / "foo").mkdir(parents=True)
        # e2e
        e2e_dir = self.tmp_path / "Product" / "web-react" / "e2e"
        e2e_dir.mkdir(parents=True)
        (e2e_dir / "end-to-end.spec.ts").write_text("// x\n")
        # PM flag
        (self.tmp_path / "Program" / "dod_pm_accepted.txt").write_text("PM ok\n")

    def test_bdd_check_dod_returns_summary_with_counts(self) -> None:
        """行为 10a: check_dod() 返回 dict 含 'items' + 'summary'."""
        result = dod_check.check_dod(repo_root=self.tmp_path)
        self.assertIn("items", result)
        self.assertIn("summary", result)
        self.assertEqual(result["summary"]["total"], 9)

    def test_bdd_check_dod_exit_code_zero_when_all_pass_or_manual(self) -> None:
        """行为 10b: 所有 PASS/MANUAL 时 exit code 0."""
        self._build_compliant_fixture()
        with patch("subprocess.run") as mock_run:
            # 模拟 5 个 wrapper pytest 全 pass
            mock_run.return_value = subprocess.CompletedProcess(
                ["pytest"], 0, "5 passed", ""
            )
            exit_code = dod_check.run_check(repo_root=self.tmp_path, exit_on_fail=False)
        self.assertEqual(exit_code, 0, f"expected exit 0, got {exit_code}")

    def test_bdd_check_dod_exit_code_one_when_any_fail(self) -> None:
        """行为 10c: 空 repo → 多个 FAIL → exit code 1."""
        # 不构造 fixture, 全部应 FAIL
        exit_code = dod_check.run_check(repo_root=self.tmp_path, exit_on_fail=False)
        self.assertEqual(exit_code, 1)


# ── 行为 11: print_report / 报告格式 ──────────────────────────────────────────


class ReportFormatTests(unittest.TestCase):
    """行为 11: print_report 输出 [PASS]/[FAIL]/[MANUAL] 行."""

    def test_bdd_print_report_format(self) -> None:
        """行为 11a: 每行以 [STATUS] 开头 + 编号 + 名字 + 详情."""
        import io
        from contextlib import redirect_stdout

        items = [
            dod_check.DoDItem(item=1, name="5 tab BDD", status="PASS", detail="all 5 pass"),
            dod_check.DoDItem(item=2, name="60min e2e", status="FAIL", detail="missing spec"),
            dod_check.DoDItem(item=3, name="PM accept", status="MANUAL", detail="awaiting PM"),
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            dod_check.print_report(items)
        captured = buf.getvalue()
        self.assertIn("[PASS]", captured)
        self.assertIn("[FAIL]", captured)
        self.assertIn("[MANUAL]", captured)
        self.assertIn("5 tab BDD", captured)
        self.assertIn("60min e2e", captured)
        self.assertIn("PM accept", captured)

    def test_bdd_print_report_separator(self) -> None:
        """行为 11b: 报告用 ==== 分隔 (可读性)."""
        import io
        from contextlib import redirect_stdout

        items = [dod_check.DoDItem(item=1, name="x", status="PASS", detail="d")]
        buf = io.StringIO()
        with redirect_stdout(buf):
            dod_check.print_report(items)
        captured = buf.getvalue()
        # 上下分隔线
        self.assertIn("=" * 70, captured)


if __name__ == "__main__":
    unittest.main()
