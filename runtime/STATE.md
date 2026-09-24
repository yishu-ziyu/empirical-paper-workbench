# econpaper Codex Runtime State Index

> 新会话先读本页，再按用户意图打开对应任务文件。这里是短索引，不承载完整运行历史。

| Task ID | State file | Status | Git context | Updated at | Next action |
|---|---|---|---|---|---|
| REPLICATION-SCRIPT-1 | `runtime/tasks/20260924-replication-script.md` | complete | `main@84f6f946` + 本任务提交 | 2026-09-24 | 两轮通过（设定运行 + 主估计）；修复 RD/SCM/CS 无系数；待办：Agent 路径核实、DiD TWFE 聚类未传入 |
| FORMAL-CONFIRMATION-CHAIN-3 | `runtime/tasks/20260918-formal-confirmation-chain-3.md` | complete | `feat/progressive-research-flow@2d83c2c9c716` + inherited changes | 2026-09-18 | ACCEPT；S1–S5、响应丢失与 run 重领已闭合，全量/真实桌面/320×568 均通过；下一步 INTENT-TO-DESIGN-1 |
| FORMAL-CHAIN-2-REVIEW | `runtime/tasks/20260917-formal-chain-2-review.md` | complete | `feat/progressive-research-flow@2d83c2c9c716` + CHAIN-2 受评实现未变 | 2026-09-18 | REJECT；153 项既有测试通过，5 个新 API 反例违约；桌面真实链路及换数据反例已验，小屏超时后恢复；详见 CHAIN-2 独立评审 |
| FORMAL-CONFIRMATION-CHAIN-2 | `runtime/tasks/20260917-formal-confirmation-chain-2.md` | review-rejected | `feat/progressive-research-flow` @ `2d83c2c9c716` + inherited + CHAIN-1/2 交付（未提交） | 2026-09-18 | 原交付保留；修复 docs/reviews/20260917-formal-confirmation-chain-2-independent-review.md 的 S1–S5，补运行重领与代码溯源证据后重审 |
| FORMAL-CHAIN-REVIEW-2 | `runtime/tasks/20260917-formal-chain-independent-review.md` | complete | `feat/progressive-research-flow@2d83c2c9c716` + 受评实现未变 | 2026-09-17 | REJECT；评审和意图优先新规格已写；交执行者修复后重审 |
| FORMAL-CONFIRMATION-CHAIN-1 | `runtime/tasks/20260917-formal-confirmation-chain-1.md` | review-rejected | `feat/progressive-research-flow` @ `2d83c2c9c716` + inherited + 17 源码/测试文件（未提交） | 2026-09-17 | C1–C12 全 PASS 不成立；按 docs/reviews/20260917-formal-confirmation-chain-independent-review.md 修复，保留原交付供对照 |
| EXECUTION-REVIEW-SPEC-1 | `runtime/tasks/20260917-execution-review-spec.md` | complete | `feat/progressive-research-flow` @ `2d83c2c9c716` + inherited changes | 2026-09-17 | 执行规范已备；交本地 Agent 按 `docs/acceptance/formal-confirmation-chain.md` 实现首批，之后独立 review；尚未执行 |
| CORE-PRODUCT-CONTRACT-1 | `runtime/tasks/20260917-core-product-contract.md` | complete | `feat/progressive-research-flow` @ `2d83c2c9c716` + existing fixes | 2026-09-17 | 短契约与页面映射已写；截图读取已验证；待确认 P0 范围后补正式确认链；未改产品代码、未提交 |
| PROGRESSIVE-RUN-TRUTH-1 | `runtime/tasks/20260917-progressive-run-truth-fixes.md` | complete | `feat/progressive-research-flow` @ `2d83c2c9c716` + uncommitted fixes | 2026-09-17 | 自动化全绿；待用户决定 commit/push，并做小屏/键盘/VoiceOver/真实方向 run 真人复验 |
| STRAY-GAP-CLOSURE-1 | `runtime/tasks/20260916-stray-gap-closure.md` | active | `feat/fm-e-build-fold-real-fetch-1` @ `a274d56` | 2026-09-16 | 补齐 14 条游离缺口，分 7 批；批 A 契约 `docs/acceptance/stray-gap-closure-batch-a.md`；不推远端 |
| STRAY-BRANCH-TRIAGE-1 | `runtime/tasks/20260916-stray-branch-triage.md` | complete | `feat/fm-e-build-fold-real-fetch-1` @ `a274d56` | 2026-09-16 | 20/20 判定已出（已重做 6 / 真缺口 14 / 待定 0）；validator ACCEPT；待用户决定 14 条缺口的补齐范围；未提交、未推送 |
| FM-E-FOLD-REAL-FETCH-1 | `runtime/tasks/20260915-fm-e-fold-real-fetch-1.md` | complete | `feat/fm-e-build-fold-real-fetch-1` | 2026-09-15 | pushed; `make test` green; no PR |
| FM-E-BUILD-BRYCE-FOLD-1 | `runtime/tasks/20260915-fm-e-build-bryce-fold-1.md` | complete | `feat/fm-e-build-bryce-fold-1` @ `2e5701b` | 2026-09-15 | pushed; `make test` green; no PR; Run Card1995 attach→confirm→estimate on full SHA |
| FM-E-BUILD-FIX-OLS-LABEL | `runtime/tasks/20260915-fm-e-build-ols-label.md` | complete | `fix/fm-e-build-ols-label-1` from `4546e4de` | 2026-09-15 | OLS label pushed; no PR |
| FM-E-BUILD-BRYCE-1 / NORMS-BE | `runtime/tasks/20260915-fm-e-build-norms-be-1.md` | complete | `feat/fm-e-build-norms-be-1` from `4546e4de` | 2026-09-15 | pushed; `make test` green; no PR |
| FM-E-BUILD-BRYCE-1 / CL-BE-winsor | `runtime/tasks/20260915-fm-e-build-cl-be-winsor.md` | complete | `feat/fm-e-build-cl-be-winsor-1` @ `a850719` | 2026-09-15 | pushed; no PR |
| FM-E-BUILD-BRYCE-1 / FL-BE-reuse | `runtime/tasks/20260915-fl-be-reuse.md` | complete | `feat/fm-e-build-fl-be-reuse-1` from `4546e4de` | 2026-09-15 | pushed; fetch_papers thin wrap; no PR |
| FM-E-BUILD-RIGOR-ATTACH-MERGE-1 | `runtime/tasks/20260915-fm-e-build-rigor-attach-merge-1.md` | complete | `fix/fm-e-build-rigor-attach-merge-1` @ `539a18ae` | 2026-09-15 | pushed; `make test` green; no PR; Run on full SHA |
| FM-E-DATA-RIGOR-1 | `runtime/tasks/20260915-fm-e-data-rigor-1.md` | complete | `fix/fm-e-build-data-rigor-1` @ `810dfa7` | 2026-09-15 | pushed; captain-local-real encoded; no PR |
| FM-E-BUILD-ATTACH-FIXTURE-MERGE-1 | `runtime/tasks/20260915-fm-e-build-attach-fixture-merge-1.md` | complete | `fix/fm-e-build-attach-fixture-merge-1` @ `a8a8665` | 2026-09-15 | merge tip pushed; no PR; Run re-smoke on full SHA |
| FM-E-BUILD-REAL-FETCH-1 / FD-BE-honesty | `runtime/tasks/20260915-fd-be-honesty.md` | complete | `feat/fm-e-build-fd-be-honesty-1` from `8303340b` | 2026-09-15 | honesty landed; `make test` green; no PR |
| FM-E-BUILD-REAL-FETCH-1 / FD-FE-honesty | `runtime/tasks/20260915-fd-fe-honesty.md` | complete | `feat/fm-e-build-fd-fe-honesty-1` | 2026-09-15 | pushed; frontend 445 passed; no PR |
| FM-E-BUILD-REAL-FETCH-1 / FD-BE-fetch-card | `runtime/tasks/20260915-fd-be-fetch-card.md` | complete | `feat/fm-e-build-fd-be-fetch-card-1` from `8303340` | 2026-09-15 | `make test` green; no PR |
| FM-E-BUILD-REAL-FETCH-1 / FD-BE-fetch-dataverse | `runtime/tasks/20260915-fd-be-fetch-dataverse.md` | complete | `feat/fm-e-build-fd-be-fetch-dataverse-1` @ `5fce294d` | 2026-09-15 | none; branch pushed; no PR |
| FM-E-BUILD-REAL-FETCH-1 / FD-BE-fetch-wdi | `runtime/tasks/20260915-fd-be-fetch-wdi.md` | complete | `feat/fm-e-build-fd-be-fetch-wdi-1` @ `9aac96b` | 2026-09-15 | pushed; `make test` green; no PR |
| FM-E-BUILD-DID-BE-SPEC re-cut | `runtime/tasks/20260915-fm-e-build-did-spec-recut.md` | complete | `feat/fm-e-build-did-spec-recut-1` from `9f154dda` | 2026-09-15 | confirmed did missing treat×period hard-blocks; no PR |
| FM-E-BUILD-FIND-MERGE-1 | `runtime/tasks/20260915-fm-e-build-find-merge-1.md` | complete | `feat/fm-e-build-find-merge-1` @ `552cf397` | 2026-09-15 | stacked on INFER; `make test` green; no PR |
| FM-E-BUILD-INFER-MERGE-1 | `runtime/tasks/20260915-fm-e-build-infer-merge-1.md` | complete | `feat/fm-e-build-infer-merge-1` @ `759ce5d6` | 2026-09-15 | pushed; `make test` green; no PR |
| 20260915-inf-be-propose | `runtime/tasks/20260915-inf-be-propose.md` | complete | `feat/fm-e-build-inf-be-propose-1` @ `874ecb3` | 2026-09-15 | slice done; no PR |
| FM-E-BUILD-INFER-DESIGN-1 / INF-BE-confirm | `runtime/tasks/20260915-inf-be-confirm.md` | complete | `feat/fm-e-build-inf-be-confirm-1` from `2a663915` | 2026-09-15 | later slices call `locked_design()`; no PR |
| FM-E-BUILD-INFER-DESIGN-1 / DID-BE-gate recut | `runtime/tasks/20260915-fm-e-build-did-gate-recut.md` | complete | `feat/fm-e-build-did-gate-recut-1` | 2026-09-15 | pushed; no PR |
| 20260915-fd-be-plan | `runtime/tasks/20260915-fd-be-plan.md` | complete | `feat/fm-e-build-fd-be-plan-1` | 2026-09-15 | FD-BE-plan pushed; no PR |
| 20260915-fl-be-search | `runtime/tasks/20260915-fl-be-search.md` | complete | `feat/fm-e-build-fl-be-search-1` | 2026-09-15 | FL-BE-search landed; no PR |
| 20260915-fm-e-build-attach-404 | `runtime/tasks/20260915-fm-e-build-attach-404.md` | complete | `fix/fm-e-build-attach-404-1` @ `1de9dfa` | 2026-09-15 | pushed; no PR |
| 20260907-localized-first-study | `runtime/tasks/20260907-localized-first-study.md` | active | `review/localized-first-study` / PR #32 | 2026-09-07 | r2 implementer 已交；待 r2 validator；不 merge |
| 20260907-m1-empty-criteria-unevaluated | `runtime/tasks/20260907-m1-empty-criteria-unevaluated.md` | complete | PR #31 squash `87c5e5b` (reviewed `0192c74`) | 2026-09-07 | 外部 ACCEPT 已 merge |
| 20260907-m1-expectation-criterion-p0 | `runtime/tasks/20260907-m1-expectation-criterion-p0.md` | complete | `review/generic-research-spine-hardening` / PR #31 | 2026-09-07 | r2 validator ACCEPT；push PR #31；不 merge |
| 20260906-card-research-semantics-consistency | `runtime/tasks/20260906-card-research-semantics-consistency.md` | complete | `review/workbench-v2` | 2026-09-06 | validator ACCEPT；浏览器 S5–S7 过；待 CI |
| 20260906-card-canonical-research-experience | `runtime/tasks/20260906-card-canonical-research-experience.md` | complete | `review/workbench-v2` | 2026-09-06 | validator ACCEPT；CI 待 Card commit |
| 20260902-run-cancellation | `runtime/tasks/20260902-run-cancellation.md` | complete | `chore/local-workspace-cleanup` | 2026-09-02 | Select the next full-stack issue |
| 20260902-upload-event-loop | `runtime/tasks/20260902-upload-event-loop.md` | complete | `chore/local-workspace-cleanup` | 2026-09-02 | Select the next full-stack issue |
| 20260902-durable-upload-recovery | `runtime/tasks/20260902-durable-upload-recovery.md` | complete | `chore/local-workspace-cleanup` | 2026-09-02 | Select the next full-stack issue |

