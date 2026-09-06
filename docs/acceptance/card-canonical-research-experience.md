# 验收契约：Card Canonical Research Experience

Status: closed

Baseline（2026-09-06，`review/workbench-v2` @ `226546b`，工作树干净）：

- frontend：47 files / 322 tests 绿；`npm run build` 通过
- backend：389 passed / 8 skipped
- agent：805 passed / 1 skipped
- `make check-api-drift` 绿；`make smoke-agent` / `make verify-deps` 绿
- 开发服已在 5173 / 8000

前置能力（不得回退）：Workbench v2 Snapshot / Evidence / 刷新恢复 / 真实 estimate provenance / Results 写作门 / Shell IA。

规格：`docs/specs/card-canonical-research-experience.md`

## Change

用户从空桌一键进入 Card 教学案例，经历 Question → Expectation → 冻结 Admissible Space → 真实多规格运行 → Surprise → Agent Cursor 演示 OLS/IV 差异与一次 Preview challenge → 批准 Claim Ledger → Paper Results 引用该 Claim 与真实数字。所有统计结果真实执行，研究状态由后端持有，刷新或清空前端存储后可恢复。

## Not this

- 不算：8 步向导、CHARLS 式 wizard、前端 hardcode 系数、用覆盖 `state.estimate` 冒充 specification space。
- 不算：Preview 偷偷改 canonical estimate / Paper / Claim。
- 不算：Agent Cursor 接受坐标、CSS selector、XPath，或接 LLM 自由操作 DOM。
- 不算：为 demo 另写一套与 production 平行的研究引擎，或重写 StatsPAI。
- 不算：只跑通测试、没从空桌用浏览器走完 canonical journey。
- 不算：用 skip/pending 掩盖失败，或弱化本契约检查项。

## Evaluator

每个里程碑由 implementer 交证据；主 agent 做浏览器实弹（1280 与 1440）并归档。

宣布 Goal 完成前：validator 子代理独立阅读本契约、查看 diff、跑程序、对照用户旅程，给 ACCEPT / REQUEST CHANGES。validator 不看实现对话。

用户保留主观产品 / 视觉 / 交互的最终验收权。

## Checks

### M1 — objects + Card boot

- [x] C1 空桌有明确 Card 入口 — 程序: `cd frontend && npx vitest run src/__tests__/DeskPage.test.tsx src/__tests__/App.test.tsx` + 浏览器 DOM — 预期: `data-testid="desk-try-card"` 可见，文案含 `Try a real study` 与 `Card`；点击后进入真实 session，不是 Guide 课设样例。
- [x] C2 teaching-case 标记 — 程序: `GET /sessions/{id}` + 浏览器 — 预期: `research.teaching_case == "card_1995"`；UI 明确这是教学/复现案例，不伪装成用户自己的研究。
- [x] C3 真实 Card 数据经既有上传管道 — 程序: backend 新测 + `GET /sessions/{id}` — 预期: dataset rows=3010；含 `lwage,educ,nearc4,exper,expersq,black,smsa,south`；provenance 有 source/citation/checksum/redistribution decision；系数不出现在 frontend 源码。
- [x] C4 Question / estimand 是研究语义 — 程序: 浏览器 + frontend 测 — 预期: 展示 Outcome / Treatment / causal threat / candidate identification / estimand；不是 20 字段统计表单。
- [x] C5 Expectation 后端对象可恢复 — 程序: backend 测（PUT expectation → GET snapshot）+ 浏览器刷新 + 清 localStorage/sessionStorage 仅回填 session id — 预期: 文本、confidence、decision history 仍在；不是聊天消息。
- [x] C6 Admissible space 揭晓前可冻结 — 程序: backend 测 + 浏览器 — 预期: 6–12 条 spec，各有 semantic id/label/rationale/dimension/value/admissible/user decision；`Freeze admissible space` 后 `frozen_at` 非空；比较结果在冻结前不可见。
- [x] C7 状态来自 backend snapshot / research read model — 程序: grep + `SnapshotRecovery` 更新用例 — 预期: 前端不为 expectation / space / teaching_case 建业务 storage；`GET /sessions/{id}/research` 与 snapshot.research 一致。
- [x] C8 M1 门禁 — 程序: `make test-frontend && make test-backend && make test-agent && make check-api-drift && cd frontend && npm run build` — 预期: 全绿，无新增 skip。浏览器从空桌走到 frozen space，console 无新增 uncaught error。

