# 核心业务与当前页面映射

> 版本说明：下文为确认链实施前的代码盘点，不是实施后的现状。FORMAL-CONFIRMATION-CHAIN-1 已交付，独立结论为需要修复，见 [2026-09-17 评审](../reviews/20260917-formal-confirmation-chain-independent-review.md)。用户新确认的意图优先顺序见 [下一批规格](../specs/research-intent-to-design.md)，不要把下文旧流程顺序重新当作产品决定。

核对日期：2026-09-17。基线：`feat/progressive-research-flow@2d83c2c9c716` + 本地未提交修复。
配套：[核心产品契约](core-product-contract.md)。本页是当前代码盘点与待办，不是新视觉方案，也不改变冻结要求。

## 当前最重要的判断

问题不只是页面太多：**有后端确认能力，却没有接到正式用户入口；有页面确认反馈，却没有对应的后端事实。**
当前不能把“各组件测试通过”当成“正式研究全程可完成”。

## 页面各自负责什么

| 当前入口/组件 | 应负责的业务 | 当前代码事实 | 后续处理 |
|---|---|---|---|
| `DeskPage` → `App` | 收想法、一次一个有效追问，建立研究问题 | `App.tsx:370–395` 的确认回调只设置 `shapedQuestion` 并关闭空桌；之后进入工作台。 | 保留入口；接设计草稿与确认，不把关掉空桌当作完整业务确认。渐进工作台后置另按现有设计基线做。 |
| `question` / `DirectionForm` | 编辑问题与执行方向 | 非教学路径同时出现 AttachPanel 和方向表单；教学路径将方向表单放在技术详情。 | 不删表单；明确它修改哪个对象，不能用普通方法选择替代正式设计锁。 |
| `design` / `SpecificationSpacePanel` | 查看确认设计，必要时管理多分析方案 | 当前主要消费 `directionRecord` 和已有 `research.specification_space`。后端有独立 design propose/confirm。 | 补正式设计操作并回读 snapshot；不要把“确认方案空间”混同“确认研究设计”。 |
| `AttachPanel` / `data` | 候选数据、清洗就绪、确认挂接 | `AttachPanel.confirmAttach()` 先本地 `setConfirmed(true)`，再调用可选回调；正式挂载处没有传 `onConfirmAttach`。Data 视图主要是上传与探索。 | 首要接线缺口：真实 confirm-attach 成功才能显示“已挂接”；失败保持未确认且可重试。回跳位置必须有可用动作。 |
| 估计前确认 | 确认 Table 1 与具体设定，再启动估计 | 后端 `outline.py` 有 `/prewrite/confirm`，串行方向 run 会停在预览处；当前挂载路径未找到相应客户端操作。 | 补两段确认及继续动作，不用自动设 true 或删除闸门来跑通。 |
| `overview` / `OverviewView` | 汇总已有对象，回到当前可执行的下一步 | 当前已有总览；不是正式设计确认或状态真相的拥有者。 | 保留为研究积累后的回看入口，不再扩一份线性流程状态。 |
| `evidence` / `EvidenceLab`、`EvidenceView` | 读结果、查来源、比较并采用 | `WorkbenchArtifact.tsx:374–401` 依据是否存在 specification runs 切换两种视图；有 EvidenceLab 才接现有结论/主分析动作。 | 保留二者，先对齐普通数据与教学案例的采用语义，不做机械合并。 |
| `literature` | 方法依据与主题材料，明确引用选用 | 当前中栏主要展示 `literatureSource` 与主张文字。 | 核对检索、选文献、正文引用链；来源标签存在不等于引用选择闭环已实现。方法/主题文献仍按已定分工。 |
| `paper` / `ChapterWriter`、`WriteLoop` | 大纲、按章编辑/评审/确认与历史 | 已有写作、预览、历史；论文页部分流程控制仍放在“研究轨迹”的折叠区。 | 保留正文编辑器与历史；必要的当前决策不应藏在审计区。先补业务动作，再调布局。 |
| 状态栏 / `RunProgressDisclosure` | 当前 run 的真实观察 | 已改为 run-scoped、统一等待入口；文案不再把已收步骤结束当整个 run 完成。 | 保留修复；真实上传/方向/刷新路径仍需浏览器验证，不引用旧截图当此次通过。 |
| Guide、Spike、设计 HTML | 说明产品、实验与视觉探索 | Guide 显式进入；Spike 受功能开关控制；`docs/design` 原型不属于已挂载业务。 | 不作为 P0 完成依据；不因历史文件还在就恢复旧入口或另造产品。 |

## 决定后续开发顺序的缺口

### 1. 正式研究的几个确认没有串起来

