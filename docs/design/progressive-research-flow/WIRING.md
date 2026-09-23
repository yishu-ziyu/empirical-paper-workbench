# 渐进研究流：审阅稿核对与最小接线（2026-09-17）

本文件记录三件事，只写结论与出处，不写探索过程：

1. 审阅稿 `index.html` 与**真实运行中的产品**逐项核对结果（哪些继承、哪些不一致）；
2. 本轮做的最小接线（接什么、读什么事实源、不做什么）；
3. 仍未接线 / 仍存疑的地方。

核对方法：在本地真实跑起前端（`127.0.0.1:5173`）与后端（`127.0.0.1:8000`），
用浏览器实测计算样式、字体、整页高度与真实 run 事件，不用静态读码替代运行。

---

## 1. 审阅稿 vs 真实产品：逐项事实

### 1.1 逐字相同的部分（继承了旧稿的底色）

在浏览器里读 `getComputedStyle`，两稿与真实产品的 token 对照：

| token | 旧稿 `first-value-entry` | 新稿 `progressive-research-flow` | 真实产品（`index.css` `:root` + `tailwind.config.cjs`） |
| --- | --- | --- | --- |
| 墨色 | `#181515` | `#181515` | `#181515`（`--ink`，实测命中） |
| 纸张 | `#f4efe4` | `#f4efe4` | `#f4efe4`（`paper`/`bg`，实测 body 背景 `rgb(244,239,228)`） |
| 米白 | `#f1f0ed` | `#f1f0ed` | `#f1f0ed`（`--cream`，实测命中） |
| 墨绿 | `#2f6b4f` | `#2f6b4f` | `#2f6b4f`（`accent`） |
| 次要文字 | `#515151` | `#515151` | `#515151`（`--muted`，实测命中） |
| 分隔线 | `#d8d6cd` | `#d8d6cd` | **`#d8d2c6`（`border`）—— 不一致** |
| 面板底 | — | `#fffdf7`（`--white`） | `#fffdf7`（`panel`） |
| 警示黄 | — | `#8a6a12`（`--amber`） | `#8a6a12`（`warning`） |

结论：审阅稿的纸张/暖灰/墨色/墨绿/米白底**逐字等于**真实产品的 legacy token 组；
只有分隔线差一档（`#d8d6cd` vs `#d8d2c6`）。两稿与真实产品都**没有**任何
`background-image` 纹理（浏览器实测：三者的带纹理元素列表都是空）。

### 1.2 不一致的部分（这些必须知道，否则会把审阅稿当成产品的样子）

1. **字体族不同。** 审阅稿沿用旧稿的 `'Iowan Old Style','Songti SC',Georgia,serif` 与
   `-apple-system,…`；真实产品的 serif 是 `"Instrument Serif","Noto Serif SC",Georgia,serif`、
   sans 是 `"Instrument Sans",system-ui,…`、mono 是 `"JetBrains Mono",Menlo`，
   由 `frontend/src/index.css:1` 从 Google Fonts 引入，实测已加载
   （`document.fonts.check('16px "Instrument Serif"') === true`）。
   即：**纸质编辑气质在真实产品里由 Instrument Serif 承担，不是 Iowan Old Style。**
2. **主按钮颜色不同。** 审阅稿的主按钮是墨绿实心（`--green #2f6b4f`）；真实产品空桌的
   主按钮是**近黑**实心（实测「体验一项真实研究」为深色药丸），工作台的主按钮是
   `--wb-primary #2563eb`（蓝）。
3. **纸张 token 只覆盖产品的一半。** 真实产品有两套 token：空桌/引导页用 legacy
   纸张组（`tailwind.config.cjs:24-34`），**主工作台三栏用 `wb-*` 近白中性 + 蓝色**
   （`index.css:19-21` 有明文 scope 注释：`Desk and Guide keep the paper/ink/green board`）。
   所以「继承旧稿底色」在真实产品里等于**继承进入工作台之前的那一段**，不是整个产品。
4. **布局密度差异是真实的、也是本轮要的。** 实测旧稿「全部页面」整页高 `3353px`（多节
   滚动 + 双栏 hero + 并排两条估计）；审阅稿单状态 `901px`（一屏、无滚动、一个焦点）。
   这一点上审阅稿做到了它自称的事。

### 1.3 审阅稿自身的问题（实测，不是印象）

