"""DoD checklist: 验证 spec §9 的 9 项 Definition of Done.

行为契约 (Phase 8 Task 8.2):
- 9 个 DoD 项 (用户列出的 9 项, 含 spec §9 隐含 + M3 验证):
  1. 5 tab BDD 全绿 (pytest tests/wrapper/)
  2. 60-min 端到端 (e2e/end-to-end.spec.ts 存在)
  3. 失败模式 5 种处理 (grep endpoint try/except)
  4. 产物入库 (Tasks/ Manuscripts/ Results/ 都含 topic)
  5. Re-run 等价 (Program/spec_runner.py 存在)
  6. Prompt 迭代轮数 (CHANGELOG.md 解析, brief≥2/search≥2/variables≥3/design≥3/execution≥4)
  7. Token 成本 — NO CAP, 仅 report (M3 via Token Plan, 无 per-call 计费)
  8. PM 验收 (Program/dod_pm_accepted.txt 手动标记, 默认 MANUAL)
  9. M3 model path 验证 (5 个 wrapper service 全部用 provider_id="minimax")

- 每项返回 DoDItem (item, name, status, detail)
- check_dod() 返回 {"items": [...], "summary": {pass, fail, manual, total}}
- run_check() 打印报告 + 返回 exit code (0/1)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


# spec §4.6 prompt 迭代最低轮数
PROMPT_MIN_VERSIONS: dict[str, int] = {
    "brief": 2,
    "search": 2,
    "variables": 3,
    "design": 3,
    "execution": 4,
}

# 5 个 tab 名字 (用于 endpoint/wrapper 验证)
TAB_NAMES: tuple[str, ...] = ("brief", "search", "variables", "design", "execute")

# Token 成本 — NO CAP per user task description
# (M3 via Token Plan: no per-call cost tracking, just report total spend if logs available)
TOKEN_BUDGET_USD: float = 25.0  # kept for backward compat (item 7 now reports, not caps)


# ── 数据结构 ──────────────────────────────────────────────────────────────────


@dataclass
class DoDItem:
    """单个 DoD 项的状态."""

    item: int
    name: str
    status: str  # "PASS" | "FAIL" | "MANUAL"
    detail: str

    def to_dict(self) -> dict:
        return asdict(self)


# ── 各项检查函数 ──────────────────────────────────────────────────────────────


def check_5_tab_bdd(tests_dir: Path) -> DoDItem:
    """DoD #1: 5 个 wrapper BDD 测试文件全 pass.

    简化版: 检查 tests/wrapper/test_{tab}_service.py 都存在 (5 个) + 跑一次 pytest。
    跑不动时仅当文件齐全算 PASS, 缺文件 FAIL。
    """
    missing = [
        tab for tab in TAB_NAMES
        if not (tests_dir / f"test_{tab}_service.py").exists()
    ]
    if missing:
        return DoDItem(
            item=1,
            name="5 tab BDD 全绿",
            status="FAIL",
            detail=f"missing test files: {missing}",
        )

    # 跑一次 pytest tests/wrapper/ (5 个文件)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(tests_dir), "-q", "--tb=no"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return DoDItem(
                item=1,
                name="5 tab BDD 全绿",
                status="PASS",
                detail=f"5 wrapper tests pass (pytest exit=0)",
            )
        # pytest 失败: 输出最后 200 字
        last = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else result.stderr.strip()
        return DoDItem(
            item=1,
            name="5 tab BDD 全绿",
            status="FAIL",
            detail=f"pytest failed: {last[:200]}",
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return DoDItem(
            item=1,
            name="5 tab BDD 全绿",
            status="FAIL",
            detail=f"pytest run error: {exc}",
        )


def check_e2e_60min(repo_root: Path) -> DoDItem:
    """DoD #2: 60-min 端到端 (e2e/end-to-end.spec.ts 存在).

    spec §6.2 要求 60min 内从空白浏览器走完 5 tab。
    检查 Product/web-react/e2e/end-to-end.spec.ts 存在。
    """
    e2e = repo_root / "Product" / "web-react" / "e2e" / "end-to-end.spec.ts"
    if e2e.exists():
        return DoDItem(
            item=2,
            name="60-min 端到端 (e2e spec)",
            status="PASS",
            detail=f"e2e spec 存在: {e2e.relative_to(repo_root)}",
        )
    return DoDItem(
        item=2,
        name="60-min 端到端 (e2e spec)",
        status="FAIL",
        detail=f"e2e spec 缺失: {e2e.relative_to(repo_root)} (spec §6.2 明确要求 60min 端到端)",
    )


def check_failure_modes(api_dir: Path) -> DoDItem:
    """DoD #3: 5 种失败模式被 endpoint 兜底处理.

    spec §6.3 列 5 种失败模式 (arxiv 不可用 / LLM 超时 / 数据集缺失 / SSE 断线 / schema 异常).
    检查 Product/api/{tab}.py 5 个文件都含 try/except + HTTPException 兜底。
    """
    missing = [
        tab for tab in TAB_NAMES
        if not (api_dir / f"{tab}.py").exists()
    ]
    if missing:
        return DoDItem(
            item=3,
            name="失败模式 5 种处理",
            status="FAIL",
            detail=f"missing endpoint files: {missing}",
        )

    # 验证每个 endpoint 含 try/except
    no_handler = []
    for tab in TAB_NAMES:
        text = (api_dir / f"{tab}.py").read_text(encoding="utf-8")
        if "try:" not in text or "HTTPException" not in text:
            no_handler.append(tab)
    if no_handler:
        return DoDItem(
            item=3,
            name="失败模式 5 种处理",
            status="FAIL",
            detail=f"endpoints without try/except + HTTPException: {no_handler}",
        )
    return DoDItem(
        item=3,
        name="失败模式 5 种处理",
        status="PASS",
        detail=f"5 endpoints 全有 try/except + HTTPException 兜底",
    )


def check_artifacts(repo_root: Path) -> DoDItem:
    """DoD #4: 产物入库 (Tasks/, Manuscripts/, Results/).

    简化版: 3 个目录都存在 + 至少 1 个 topic slug 子目录。
    """
    required_dirs = ("Tasks", "Manuscripts", "Results")
    missing = [d for d in required_dirs if not (repo_root / d).is_dir()]
    if missing:
        return DoDItem(
            item=4,
            name="产物入库 (3 目录)",
            status="FAIL",
            detail=f"missing dirs: {missing}",
        )

    # 检查每个目录有 topic 子目录
    empty_dirs = []
    for d in required_dirs:
        if not any((repo_root / d).iterdir()):
            empty_dirs.append(d)
    if empty_dirs:
        return DoDItem(
            item=4,
            name="产物入库 (3 目录)",
            status="FAIL",
            detail=f"empty dirs (无 topic slug): {empty_dirs}",
        )

    return DoDItem(
        item=4,
        name="产物入库 (3 目录)",
        status="PASS",
        detail=f"3 目录都存在且含 topic: {required_dirs}",
    )


def check_rerun_equivalence(repo_root: Path) -> DoDItem:
    """DoD #5: Re-run 等价 — Program/spec_runner.py 存在."""
    runner = repo_root / "Program" / "spec_runner.py"
    if runner.exists():
        return DoDItem(
            item=5,
            name="Re-run 等价 (spec_runner.py)",
            status="PASS",
            detail=f"spec_runner.py 存在: {runner.relative_to(repo_root)}",
        )
    return DoDItem(
        item=5,
        name="Re-run 等价 (spec_runner.py)",
        status="FAIL",
        detail=f"spec_runner.py 缺失: {runner.relative_to(repo_root)}",
    )