## 启动与写回

1. `active` / `blocked` 且与用户意图匹配：读取对应任务文件后继续。
2. 多个任务都可能匹配：先确认，不覆盖任何状态。
3. 新长任务：复制 `runtime/tasks/TEMPLATE.md` 为 `runtime/tasks/YYYYMMDD-short-slug.md`，再登记一行。
4. 里程碑、压缩、交接或退出前：先更新任务文件，再更新本表。
5. 完成后标为 `complete`，生成不可变去敏运行记录；旧任务文件保留。

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。

---

## 游离分支三分类盘点（STRAY-BRANCH-TRIAGE-1，2026-09-16）

契约：`docs/acceptance/stray-branch-triage.md`。对象：20 个非顶端 `feat/fm-e-build-fold-real-fetch-1`（`a274d56`）祖先的 2026-09-15 远端分支。本轮只读 git：不合并、不 rebase、不删除、不 push、不改 `origin/*`。

**判定口径（可复现）**：先定每个分支「自己的产物」＝ 该分支与 9/15 参照集中最近的祖先 ref 之间的提交与文件（`git log --format='%h %s' <parent>..<branch>`）；再在顶端树里查同一意图。`已重做` 必须给出顶端实现同一意图的文件与符号/行号；`真缺口` 必须给出产物路径在顶端不存在的证据（`git cat-file -e <top>:<路径>` 非零退出）；`待定` 必须写清缺哪个判据。分支名里的 `recut`/`merge`、顶层台账同名行一律不作为证据。

