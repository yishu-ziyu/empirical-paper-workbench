# econpaper Codex Task State

- Task ID: 20260907-m1-expectation-criterion-p0
- Status: complete
- Git context: `review/generic-research-spine-hardening` / PR #31
- Goal: 只修 M1 ExpectationCriterion 最后研究语义（P0-1..P0-4）。M0/M2/M3/M4 不改。不 merge。
- Hard bar: `docs/acceptance/generic-research-spine-hardening.md` C29–C37 全绿；seed 绑定 exact comparable spec_id；后来的 OLS preview 不漂移 Surprise；非法组合 422；equality/zero 边界；unresolved → Unevaluated；post-reveal criterion 409 锁定。
- Session / run ID:
- Current research stage: M1 P0 implementation
- Current review / approval gate: PR #31 external REQUEST CHANGES
- Verified facts: 分支 HEAD `cbb6b71`；PR https://github.com/yishu-ziyu/empirical-paper-workbench/pull/31 仍 OPEN。
- Current hypothesis: `_criterion_ref_value` 在 spec_id 未命中时 fallback 到同 estimator 最新 run；seed 未写 spec_id；未解析判据被标 Expected；揭晓后仍可改 criteria。
- Changed files:
- Failed paths:
- Data / output evidence locations: `docs/acceptance/generic-research-spine-hardening.md`
- Test evidence: make test 819+444+390；C29–C36 定向 pytest/vitest 全绿；tsc/lint/build 0
- Pending external state: push PR #31，不 merge
- Next action: 无（已 push 前收尾）
- Updated at: 2026-09-07