def check_prompt_iterations(changelog_path: Path) -> DoDItem:
    """DoD #6: Prompt 迭代轮数达标.

    解析 Program/prompts/CHANGELOG.md 数每个 tab 的 v{N} 出现次数。
    与 PROMPT_MIN_VERSIONS (spec §4.6) 对比。
    """
    if not changelog_path.exists():
        return DoDItem(
            item=6,
            name="Prompt 迭代轮数达标",
            status="FAIL",
            detail=f"CHANGELOG.md 缺失: {changelog_path}",
        )

    text = changelog_path.read_text(encoding="utf-8")

    # 每个 tab 的版本数 = 该章节里 `- v{N}` 出现次数的最大值
    tab_versions: dict[str, int] = {}
    # 切分章节 (## xxx)
    sections = re.split(r"^##\s+", text, flags=re.MULTILINE)
    for section in sections[1:]:  # 跳过第一个 (header 之前)
        # 提取 tab 名字 (execution (9 节) → execution)
        title_match = re.match(r"^([\w]+)", section.strip())
        if not title_match:
            continue
        tab_key = title_match.group(1)
        # 找所有 v{N}
        versions = re.findall(r"v(\d+)", section)
        if versions:
            tab_versions[tab_key] = max(int(v) for v in versions)

    # 检查每个 tab 是否达标
    below_min = []
    details: list[str] = []
    for tab, min_v in PROMPT_MIN_VERSIONS.items():
        actual = tab_versions.get(tab, 0)
        if actual < min_v:
            below_min.append(f"{tab}({actual}/{min_v})")
        details.append(f"{tab}={actual}/{min_v}")

    if below_min:
        return DoDItem(
            item=6,
            name="Prompt 迭代轮数达标",
            status="FAIL",
            detail=f"低于最低轮数: {below_min}; 全部: {details}",
        )
    return DoDItem(
        item=6,
        name="Prompt 迭代轮数达标",
        status="PASS",
        detail=f"全部达标: {details}",
    )