合计：**已重做 6 / 真缺口 14 / 待定 0**（其中 3 条判 `真缺口` 但同时标注「部分覆盖」）。

| 分支 | 判定 | 顶端可复核证据 |
|---|---|---|
| `cursor/backend-typed-review-dep-70ab` | 真缺口 | `git grep -n -i pydantic <top> -- backend/requirements.txt` 唯一命中 `backend/requirements.txt:8:pydantic==2.13.5`；分支 own commit `bca3313` 新增 `pydantic-ai-slim[openai]==2.35.3`。顶端降级路径在 `agent/nodes/review_chapter.py:318-331`（`except Exception` → `review_source="mock_fallback"`），由 `backend/facade/__init__.py:724` 落账。CI 会把 `agent/requirements.txt` 装进 backend venv（`.github/workflows/ci.yml:30`），但 `Makefile:47`（install-backend）与 `backend/Dockerfile:17` 不装 → 本机 dev 与容器仍静默降级。`gh pr view 37` → OPEN |
| `cursor/dc-be-suggest-classic-5` | 已重做 | 顶端同路径超集：`backend/services/classic5_catalog.py:144 rank_entries_for_design`、`:166 suggest_candidates`；`backend/routers/classic5.py:46 suggest_classic5`；`backend/tests/test_classic5_suggest.py` 412 行（分支 177 行） |
| `cursor/did-be-gate-8102` | 已重做 | 顶端 `agent/engine/did_spec.py:51 did_spec_applies`、`:166 apply_did_spec`、`:185 did_spec_block_reason`；`backend/services/allow_did.py:105 session_allow_did`。顶端 `runtime/tasks/20260915-fm-e-build-did-gate-recut.md` 记「Did not revive `cursor/did-be-gate-8102` @ `71be39f1`」；分支旧口径（`catalog_identity_allows` / `title_topic_allows` 用目录令牌放行）被 DECIDE-6 主动撤销，顶端 `docs/contracts/did-narrow-exception-contract.md` 15 行存根写明 superseded |
| `cursor/fm-e-build-b-six-chapter-bodies` | 真缺口 | `git cat-file -e <top>:agent/engine/outline_bodies.py` → exit 128；顶端 `agent/nodes/export_docx.py:251-257` 只跳空 pad（`if not str(content).strip()`），不剥 ATX 标题、不按 outline 顺序；顶端 `agent/tests/test_export_docx.py` 无 `test_extract_sections_skips_heading_only_chapter` 与 `..._follows_six_chapter_outline_order` |
| `cursor/fm-e-build-c-ols-export` | 真缺口（部分覆盖） | 注：该分支 4 个 own 文件在顶端都存在，缺口在既有文件的内容里（无新文件可 `cat-file`）。顶端有 `agent/nodes/translate_code.py:380 _method_is_panel` + `:440 _scripts_from_direction`（OLS → `regress` / `lm`），且 `agent/tests/test_translate_code.py:392 test_translate_code_ols_guessed_id_year_emits_regress_not_xtreg` 存在；但顶端无 `_method_is_ols` / `_pooled_ols_command`，`_translate_line_to_stata`（`:160-174`）无 `smf.ols(...)`→`regress` 分支，分支的 `test_translate_to_stata_smf_ols_formula_becomes_regress`、`test_ols_chapter_feols_python_exports_regress_not_xtreg`、`test_ols_six_chapter_paper_exports_regress_not_xtreg` 在顶端 0 命中 |
| `cursor/fm-e-build-merge` | 真缺口 | 该分支 own 提交 = 3 个 merge，整合 OLS 硬锁 + 六章正文 + OLS 导出；三个被整合件在顶端均未落地（见第 4、5、20 条）。`git cat-file -e <top>:agent/engine/ols_lock.py` → exit 128 |
| `docs/fm-e-build-data-complete-1-g0` | 真缺口 | `git cat-file -e <top>:docs/contracts/data-completion-contract.md` → exit 128；而顶端合同把它当 sister contract 引用（悬空引用）：`docs/contracts/find-data-lit-contract.md:8`、`:502`，`docs/contracts/infer-design-contract.md:320`、`:478`，`docs/contracts/real-fetch-contract.md:583` |
| `feat/dc-fe-gate` | 真缺口 | `git grep -l dataAttached <top> -- frontend/src` 只命中生成物 `frontend/src/types/api.ts`；`git cat-file -e <top>:frontend/src/lib/dataAttachedGate.ts` → exit 128；`git grep -nE 'canRunEstimate\|parseAdmissionConflict\|shouldDivertToAttach' <top> -- frontend/src` 0 命中 |
| `feat/dc-fe-step-attach-panel` | 真缺口 | `git cat-file -e <top>:frontend/src/components/AttachPanel.tsx` → exit 128；`frontend/src/lib/attachCandidate.ts` 同；`git grep -n AttachPanel <top> -- frontend/src` 0 命中 |
| `feat/fm-e-build-bryce-g0` | 已重做（实现落地，G0 文书未随身带） | 分支只加 `docs/contracts/bryce-tools-contract.md`（冻结「四件 IN」）；四件在顶端都有实现：FL `agent/find_lit/fetch_papers.py`、CL `agent/cleaning/winsor.py:88 clean_winsor` + `agent/requirements.txt:15 pywinsor2==0.4.3`、NORMS `agent/norms/chapter_gates.yaml`、OLS `agent/design/spec.py:42 display_estimate_engine_label`。注：顶端合同 §11 表未列 BRYCE，也未引用该契约文件（文书层面的遗留，见文末「遗留」） |
| `feat/fm-e-build-classic-fixtures-1` | 已重做 | 三个 own 产物在顶端 blob 完全相同：`fixtures/classic-5/SOURCE.txt` `beb66616`、`barro1991_growth.csv` `e43e4f61`、`ck1994_long.csv` `56b0cab3`（`git rev-parse <branch>:<p>` == `git rev-parse <top>:<p>`）。`fixtures/classic-5/catalog.json` 顶端 133 行 > 分支 103 行 |
| `feat/fm-e-build-data-complete-1` | 真缺口 | own 8 提交里后端两片在顶端是超集（第 2、13 条），但 DC-FE-gate、DC-FE-step、data-completion 合同三件在顶端缺失（第 7、8、9 条） |
| `feat/fm-e-build-data-complete-1-dc-be-attach` | 已重做 | 顶端同路径超集：`backend/routers/attach.py:138 confirm_attach_dataset`、`backend/services/data_attach.py:39 attach_gate_fields`（分支没有）、`backend/tests/test_data_attach.py` 416 行（分支 354 行） |
| `feat/fm-e-build-did-narrow-1` | 已重做 | own 唯一产物 `docs/contracts/did-narrow-exception-contract.md`（219 行，blob `64c79d5a`）在顶端是 15 行存根（blob `05c0df26`），正文明写「Superseded by: `docs/contracts/infer-design-contract.md` §7」；替代实现 `agent/engine/did_spec.py` / `backend/services/allow_did.py` |
| `feat/fm-e-build-eval-top5-1` | 真缺口 | `git cat-file -e <top>:eval` → exit 128（`eval/harness.py`、`eval/slots.json`、`eval/tests/test_eval_top5.py` 同）；顶端 `eval` 相关只有 `agent/eval/`（12 文件），两者不是同一件事，见 C3-2 |
| `fix/fm-e-build-het-interaction-1` | 真缺口（部分覆盖） | 分支 own 提交 `f72207d`（`infer_heterogeneity_groups`）与 `51679b0`；顶端 `git grep -n infer_heterogeneity_groups` 0 命中，`agent/tests/test_heterogeneity_interaction.py` exit 128。顶端只有阻断侧：`agent/norms/loader.py:272 _check_het_interaction` → `het_missing_interaction`，挂 `agent/norms/chapter_gates.yaml:30`。即「缺交互项会拦住」在，但「从题目推出 educ×region 并写成交互项」不在 |
| `fix/fm-e-build-math-1-docx-typesetting` | 真缺口 | 注：该分支 own 文件只有 `agent/nodes/export_docx.py` 与 `agent/tests/test_export_docx.py`，两者顶端都在，缺口是内容级（无新文件可 `cat-file`）。`git grep -n mathrm <top>` 0 命中；分支 16 个 math 用例（`test_rewrite_mathrm_to_text_for_word_keeps_identifier`、`test_convert_docx_math_is_readable_omml`、`test_markdown_to_latex_keeps_inline_math_and_i` 等）在顶端 0 命中；`git diff --stat <branch> <top> -- agent/nodes/export_docx.py` → 顶端少 261 行 |
| `fix/fm-e-build-prewrite-pause-1` | 真缺口 | `git cat-file -e <top>:agent/engine/prewrite_gates.py` → exit 128，`agent/engine/prewrite_preview.py`、`docs/api/prewrite-confirm.md` 同；`git grep -n 'prewrite/confirm' <top> -- backend` 0 命中；顶端 `agent/norms/loader.py:302-311` 只读 `table1Confirmed` / `specConfirmed`，全树没有写入方（测试只断言「不应存在」） |
| `fix/fm-e-takeaway-g0-contract` | 真缺口 | `git grep -i -n takeaway <top>` 0 命中；`git cat-file -e <top>:docs/notes/takeaway-math-research-notes.md` → exit 128。该笔记自述状态 BLOCKED/OPEN，记录 MATH-1 在真机 Word 里公式仍是转义 LaTeX —— 与第 17 条合读：公式门既没落顶端，也没被验证 |
| `fix/ols-lock-twfe-phrasing` | 真缺口 | 顶端无 `agent/engine/ols_lock.py` / `agent/tests/test_ols_lock.py`（`git cat-file -e` exit 128）；`agent/prompts/methods.py` 无 OLS 硬锁注入，`agent/nodes/generate_chapter.py` 无 TWFE 清洗（grep `sanitize\|TWFE\|固定效应` 0 命中）。顶端只留合同文本 `docs/contracts/infer-design-contract.md:423` 与标签函数 `agent/design/spec.py:42`。详见 C3-1 |

