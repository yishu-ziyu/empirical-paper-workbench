# 给云端 ChatGPT Pro 的「渐进研究流」评审问题

日期：2026-09-17。评审对象是 `feat/progressive-research-flow` 上 `cd45d65..60feb83` 的五个提交（已 push 到 origin，未合入 main）。本文由本地 Agent 汇总。

读法约定：标〔实测〕的是本次实际跑出来、可复现的结果；标〔上轮自述〕的来自被评审分支里的文档，我没有复验。**本文不是完成报告，下面所有问题的答案都不预设成立。**

## 0. 交接块（按 `docs/specs/frontend-interaction-current.md` §7 格式）

```text
HANDOFF TO CHATGPT
repo: yishu-ziyu/empirical-paper-workbench
branch: feat/progressive-research-flow
base_sha: cd45d65d952649f84d4c6b19a52f71294d79e5b0
head_sha: 60feb83b57ca33c4a230a01d0120a62d2f5dec12

changed_files:
- docs/specs/frontend-interaction-current.md（新：前端交互基线 + §7 Agent↔Agent 交接协议）
- docs/design/progressive-research-flow/index.html（新：8 个状态的静态审阅稿，自标“未接入业务”）
- docs/design/progressive-research-flow/README.md、WIRING.md、HANDOFF.md（新：核对结论、接线记录、给下一个 Agent 的提示词）
- docs/design/progressive-research-flow/shots/{draft-01-idea,live-desk-entry,live-run-progress-open,old-first-value-hero}.png（新：4 张截图）
- frontend/src/lib/runSteps.ts（新：真实 run 事件 → 步骤列表的纯投影函数）
- frontend/src/lib/__tests__/runSteps.test.ts（新：11 项）
- frontend/src/components/RunProgressDisclosure.tsx（新：次级披露组件）
- frontend/src/components/__tests__/RunProgressDisclosure.test.tsx（新：8 项）
- frontend/src/lib/i18nWorkbench.ts（+39：runStep.* 中英文案）
- frontend/src/lib/workspace.ts（+39/-2：收集 run.progress 事件，向组件暴露 runSteps）
- frontend/src/App.tsx（+3：渲染在既有 run-status-bar 内）

what_changed:
- 「分析中」新增次级披露：默认只有一句真实状态 + 一个安静呼吸点；用户展开才看路径。
- 路径的每一步都来自后端真的发过的 `run.progress`（node / status / spec_id）；没有事件就整块不渲染。不产出百分比、不产出预计时间、不产出“还剩几步”。
- 在三条链路（上传、教学案例、方向 run）复用 `waitForRun` **已有的** `onEvent` 形参收集事件；未改动 `runEvents.ts` 的行为。
- 未改后端、未新增状态机、未做数字 count-up、未给账本加编辑入口。

runtime_evidence:
- 实际打开/运行了什么：本次评审未新开浏览器；也没有重跑真实 run。〔上轮自述〕的浏览器记录见 docs/design/progressive-research-flow/WIRING.md 与 shots/。
- 我实际做的是代码路径核对与测试执行，逐条见 verification。
- 实际观察到什么：见下方 verification 每条的原始结果。

verification:
- command: `cd frontend && npx vitest run`
  result: PASS — 67 个测试文件 / 491 项全部通过，16.26s。
- command: `git diff --stat cd45d65..60feb83`
  result: 16 files changed, 949 insertions(+), 2 deletions(-)。
- command: 核对全部 6 处 `waitForRun` 调用点是否传了事件收集器
  result: 3 处传（workspace.ts:1288 / 1371 / 1716），3 处未传（:918 会话恢复、:1214 另一条上传路径、:1461 设定跑批）。
- command: 核对 `runStep.held` 与 `runStep.node.specRun` 的可达性（代码路径，非运行时）
  result: 两者在真实事件/调用路径下不可达，依据见 §5 的 Q3、Q4。
- command: 核对后端真实 node 词表（agent/engine/prewrite.py、upload.py、backend/services/spec_run.py）
  result: 当前发出的 node 全部落在 `RUN_NODE_LABEL_KEYS` 表内；表外的回落分支现在不触发。

known_gaps_or_disagreements:
- 方向 run 的披露只在代码层接了，浏览器里没走通（教学案例之后表单落在隐藏子树、提交按钮 disabled、自动点击超时），需要一次人工点完的手动验收。〔上轮自述〕
- 设定跑批（`spec_run`）有自己的 k/总数 进度，没有并进同一块披露。
- pages/AgentSpikePage.tsx:36 仍有一份硬编码三阶段列表 `STAGES = ['明确关心结果','查看公开数据','形成研究方向']`，由本地 `phase` 状态驱动 —— 与本轮“不用假步骤”的形态相反，本轮未动。
- 分支基线落后 main：main 已到 `d2f5533`（含 #40 识别三轴），本分支停在 `cd45d65`。`git diff main..HEAD` 会把 #40 显示成约 2900 行删除，看起来像回退。
- 真人日常使用复测没有做；本轮证据是代码路径与自动化测试。

facts_vs_requests:
- 这批改动被称作「本地改动」：事实上五个提交在 2026-09-17 15:24 之前已经 push 到 `origin/feat/progressive-research-flow`，本地与 origin 同为 `60feb83`。真正没进版本库的只有未跟踪的 `frontend/public/_tmp-choice-progressive.html`。评审时请以 `cd45d65..60feb83` 为准，不要把那个临时页算进改动。
- 这个仓库被称为「论文那个项目」：仓库里的产品名是 econpaper，且 main 上已有 #40。**「本机最新」与「主线最新」不是同一份代码**，任何结论都要指明针对哪一个。

commits_pushed:
- e05ba85 docs: freeze current progressive interaction baseline
- a6acd91 design: add progressive research flow review
- 631cd35 docs: document progressive flow review usage
- 0b147eb docs: add local agent handoff prompt
- 60feb83 feat(workbench): drive the analysis-step disclosure from real run events
```