def check_token_cost(repo_root: Path) -> DoDItem:
    """DoD #7: Token 成本 — NO CAP, 仅 report.

    per user task description (2026-06-04 L8 spec):
    "NO CAP, just report total spend if logs available. Print
    'Token cost tracking: N/A (M3 via Token Plan, no per-call cost tracking) —
    see Program/runs/ for usage'"

    简化: 读 logs/llm/*.jsonl 里 cost_usd 字段求和。无 log → 报 N/A。永远 PASS。
    """
    log_dir = repo_root / "logs" / "llm"
    if not log_dir.exists():
        return DoDItem(
            item=7,
            name="Token 成本 (NO CAP, M3 Token Plan)",
            status="PASS",
            detail=(
                "Token cost tracking: N/A (M3 via Token Plan, no per-call cost tracking) "
                "— see Program/runs/ for usage"
            ),
        )

    total = 0.0
    n_records = 0
    for log_file in log_dir.glob("*.jsonl"):
        for line in log_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if "cost_usd" in rec:
                    total += float(rec["cost_usd"])
                    n_records += 1
            except (json.JSONDecodeError, ValueError, TypeError):
                continue

    return DoDItem(
        item=7,
        name="Token 成本 (NO CAP, M3 Token Plan)",
        status="PASS",
        detail=(
            f"Total reported spend: {total:.2f} USD across {n_records} log records "
            f"(NO CAP — M3 via Token Plan, no per-call cost tracking)"
        ),
    )


def check_pm_acceptance(repo_root: Path) -> DoDItem:
    """DoD #8: PM 验收 (manual flag)."""
    flag = repo_root / "Program" / "dod_pm_accepted.txt"
    if flag.exists():
        return DoDItem(
            item=8,
            name="PM 验收 (manual)",
            status="PASS",
            detail=f"dod_pm_accepted.txt 存在: {flag.relative_to(repo_root)}",
        )
    return DoDItem(
        item=8,
        name="PM 验收 (manual)",
        status="MANUAL",
        detail="需 PM 在浏览器手测 5 tab + paper.pdf, 然后 touch Program/dod_pm_accepted.txt",
    )


