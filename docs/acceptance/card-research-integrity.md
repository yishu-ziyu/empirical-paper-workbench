# 验收契约：Card 研究语义完整性（PR #28 supplement）

Status: closed

前置：`docs/acceptance/card-canonical-research-experience.md`（closed）全部仍成立。本契约只增不弱化。

Branch：`review/workbench-v2` / PR #28。不新开 PR，不改 main，不合并。

## Change

写作动作不能偷偷 Promote canonical。Claim 批准绑定当时的 evidence revision；新 SpecificationRun / Challenge / 其他真正新增 Claim-relevant evidence 让旧 Claim 变 stale，stale Claim 不能 grounded Paper。Promote / Revert 属于 decision history，不是 new evidence。Card 措辞边界用同一套 deterministic policy，而不是 exact sentence match。Compare 的 why_moved / changed / unchanged 以 backend 为准。无 admissible spec 时是受控业务失败，不是 NameError/500。

## Not this

- 不算：重做 Card UI、扩 specifications、新 LLM、新 Cursor 动作、通用 NLP judge。
- 不算：自动替用户改 Claim 文本或自动 Promote 来“打通”写作。
- 不算：只修 NameError 但 prepare-paper 仍隐式 promote。
- 不算：前端继续自己推导 identification strategy / why_moved。

## Evaluator

主 agent 跑程序与浏览器 Scenario A–D；validator 子代理对照本契约独立 ACCEPT / REQUEST CHANGES。用户保留主观视觉验收权。

## Checks

- [x] I1 写作不隐式 Promote — 程序: backend 测：canonical=OLS，Claim approved 且 supporting 含 IV，POST prepare-paper — 预期: 409 `canonical_mismatch`；`canonical_spec_id` 与 `state.estimate` 仍为 OLS；不调用 promote。随后 POST preview/promote 才把 canonical 改为 IV。
- [x] I2 UI 明确 mismatch — 程序: 浏览器 Scenario A + frontend 测 — 预期: 文案含「当前 Claim 依赖 IV specification，但正式主规格不是该 IV。」；有 `[Promote supporting specification]`；该按钮走既有 promote command。
- [x] I3 Claim 绑定 evidence revision — 程序: backend 测 — 预期: lab 有 `evidence_revision`；draft/approve 的 claim 有 `based_on_evidence_revision`；新 completed spec_run / challenge run / 其他真正新增 Claim-relevant evidence 使 revision +1；旧 claim 文本保留且 `stale=true`。Promote existing run / Revert canonical 只写 decision_event 与 canonical_history，不改变 `evidence_revision`，已批准 Claim 不因此 stale。
- [x] I4 stale 不能 grounded — 程序: backend + agent 测 + 浏览器 Scenario B — 预期: write_blockers 含 `claim_stale`；Results `grounded=false`；badge 未 grounded；refresh 后仍 stale。重新 draft → v2 based_on=current → approve 后才可 grounded。
- [x] I5 措辞 policy 非 exact match — 程序: agent/backend 单测 + 浏览器 Scenario C — 预期: `Education causes wages to rise by about 13%.` / `An additional year of schooling raises wages by 13%.` / 中文无条件因果 → `wording_exceeds_evidence` / 非 grounded。caveated IV 句可 grounded。`check_grounding`、`results_is_grounded`、Paper badge 走同一 policy 函数。
- [x] I6 Compare 研究语义来自 backend — 程序: EvidenceLab 不再用本地 why_moved 规则作为权威；POST `/research/compare` 的 `why_moved`/`changed`/`unchanged` 驱动 UI 与 Cursor intent。
- [x] I7 无 admissible spec 受控失败 — 程序: 直接调 `execute_spec_run` + HTTP — 预期: 无 `NameError`；稳定业务错误（409 或 run FAILED `no_admissible_specifications`），不是 500。
- [x] I8 原 Card journey 回归 — 程序: 既有 card tests 仍绿；C10 preview 不覆盖 canonical 仍成立。
- [x] I9 门禁 — 程序: `make test` + frontend tsc/lint/build + check-api-drift + CI on PR #28 — 预期: 全绿，无新增 skip。

## Evidence

- I1 `test_prepare_paper_does_not_implicitly_promote_canonical` + browser Scenario A (`fbd498a0-dfaa-405c-bf4d-06d555e84818`): canonical OLS `ols_linear_exper` (β 0.0932), Write Results 409 toast 「当前 Claim 依赖 IV specification，但正式主规格不是该 IV。」, canonical unchanged; explicit Promote then IV `iv_region_dummies` (β 0.1315). Screenshots `/tmp/card-integrity-walk/A-mismatch.png`, `A-paper.png`.
- I2 EvidenceLab test: mismatch copy + Promote supporting specification + Write Results still clickable to surface the 409.
- I3/I4 `test_new_spec_run_stales_approved_claim` + `test_merge_spec_run_does_not_clobber_newer_claim_or_canonical` + browser Scenario B: preview bumps revision, Claim text preserved and `stale=true`, Paper badge `未 grounded`, refresh still stale; Review new evidence → new version based_on=current → approve → grounded returns. Promote / Revert 不 bump（见 C-rev 与 `card-research-semantics-consistency.md`）。
- I5 `agent/tests/test_claim_wording.py` + browser Scenario C: paraphrased EN/ZH causal → not grounded; caveated IV sentence → grounded. Same policy for `check_grounding` / `results_is_grounded` / Paper badge.
- I6 EvidenceLab compare `why_moved` from POST `/research/compare`.
- I7 `test_execute_spec_run_rejects_empty_admissible_set` + browser Scenario D: HTTP 409 `no admissible specifications to run`, toast, `SpecRunRejected.code == no_admissible_specifications`, no NameError/500.
- I8/I9 `make test` + frontend tsc/lint/build + check-api-drift + CI on PR #28.

## Named relaxations

- R1 措辞 policy 仅 Card 教学案例；不做通用 NLP。
- R2 浏览器 Scenario 用 `ECONPAPER_LLM=mock`。章节文案质量不在范围。
- R3 既有 agent 1 skip / backend 8 skip 不视为 regression。
- C-rev（2026-09-06 定义修正，非放宽）：原 I3 把 Promote / Revert 误列为 `evidence_revision +1`。那会把 decision history 当成 new evidence，导致 explicit Promote 后刚批准的 Claim 立即 stale。已从 I3 删除。Promote / Revert 继续写 `decision_events` / `canonical_history`。新证据 stale 保证仍在：completed SpecificationRun / accepted Challenge producing new run。细节见 `card-research-semantics-consistency.md`。