| 现象 | 证据 |
| --- | --- |
| 5 个按钮没有处理逻辑，点了没反应 | 「＋ 也可以写下你预期看到什么」「示例」「我想改一句」「先看完整设定」「先保留为候选」——逐个点击后 `data-stage` 不变 |
| 第 02 状态的两个选项走**同一条路** | 选 1 与选 2 都到 `03/08`，问题文本都是「教育程度是否提高工资？」——那个「真正影响研究方向的追问」实际上不影响任何下游 |
| 第 05 状态的 3 个步骤是**定时器**，不是事件 | `setTimeout` 750/1500/2250ms 依次点亮；步骤名「核对数据与结果变量 / 比较候选估计设定 / 检查 IV 强度提示」在后端没有对应事件。审阅稿自己标了「未接入业务」，但它也正是本轮规范禁止的「假步骤」形态——**接线时不能照搬这 3 个名字，只能接真实事件。** |
| 所有数字都能追溯到历史记录 | OLS `0.0747`(SE `0.0035`, HC1, n 3010)、IV `0.1315`(SE `0.0550`, nonrobust)、`F_eff 14.1387`、`F first-stage 13.2558`、复现状态、数据 SHA-256、producer run id —— 逐项等于 `first-value-entry/card-pair.json`。来源抽屉与风险页读数也一致。**没有把历史结果说成新运行。** |

---

## 2. 本轮最小接线

### 2.1 接的是什么

审阅稿第 05 状态（分析中）的核心主张是：**默认给一句真实状态 + 安静呼吸点，
路径是次级信息、用户主动展开；没有真实事件就不出现步骤。**
真实产品里这件事只做到一半：`run.progress` 事件**已经存在**（`backend/runner.py:187-200`
发出，`backend/routers/run_execution.py:182-197` 只公开 `seq/type/kind/status/node/spec_id`），
但前端只有设定跑批用了它的 `spec_id` 做「k/总数」，**没有任何地方把 `node` 展示成路径**。

所以接线只做一件事：把真实事件投影成「这一步怎样推进」，接到已有的状态栏上。

| 文件 | 改动 |
| --- | --- |
| `frontend/src/lib/runSteps.ts`（新增） | 纯函数 `projectRunSteps(events)`：只吃 `run.progress` + `node`，产出 `activeNode` / `steps` / `blocked` / `hasSteps`。**没有百分比、没有预计时间、没有剩余步数。** 节点名 → 文案 key 的映射表逐字对齐 `agent/engine/prewrite.py` 的 `PRWRITE_SEQUENCE` 与 `agent/engine/upload.py`；认不出的节点**原样保留节点名**，不丢弃、不改名；认不出的 `status` 直接忽略，不猜。 |
| `frontend/src/components/RunProgressDisclosure.tsx`（新增） | 一句当前动作（来自真实事件的节点）+ `<details>＋ 这一步怎样推进</details>`，默认**折叠**。复用现有 primitive：`wb-dot-running`（呼吸点）、`wb-pane-in`（进入）、`wb-stagger`（错峰）。没有事件时返回 `null`，整块不存在。 |
| `frontend/src/lib/workspace.ts` | 复用 `waitForRun` **已有的** `onEvent` 形参（`lib/runEvents.ts:127`，原文件就有，无需改 runEvents），把三个真实 run 的事件收进 `runSteps` 状态：上传（`uploadCsv`）、教学案例（`handleTryCard`）、方向 run（`handleDirectionSubmit`）。事件上限 200 条。 |
| `frontend/src/App.tsx` | 在既有状态栏 `run-status-bar` 里渲染该组件（`run-state` 之后）。原本的「● 正在估计…」一句真实状态保留不动。 |
| `frontend/src/lib/i18nWorkbench.ts` | 中英各新增 18 条 `runStep.*` 文案（含 12 个真实节点名）。 |

### 2.2 明确没有做（避免造第二套系统）

- **没有新状态机**：不新增 store、不新增 reducer、不缓存「阶段」。`runSteps` 只是
  把 `waitForRun` 已经推给前端的事件留了一份，展示层每次现投影（`useMemo`）。
- **没有改后端、没有改 `runEvents.ts` 的既有行为**，也**没有动 `wb-*` 工作台视觉**。
- **没有把审阅稿的 3 个假步骤名搬进来**（见 §1.3）。真实上传链路只有
  `upload_data` / `clean_data` 两个节点，页面就只显示两个。