### C3-1 `fix/ols-lock-twfe-phrasing` vs issue #24 的两个漏法

独立结论：**顶端没有等价实现，是真缺口。**

- 否定跨度（`不是……而是采用双向固定效应`）：分支 `agent/engine/ols_lock.py` 的模块 docstring 末行（第 14 行）原文为 `There is intentionally no negation window. Any hit is a TWFE claim.`（此前本文写作中译「有意不设否定窗口，任何命中都算 TWFE 主张」，语义一致但非逐字引文，2026-09-16 按 validator 复核意见改为原文），并在 `agent/nodes/generate_chapter.py:161-208` 调 `sanitize_ols_text` 清洗正文。顶端 `git grep -nE "否定窗口|denial_window|denial span" <top> -- agent backend` → 0 命中；顶端 `agent/nodes/generate_chapter.py` grep `sanitize|TWFE|固定效应` → 0 命中。顶端 `git grep -n 而是 <top>` 的命中全是文档/提示词里的普通中文句子，没有任何一处是把「不是…而是…」当否定跨度处理的代码。
- 不带「双向固定效应」字面的写法（`加入州固定效应与年份固定效应`）：分支用 `_FE_PAIR_RE` 与 `_ENTITY_TIME_FE_RE` 两个正则覆盖。顶端 `git grep -n 固定效应 <top> -- agent/prompts agent/nodes agent/engine agent/design agent/norms` 只有 1 处普通语料串（`agent/nodes/literature_sources/mock_corpus.py:241` 的 mock 摘要），无任何提示词锁或清洗规则。顶端 `agent/prompts/methods.py:17` 只禁「OLS/association 的因果表述」，没有 TWFE 硬锁；分支在 `agent/prompts/methods.py:118-119` 注入 `OLS_PROMPT_LOCK`。
- 该分支测试用例名单（对照用，`agent/tests/test_ols_lock.py`）：`test_denial_span_does_not_skip_contrast_twfe_claim`、`test_spec_sentence_state_and_year_fe_is_forbidden`、`test_ols_lock_active_for_ols_and_unspecified_not_did`、`test_estimator_label_is_ols_regress_or_lm`、`test_methods_and_results_prompts_lock_ols_not_did`、`test_bind_rewrites_feols_estimator_when_direction_is_ols`、`test_generate_chapter_strips_contrast_and_spec_twfe`、`test_generate_chapter_did_keeps_twfe_wording`、`test_estimate_ols_labels_ols_not_feols`；两个用例常量是 `CONTRAST_TWFE`（`不是简单相关回归，而是采用双向固定效应估计政策效应`）与 `SPEC_STATE_YEAR_FE`（`主回归加入州固定效应与年份固定效应，并在州层面聚类`）。顶端 `git grep -n test_ols_lock <top>` 0 命中。
- GitHub 侧：`gh issue view 24 --repo yishu-ziyu/empirical-paper-workbench --json state,title` → `{"state":"OPEN","title":"OLS lock still lets 双向固定效应 phrasing through"}`。顶端有的只是合同文字（`docs/contracts/infer-design-contract.md` §7.4 与 §10 的 OLS lock 行），而且那份表格把它列为「外部并行写集，G0 不得触碰」——即顶端自己记录了这个缺口尚未实现。

