# 验收契约：Card 研究语义一致性（PR #28, HEAD 732d55a 后 3 个 fixes）

Status: closed

前置：`docs/acceptance/card-canonical-research-experience.md` 与 `docs/acceptance/card-research-integrity.md` 全部仍成立。本契约只增不弱化。

Branch：`review/workbench-v2` / PR #28。不新开 PR，不改 main，不合并。禁止 redesign，禁止扩功能。

独立验收 HEAD `732d55a`：主体通过；本契约覆盖剩余 3 个 research-semantics consistency fixes。

## Change

`evidence_revision` 只表示 Claim 可见的证据集合版本。只有真正产生 / 引入新 evidence 时递增。Promote / Revert 现有 run 只写 decision history，不 bump revision，不把已批准 Claim 标 stale。Card wording 在标点无空白与 LATE-vs-ATE 人口范围上 fail closed。agent readiness 与 backend paper gate 用同一套 revision 规则；缺 `based_on_evidence_revision` 视为 stale。

## Not this

- 不算：Promote 后偷偷 auto draft / auto approve Claim。
- 不算：重做 UI、扩 specifications、上 LLM/NLP judge、新 Cursor 动作。
- 不算：把 Promote / Revert 从 decision_event / canonical_history 里删掉。
- 不算：只改测试预期、不改 `promote_run` / `revert_canonical` / wording / stale 实现。
- 不算：merge PR #28。

## Evaluator

implementer 循环改到本契约 Checks 全绿。主 agent 跑浏览器 Scenario A–C 并截图。validator 子代理对照本契约独立 ACCEPT / REJECT，不看实现对话。用户保留主观视觉验收权。

## Checks

- [x] S1 evidence_revision 定义 — 程序: backend 单测 + `test_prepare_paper_does_not_implicitly_promote_canonical` 回归 — 预期: `promote_run()` / `revert_canonical()` 不调用 `bump_evidence_revision`；仍写 `decision_events` 与 `canonical_history`。completed SpecificationRun / accepted Challenge producing new run 仍 +1 并 stale 旧 Claim。Scenario A：approved Claim `based_on` = N → canonical OLS → Write Results 409 `canonical_mismatch` → Claim NOT stale → explicit Promote supporting IV → canonical = IV → `evidence_revision` 仍为 N → Claim 仍 NOT stale → Write Results / Prepare Paper 立即 200。Promote 后不得出现新 draft / 自动 approve。
- [x] S2 wording 标点切分 — 程序: `agent/tests/test_claim_wording.py` — 预期: 中/英标点后即使没有 whitespace 也切分 sentence。必须拒绝：`在工具变量假设成立时，IV 估计表明存在局部因果回报。多读一年书导致所有人工资提高13%。` Grounding / `results_is_grounded` / Paper badge 走同一 policy。
- [x] S3 wording 人口范围 — 程序: `agent/tests/test_claim_wording.py` — 预期: caveat 不能给同一句中明显超出 LATE 范围的 universal claim 放行。必须拒绝：`Under the college-proximity IV assumptions, IV estimates suggest a local return, but education raises everyone's wage by 13%.` 以及 `everyone` / `everyone's` / `all workers` / `all people` / `所有人` / `每个人` / `普遍提高`。已有 caveated wording 仍通过：`Under the college-proximity IV assumptions, IV estimates suggest a positive local causal return to schooling.` 不上 LLM/NLP。
- [x] S4 stale fail closed 且统一 — 程序: agent + backend 测 — 预期: `agent.engine.readiness._claim_is_stale` 与 `backend require_claim_ready_for_paper` 同一 revision 规则。当 Research Lab 存在 `evidence_revision` 时，Claim 必须同时满足 `based_on_evidence_revision` 存在、`int(based_on_evidence_revision) == int(evidence_revision)`、`stale != true`，否则视为 stale。用例：lab `evidence_revision=3`、approved claim 缺 `based_on_evidence_revision` → `paper_ready_to_write` Results blocked `claim_stale` → `results_is_grounded` false → snapshot Paper badge not grounded → prepare-paper 同样 `claim_stale`。
- [x] S5 浏览器 Scenario A — 程序: Card 教学案例浏览器 — 预期: approved Claim 依赖 IV、canonical 为 OLS 时 Write Results 409 mismatch 且 Claim 不显示 Review new evidence；explicit Promote supporting IV 后 `evidence_revision` 不变、Claim 仍 Approved / not stale、不再要求 Review new evidence、Paper 立即解锁。
- [x] S6 浏览器 Scenario B — 程序: 同一 session Preview/Challenge — 预期: 新 Preview/Challenge 仍 bump `evidence_revision` 并 stale Claim，出现 Review new evidence。
- [x] S7 浏览器 Scenario C — 程序: wording bypass — 预期: S2 与 S3 两句均被拒绝（非 grounded / wording_exceeds_evidence）；正常 caveated IV 句仍通过。
- [x] S8 回归与门禁 — 程序: 相关回归 + `make test-backend` / `make test-agent` / `make test-frontend` / frontend tsc / lint / build / `make check-api-drift` / CI on PR #28 — 预期: 全绿，无新增 skip。不 merge。

## Evidence

Session `9ffc700d-f272-40a5-9011-0605fd1fd3c8`（DEBUG=true, `ECONPAPER_LLM=mock`）。截图 `docs/acceptance/evidence-card-semantics/`。

- S1/S5 Scenario A: approved Claim `based_on=1`。Promote OLS → `evidence_revision` 仍为 1，Claim `stale=false` / version 1 / 无新 draft。Write Results toast `当前 Claim 依赖 IV specification，但正式主规格不是该 IV。`，prepare-paper 409 `canonical_mismatch`。explicit Promote supporting IV → canonical `iv_region_dummies`，revision 仍 1，Claim 仍 Approved、无 Review new evidence。prepare-paper 200；Write Results 立即成功；badge「基于证据」；educ 0.1315。`claim_drafted` 事件仍为 1（space-run 原始 draft），`claim_approved` 事件 1。
- S6 Scenario B: Preview `ols_full_controls` → revision 1→2，Claim 文本保留、`stale=true`、`based_on=1`。UI：`New evidence available · 结论需要重新审视` + Review new evidence。snapshot `write_blockers` 含 `claim_stale`，Results `grounded=false`。
- S2/S3/S7 Scenario C: `wording_exceeds_evidence` 拒绝无空白 `。` 切分句与 `everyone's` ATE 句；caveated local 句通过。注入 Results 后 snapshot `chapter_grounded=false`；浏览器 badge「未 grounded」。
- S4: `claim_revision_is_stale` 共用。lab revision=3 缺 `based_on` → Results `claim_stale`、`results_is_grounded` false、prepare-paper 409 `claim_stale`。
- S8: validator ACCEPT `docs/acceptance/card-research-semantics-consistency-validator.md`。agent 819/1skip；backend 421/8skip；frontend 348；tsc / lint / build / api-drift 绿。CI 在 push 后跟。

Promote 后 `evidence_revision` before/after: **1 → 1**（OLS promote 与 IV promote 均不变）。Preview 才 1→2。

## Named relaxations

- R1 措辞 policy 仅 Card 教学案例；deterministic / Card-only；不做通用 NLP。
- R2 浏览器 Scenario 用 `ECONPAPER_LLM=mock`。章节文案质量不在范围。
- R3 既有 agent 1 skip / backend 8 skip 不视为 regression。禁止为本契约新增 skip。
- R4 Promote 后已写 Results 章仍可标 chapter `stale` / `needs_regeneration`（canonical estimate 变了要重写正文）。这不等于 Claim stale，不得出现 Review new evidence。