## 1. 这个产品希望做到什么

econpaper 是给写实证论文的人（当前定位：课程作业与学位论文）跑数据分析并生成正文的工具：上传数据 → 确认研究方向 → 估计主结果 → 稳健性 → 文献 → 大纲，每一步都有真实运行。

本轮只做一件事：把「分析中」这一段，从“看起来在忙”改成“如实报告后端真的发生了什么”。

当前设计基线是 `docs/specs/frontend-interaction-current.md`（本分支新增）。它的 §0 是工作规则「**总是以事实为准，不要附和我**」；§3 规定分析中默认只给一句当前动作 + 一个安静呼吸点，路径是次级信息、用户展开才看；**没有真实事件就不要造百分比、倒计时或假步骤**。§7 是 Agent↔Agent 交接协议。

前端能拿到的后端事实只有三样：`run.progress` 的 `node` / `status` / `spec_id`（`backend/routers/run_execution.py` 的 `_public_event` 只公开这些）。没有“还剩几步”、没有预计时间、没有百分比 —— 所以这一块的任何进度感都必须从真实事件里长出来。

## 2. 建议阅读顺序

1. 设计与规则：`docs/specs/frontend-interaction-current.md`（先读 §0、§3、§7）。
2. 被评审的代码，按数据流向：`frontend/src/lib/runSteps.ts` → `frontend/src/components/RunProgressDisclosure.tsx` → `frontend/src/lib/workspace.ts` 里三处 `collectRunStep` 调用点 → `frontend/src/App.tsx` 的渲染点。
3. 后端事实来源：`agent/engine/prewrite.py`（`PRWRITE_SEQUENCE` 与 `blocked` 的发出顺序）、`agent/engine/upload.py`、`backend/services/spec_run.py`、`backend/routers/run_execution.py`。
4. 上一轮的核对记录（自述，未由我复验）：`docs/design/progressive-research-flow/README.md`、`WIRING.md`、`HANDOFF.md`、`index.html` 与 `shots/`。
5. 测试：`frontend/src/lib/__tests__/runSteps.test.ts`、`frontend/src/components/__tests__/RunProgressDisclosure.test.tsx`。

文档按文件定位，不依赖容易过时的行号。请以实际代码检验本文描述。

## 3. 本轮改动的链路与约束

**事件来源与词表**（后端实际会发出的 node）：

- 上传链路 `agent/engine/upload.py`：`upload_data`、`clean_data`。
- 预写链路 `agent/engine/prewrite.py`：`PRWRITE_SEQUENCE` 的节点 —— `set_direction`、`identification_verify`、`run_estimate`、`robustness_check`、`search_literature`、`build_citation_graph`、`generate_title`、`generate_outline` —— 外加 `prewrite_preview`。
- 设定跑批 `backend/services/spec_run.py:164,220`：`spec_run`，带 `spec_id`。

