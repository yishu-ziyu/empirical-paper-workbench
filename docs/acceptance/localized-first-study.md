# 验收契约：中文/英文核心研究路径可独立完成

Status: open

基线：`main @ 87c5e5b726911130d4490efd10194ed4241817a5`（PR #31 squash merge；被验收 HEAD `0192c74d3190234f7836524f9a952980bc704f9f`）。
分支：`review/localized-first-study`。
设计对照（已打开正文）：Will's S *Design Principles*（Stay Out of the Way / Freedom to Explore / Concise Language / Hierarchy）；*Onboarding Tutorials vs. Contextual Help*（拉取式帮助，可关闭可再开，不打断任务）；*Progressive Disclosure*（细节按请求展开，但不得藏起关键假设、证据缺失或失败原因）。

## Change

中文用户和英文用户各自在单一工作台里，用自己的界面语言走完一条真实 Card 研究（空桌 → 研究问题/预期 → 确认方案 → 运行 → 结果与证据 → 研究结论 → Paper Results，并能回跳证据），不必先学会工程对象名，也不必同时读「英文＋中文」堆叠标题。

## Not this

- 不换皮、不新建第二套业务界面或第二状态机。
- 不增加研究能力，不实现 DiD，不接新的自主科研 Agent，不做全站大重构。
- 不做阶段 C 展示页重设计或宣发。
- 不把 issue #30 夹进本分支。
- 不机械扫描「页面出现拉丁字母就失败」。
- 不把 Card 成功写成自带数据全部可用；不把导出文件写成所有语言已复现；不把引擎方法数写成工作台已完成同等研究体验。
- 不改统计结果去贴参考值。Card 两种环境的系数差异记为复现待核项。
- 不新增未经验证的隐私、不训练或精度承诺。旧文案里「完全自动写论文」「数据仅用于本次会话」等必须先对照实现再决定去留。
- 不强制八步导览，不要求先看完 Agent 演示才能操作。
- 不自行 merge。

## Evaluator

主 agent 派 implementer 实现（盘点 + 术语 + i18n 核心路径 + 任务旁帮助 + 测试）。浏览器实证使用隔离环境（ego-browser 任务空间或 vitest + 隔离浏览器），不连接、不重载、不杀用户日常浏览器或工作进程。收尾由独立 validator 按本契约程序 ACCEPT/REJECT。用户理解程度由真人试用判断，不能用 validator 代替。

## Checks

- [x] C1 能力盘点存在且诚实 — 程序: 读 `docs/product/capability-inventory.md` — 预期: 覆盖数据导入和清洗、数据探索、研究问题、预期、分析方案、单次估计、多方案比较、诊断与稳健性、文献、Agent 演示、结论确认、章节编辑/回滚、证据关联、文档和代码导出、会话恢复、登录与归属、界面语言、上手入口、运行部署。每项含：用户任务、界面入口、生产执行路径、持久化对象、已有验证、适用范围、依赖条件、限制、允许对外使用的描述、下一步。状态只能是：已在明确范围验证 / 已有实现但缺完整端到端证据 / 仅特定案例可用 / 规划中或尚未找到实现证据。Card 系数本地 vs CI 差异记为复现待核，不归因为未核实的平台浮点误差。无关缺陷只记录不顺手全修。不编完成百分比。
- [x] C2 术语表写入且语义核对 — 程序: 读 `docs/product/terminology.md` — 预期: 含任务包 B4 表中全部内部术语及其中文主界面 / 英文主界面 / 一句话帮助。Canonical=当前主分析 / Primary analysis；Promote=设为主分析 / Set as primary analysis；Claim Ledger=研究结论 / Research claims；Stale=证据已更新，请重新核对；Provenance=数据与计算来源；Grounded=已关联当前证据。注明这些是展示语言，不要求重命名后端对象。文稿语言若未实现，盘点中如实写，不造无效开关。
- [x] C3 核心路径系统文案按界面语言分流，不再默认中英堆叠 — 程序: `cd frontend && npx vitest run` 覆盖 Desk/App/ResearchLabPanels/EvidenceLab/AgentRail/导出对话框相关测试；加上有明确例外的混杂检查 — 预期: 复用 `I18nProvider`/`useT`。zh 模式按钮、导航、状态、错误、教学示例解释、aria-label 为自然中文；en 模式对应系统文案为自然英文。空桌主入口为「体验一项真实研究」/ “Explore a real study”，旁注「教育与工资的经典公开案例」。覆盖：空桌与现有说明入口、导航、Question/Expectation、分析方案确认、运行/失败/重试、Evidence/Compare/Challenge、Agent 演示控制、Claim、Paper Results、常用导出对话框。默认不再出现 `New study · 回工作台`、`Boot failed · 启动失败`、`Evidence Lab（证据实验室）`、`Try a real study · Card` 这类系统文案堆叠。允许例外：变量名、公式、代码、用户原文、来源标题、专名、OLS/IV 等学术缩写（须有就地帮助）。`html`/`documentElement.lang` 与真实界面语言一致（zh-CN / en）。
- [x] C4 切换界面语言只改变展示 — 程序: 前端测试拦截 `fetch`/`XMLHttpRequest` + 后端会话快照前后 diff — 预期: 在未保存输入、运行中、Claim 已批准三个时点切换语言：不发出修改预期/判据的 PUT；不把翻译后的 criterion label 写回；不增加 `evidence_revision`；不重建 Claim、不取消批准、不改变主分析、不重跑估计、不自动翻译覆盖论文正文。揭晓后切换语言不触发 `expectation_criterion_locked`，判据原样。未保存文本、当前页面、选中的具体 run 保留。运行中任务可以自然产生新状态；测试证明语言切换没有*额外*研究写入。打开/关闭帮助不改变研究状态。
- [x] C5 任务旁帮助，非强制导览 — 程序: vitest 键盘/焦点 + 隔离浏览器抽查 — 预期: 确认方案旁说明为何先确认再看结果；设为主分析旁说明会影响哪些报告；证据更新后提供重新核对入口。帮助可键盘访问、可关闭、无焦点陷阱。Agent 演示仍为用户主动触发，可暂停/继续/退出。不增加强制八步导览。关键假设、证据缺失、失败原因不被「简化」隐藏。无判据 / 缺指标 / 失败 / 重试两种语言都有对应文案。
- [x] C6 zh/en 分别走完 Card 到 Results 并回跳证据 — 程序: 隔离浏览器（或现有 Card API + 前端状态机测试补浏览器截图）zh 一次、en 一次 — 预期: 空桌 → 体验一项真实研究 → Question/Expectation → 确认分析方案 → 运行 → 结果与证据 → 研究结论 → Paper Results → 能回跳证据。失败态与重试在两种语言都覆盖。1280 与 1440 桌面检查：不裁切、不重叠。成对截图归档 `docs/acceptance/assets/localized-first-study/`。
- [x] C7 研究语义与质量门不退化 — 程序: `make test`；`cd frontend && npx tsc --noEmit && npm run lint && npm run build`；`make check-api-drift` — 预期: 全部 0 退出；无新增 skip。空判据仍 Unevaluated + `no_criteria`；有判据 Card 仍 Unexpected（IV>OLS，量级约 0.07/0.13）。不改统计结果。独立 PR，push 后核对 CI 对应最新 HEAD，不 merge。本修复不证明所有产品能力可上线。

