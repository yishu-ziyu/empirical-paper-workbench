# 验收契约：中文/英文核心研究路径可独立完成

Status: open

基线：`main @ 87c5e5b726911130d4490efd10194ed4241817a5`（PR #31 squash merge；被验收 HEAD `0192c74d3190234f7836524f9a952980bc704f9f`）。
分支：`review/localized-first-study`。
Round 2 起点：PR #32 HEAD `c9d36387ea6e2f554376fa046527b802a825387c`。外部独立验收 **REQUEST CHANGES**（P0-1…P1-5）。历史 validator 报告 `docs/acceptance/localized-first-study-validator.md` **不得改写**。Round 2 独立复核写入 `docs/acceptance/localized-first-study-r2-validator.md`。
设计对照（已打开正文）：Will's S *Design Principles*（Stay Out of the Way / Freedom to Explore / Concise Language / Hierarchy）；*Onboarding Tutorials vs. Contextual Help*（拉取式帮助，可关闭可再开，不打断任务）；*Progressive Disclosure*（细节按请求展开，但不得藏起关键假设、证据缺失或失败原因）。帮助与术语文案按 Concise Language：最短、准确，不把 Promote 说成改写 Claim，不把 mismatch 说成 stale。

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
- 不进入 Phase C。不夹带 issue #30、DiD 或 Research Continuity 实现。
- 不改写 `localized-first-study-validator.md` 的历史 REJECT。
- 不为压 lint 而只删掉 restore effect 的 `t` 依赖；必须证明会话恢复的语义边界：语言切换不得重跑 restore。
- 不对任意后端句子做正则翻译；不把展示翻译写回 criterion / specification / claim 原文。

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
- [ ] C8 语言切换真正 display-only，不得重跑会话恢复 — 程序: 扩展 `frontend/src/__tests__/languageSwitchDisplayOnly.test.tsx`（及必要时 workspace restore 单测）；监测 restore snapshot GET、EventSource 构造次数、当前 tab、selected run ids、Compare 展开；不得只过滤非 GET。场景 A：停在 Results & evidence，选中精确 OLS run 与 IV run，Compare 展开，切换 zh→en→zh — 仍停在 Results & evidence，两个具体 run id 不变，Compare 仍展开，不回 Overview，不新建 Claim/Promote/Run，restore snapshot GET 次数不因切换增加，不重新 apply snapshot / 不 `setWorkbenchTab('overview')`。场景 B：`spec_run` 进行中切换语言 — active run id 不变，EventSource 不重复建立，不 abort/recover/resubmit，运行状态自然继续。场景 C：未保存预期文本、当前 tab、selected run、帮助开闭按契约保留。实现：为 translator 建稳定引用，和/或让 workspace orchestration 与 `t` 解耦（ref 读当前文案）。禁止只删 dependency 压 lint。
- [ ] C9 核心路径真正单语言展示 — 程序: vitest 覆盖 OverviewView / EvidenceView / ResearchLabPanels / EvidenceLab / AgentCursorLayer；源码 grep 硬编码中文 chrome；zh/en 成对截图。预期: Overview 统计卡与进度（数据集、样本行数、主方法、上次运行、研究进度、完成、主结果、当前设定下的主要估计、为什么看证据、变量/系数/标准误/p 值等）全部走 i18n。EvidenceView 主张、失败/缺失、统计卡、表头、识别、稳健性、设定详情、provenance、行/列/trace、代码入口全部按界面语言。ResearchQuestion estimand 按当前界面语言；criterion 展示由 kind/operator/refs 生成，不把存储英文 label 当中文 UI；Card specification label/rationale 按稳定 semantic id 生成中/英展示。不写回 criterion/specification state。不从自由文本猜翻译。Results：surprise expected/observed、compare why、changed/unchanged 维名、Card claim 决策面、unresolved assumptions 按结构化数据本地化。权威 Claim 原文/版本/approval/provenance 不变，可用当前语言解释并提供「查看原文」。Agent Cursor：zh 只显示中文 intent，en 只显示英文 intent；fallback 「正在查看」/ “Looking”；身份「研究助手」/ “Agent”；切换语言不重播、不移动目标、不改 presentation 状态。允许：变量名、公式、代码、用户原文、来源标题、Card 1995、OLS、IV、β、SE、p、N。OLS/IV 缩写保留，任务旁帮助用当前界面语言解释。
- [ ] C10 Promote / Stale 帮助语义正确 — 程序: 读 `docs/product/terminology.md` 与 `frontend/src/lib/i18nWorkbench.ts`；新增文案语义回归测试。预期: Promote/设为主分析不得再说「研究结论所依据的数字会跟着当前主分析走」。正确：当前主分析改变论文和导出默认引用的主结果；已有 Claim 仍绑定形成它时的证据；Claim 与主分析不一致时显示 mismatch；系统不会静默改写 Claim。Stale 不得再说「主分析变化就让 Claim stale」。正确：新的、与 Claim 相关的证据产生或证据集合变化 → Claim 需要重新核对；Promote / Revert existing run 是 decision event，本身不增加 `evidence_revision`；mismatch 与 stale 是不同状态。
- [ ] C11 能力盘点路径与恢复承诺诚实 — 程序: 读 `docs/product/capability-inventory.md` 并对照 `backend/routers` / OpenAPI。预期: 上传路径写 `POST /upload`，不是不存在的 `/uploads`。导出写 `GET /sessions/{id}/doc-export` 与 `GET /sessions/{id}/code-export`，不是笼统 `/export`。会话恢复：若只支持浏览器保存的 session id，描述为「当前浏览器里的最近研究会话可在刷新或重新打开后恢复」，不作项目列表/跨设备发现承诺。界面语言在最终 zh/en 路径通过前，不提前标「已在明确范围验证」。
- [ ] C12 Round 2 最终验收证据 — 程序: 独立 validator 针对 PR 最终 HEAD 写 `docs/acceptance/localized-first-study-r2-validator.md`；实现侧重新生成成对截图。预期: 至少 zh/en empty desk、question+expectation、analysis plans、results & evidence、Agent Cursor mid-demo、research claim、Paper Results、evidence provenance view。1280 与 1440 至少覆盖核心工作台页面。删除或明确标记拍摄于旧 source 的陈旧截图；文件名与画面状态一致。另提供语言切换连续证据：Evidence Compare open → switch language → same tab / same run ids / same Compare state。不把论文正文原语言视为系统 chrome 混杂；Claim 决策、按钮、状态、帮助必须使用当前 UI 语言。保留历史 REJECT 原文。不 merge。

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