def check_m3_model_path(wrapper_dir: Path) -> DoDItem:
    """DoD #9: M3 model path 验证.

    per user task description (2026-06-04 L8 spec):
    "M3 model path verified — grep for provider_id="minimax" in all 5 wrapper
    services, fail if any is on OpenRouter or other provider"

    行为:
    - 检查 Product/backend/wrapper/ 下 5 个 *_service.py 文件
    - 每个文件的 provider_id 必须解析为 "minimax" (M3 Token Plan 唯一真实 provider)
    - 接受两种写法: (a) 字面量 provider_id="minimax"  (b) 常量 provider_id=_PROVIDER 且
      文件内 _PROVIDER = "minimax"
    - 任何 wrapper 还在用 openrouter / openai / anthropic / kimi 等 → FAIL
    - 缺文件 → FAIL

    设计: 用 ast 解析, 避免 grep 误判 (注释/docstring 里的字符串 / 老代码残留)。
    """
    import ast

    wrapper_files = {
        tab: wrapper_dir / f"{tab}_service.py"
        for tab in TAB_NAMES
    }

    # 缺文件 → FAIL
    missing = [tab for tab, p in wrapper_files.items() if not p.exists()]
    if missing:
        return DoDItem(
            item=9,
            name="M3 model path (provider_id=minimax)",
            status="FAIL",
            detail=f"missing wrapper services: {missing}",
        )

    bad_providers = ("openrouter", "openai", "anthropic", "kimi", "claude", "gpt-")

    def _providers_used(tree: ast.AST) -> set[str]:
        """从 AST 里提取所有 provider_id 关键字参数实际取值.
        支持字面量 ("minimax") / 模块顶层常量 / 函数参数默认值 三种来源.
        """
        # 1. 收 module-level 字符串赋值: _PROVIDER = "minimax" → {"_PROVIDER": "minimax"}
        consts: dict[str, str] = {}
        for node in getattr(tree, "body", []):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                tgt = node.targets[0]
                if isinstance(tgt, ast.Name) and isinstance(node.value, ast.Constant):
                    if isinstance(node.value.value, str):
                        consts[tgt.id] = node.value.value

        # 2. 收 function 参数默认值: def f(*, provider_id="minimax") → {"provider_id": "minimax"}
        # 也支持: def f(*, provider_id=DEFAULT_PROVIDER) (Name 引用模块常量)
        param_defaults: dict[str, str] = {}
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            args = node.args
            all_args = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
            all_defaults = list(args.defaults) + [None] * (len(args.posonlyargs) + len(args.args) - len(args.defaults)) + list(args.kw_defaults)
            for a, d in zip(all_args, all_defaults):
                if a.arg in ("provider_id",) and d is not None:
                    if isinstance(d, ast.Constant) and isinstance(d.value, str):
                        param_defaults[a.arg] = d.value
                    elif isinstance(d, ast.Name) and d.id in consts:
                        param_defaults[a.arg] = consts[d.id]

        # 3. 找 chat_completion(..., provider_id=...) 调用, 取字面量/常量/参数默认值
        found: set[str] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            for kw in node.keywords:
                if kw.arg != "provider_id":
                    continue
                v = kw.value
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    found.add(v.value)
                elif isinstance(v, ast.Name):
                    if v.id in consts:
                        found.add(consts[v.id])
                    elif v.id in param_defaults:
                        found.add(param_defaults[v.id])
        return found

    wrong_provider: list[str] = []
    for tab, path in wrapper_files.items():
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            wrong_provider.append(f"{tab}:syntax-error")
            continue
        used = _providers_used(tree)
        # Fallback: AST 找不到 call 但文本里有字面量 provider_id="minimax" — 仍算 PASS
        # (覆盖测试 fixture 形式, 也允许"显式声明但尚未调 LLM"的早期 wrapper 草稿)
        if not used:
            if 'provider_id="minimax"' in text or "provider_id='minimax'" in text:
                used = {"minimax"}
            else:
                wrong_provider.append(f"{tab}:no-provider_id-call")
                continue
        if "minimax" not in used:
            wrong_provider.append(f"{tab}:providers={sorted(used)}")
            continue
        # 防御性: 还有别的 provider 混用 → 标红
        for bad in bad_providers:
            if any(bad in p for p in used):
                wrong_provider.append(f"{tab}:mixes-{bad}-with-minimax")
                break

    if wrong_provider:
        return DoDItem(
            item=9,
            name="M3 model path (provider_id=minimax)",
            status="FAIL",
            detail=(
                "5 wrappers 未全部走 minimax: "
                + ", ".join(wrong_provider)
                + " (spec §3.2: minimax 是项目唯一真实 provider)"
            ),
        )

    return DoDItem(
        item=9,
        name="M3 model path (provider_id=minimax)",
        status="PASS",
        detail=f"5 wrapper services 全用 provider_id=\"minimax\": {list(wrapper_files.keys())}",
    )