- **没有 count-up**：全仓本来就 `grep` 不到 count-up 实现，本轮也没有加。
- **账本仍是只读**：本轮没有给账本加编辑入口。

### 2.3 真实运行证据

真的跑了一次教学案例（`POST /api/demos/card` → run `f08ccee6-6451-4ca4-8b16-6825d2a6bd31`）：

- 页面在 `t+1.2s` 出现披露区，折叠态摘要显示「清洗数据」，展开后是
  `upload_data:已完成`、`clean_data:进行中`；run 结束后两条都是「已完成」。
- 同一 run 的 SSE 原始帧（`curl /runs/{id}/events`）：
  `run.accepted` → `run.claimed` → `run.progress node=upload_data started/completed`
  → `run.progress node=clean_data started/completed` → `run.succeeded`。
  **页面显示的步骤条数 = 真实 `run.progress` 去重后的节点数（2），
  accepted/claimed/succeeded 三类事件被正确忽略，没有多出一条。**

---

## 3. 仍未接线 / 仍存疑

1. **方向 run 的真实路径没能在浏览器里走通。** 教学案例之后方向表单已确认
   （`rail-question` 显示「研究问题已确认」），表单在隐藏子树里、提交按钮 disabled，
   自动点击走不通。方向 run 的接线代码是同一份（复用 `collectRunStep`），
   但**浏览器端只验证了上传路径**，`identification_verify / run_estimate /
   search_literature` 这些节点尚未在真实浏览器里看到。需要一次人工点完的手动验收，
   或修好自动化路径。
2. **设定跑批（`spec_run`）没有接进同一块披露。** 它已经有自己的 `k/总数`
   进度（`workspace.ts` 的 `waitForSpecRun`），本轮没动它，避免两处显示同一件事。
3. **`AgentSpikePage` 的 3 个「阶段」仍是前端硬编码启发式**
   （`pages/AgentSpikePage.tsx` 的 `STAGES`），不是后端事件。它与本轮改动无关，
   但正好是本轮规范点名禁止的形态；是否要用同一机制替掉，需要单独决定。
4. **折叠区用 `position: fixed` 贴在状态栏上方**，会盖住左下角的侧栏内容。
   在 1440×900 下可接受；如果它在真实使用里碍事，应改成侧栏内锚定而不是 fixed。
5. **审阅稿第 02 状态的两个选项不改下游**（§1.3）。产品里对应的是
   「因果 vs 相关」这个真正的设计分叉，后端有 `claim_mode` / 识别许可这套真实语义
   （见 `agent/engine/identification_state.py`），但审阅稿把它画成了一个装饰性追问。
   这条属于设计待定，本轮没有替它做决定。

---

## 4. 独立评审后的加固（2026-09-17）

上面的 §2–§3 是 `60feb83` 当时的实现与已知缺口，保留作历史记录；后续修复以
`docs/acceptance/progressive-run-truth-fixes.md` 为准。已经闭合的关键项：

- 分支先合入 `main@d2f5533`，#40 与渐进披露在同一集成树上验证，不再用端点 diff 猜合并结果。
- `runSteps` 改为带 `sessionId / runId / kind` 的当前-run观测；旧 run 晚到事件不再污染新 run。
- 新运行与刷新恢复共用 `waitForTrackedRun`，不再有三处接了、三处漏接的分叉。
- blocked 摘要明确写「被拦住」；progress 全 done 但 run 未终结时只写“等待运行结果”。
- 200 条容量改为可更新、可淘汰、可见截断，不再达到上限后静默冻结。
- `spec_run` 继续使用自己的 k/总数，删除通用披露中的不可达映射与死文案。
- 未知节点摘要使用中性文案，展开详情保留原始 node。
- 面板增加小屏高度上限、滚动、锚定与 live region；实验 `/spike` 加生产门禁。
- App 级测试现已覆盖 SSE → workspace → 披露，以及刷新恢复与旧 run 晚到事件。
- 完整 backend 压测式套件暴露出 authority probe 的 200ms timeout 会在短暂数据库拥塞时
  误把合法 run 留在 `RUNNING`；现允许慢探针在 650ms 内返回，同时保留持续失权 <1s 取消与
  owner/epoch 写入 fencing，不以放宽旧安全要求换稳定性。

仍需真人浏览器证据的不是接线正确性，而是小屏/键盘/VoiceOver 与一次真实方向 run 的体验。