Round 2（REQUEST CHANGES，C8–C12）证据见 `docs/acceptance/localized-first-study-r2-implementer.md`；独立复核见 `docs/acceptance/localized-first-study-r2-validator.md`。Status 在 r2 validator ACCEPT 且用户未要求 merge 之前保持 **open**。

## Named relaxations

- C6 浏览器使用隔离任务空间，不连接用户日常浏览器。若本地 `make dev` 端口被用户占用，改用隔离端口，并在证据中写明。失败/重试以 vitest + 词条覆盖；未拍到 boot-failure 截图。部分 EN 工作台截图拍于决策栏词条落地前，源码已改为 `t()`，截图可能仍显示旧中文栏。
- C4 以前端拦截 `fetch` 证明语言切换无额外研究写入；未另做后端会话快照 diff。
- C1 盘点依据源码、现有验收记录和本轮实际跑过的检查；未独立运行的能力必须标「缺完整端到端证据」或更弱状态。
- C3 混杂检查允许清单写在测试里：OLS/IV/CSV/Stata/Excel/Card 1995 等专名；用户自由文本；公式；代码。
- Card 系数本地 0.0747/0.1315 与 CI 0.0740/0.1323 记入盘点「复现待核」，本轮不改估计器、不把差异写成已证实的平台浮点误差。
- 用户理解程度不在本契约用 Agent 代替真人试用。
- C8 以 vitest 拦截 `fetch` + 计数 `EventSource` 构造为主证明 restore 不重跑；隔离浏览器补 Compare 连续截图。未另做后端会话快照 diff（与 C4 同一豁免）。
- C9 论文正文、Claim 权威原文、变量名、公式、代码、来源标题保持原语言，不算系统 chrome 混杂。
- C12 旧截图若文件名与画面不符，删除或在文件旁 `.stale.md` 标注拍摄源；不得把旧 source 截图冒充最终 HEAD。
