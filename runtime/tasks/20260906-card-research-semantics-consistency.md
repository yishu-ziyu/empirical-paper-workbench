# econpaper Codex Task State

- Task ID: 20260906-card-research-semantics-consistency
- Status: complete
- Git context: `review/workbench-v2` / PR #28
- Goal: 修 3 个 research-semantics consistency fixes；不 merge、不 redesign、不扩功能
- Hard bar: `docs/acceptance/card-research-semantics-consistency.md` S1–S8
- Session / run ID: `9ffc700d-f272-40a5-9011-0605fd1fd3c8`
- Current research stage: closed
- Current review / approval gate: validator ACCEPT；浏览器 S5–S7 由主 agent 完成
- Verified facts: promote/revert 不 bump evidence_revision（A: 1→1）；preview 仍 bump（B: 1→2）；wording 拒绝无空白句切与 LATE-as-ATE；stale fail-closed 共用 `claim_revision_is_stale`
- Changed files: research_lab.py, claim_wording.py, readiness.py, AgentRail.tsx, 对应测试, 契约, 截图
- Failed paths:
- Data / output evidence locations: `docs/acceptance/evidence-card-semantics/`
- Test evidence: agent 819/1skip；backend 421/8skip；frontend 348；tsc/lint/build/api-drift
- Pending external state: push PR #28；不 merge
- Next action: CI on PR #28
- Updated at: 2026-09-06
