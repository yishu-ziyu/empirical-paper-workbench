# econpaper Codex Task State

- Task ID: 20260907-m1-expectation-criterion-p0
- Status: complete
- Git context: `review/generic-research-spine-hardening` / PR #31
- Goal: 只修 M1 ExpectationCriterion 最后研究语义（P0-1..P0-4）。M0/M2/M3/M4 不改。不 merge。
- Hard bar: `docs/acceptance/generic-research-spine-hardening.md` C29–C37 全绿；seed 绑定 exact comparable spec_id；后来的 OLS preview 不漂移 Surprise；非法组合 422；equality/zero 边界；unresolved → Unevaluated；post-reveal criterion 409 锁定。
- Session / run ID:
- Current research stage: M1 P0 implementation
- Current review / approval gate: PR #31 external REQUEST CHANGES
- Verified facts: 分支 `review/generic-research-spine-hardening`；PR #31 OPEN。M1 P0 r2：UI 不再用 estimator-only 常量覆盖/伪造 refs；ordering+tolerance 422；PUT spec_id 不丢。C29–C37 程序本轮已跑绿。契约 Status 未改。
- Current hypothesis: 上一轮 seed/fail-closed/Unevaluated/409 保留；剩余 P0 是前端 IV_METRIC/OLS_METRIC 可伪造无 spec_id 判据，以及 ordering+tolerance 曾被接受。
- Changed files: backend/schemas/responses.py；backend/tests/test_card_research_lab.py；frontend/src/components/ResearchLabPanels.tsx；frontend/src/components/WorkbenchArtifact.tsx；frontend/src/components/__tests__/ResearchLabPanels.test.tsx；openapi + api.ts（gen-api）
- Failed paths: none this round
- Data / output evidence locations: `docs/acceptance/generic-research-spine-hardening-m1-p0-r2-implementer.md`
- Test evidence: C29–C36 定向全绿；make test agent 819p/1s backend 445p/8s frontend 393p；check-api-drift 三段绿；tsc/lint/build 0
- Pending external state: push PR #31，不 merge
- Next action: 无（r2 validator ACCEPT；push PR #31；不 merge）
- Updated at: 2026-09-07