### M2 — spec runs + Evidence Lab

- [x] C9 多条真实 SpecificationRun — 程序: backend 测跑 Card OLS + IV — 预期: `research_lab.specification_runs` ≥ 2；每条含 spec id、choices、estimator、formula、covariance、analysis dataset identity、producer run、coef/se/p/n、status、provenance、created_at、relation。
- [x] C10 preview 不覆盖 canonical — 程序: backend 测：记录 canonical estimate → preview 另一 spec → 再读 snapshot — 预期: `state.estimate` 的 coef/formula/source_run_id 不变；Paper/Claim 不自动变。
- [x] C11 Promote / Revert — 程序: backend 测 — 预期: promote 后 canonical 指向该 run 且 `state.estimate` 更新并记 decision；revert 恢复先前 canonical。
- [x] C12 Evidence Lab 三层 — 程序: 浏览器 DOM + frontend 测 — 预期: results space（point，CI 若可靠，canonical/selected，method grouping，hover）；choice matrix；任意两条 Compare 显示 βA→βB、Δ abs、Δ %、changed/unchanged。
- [x] C13 OLS vs IV 主变化是 identification — 程序: `POST .../research/compare` + 浏览器 — 预期: OLS/IV 系数来自真实 run；changed choices 含 estimator/identification；intent 可被读成 identification strategy。数值相对 anchor 可解释（记录实际 formula/covariance）；禁止为贴 0.0747/0.1315 改结果。
- [x] C14 Surprise 确定性规则 — 程序: `agent` 或 `backend` 单测覆盖 direction / ordering / magnitude；Card 默认 expectation 在 IV>OLS 时为 Unexpected — 预期: 无 LLM 参与判定；规则与规格第 8 节一致。
- [x] C15 Challenge 可执行 — 程序: backend + 浏览器 — 预期: 至少一个 Next best challenge（instrument strength 或 experience form）；accept 后产生真实 spec_run。
- [x] C16 IV diagnostic 真实 — 程序: 浏览器 + evidence/research payload — 预期: first-stage F（或等价 strength）来自 identification/spec diagnostics，不是文案常量。

### M3 — Agent Cursor

- [x] C17 SemanticTargetRegistry — 程序: grep frontend — 预期: 存在 registry；script 只引用 semantic id（`evidence.spec.ols` 等）；源码无 Agent 输出 x/y、querySelector、XPath 作为控制面。
- [x] C18 Point 不改研究状态 — 程序: 跑 script 的 point/compare 前后 snapshot.estimate / claim 不变。
- [x] C19 Demonstrate/Preview 不改 canonical — 程序: 跑 preview script + Run Preview — 预期: 新 SpecificationRun 出现，canonical 不变，直到用户 promote。
- [x] C20 Cursor 行为 — 程序: 浏览器 — 预期: 使用 `motion`（不新增 GSAP 用法）；transform 移动；`pointer-events: none`；有 Agent 身份与短 intent label；target 缺失 abort；resize/scroll 后仍对准；用户 pointer/keyboard 时 yield；cancel / replay 可用；`prefers-reduced-motion` 有行为。导航中途 abort。

### M4 — Claim → Paper

- [x] C21 Claim Ledger 真实一条 — 程序: `GET /sessions/{id}/research` — 预期: 含 supported / conditionally supported / unsupported wording（语义对齐规格第 11 节）；supporting / counter evidence 链回 spec runs；unresolved assumptions 非空；version + provenance。
- [x] C22 用户批准 — 程序: 未批准不得进入 grounded Results；批准后 `approved_by_user=true`。
- [x] C23 Paper Results 消费 Claim — 程序: 生成 results 章 + 浏览器 — 预期: 核心数字来自 approved Claim / SpecificationRun；点击关键句或数字回到 Claim/Evidence；超界措辞不得标 grounded。
- [x] C24 stale — 程序: promote 或改 claim 后读章节 — 预期: 旧正文明确 stale / needs regeneration，不伪装仍 grounded。既有 approve/edit/rollback 仍可用。

