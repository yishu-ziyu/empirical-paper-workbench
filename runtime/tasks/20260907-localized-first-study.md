# econpaper Codex Task State

- Task ID: 20260907-localized-first-study
- Status: active
- Git context（分支可选）: `review/localized-first-study` from `main @ 87c5e5b`; round 2 start `c9d3638`; PR #32
- Goal: 中文/英文用户各自走完真实 Card 研究路径；语言切换只改展示；Promote/Stale 帮助语义正确；盘点路径诚实。
- Hard bar: `docs/acceptance/localized-first-study.md` C8–C12（C1–C7 不削弱）
- Session / run ID: 隔离 5174/8001；`ECONPAPER_LOCAL_STATE_ROOT=/tmp/econpaper-lfs-r2`；Playwright 独立 Chrome
- Current research stage: Phase B round 2 implementer complete, awaiting r2 validator
- Current review / approval gate: push PR #32; do not merge
- Verified facts: Scene A/B/C vitest pass (restore GET and EventSource unchanged). make test 819/451/419, existing skips only. Card Compare language switch screenshots exist.
- Current hypothesis: stable `t` via langRef + workspace tRef; presentation adapter keyed by spec id / criterion refs
- Changed files: i18n.tsx, workspace.ts, i18nPresentation.ts, i18nWorkbench.ts, Overview/Evidence/Research/EvidenceLab/AgentCursor, inventory/terminology, screenshots, r2 implementer report
- Failed paths: Chrome DevTools MCP could not attach; used Playwright isolated Chrome. Isolated Card paper write blocked by canonical_mismatch.
- Data / output evidence locations: `docs/acceptance/assets/localized-first-study/`; `docs/acceptance/localized-first-study-r2-implementer.md`
- Test evidence: `make test` 2026-09-07 r2; vitest 419; tsc/lint/build 0
- Pending external state: r2 validator; issue #30 and phase C out of scope
- Next action: independent r2 validator; do not merge
- Updated at: 2026-09-07