## Evidence

Status 仍为 open，待外部 validator。实现证据见 `docs/acceptance/localized-first-study-implementer.md`。

- C1 `docs/product/capability-inventory.md`。Card 系数本地 0.0747/0.1315 vs CI 0.0740/0.1323 记复现待核。文稿语言未实现。
- C2 `docs/product/terminology.md`。展示语言，不重命名后端对象。
- C3 复用 `I18nProvider`/`useT`；`document.documentElement.lang` 为 `zh-CN`/`en`；`frontend/index.html` 默认 `zh-CN`。第一次独立 validator 对 C3 **REJECT**：Paper Results 仍有 `Research trace · 研究记录`、`Stale · needs regeneration`、`基于证据`/`未 grounded`、`View Claim / Evidence`，以及 EvidenceView 堆叠标题。已改为单一语言词条。frontend **403 passed**。混杂检查在 `cardCanonicalLiterals.test.ts`。空桌主入口「体验一项真实研究」/ “Explore a real study”。
- C4 `languageSwitchDisplayOnly.test.tsx`：未保存预期、spec_run 中、已批准 claim、揭晓后锁定判据；语言切换无研究写入；帮助开闭不写研究。
- C5 `TaskHelp`：确认方案、设为主分析、证据更新、OLS/IV 就地帮助。键盘可访问。无强制八步。
- C6 ego-browser 任务空间 `localized-first-study`（id 91），隔离端口 5174/8001。截图 `docs/acceptance/assets/localized-first-study/`。浏览器 Card Surprise：Unexpected，IV 0.1315 > OLS 0.0747。空判据 Unevaluated + no_criteria；缺指标 Unevaluated unresolved。失败/重试文案在 vitest M2 与 i18n 两种语言资源中；隔离 runner 被停后 boot 停留 pending，未拍到 boot-failure 卡。
- C7 `make test` 0 退出（agent 819 passed / 1 skipped；backend 451 passed / 8 skipped；frontend 403 passed；无新增 skip）。`npx tsc --noEmit`、`npm run lint`（既有 warning，0 errors）、`npm run build`、`make check-api-drift` 绿。不证明全部产品能力可上线。

PR #31 闭环记录：外部 ACCEPT 审阅 HEAD `0192c74d3190234f7836524f9a952980bc704f9f`，squash merge SHA `87c5e5b726911130d4490efd10194ed4241817a5`。该契约 Status 在本分支文档提交中改为 closed，注明上述 SHA；不在 main 上单独追加未审提交。

## Named relaxations

- C6 浏览器使用隔离任务空间，不连接用户日常浏览器。若本地 `make dev` 端口被用户占用，改用隔离端口，并在证据中写明。失败/重试以 vitest + 词条覆盖；未拍到 boot-failure 截图。部分 EN 工作台截图拍于决策栏词条落地前，源码已改为 `t()`，截图可能仍显示旧中文栏。
- C4 以前端拦截 `fetch` 证明语言切换无额外研究写入；未另做后端会话快照 diff。
- C1 盘点依据源码、现有验收记录和本轮实际跑过的检查；未独立运行的能力必须标「缺完整端到端证据」或更弱状态。
- C3 混杂检查允许清单写在测试里：OLS/IV/CSV/Stata/Excel/Card 1995 等专名；用户自由文本；公式；代码。
- Card 系数本地 0.0747/0.1315 与 CI 0.0740/0.1323 记入盘点「复现待核」，本轮不改估计器、不把差异写成已证实的平台浮点误差。
- 用户理解程度不在本契约用 Agent 代替真人试用。