### M5 — 全程 + 回归

- [x] C25 浏览器 canonical journey — 程序: `make dev`（DEBUG=true，ECONPAPER_LLM=mock）+ 浏览器，1280 与 1440 — 预期: 空桌 → Try Card → Question → Expectation → 看提议 choices → Freeze → 真实跑 baseline/比较 → OLS vs IV → Surprise → Show me（Cursor）→ Diagnose changed/unchanged → 接受 challenge → Cursor preview → Run Preview 真执行 → compare → IV diagnostic → Claim Ledger → 批准 → Paper Results → 回跳 provenance。流畅，不是 20 个「下一步」页。全程 `window.__errors` 无新增 uncaught。截图与 DOM 断言归档 `docs/acceptance/evidence-card-canonical/`。
- [x] C26 刷新恢复 — 程序: journey 中途与结束后清前端存储（保留 session id）刷新 — 预期: Question / Expectation / freeze / runs / claim 仍在。
- [x] C27 回归门禁 — 程序: `make test` + `cd frontend && npx tsc --noEmit && npm run lint && npm run build` + `make check-api-drift` + `make verify`（服务已起时）— 预期: 全绿；Workbench v2 恢复测试仍过；无新增 skip。
- [x] C28 ADR 0015 — 程序: 读 `docs/adr/0015-card-canonical-research-experience.md` — 预期: 记录 SpecificationRun 模型、preview vs canonical、Cursor semantic-target contract、Claim Ledger 真相边界。
- [x] C29 validator 独立 ACCEPT。

后续完整性（只增）：`docs/acceptance/card-research-integrity.md`（写作不得隐式 Promote；Claim 绑定 evidence revision；措辞 policy；Compare 以 backend 为准）。

## Evidence

（收尾填写。每个里程碑结束后追加命令输出、payload、截图路径、系数核验。）