**状态词表有两套，前端按原样接受、不替后端归一**：

- 上传与预写：`started` → 进行中；`completed` → 已完成；`blocked` → 被拦住。
- 设定跑批：`running` → 进行中；`done` → 已完成。

**`blocked` 的发出顺序值得注意**：`agent/engine/prewrite.py:116-130` 对同一个节点先发 `started`、再发 `completed`，识别失败时**紧接着对同一节点再发 `blocked`**，然后 run 结束。前端靠“同一 key 用最新状态覆盖”得到 `blocked`。

**前端契约**：

- `collectRunStep` 只留下带 `node` 的 `run.progress`（其它事件不构成步骤）；顺序即真实顺序，不排序、不补齐；最多留 200 条。
- `projectRunSteps` 用 `node::specId` 作 key：同节点重复出现时保留首次位置、用最新状态覆盖。
- `activeNode` = 最后一个未完成的步骤；`blocked` 是**全局** `any()`，不是逐步的。
- 认不出的 `status` 直接忽略（不猜）；认不出的 `node` 原样保留节点名。

**边界与不做**：不改后端；不改 `runEvents.ts` 行为；不新建状态机；不做 count-up；不给账本加编辑入口；不产出百分比/倒计时/剩余步数。

## 4. 已知证据

〔实测〕（可复现，命令见 §0）

- `cd frontend && npx vitest run`：67 个测试文件、491 项全部通过。
- `git diff --stat cd45d65..60feb83`：16 files changed, 949 insertions(+), 2 deletions(-)。
- 6 处 `waitForRun` 调用点中只有 3 处传了事件收集器；未传的三处是 `:918`（刷新后恢复正在跑的 run）、`:1214`（另一条上传路径）、`:1461`（设定跑批，改用自己 `done/total`）。
- `runStep.held` 与 `runStep.node.specRun` 按代码路径不可达（依据在 Q3、Q4）。
- 后端当前发出的 node 全部落在映射表内，表外的“原样显示节点名”回落分支现在不触发。
- `pages/AgentSpikePage.tsx:36` 的硬编码三阶段列表仍然存在。

〔上轮自述〕（来自分支内文档，未由我复验）

- 浏览器实测与审阅稿的核对结论（`WIRING.md`）：六个旧 token 逐字相同（`#181515`/`#f4efe4`/`#f1f0ed`/`#2f6b4f`/`#515151`/`#fffdf7`），只有分隔线不同；产品字体已经是 Instrument Serif + Instrument Sans + JetBrains Mono（`frontend/src/index.css:1`），不是审阅稿沿用的旧 serif 栈；纸张色板只覆盖空桌/引导页（`index.css:19-21` 有明文 scope 注释，工作台三栏是 `wb-*` 近白 + 蓝）；主按钮颜色与审阅稿不同；两稿与产品**都没有**背景纹理；审阅稿里的所有统计数字都能对上 `docs/design/first-value-entry/card-pair.json`，没有把历史结果说成本轮新运行。
- 审阅稿自身的实测问题：5 个按钮没有 handler；第 02 状态的两个选项走同一条路且问题文本相同；**第 05 状态那 3 个分析步骤是 `setTimeout` 驱动的假步骤** —— 这正好是本轮规范禁止的形态，本轮实现刻意没有照搬。
- 未验证：方向 run 的披露浏览器内未走通；真人复测未做。

## 5. 希望重点分析的问题

### Q1：这个分支的基线会不会静默回退 main 上的 #40？最高优先级

**事实**：本分支从 `cd45d65` 切出，main 已到 `d2f5533`（#40：识别三轴拆解、许可判定、三态 passed、EvidenceView）。因此 `git diff main..HEAD` 会把 #40 显示成约 2900 行删除，看着像回退，其实只是基线更早；这条分支上的前端也**不含** #40 的三轴识别读数。

**请判断**：
- 直接把这个分支合进 main，会不会丢掉 #40？如果不会，是靠什么机制保证的？
- 合并前应该 rebase 到 main，还是先把 #40 合进本分支？请给判断依据，不要给“都可以”。
- 在这个仓库的既有习惯（一条分支一个设计主题、main 持续前进）下，有没有办法让“看起来像回退、其实是基线更早”这类错误不再依赖人眼发现？最小可落地的做法是什么？

