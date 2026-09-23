# FORMAL-CONFIRMATION-CHAIN-1 独立评审

日期：2026-09-17。结论：**REJECT，需要修复后重审。**

本结论针对交付版本的正确性，不以产品随后改变流程顺序为拒绝理由。新顺序及下一批方案见 [研究意图到可执行设计](../specs/research-intent-to-design.md)。

## 1. 评审对象与证据范围

- HEAD：`2d83c2c9c716c0708eb5303840e76f51749583d1`，未变。
- 比较对象：执行者 `baseline/files/` 与当前工作区；不是只比较 HEAD。
- `final/changed-files-sha256.txt` 中 **17 个源码/测试文件全部匹配**当前内容；另外两个任务/索引文件不匹配交付哈希。全量清单排除环境文件后核对 1007 个文件，同样只有这两项不匹配（本轮写回评审索引前核对）。
- 增量实际为 12 个修改文件 + 5 个新源码/测试文件；交付摘要“16 个、12+4”计数不准确。`diff -ru` 对新文件仅列 `Only in`，没有新文件内容，因此交付 patch 本身不能独立重建版本；本轮另读了实际新文件。
- 证据根目录：仓库外 `../empirical-paper-workbench-evidence/formal-confirmation-chain-1/`；本轮反例与日志在 `review/`。
- 本轮未修改产品实现。临时前端反例测试运行后已移出产品树，归档到 `review/independentReviewProbes.test.tsx`；没有替执行者修实现后宣称原交付通过。

已成立的进展：同会话 attach、响应驱动的挂接反馈、真实样本/方程展示、200/202 分流已经接线。原浏览器 happy path 与计算证据有价值，但不能覆盖版本变化、失序请求与网络故障。

## 2. 必修问题