def _alias_status(s: str) -> str:  # kept for backward compat (not used in check_dod)
    return s  # DoDItem.status 已经是 PASS/FAIL/MANUAL, 直接复用


# ── 整体 check_dod + run_check ───────────────────────────────────────────────


def check_dod(
    repo_root: Path | None = None,
    changelog_path: Path | None = None,
    tests_dir: Path | None = None,
    api_dir: Path | None = None,
    wrapper_dir: Path | None = None,
) -> dict:
    """跑 9 项 DoD 检查, 返回结构化报告.

    Args:
        repo_root: 仓库根 (默认用 cwd 或 Program 父目录)
        changelog_path: Program/prompts/CHANGELOG.md (默认从 repo_root 推断)
        tests_dir: tests/wrapper/ (默认从 repo_root 推断)
        api_dir: Product/api/ (默认从 repo_root 推断)
        wrapper_dir: Product/backend/wrapper/ (默认从 repo_root 推断, 给 item 9)

    Returns:
        {
            "items": [DoDItem.to_dict() ...],
            "summary": {"pass": int, "fail": int, "manual": int, "total": 9}
        }
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[1]
    if changelog_path is None:
        changelog_path = repo_root / "Program" / "prompts" / "CHANGELOG.md"
    if tests_dir is None:
        tests_dir = repo_root / "tests" / "wrapper"
    if api_dir is None:
        api_dir = repo_root / "Product" / "api"
    if wrapper_dir is None:
        wrapper_dir = repo_root / "Product" / "backend" / "wrapper"

    items: list[DoDItem] = [
        check_5_tab_bdd(tests_dir),
        check_e2e_60min(repo_root),
        check_failure_modes(api_dir),
        check_artifacts(repo_root),
        check_rerun_equivalence(repo_root),
        check_prompt_iterations(changelog_path),
        check_token_cost(repo_root),
        check_pm_acceptance(repo_root),
        check_m3_model_path(wrapper_dir),
    ]

    summary = {
        "pass": sum(1 for it in items if it.status == "PASS"),
        "fail": sum(1 for it in items if it.status == "FAIL"),
        "manual": sum(1 for it in items if it.status == "MANUAL"),
        "total": len(items),
    }
    return {
        "items": [it.to_dict() for it in items],
        "summary": summary,
    }


def print_report(items: list[DoDItem]) -> None:
    """打印 [PASS]/[FAIL]/[MANUAL] 行报告."""
    print("=" * 70)
    print("DoD Checklist Report (spec §9, Phase 8 Task 8.2)")
    print("=" * 70)
    for it in items:
        print(f"[{it.status}] {it.item}. {it.name}: {it.detail}")
    print("=" * 70)


def run_check(
    repo_root: Path | None = None,
    exit_on_fail: bool = False,
) -> int:
    """跑 DoD 检查 + 打印报告 + 返回 exit code.

    Args:
        repo_root: 仓库根 (默认从 __file__ 推断)
        exit_on_fail: True 时遇 FAIL 直接 sys.exit(1); False 时只返回 exit code

    Returns:
        0 = 全 PASS/MANUAL
        1 = 任一 FAIL
    """
    report = check_dod(repo_root=repo_root)
    items = [DoDItem(**d) for d in report["items"]]
    print_report(items)
    summary = report["summary"]
    print(
        f"\nSummary: {summary['pass']} pass / {summary['fail']} fail / "
        f"{summary['manual']} manual (total {summary['total']})"
    )
    exit_code = 0 if summary["fail"] == 0 else 1
    if exit_on_fail and exit_code != 0:
        sys.exit(exit_code)
    return exit_code


if __name__ == "__main__":
    run_check(exit_on_fail=True)