### Q2：200 条上限的静默截断，会不会造出“看着正常但其实是半截”的界面？

**事实**（`frontend/src/lib/workspace.ts` 的 `collectRunStep`）：`prev.length >= 200 ? prev : [...prev, event]` —— 到 200 条之后**直接不再追加，没有任何标记或提示**。

**请判断**：
- 哪些真实链路可能超过 200 条（设定跑批一次几十个 spec？长预写？）？超出后用户看到的是“步骤停在中途、界面一切正常”吗？
- 应该保留什么、丢弃什么？该以什么形式让人知道被截断（界面、控制台、还是干脆不设上限而改成分页/折叠）？

### Q3：事件收集的覆盖不对称，是有意还是遗漏？

**事实**（6 处 `waitForRun` 调用点，3 处传了收集器）：

| 位置 | 场景 | 是否收集 |
|---|---|---|
| `workspace.ts:1288` | 上传 | 是 |
| `workspace.ts:1371` | 上传/教学案例 | 是 |
| `workspace.ts:1716` | 方向 run | 是 |
| `workspace.ts:918` | 刷新后恢复正在跑的 run | 否 |
| `workspace.ts:1214` | 另一条上传路径 | 否 |
| `workspace.ts:1461` | 设定跑批 `spec_run` | 否（改用自己 `done/total`） |

**请判断**：
- 这三处不收集，分别是有意的最小边界还是遗漏？请分开回答。
- “刷新页面后披露整块消失”与“同一件事两条上传路径行为不同”，哪个更严重、更该先修？
- `RUN_NODE_LABEL_KEYS` 里的 `spec_run` 与 i18n 的 `runStep.node.specRun`，按上面的调用路径是否已经是不可达的死文案（我判断是）？设定跑批该并进这块披露，还是保持它自己的 k/总数 更诚实？

### Q4：这里有没有把“没发生的事”说成“已发生”？

**事实**（`RunProgressDisclosure.tsx:44-48`）：摘要文案是

```
activeNode ? 节点名 : blocked ? '停在一个需要你决定的检查上' : '这一步已完成'
```

`projectRunSteps` 的 `activeNode` 取最后一个 `status !== 'done'` 的步骤，而 `blocked` 本身就是一种非 done 状态。因此 **`blocked === true` 必然推出 `activeNode !== null`**，中间那句永远不出现；反过来，一个被 `blocked` 卡住的 run，摘要只显示节点名（例如“核对识别策略”）加一个琥珀色圆点，用户看不出自己正停在一个需要他决定的地方。另一头，“这一步已完成”会在所有已发事件都已 done、但 run 还没报 `run.succeeded` 的时刻出现。

**请判断**：
- 这是不是本项目最该避免的那类形态（把未知/进行中说成已完成）？请给出你能构造的最短反例。
- 被 blocked 时用户能不能从摘要知道“轮到我了”？最小且诚实的修法是什么（改判断顺序？加一句真实状态？还是这个摘要根本不该由前端推断）？
- 顺带请核：`runStep.held` 是否已成死文案，应当删掉还是应当在修好判断顺序后变得可达？

### Q5：并行扇出下，“当前动作”这个取法站得住吗？

**事实**：`runSteps.ts` 把 `activeNode` 定义为“最后出现的未完成项”，注释说并行扇出时事件顺序就是真实发生顺序、不能假设这是一条线性流水线。后端 `prewrite.py` 的图是有并行扇入的（`estimate` 先于 `literature` 跑，注释写明是为了避免慢检索盖住表格）。`blocked` 用的是全局 `any()`，不是逐步标记。

**请判断**：
- 请用真实的事件交错（例如 `search_literature` started 之后 `run_estimate` 的 started/completed 夹进来）检验：这个取法给出的“当前动作”在哪些交错下会是错的？给出最短的交错序列。
- `blocked` 全局化会不会把已被后续事件解除的状态一直标红？（注意 `prewrite.py` 对同一节点是先 `completed` 后 `blocked`。）
- 如果要更准，应该在后端补什么事件，还是前端能靠现有字段算对？请优先给不改后端也能准确的做法。

### Q6：认不出的节点直接摆给用户，是诚实还是隐患？