M1：
- 2026-09-06 implementer：`docs/acceptance/card-canonical-m1-implementer.md`。`make test-backend` 396/8skip；frontend 327；agent 805/1skip；api-drift；build 绿。
- 浏览器空桌 → `desk-try-card` → session `3f785f7f-6243-4579-814c-64e35fa4cd0c`：dataset 3010 行、`wooldridge_card_34`、teaching badge、Question/Expectation、Design freeze。清存储仅留 session id 刷新后 expectation（high / 用户改写）与 `frozen_at` 仍在。console `__errors=[]`。1280/1440 `scrollWidth==clientWidth`。
- 截图：`docs/acceptance/evidence-card-canonical/m1-empty-desk-1280x800.png`、`m1-question-1280x800.png`、`m1-frozen-1280x800.png`、`m1-frozen-1440x900.png`、`m1-recovery-frozen-1280x800.png`。
M2：
- implementer 摘要 `docs/acceptance/card-canonical-m2-implementer.md`。backend 409/8skip；frontend 328；agent 805/1skip。
- 浏览器 session `a27ff608-34b0-452f-b828-be9fedc8435b`：freeze → Run specifications → Evidence Lab。Compare OLS→IV **0.0747 → 0.1315**（Δ 0.0568 / 76.1%），why-moved `Identification strategy changed`；Surprise Unexpected（IV>OLS）；challenge effective F=14.14。spec_run 必须读 `extract_csv_path`（教学 extract），不能用 winsorize 后的 cleaned sidecar（否则 OLS≈0.0687）。
- 截图：`m2-evidence-lab-1280x800.png`、`m2-compare-1280x800.png`。
M3：
- implementer `docs/acceptance/card-canonical-m3-implementer.md`。Show me 存在；cursor overlay `pointer-events:none`；intent「Identification strategy changed / 识别策略发生变化」。CDP 截图不稳定，DOM 断言成立。
M4：
- implementer `docs/acceptance/card-canonical-m4-implementer.md`。session `a27ff608-34b0-452f-b828-be9fedc8435b`：Claim 三档措辞已批准；prepare-paper 提升 IV educ=0.1315；Results grounded=true 且含真实 educ 行；`paper-claim-link`；badge「基于证据」。ADR `docs/adr/0015-card-canonical-research-experience.md`。
M5：
- C26 修复：`researchQuestionPrompt` / `hasConfirmedResearchQuestion`；freeze / runs / claim 计入 `snapshotHasResearchContent`；teaching case 标题不再回落到 csv 文件名。`SnapshotRecovery.test.tsx` 断言 project-name / rail「已确认」/ 非「待确认方向」，以及 runs+claim 恢复。
- 单次 canonical journey session `5cafe0c4-00e9-41d5-85ef-24792cf71d75`（1280 与 1440）。空桌 `desk-try-card` → Question/Expectation → Freeze → 清存储仅留 session id 刷新（标题仍是 Does education increase earnings?，rail 已确认，非 csv / 待确认方向）→ 12 条真实 spec_run。Comparable OLS·1966 region dummies **0.0747** → IV **0.1315**（Δ 0.0568 / 76.1%），`Identification strategy changed`；Surprise Unexpected；challenge effective F=14.14（非 winsorize sidecar 0.0687）。Show me cursor：`Agent Looking` overlay、`pointer-events: none`、Cancel/Replay；pointer yield → Paused。Run Preview 真执行（矩阵出现 OLS·linear experience 0.0932；canonical 仍 0.1315）。Claim 三档措辞批准 → Write Results：Results 章 `View Claim / Evidence`，badge「基于证据」，educ 0.1315038…；点击回跳 Claim Ledger（Approved）。结束后再次清存储刷新：Question / Expectation / freeze / runs / claim 仍在。`window.__errors=[]`。`scrollWidth==clientWidth` at 1280 and 1440。
- DOM dump：`docs/acceptance/evidence-card-canonical/m5-dom-assertions.json`、`m5-errors.json`。
- 截图（同一 session）：`m5-empty-desk-1280x800.png`、`m5-question-1280x800.png`、`m5-frozen-1280x800.png`、`m5-recovery-frozen-1280x800.png`、`m5-evidence-lab-1280x800.png`、`m5-compare-1280x800.png`、`m5-challenge-1280x800.png`、`m5-cursor-1280x800.png`、`m5-preview-proposal-1280x800.png`、`m5-run-preview-1280x800.png`、`m5-claim-ledger-1280x800.png`、`m5-paper-results-1280x800.png`、`m5-claim-jump-1280x800.png`、`m5-recovery-claim-question-1280x800.png`、`m5-recovery-claim-1280x800.png`，以及对应 1440：`m5-question-1440x900.png`、`m5-frozen-1440x900.png`、`m5-evidence-lab-1440x900.png`、`m5-compare-1440x900.png`、`m5-cursor-1440x900.png`、`m5-claim-ledger-1440x900.png`、`m5-paper-results-1440x900.png`。m1/m2/m3/m4 同名文件已用同一 journey 覆盖，避免旧包 0.0687 / csv 标题混入。
- runner 必须加载 `spec_run`（uvicorn `--reload` 不会热加载 runner）。Space run 12 specs 在租约争用下可能 >2min；跑完后 Evidence Lab 在 Evidence 轨。
- Validator 2026-09-06：**ACCEPT**。报告 `docs/acceptance/card-canonical-research-experience-validator.md`。`make test` agent 809/1skip、backend 416/8skip、frontend 345；tsc/lint/build/verify 绿。C1–C29 PASS。

## Named relaxations

- R1 浏览器走查使用 `ECONPAPER_LLM=mock`（DEBUG=true）。章节文案质量不在范围；estimate / spec_run 必须是真实统计执行。
- R2 数值与公开复现允许可解释差异；测试不得 hardcode UI 常量 0.0747 / 0.1315 / 14.214。比对以独立复算同一 formula/estimator/covariance 为准，或记录与 anchor 的差异原因。
- R3 若运行时只能加载 9 列 StatsPAI extract，region / `smsa66` 规格标为 unavailable，不假装跑过；OLS vs IV 主比较仍必须真实执行。
- R4 既有 agent 1 skip、backend 8 skip 不视为本阶段 regression。禁止为本契约新增 skip。
- R5 C20 不以像素级动画曲线为门槛；以 semantic target、yield、reduced-motion、不改研究状态为准。
- R6 本阶段不要求 LLM 接入、不要求自主 Act、不要求 38 methods。
