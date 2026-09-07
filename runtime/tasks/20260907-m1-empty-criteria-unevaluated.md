# econpaper Codex Task State

- Task ID: 20260907-m1-empty-criteria-unevaluated
- Status: active（本地 validator ACCEPT；待 push 与外部复核）
- Git context（分支可选）: `review/generic-research-spine-hardening` / PR #31 / baseline `1aa5e95cc66704d5755518eec099831e5c1c2b73`
- Goal: 无结构化判据时 Surprise 不得显示 Expected；采用 Unevaluated + `no_criteria`；Card 有判据路径不退化。
- Hard bar: `docs/acceptance/generic-research-spine-hardening.md` C38–C42。空列表 / 缺 criteria / 全部未解析 / 部分未解析 / 全部满足 / 有违反 / 无完成运行均有测试。写入→运行→读取→展示不得把无判据变成符合预期。
- Session / run ID:
- Current research stage: M1 P0 r3 empty-criteria
- Current review / approval gate: external-review changes requested；不 merge
- Verified facts: HEAD `1aa5e95cc66704d5755518eec099831e5c1c2b73`；`evaluate_surprise` 在 `criteria=[]` 且有完成运行时显式返回 Expected；`test_surprise_without_criteria_stays_expected` 与 C3④/C34 历史特例固化了该行为。
- Current hypothesis: 复用现有 Unevaluated，加稳定 `unevaluated_reason=no_criteria`；无完成运行仍返回 None；GET 对陈旧 Expected+空判据做 fail-closed 校正。
- Changed files: `docs/acceptance/generic-research-spine-hardening.md`（契约重开 + C38–C42）
- Failed paths:
- Data / output evidence locations:
- Test evidence: validator C38 8 passed；C39 25 passed；C40 3 passed；C41 drift 3/3；C42 make test agent 819/1 skip、backend 451/8 skip、frontend 395；tsc/lint/build 0。
- Pending external state: push PR #31 后等待外部复核；issue #30 与阶段 B/C 不在本任务。
- Next action: commit + push PR #31；不 merge；返回证据后停止。
- Updated at: 2026-09-07