证据：`backend/routers/design.py:1–65` 提供设计提出/确认；`backend/routers/outline.py:174–239` 提供估计前确认。
当前 `App` / `WorkbenchArtifact` 已核对的挂载路径没有调用这些动作。对整个 `frontend/src` 排除生成类型后搜索 `/design/`、`/prewrite/`、`/confirm-attach` 也未发现对应网络调用。
生成的 `types/api.ts` 包含端点定义，不等于用户能操作端点。

应先失败的测试：从空桌的可见入口确认问题 → 提出设计 → 编辑/确认设计 → 回读确认对象；不能由测试偷偷 POST 确认来补上缺失 UI。

### 2. 数据确认当前可能只改变按钮文字

证据：`frontend/src/components/AttachPanel.tsx:90–94` 先设置本地 confirmed，再可选调用回调；`WorkbenchArtifact.tsx:183–197` 挂载组件时只传候选、上传状态与选文件动作。
据此可确定该回调未接到这一正式入口；此判断来自代码，没有冒充本轮浏览器点击复现。

应先失败的测试：真实已就绪候选点击“确认挂接”，必须请求后端且 snapshot 返回 `dataAttached=true`；后端拒绝或网络失败时不得显示已挂接。刷新后确认状态仍与后端一致。
同时检查被引导至 Data 视图时能否看到并执行同一确认动作。

### 3. “采用结论 → 写结果章”不能只在教学入口成立

证据：`WorkbenchArtifact.tsx:374–389` 的 EvidenceLab 分支承载批准结论/采用动作；`agent/engine/readiness.py:68–76` 仅在已有 claims 时检查批准、stale 和主分析不匹配，`:143–162` 在无 claims 时另有旧估计回退。
这不能证明普通 CSV 入口已经满足“论文只消费用户明确采用的结果”。应保留历史兼容，不把兼容回退当新正式路径的完成标准。

应先失败的测试：非 Card 研究未采用结论时不能将结果章标成已关联当前证据；采用后才能成立；更换关联证据后需重核，旧结论仍可回查。

### 4. 上游修改后的失效传播需要一张依赖表

已有机制：`session_design.lock_confirmed_design/locked_design`、`research_lab.bump_evidence_revision/mark_results_chapters_stale`、`readiness.claim_revision_is_stale`。
尚未逐入口验证：修改问题/设计、替换数据、重跑或设为主分析时，各自应撤销哪些确认与批准。不能一概清空全部，也不能一概沿用。

应先失败的测试：选择一种实际改变分析含义的修改，追踪其受影响的设定、证据、结论和结果章；另加只改 UI 语言的负例，确保不会无理由全部失效。

## 收敛而不是重建

不新增研究状态数据库或全局前端 stage；不因界面看着相似就合并 EvidenceLab 与 EvidenceView；不删默认六章、引用约束或必要确认。
先做缺口 1–2 及估计前确认，使一条正式研究路径可走；再做 3–4 与导出一致性。每一项建立对应业务测试，再考虑展示精简。
Card 继续作独立回归路径；不把教学模板偷偷注入普通研究。多方法、外部数据源、光标演示暂不扩展，但已有功能不删除。

## 截图读取验证与后续 QA

本轮已用本地 Vite 在 `127.0.0.1:5189` 启动当前前端，通过已安装 Playwright / Chrome 截取 1440×900 空桌，再由 `DevSpace.read` 返回图片进行视觉查看。
截图位于仓库外：`../.devspace-evidence/econpaper-core-20260917/current-empty-desk.png`。
图片可见真实空桌的中央想法输入、教学案例与自带数据入口、左侧导航；不是设计 HTML 的截图。
这证明“截图 → 读取图片 → 视觉检查”可用。没有在此轮启动后端/runner、调用模型或完成研究交互；不计作端到端验收、无错误控制台验收或 VoiceOver 验收。
实际日志出现 `/auth/me` 代理连接 `127.0.0.1:8000` 被拒绝，符合本轮后端未启动的条件，不能记作无错误。截图完成后已停止本轮 Vite 进程，并确认 5189 不再监听。

后续独立 QA：待 P0 范围确认、接线完成后再启动。给 Pi 的范围应是读取契约和同一份待验代码、调用 Playwright、输出失败复现与证据；禁止改产品代码、提交、推送或操作真实研究数据。
若需要写自动化脚本，使用独立 worktree，并先核对它确实含本地待验修改，不能从旧 HEAD 开分支就声称测了新代码。不同任务隔离端口、数据库和临时文件，收尾关闭所启进程。
必须覆盖关键确认的失败分支、运行中刷新、旧 run 隔离、采用后证据更新、实际导出文件及小屏/键盘。截图可判视觉问题；VoiceOver 的实际播报仍单列验收。