**事实**：组件在 `labelKey` 为空时回落到 `step.node` 原文。我核对了后端真实词表（`PRWRITE_SEQUENCE` + `prewrite_preview` + `upload_data`/`clean_data` + `spec_run`），当前**没有**落在表外的节点，所以这条回落现在不触发。

**请判断**：
- 这是一个应当保留的诚实回落（宁可见到内部标识，也不要假装知道），还是一个迟早会把 `identification_verify` 这类英文标识摆给写论文的人看的隐患？
- 如果保留，回落到什么措辞更符合本产品“给课程作业与学位论文作者看”的基准？如果改成隐藏未知节点，会不会违反基线 §0 的“以事实为准”？

### Q7：披露组件的呈现与无障碍

**事实**：展开面板用 `fixed bottom-9 left-5 z-40 w-[min(360px,90vw)]` 固定定位；`summary` 里有一个 `sr-only` 文案；动效复用 `wb-dot-running` / `wb-pane-enter` / `wb-stagger`。

**请评审**：
- 极小屏、侧栏折叠、同时展开多处时会不会重叠或遮挡？这个面板该不该是 `fixed`，还是应当跟着状态栏走？
- 键盘可达吗（`<details>/<summary>` 的默认行为够不够，`sr-only` 文案读出来是什么）？
- `prefers-reduced-motion` 下这三个 primitive 是否真的会停 —— **请去 CSS 里核实，不要只看类名**。
- `status` 的文字（“进行中”/“已完成”/“被拦住”）与圆点颜色是两套信号，色觉障碍用户是否仍能分辨？

### Q8：测试盲区，以及“代码接了但没人走过”的那一条

**事实**：本轮新增 19 项测试全部是纯函数与组件级，没有一项覆盖“真实 run 事件 → `workspace.ts` 收集 → 组件显示”这条链。我实跑全前端 491 项全通过。〔上轮自述〕方向 run 的披露在浏览器里没走通。另外，`pages/AgentSpikePage.tsx:36` 的硬编码三阶段列表仍在。

**请评审**：
- 最少但最有辨别力的补齐方式是什么？它要能区分“收集器没接上”和“组件没渲染”这两种失败 —— 单靠组件测试做不到这一点，对吗？
- “方向 run 的披露在浏览器里没走通”该用什么验收关掉？请给出一个可重复的、不依赖自动点击隐藏表单的做法。
- `AgentSpikePage` 那三阶段是本轮应当一并清掉的同类形态，还是单独立项？请给判断，不要给“都可以”。

### Q9（流程）：交接协议要不要进 CI？

**事实**：本轮新增的 §7 要求每次交接带 `base_sha` / `head_sha` / `changed_files` / `what_changed` / `runtime_evidence` / `verification` / `known_gaps_or_disagreements` / `facts_vs_requests` / `commits_pushed`。但这五个提交里没有一份符合该格式的交接块（`HANDOFF.md` 只是给下一个 Agent 的提示词，不是交接记录）。

**请判断**：这套协议该进 CI 检查（例如要求分支上有对应文件），还是留在文档里靠人遵守？在“一条分支一个设计主题”的既有习惯下，什么位置放这份交接记录最不容易过时？

## 6. 希望收到的输出

请先独立阅读代码，**不要因为本文写了“实测”就认定正确**（我的核对只有代码路径与自动化测试，没有浏览器与真实运行的复验）。不要只做通用架构讲解，也不需要肯定已有方案。

1. 一张问题表：优先级 / 可观察影响 / 证据文件 / 根因判断 / 置信度 / 最小修复 / 验收办法。
2. 对 Q1–Q9 逐项答复。证据不足就指出缺什么，不要猜成定论。区分“我读了代码可以确定”和“需要运行才能确定”。
3. 对前三项关键修复给函数级改动建议，并列出**应该先失败的测试**。
4. 指出本地 Agent 的假设或验收标准哪里不合理；但不要自行放宽基线已冻结的要求（`docs/specs/frontend-interaction-current.md` §0/§3）。需要取舍的地方单列给用户决定。
5. 最后给用户不超过 5 个真正影响决策的问题，不要把技术排查工作交回给用户。

若你通过 DevSpace 连着本机工作区：可以读文件、跑测试（`cd frontend && npx vitest run`）。**请不要 commit、不要 push、不要改生产代码**，也不要访问本机私有数据（原始数据与受限制样本不在这个仓库里）。仓库里只有整理后的证据与截图。