### C3-2 顶层 `eval/` 与顶端 `agent/eval/` 是不是同一件事

独立结论：**不是同一件事。`feat/fm-e-build-eval-top5-1` 的顶层 `eval/` 是真缺口。**

- 分支顶层 `eval/` 清单（`git ls-tree -r --name-only origin/feat/fm-e-build-eval-top5-1 -- eval`）：`eval/README.md`、`eval/harness.py`、`eval/pytest.ini`、`eval/slots.json`、`eval/tests/test_eval_top5.py`、`eval/top5-set.submodule`。`eval/harness.py` 自述「Optional EVAL-top5 offline harness. Not a product runtime module… 会话启动 / FIND / attach / estimate / export 不得 import 本文件」，由 `ECONPAPER_EVAL_TOP5` 开关启用，核心是「classic-5 目录 id 永不作 gold」的拒绝规则（`FORBIDDEN_GOLD_IDS` / `refuse_catalog_gold`）。
- 顶端 `agent/eval/` 清单（`git ls-tree -r --name-only <top> -- agent/eval`）：`__init__.py`、`ab_review.py`、`ab_review_report.sample.json`、`judge.py`、`packets.py`、`personas.py`、`run_task.py`、`tasks/undergrad_did_01/{dataset.csv,gen_dataset.py,rubric.json,task.json}`。它是产品内的 agent 质量评测（判官、人格、任务包），与离线 top5 台架无文件重合。
- 顶端不存在顶层 `eval/`：`git cat-file -e <top>:eval` → exit 128，`eval/harness.py` → exit 128。
- 佐证：顶端 `agent-learning/raw/2026-09-15_fm-e-fold-real-fetch-1.md:30` 自己写「Do not fold EVAL-top5 into product runtime」。

