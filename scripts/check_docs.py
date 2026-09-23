#!/usr/bin/env python3
"""Documentation health check (`make docs-check`).

Checks, in order:
  1. links   — every relative Markdown link in README.md, AGENTS.md and docs/**
               points at an existing file.
  2. orphans — every docs/**/*.md is reachable from README.md by following links
               (evidence folders are exempt; see ORPHAN_EXEMPT).
  3. size    — no doc exceeds MAX_LINES unless it is a historical record listed
               in docs/.doc-size-baseline, and a listed doc may not grow past its
               recorded size. Split oversized docs; do not raise the baseline.
  4. sync    — with --changed <base>, code areas touched since <base> (plus the
               working tree) must be accompanied by a change in their docs
               (see DOC_MAP). Advisory by default; --strict makes it fail.

Standard library only; run from any directory.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BASELINE = DOCS / ".doc-size-baseline"
MAX_LINES = 400

# Evidence and generated material: linked as folders, not file by file.
ORPHAN_EXEMPT = [
    "docs/acceptance/assets/*",
    "docs/acceptance/evidence-*",
    "docs/acceptance/shots/*",
    "docs/design/*/shots/*",
    "docs/design/od-fullflow-screenshots/*",
]

# Code area -> docs that must change alongside it. First matching rule wins.
DOC_MAP: list[tuple[str, list[str], str]] = [
    ("backend/routers/*", ["docs/api/*"], "HTTP 端点变更 → docs/api/"),
    ("backend/schemas/*", ["docs/api/*", "frontend/openapi.json"], "响应模型变更 → docs/api/"),
    ("backend/main.py", ["docs/api/*"], "应用装配变更 → docs/api/"),
    ("frontend/src/components/*", ["docs/specs/frontend-interaction-current.md", "docs/specs/*", "docs/product/*"], "界面行为变更 → 前端交互基线"),
    ("frontend/src/App.tsx", ["docs/specs/frontend-interaction-current.md", "docs/specs/*", "docs/product/*"], "界面行为变更 → 前端交互基线"),
    ("agent/nodes/*", ["docs/specs/*", "docs/adr/*", "docs/contracts/*", "docs/product/glossary.md"], "Agent 节点变更 → 规格/契约"),
    ("agent/engine/*", ["docs/specs/*", "docs/adr/*", "docs/contracts/*"], "计量引擎变更 → 规格/契约"),
    ("agent/llm/*", ["docs/adr/0008-multi-llm-routing.md", "docs/deployment/README.md", "docs/deployment/*"], "LLM 路由变更 → ADR-0008 / 部署配置"),
    ("backend/services/*", ["docs/contracts/*", "docs/specs/*", "docs/api/*"], "后端服务变更 → 契约/规格"),
    ("Makefile", ["README.md", "docs/dev/local-runner.md", "docs/deployment/README.md"], "开发命令变更 → README / local-runner"),
    ("docker-compose.yml", ["docs/deployment/README.md", "docs/deployment/*"], "部署拓扑变更 → 部署文档"),
    ("deploy/*", ["docs/deployment/README.md", "docs/deployment/*"], "部署拓扑变更 → 部署文档"),
    (".env.docker", ["docs/deployment/README.md"], "环境变量变更 → 部署文档"),
]
SYNC_IGNORE = ["*/tests/*", "*/__tests__/*", "*.test.ts", "*.test.tsx", "test_*.py"]

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^(```|~~~)")


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in patterns)


def doc_files() -> list[Path]:
    files = [ROOT / "README.md", ROOT / "AGENTS.md"]
    files += sorted(p for p in DOCS.rglob("*.md") if "node_modules" not in p.parts)
    return [p for p in files if p.exists()]


def links_of(md: Path) -> list[tuple[int, str]]:
    out, fenced = [], False
    for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE_RE.match(line.strip()):
            fenced = not fenced
            continue
        if fenced:
            continue
        for target in LINK_RE.findall(line):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                continue
            out.append((n, target.split("#", 1)[0]))
    return out


def resolve(md: Path, target: str) -> Path:
    from urllib.parse import unquote

    return (md.parent / unquote(target)).resolve()


def check_links(files: list[Path]) -> list[str]:
    errors = []
    for md in files:
        for n, target in links_of(md):
            if not resolve(md, target).exists():
                errors.append(f"{rel(md)}:{n}: broken link → {target}")
    return errors


def check_orphans() -> list[str]:
    seen: set[Path] = set()
    queue = [ROOT / "README.md"]
    while queue:
        md = queue.pop()
        if md in seen or not md.exists():
            continue
        seen.add(md)
        for _, target in links_of(md):
            dest = resolve(md, target)
            if dest.is_dir() and (dest / "README.md").exists():
                dest = dest / "README.md"
            if dest.suffix == ".md" and dest.is_file():
                queue.append(dest)
    orphans = []
    for md in sorted(DOCS.rglob("*.md")):
        r = rel(md)
        if md.resolve() not in {s.resolve() for s in seen} and not matches(r, ORPHAN_EXEMPT):
            orphans.append(f"{r}: not reachable from README.md → add it to its folder README.md")
    return orphans


def read_baseline() -> dict[str, int]:
    if not BASELINE.exists():
        return {}
    out = {}
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            count, path = line.split(None, 1)
            out[path] = int(count)
    return out


def check_size(files: list[Path]) -> tuple[list[str], list[str]]:
    baseline, errors, debt = read_baseline(), [], []
    for md in files:
        r = rel(md)
        if matches(r, ORPHAN_EXEMPT):
            continue
        n = len(md.read_text(encoding="utf-8").splitlines())
        if n <= MAX_LINES:
            continue
        allowed = baseline.get(r)
        if allowed is None:
            errors.append(f"{r}: {n} lines > {MAX_LINES} → split into an overview + linked section files")
        elif n > allowed:
            errors.append(f"{r}: grew {allowed} → {n} lines; it is on the split list, shrink it instead")
        else:
            debt.append(f"{r}: {n} lines (frozen at {allowed})")
    return errors, debt


def changed_paths(base: str) -> list[str]:
    def git(*args: str) -> list[str]:
        res = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True)
        return [l for l in res.stdout.splitlines() if l]

    paths = set(git("diff", "--name-only", f"{base}...HEAD"))
    paths |= set(git("diff", "--name-only", "HEAD"))
    paths |= set(git("ls-files", "--others", "--exclude-standard"))
    return sorted(paths)


def check_sync(paths: list[str]) -> list[str]:
    problems = []
    for pattern, docs, why in DOC_MAP:
        code = [p for p in paths if fnmatch.fnmatch(p, pattern) and not matches(p, SYNC_IGNORE)]
        if code and not any(matches(p, docs) for p in paths):
            problems.append(f"{why}: {len(code)} file(s) changed (e.g. {code[0]}), no change under {', '.join(docs)}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--changed", metavar="BASE", help="also check code→doc sync against git BASE (e.g. main)")
    ap.add_argument("--strict", action="store_true", help="make sync problems fail the check")
    args = ap.parse_args()

    files = doc_files()
    failures = 0

    def section(title: str, items: list[str], fatal: bool = True) -> None:
        nonlocal failures
        mark = "FAIL" if items and fatal else ("WARN" if items else "ok")
        print(f"[{mark}] {title} ({len(items)})")
        for item in items:
            print(f"  - {item}")
        if items and fatal:
            failures += 1

    section("broken links", check_links(files))
    section("orphan docs", check_orphans())
    size_errors, debt = check_size(files)
    section(f"oversized docs (> {MAX_LINES} lines)", size_errors)
    section("frozen oversized records (docs/.doc-size-baseline)", debt, fatal=False)
    if args.changed:
        section(f"code → doc sync vs {args.changed}", check_sync(changed_paths(args.changed)), fatal=args.strict)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