| ID / 优先级 | 用户可观察影响及根因 | 代码与证据 | 最小修复与应先失败的测试 |
|---|---|---|---|
| R1 / P1 | 新正式会话只要从未提出设计，就绕过设计确认；越少信息反而越容易放行。 | `backend/services/formal_chain.py:require_design_confirmed` 遇到非 dict 直接 return。独立 API：`upload_readiness=READY,dataAttached=true`、无 design，`/direction` 返回 **202** 并入队。 | 以明确会话类别区分 legacy；新正式会话 missing/null/malformed/draft 均不能执行正式分析。数据接入/结构检查不受该门约束。测试这四种缺失形态、legacy 与 Card 边界。 |
| R2 / P1 | 可以确认尚不存在的样本/设定；样本尚未确认，设定已经被标成已确认。 | `facade.record_prewrite_confirms` 不验证当前预览和顺序；`PrewriteConfirmCard` 的设定按钮不依赖 table1Confirmed。独立 API：无 direction、Table 1、方程时 record spec 返回 **200**，写 `specConfirmed=true`；前端顺序反例也失败。 | 确认必须绑定当前已生成的预览，验证样本与方程存在、无冲突活动 run，样本确认在设定确认前。双方校验；不能仅改按钮 disabled。增加无预览/逆序/运行中确认测试。 |
| R3 / P1 | 确认的是设计 A，实际可以运行 B；改了设计或换了数据，还能沿用旧确认和旧预览。 | `/direction` 只查 design 确认布尔值，不核对执行内容；`design.py:propose_design_endpoint` 与 `RunRepository.admit_session_upload` 未撤销依赖确认。独立 API：锁定 treatment=age，提交 schooling 得 **202**；把设计重提为 schooling 再确认，仍用旧 age 方向启动 **202**。换数据后 READY→PROCESSING，但旧 Table 1、两个 true 和 awaiting_estimate 仍保留。 | 用 design revision + dataset revision + specification/preview identity 绑定确认和 run；原子变更时使受影响批准失效并保留历史；正式执行内容必须匹配已确认版本。测试改 treatment/样本/数据、旧预览 confirm、旧 run 提交终态；不把纯措辞/界面语言变化一概视作数据变化。 |
| R4 / P1 | 已进入研究 B，研究 A 迟到的确认响应又把 A 的设计/数据写到 B 的界面。 | `workspace.ts:invalidateSessionWork` 未清 `designOperationRef`、`attachOperationRef`；propose/confirm 回调仅比对自身 operation，不比会话 epoch/对象版本。两个独立 hook 测试均实测 B 切换后收到 `研究A`。 | 所有新增请求统一持有 sessionId + epoch + 对象版本；每个 await 后应用前检查，切会话/退出清 operation 和 busy。同会话换候选也使旧确认失效。覆盖 design 与 attach 的成功、失败、回读迟到。 |
| R5 / P1 | 用户修改题目后直接点“确认设计”，确认的是修改前的草稿。 | `DesignProposalCard` input 是本地 title，onConfirm 无 payload；确认按钮只看 draftVisible，不看 dirty。组件反例：修改成 B，旧 A 的确认回调仍执行。 | 未保存编辑不能批准旧草稿；采用保存/重提完成后再确认，或一个明确事务保存并确认当前版本。后端校验 expected revision，防另一窗口替换草稿。确认后须有显式修订入口，不以禁止一切修订代替 C8。 |
| R6 / P1 | #40 要求用户针对风险明确决定时，当前入口仍可直接启动，且没有相应风险确认记录。 | `prepare_prewrite_confirm` 仅消费 `identification_hard_block`；PrewriteConfirm 只看异质性 blockingDecision。独立 API：`continue_to_estimate=confirm`，仅发 action，仍返回 **202**。 | 分别消费 allow/confirm/forbid；confirm 的记录须绑定具体诊断和设计版本，不能用“确认样本/方程”代替风险决定；forbid 不得越过，unknown 的 allow 不额外加门。测试三档许可及风险记录过期。 |
| R7 / P1 | 显式 mock 仍可能调用真实付费模型；证据采集也越过了禁止复制环境文件的边界。 | **既存问题，非本批引入。** `agent/llm/router.py:98–107` 在 mock 后用 MiniMax key 覆盖 desk；本轮仅以无效占位 key 构造配置，复现 generate/review=mock、desk=minimax，未发模型请求。基线目录存在 `.env`、`.env.docker`，仅查文件名，未读取值。 | 真模型测试前先修：mock 必须为最高优先级且不读取真实 SSOT；加外部连接阻断与启动配置断言，涵盖非 pytest 子进程、reload、所有角色。基线用源码 allowlist，排除配置/凭据/数据；完成授权的脱敏副本清理后重新建清单，禁止上传原始基线包。 |
| R8 / P2 | 同一页面一边要求确认样本，一边写“没有需要你确认的事”；未知核查却被统一称作“已通过”。 | `i18nWorkbench.ts` 的 `prewrite.lead` 固定“方向核查已通过”；PrewriteConfirm 不接收诊断状态。组件反例失败。原截图 `06` 可直接看到正文待确认与右栏“没有需要确认”的冲突；`09` 同一会话显示“识别：尚未核查”。 | 正文只报“样本与分析设定已准备好”等已知事实；核查结果来自 #40；右栏下一动作消费相同待办事实。加入 unknown + awaiting-preview 的整页一致性测试。 |

上述 R1–R6 是旧 C1–C9 中已经要求的语义，不能归因于这次产品顺序变更。R7 是本批运行暴露的既存环境问题，先独立修，不回写成原执行者引入。

## 3. 幂等与故障恢复：尚不能判通过

`workspace.ts:continueEstimate` 每次调用新建 UUID，仅以 operation ref 防同时点击；响应丢失后的同一意图重试没有持久投递凭证。catch 回读 active_run 后没有在该分支显式接回统一等待。`attachCsvToSession` 也没有保留请求意图，catch 走普通上传错误提示。以上为代码路径风险，本轮没有完成该竞态的独立浏览器复现，标 **NEEDS EVIDENCE**，不写成已观察重复计算。

`confirmDesign` / `recordPrewriteConfirms` 的 POST 失败分支没有像 confirmAttach 一样回读确认；“服务端已写入、响应丢失”的结果不可按普通拒绝处理。成功分支先应用响应，随后 snapshot 失败被吞掉，交付所谓“回读一致后才显示”也不成立。

补测：服务器接收并创建 run 后断开响应；恢复/重试应使用同一意图凭证，接回同一 run；已完成也不能创建第二个。200 确认服务端落库后断开响应，回读判定；确定拒绝、未知、已接受必须分开。只证明并发按钮禁用不满足 C6/C7。