### C3-3 `cursor/backend-typed-review-dep-70ab`（PR #37）对 `backend/requirements.txt` 的改动

独立结论：**顶端没有这一行，`backend/runner` 仍会静默降级为 mock，判真缺口。**

- 程序：打印顶端 `backend/requirements.txt` 里所有 pydantic 相关行。输出只有一条：`backend/requirements.txt:8:pydantic==2.13.5`（`git grep -n -i pydantic <top> -- backend/requirements.txt`）。
- 分支的改变：`git diff origin/main origin/cursor/backend-typed-review-dep-70ab -- backend/requirements.txt` 新增注释 + `pydantic-ai-slim[openai]==2.35.3`（分支 blob `b6c00ee5`，顶端 `e035fe07`）。顶端该字符串只出现在 `agent/requirements.txt:33`。
- 后果可复核：顶端 `agent/nodes/review_chapter.py:208 build_review_agent` 里是惰性 `from pydantic_ai import Agent`，`:302-331` 用 `except Exception` 兜底成 `review_source="mock_fallback"` + `review_degraded=True`；所以缺依赖不会报错，只会把「真模型评审」换成 mock。本机 dev 路径 `Makefile:47` 与 `backend/Dockerfile:17` 都不装 agent 依赖（只有 `.github/workflows/ci.yml:30` 装），因此本机与容器都命中这条降级。
- GitHub 侧：`gh pr view 37 --repo yishu-ziyu/empirical-paper-workbench` → OPEN（`gh pr list --state open` 当前共 3 条：#37 本分支、#36 `deploy/private-pilot`、#35 `review/first-value-entry`）。

### 遗留（不在本轮动手范围）

- 3 条判 `真缺口` 但同时有覆盖：`cursor/fm-e-build-c-ols-export`、`fix/fm-e-build-het-interaction-1`（两者只缺「自己那一半」）、`feat/fm-e-build-data-complete-1`（后端在、前端不在）。是否补做由用户决定。
- 悬空合同引用：顶端 `docs/contracts/find-data-lit-contract.md`、`docs/contracts/infer-design-contract.md`、`docs/contracts/real-fetch-contract.md` 都把 `docs/contracts/data-completion-contract.md` 列为 sister contract，但该文件在顶端不存在。这是文档层面的不一致，需要用户决定是补文件还是改引用。
- 两个 GitHub 未闭合项：#24（OLS 锁仍漏 TWFE 措辞）OPEN、#37（backend 声明 pydantic-ai）OPEN。
- 本轮未跑任何测试（契约 Not this 明确排除），所有结论只基于 git 树与 GitHub 查询。