建议小范围整理新职责：将确认命令和短期请求状态从 workspace 抽成一个有明确所有权的模块，仍使用既有 snapshot 与 waitForTrackedRun。当前单文件新增约 480 行与多组不一致请求模式，已直接造成 R4；不做全仓重构或引入状态库。

## 4. 重新判定 C1–C12

| 验收项 | 独立结论 | 原因 |
|---|---|---|
| C1 | 部分成立，整体 FAIL | 创建/提出/确认 happy path 存在；编辑确认存在 R5。 |
| C2 | NEEDS EVIDENCE | 只覆盖部分挂接错误，非设计/挂接/样本/设定各类延迟、拒绝、响应丢失完整矩阵。 |
| C3 | 初次接入成立 | 保留同会话且 READY 与挂接分开；替换候选的绑定问题见 C8/R3。 |
| C4 | FAIL | R1、R2、R3 直接 API 可绕过。 |
| C5 | FAIL | Table 1 与方程有真实呈现，但逆序与无预览确认可发生。 |
| C6 | NEEDS EVIDENCE | 200/202 分流成立；丢响应后幂等、队列拒绝、同意图重投证据缺失。 |
| C7 | 部分成立 | 原脚本验证的是完成后刷新；新增上传/估计意图在运行中刷新与恢复未完整覆盖。 |
| C8 | FAIL | 两个迟到响应反例 + 设计/数据改变后旧确认残留。 |
| C9 | FAIL | confirm 许可未消费、未知被称通过；只重跑 #40 计算函数不能证明消费端遵守。 |
| C10 | 部分成立 | 合成数据真实统计与独立系数复算有证据。执行代码溯源层为空，不能以“不做导出”免掉本项对执行代码的要求；不要求扩成完整论文导出。真实数据验收仍未完成。 |
| C11 | 部分成立 | 已读桌面与 320×568 截图；小屏截图为导航展开，没有证明在小屏完成全部确认。一次键盘确认有证据，VoiceOver 未验。 |
| C12 | 已有测试子集通过 | 本轮 42 个后端 + 38 个前端既有测试通过；不能推导新路径兼容绕过不存在。 |

## 5. 本轮实际验证与未验

- 既有后端：formal_chain_gates、outline、session_design_confirm，**42 passed**。
- 既有前端：formalConfirmationChain、AttachPanel、workspaceRunRecovery、runSteps，**38 passed**。
- 独立前端反例：**5 failed**，分别为两条跨会话迟到响应、编辑后误确认、设定确认逆序、未知核查宣称通过。日志 `review/frontend-invariants.log`。
- 独立 API/配置探针：7 个反例，详见 `review/backend-probes.json` 与脚本 `backend_probes.py`。脚本退出 0 代表完成采集，不代表验收通过；expected/actual 明确相反。
- 原浏览器材料实读 `06`、`09`、`11` PNG、测试脚本与复算 JSON。截图是执行者交付证据，本轮未冒充重跑其三进程 happy path。
- 本轮尝试浏览器故障 harness 时遇到测试注入的 React 模块实例/导出问题，没有拿到有效故障截图；改为同依赖环境 Vitest 精确复现，未将 harness 错误归为产品缺陷。临时 Vite :5193 已停止。
- 初次从 stdin 调 pytest 导致 macOS spawn 找不到 `<stdin>`，两项失败；改用有 `__main__` 保护的文件入口后 42 项通过。保留两次日志，不把测试入口错误算作产品回归。
- 所有本轮 API 探针使用独立临时数据库与合成状态，禁止外部网络，禁用真实 SSOT。配置事故复现只使用占位 key 构造配置，未调用真实模型。
- 本轮没有重跑 1066/645/509 的全套，也没有独立真人 VoiceOver 验收；原全套记录不替代上述新反例。

## 6. 交回执行者

先修 R7 测试隔离，再修 R1–R6/R8 和第 3 节故障恢复缺口。保留已实现的同会话 attach、真实预览与统一 Run 等待；不删重来。

修复后，提供相对当前待评版本的真正可重建增量（包含新文件内容）、最终哈希、全部反例从 RED 到 GREEN、C1–C12 逐项证据。评审对象停止变化后再独立复核。

新的顺序已经获用户认可，后续任务必须使用 [新流程规格](../specs/research-intent-to-design.md)。修正确认完整性不等于继续把“接入数据前必须确认设计”写死；前者约束执行与批准，后者已被产品决定替代。
