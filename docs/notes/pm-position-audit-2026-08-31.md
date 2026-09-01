# PM 定位审计：识别迭代 vs 线性流水线

> 日期：2026-08-31 · 应 team-lead（Sun）判断做验证/推翻
> 结论：**Sun 的矛盾成立，但归因错了。代码里藏着一个更致命的问题。**
>
> **修订 1（pm2 复核后）**：证据 5 原判"设定表是死代码"**错误**，已更正为"接线已完成但会谎报成功"；方向 C 工作量由 1–2 周下修至半天–1 天；方向 A 补入路由/星级必须同改的隐含坑。正文保留修订痕迹，不掩盖原错。

---

## 一、对 Sun 判断的裁定

**判定：成立，但错不在"用户想迭代而流程不让"。真正的问题更靠前两层。**

### 证据 1：Sun 举例的那个检验，产品里根本没有

`agent/nodes/identification_verify.py` 全节点只跑 6 个诊断（grep `"test":` 共 22 处，去重后）：

| 方法 | 实际跑的检验 | 缺失的关键检验 |
|---|---|---|
| DiD | `bacon_decomposition`、`callaway_santanna` | **平行趋势、事件研究/前趋势、无预期效应** |
| IV | `iv_diag`、`effective_f_test`（弱工具 F<10） | **过度识别（Sargan / Hansen J）** |
| RD | `mccrary_test`、`rdrobust` | — |
| SCM | `synth_time_placebo` | — |

`robustness_check.py` 的 DiD 套餐是 clustering + heterogeneity + `wild_cluster_bootstrap`，**也没有前趋势安慰剂**。

所以「试 DID → 平行趋势检验不过 → 换事件研究」这个循环，产品连入口都没有：**它从不检验平行趋势，也就永远不会不过。**

### 证据 2：更糟——方法章被强制要求写下"平行趋势"

`agent/nodes/review_sources/structure_checks.py:23-24`：

```python
"did": ["平行趋势", "parallel trend", "sutva", "无预期效应", "no anticipation"],
```

假设菜单命中 <2 条 → 结构检查失败 → 打回重写。

即：**引擎从未验过的假设，评审逼模型写进论文。** paper-engine spec 花整章防"AI 编造"，防住了数字（`treatment_row` 子串接地），**没防住识别论证**。

### 证据 3：迭代环存在，但只对"全失败"开放

`agent/graph.py:168` 有环 `hitl_pause → identification_verify`。触发条件在 `route_after_identification`（graph.py:56）：

```python
if state.get("star_rating") == 0:
    return "hitl_pause"
```

`_compute_star_rating`（identification_verify.py:501-507）：有 pass 有 fail → **1 星**。1/2/None 星一律放行进估计。

真实场景（DiD 部分诊断 fail）→ 1 星 → 不暂停 → 直接往下写。产品对"部分失败"的策略是"标注风险继续走"，不是"回到识别重来"。

### 证据 4：换方法的路径存在，但不做失效传播（最危险）

`backend/facade/__init__.py:331-351` `run_identification_verify`：

```python
state = self.get_state(session_id)
result = identification_verify_node(state)
state = {**state, **result}   # ← 只 merge，不清下游
self.save_state(session_id, state)
```

改 DiD → IV 之后：
- 旧 DiD `estimate` 仍带 `produced_by="estimate"`（合法）
- `_infer_journey`（progress.py:143）仍判定第 4/5 站已完成
- `paper_ready_to_write` 仍放行结果章
- 已写的旧章节仍可导出

全仓唯一一处 stale 清理是 `facade/__init__.py:564`（改章节后删旧评分）。**没有任何一处做方法/方向变更的级联失效。**

### 证据 5（**已更正，原结论错误**）：设定表不是死代码，但它会谎报成功

> **更正说明（pm2 复核后我自行验证）**：原稿称"spec_curve 是死代码、无任何节点调用"——**这是错的**。
> 错因：我用一个 `head_limit=20` 的全仓 grep 得出"无调用"，结果被截断，我把"没看到"当成了"不存在"。**取证方法错误，结论作废。**

实际调用链（`agent/nodes/robustness_check.py:671-691`）：

```python
spec_curve = None
if not cs_main and method not in {"iv", "rd", "scm"}:
    try:
        from ..design.spec_curve import run_spec_curve_from_state
        spec_curve = run_spec_curve_from_state({...})
    except Exception as exc:
        diagnostics.append({"test": "spec_curve", "status": "error", "error": str(exc)})
```

`spec_curve` 确实跑在 `robustness_check` 内，产物写进 `payload["spec_curve"]`。前端 `PAPER_NODES`（`paperPath.ts:7`）也有它的节点位。

真问题换了，且比"死代码"更糟：

1. **对 IV / RD / SCM / CS 静默跳过。** `method not in {"iv","rd","scm"}` 且 `not cs_main` 才跑。跳过时**不写 diagnostics、不报错、不提示**，只是 `spec_curve = None`。四类方法（恰好是需要识别策略的那四类）拿不到设定表，且无从察觉。

2. **前端谎报完成。** `paperPath.ts:86`：

   ```ts
   const spec: PathStatus = state.hasReadout ? 'completed' : state.hasDirection ? 'active' : 'pending'
   ```

   而 `hasReadout`（`workspace.ts:1000`）= `claim || treatmentRow || literatureSource || identFailed || robustnessStatus`，**与 spec_curve 无关**。
   → IV/RD/SCM/CS 下 spec_curve 为 None，UI 照样显示"设定表 completed"。

这跟 `_infer_journey` 用 `body_chapters` 推断"建模已完成"（paper-engine spec 第 65 行已标记）是同一类 bug：**进度由无关的代理信号推断，而非由产物本身。**

### 证据 6：第 8 站是空壳

8 站 = 选题/文献/数据清洗/识别策略/估计建模/稳健性审计/写作评审/**降AIGC导出**。
「降AIGC」全仓只出现在 `openapi.json:3569` 和 `frontend/src/types/api.ts:1673` 的描述字符串里，**零实现**。实际是 7 站 + 一个标签。

### 证据 7（pm2 提出，我已逐条验证）：用户可见层没有产品层

**7a. 两处"永不完成"。** `paperPath.ts:95-96`（pm2 写 93-94，行号有 ±2 偏移，内容正确）：

```ts
const translate: PathStatus = state.canExport ? 'active' : 'pending'
const exportDoc: PathStatus = state.canExport ? 'active' : 'pending'
```

`canExport`（`workspace.ts:1003`）= `writtenChapters.some(ch => Boolean(ch.content))`，即"任意一章有内容"，**与实际导出无关**。
→ 用户导完 PDF/Word 后，**最后两站永久停在"进行中"**。

**7b. 8 个站点标签是原始代码标识符。** `i18n.tsx:190-197`（pm2 写 181-188，偏移 ±9，内容正确）：

```
'path.upload_data': 'upload_data'      'path.spec_curve': 'spec_curve'
'path.generate_chapter': 'generate_chapter / approve_chapter'
'path.export_docx': 'export_docx'
```

而**同一词典里 8 个清洗步骤是正常翻译的**（`i18n.tsx:199+`：`'profiling · 契约'`、`'merge · 合并'`、`'audit · 留痕'`）。
→ **翻译基础设施没问题，是路径站点从未被给过产品名。**
且 `getInitialLang()` 兜底返回 `'zh'`（`i18n.tsx:1077`），所以默认中文用户看到的就是这串标识符。

**7c（我在验证 7b 时发现，比 7a/7b 更重要）：两套 8 站并存，用户看到的是没名字的那套。**

| | 站点名 | 渲染状态 |
|---|---|---|
| `PaperPath`（`paperPath.ts:3-12` `PAPER_NODES`） | `upload_data` / `clean_data` / `set_direction` / `spec_curve` / `generate_outline` / `generate_chapter` / `translate_code` / `export_docx` | **`App.tsx:587` 无条件挂载**（右栏 `agent={...}`，每屏可见） |
| `JourneyTimeline`（后端 `_JOURNEY_STAGES`，`progress.py:39-48`） | 选题 / 文献 / 数据清洗 / 识别策略 / 估计建模 / 稳健性审计 / 写作评审 / 降AIGC导出 | **全仓仅被自己的测试 import，App 里零挂载** |

两者站点集合**并不一致**（journey 有文献/识别策略/估计建模/稳健性审计，PAPER_NODES 没有；PAPER_NODES 有 spec_curve，journey 没有）。

后果：
- **有中文产品名的那套旅程（JourneyTimeline）只活在测试里；用户看到的（PaperPath）标签是代码标识符。**
- 我证据 6 说"第 8 站降AIGC 是空壳"——更准确的说法是：**"降AIGC"这个名字只存在于未挂载组件的数据源里**，用户根本看不到它，也看不到任何第 8 站。
- Sun / 我 / pm2 三方争论的"8 站线性流水线"，**用户实际看见的那 8 站是后端节点名直出**。

**根因（pm2 的提法，我认同并采纳）**：不只是"进度由代理信号推断"，而是**用户可见层是实现的直接投影，中间没有产品层**。8 站从来不是被设计出来的用户旅程，它是后端节点列表渲染成了 UI——连名字都没改。

这与 pm2 第三节的定位问题是同一个根：**从定位到用户旅程、从节点到标签，两次翻译都没有人做。**
对应到我的证据 4：state 里没有"这个产物是否当前/是否真跑过"的一等表示；对应的前端是：UI 层也没有"这个东西对用户叫什么"的一等表示。

### 证据 8（pm2 报了四套，我验证后是五套，且**两套活的在同一屏上互相打架**）

pm2 复出两套（#3 中文 8 步文案、#4 四步文案），我逐条验证成立，并在验证时发现**第 5 套，它是活的，且和第 4 套内容冲突**：

| # | 载体 | 内容 | 状态 |
|---|---|---|---|
| 1 | `_JOURNEY_STAGES`（`progress.py:39-48`） | 8 站，末站"降AIGC导出" | API；`JourneyTimeline` **未挂载** |
| 2 | `PAPER_NODES`（`paperPath.ts:3-12`） | 8 个英文标识符 | **挂载** `App.tsx:587`（右栏） |
| 3 | `journey.step1–8`（`i18n.tsx:530-546`） | 8 步，中文优质（如"主表出现之前，结果章不能写"）；step8 = `⑧ 导出` | **悬空**（同 #1，组件未挂载） |
| 4 | `bench.journey`（`i18n.tsx:353`） | **4 步** `上传 → 方向 → 估计 → 按章写` | **挂载** `App.tsx:406-411`，`data-testid="product-journey"` |
| 5 | `StepTimeline` + `deskSteps.*`（`StepTimeline.tsx`；`i18n.tsx:117-124`） | **4 步** `方向凝练 → 清洗八步 → 估计门 · 估计 Agent → 各章写作` | **挂载** `App.tsx:450-462` |
| — | `StepIndicator.tsx`（注释：Upload Data → Explore Data → Generate Paper） | 3 步，英文 | **死代码**，无任何 import |

**关键事实：#4 与 #5 都在 `App.tsx` 同一段 JSX 里、前后相邻（406 / 450）、无条件渲染——用户在同一屏同时看到两条不一样的 4 步旅程。**

两条不只顺序不同，**站点集合互斥**：
- #4 有 `上传`，**无清洗**
- #5 有 `清洗八步`（8 步数据清洗，产品的主打功能之一），**无上传**

即：工作台头部告诉用户流程是"上传→方向→估计→按章写"，下方步骤卡同时告诉用户是"方向凝练→清洗八步→估计门→各章写作"。**8 步数据清洗在其中一条旅程里根本不存在。**

**补充**：#4 的字符串在 `i18n.tsx:84` `guide.badge` 里被原文复制了一遍（zh/en 各一处，即 84/353 与 622/880），所以"4 步"实际占 4 个 key。`guide.badge` 渲染于 `GuidePage.tsx:144`（引导页，与工作台不同屏）。

#### 三套活旅程的出生日期（git 溯源，推翻 pm2 的定位映射）

pm2 提出"三套活旅程恰好对应三次定位决策（08-16 / 08-18 / 08-27-29）"。**结构对，日期错。** `git log -L` 溯源：

| 活旅程 | 引入日期 | commit | commit message |
|---|---|---|---|
| #2 `PAPER_NODES`（右栏） | **2026-08-27** | `e4484fb` | feat(frontend): live paper-path desk with locked CONTEXT nodes |
| #4 `bench.journey`（中栏） | **2026-08-27** | `0f1b382` | feat(frontend): Copaper How-It-Works journey on first screen and desk |
| #5 `deskSteps`（中栏） | **2026-08-29** | `9b00ca2` | feat: 对话优先翻转 + 多格式上传 + Phase A 装手（沙箱/估计Agent/评测基线） |

两点更正：

1. **`bench.journey` 不是 08-18 课设定位的产物，是 08-27 的落地页营销文案**（commit 标题直接写 "Copaper How-It-Works journey on first screen and desk"）。它的"隐藏清洗"不是课设取舍，是**对外营销话术**。
2. **三套活旅程全部生于 08-27 → 08-29 的 72 小时内，其中两套是同一天、由两个不同 commit 分别引入的。** 不是跨越 13 天的三次定位迭代各留一块化石。

**结论要重写**：这不是"定位漂移在 UI 上留痕"，是**最近三天的一次并发施工，三套框架同时被建出来，没有任何一次提交负责让它们对齐**。08-16 的 spine 并不在三套活着的里面——`PAPER_NODES` 的**内容**取自 08-16 的后端节点名，但**组件本身是 08-27 新建的**。

补充佐证：pm2 引作 08-27 北极星的 devlog（"替你干完"、对标 Apodex）与 #2、#4 的生日是**同一天**——同一个北极星在一天之内产出了两套互相矛盾的 UI。

**计数最终版**：6 个表述 / 5 种内容 / **3 个工作台同屏** / 1 个引导页（与 #4 同内容）/ 1 个死代码（`StepIndicator`）。

#### 完整时间线（git 溯源，pm2 提出"有意删除"，我逐条验证）

pm2 用 `git log -S` 挖出 08-18 那次卸载是**有意的**。我独立复核，全部成立：

```
08-16  ADR-0010 研究者级定位（后端 spine）
08-17  bc8c612  JourneyTimeline 挂载
08-18  20a3c57  课设定位 → 八站 rail 被有意卸载（devlog 明写）
08-27  e4484fb  PAPER_NODES（右栏，英文节点名）
08-27  0f1b382  bench.journey（中栏，隐藏清洗的 4 步）
08-29  9b00ca2  deskSteps / StepTimeline（中栏，含清洗八步的 4 步）
```

验证细节：
- `git log -S "JourneyTimeline" -- frontend/src/App.tsx` → 仅两条：`bc8c612`(08-17) 与 `20a3c57`(08-18)
- `git show 20a3c57 -- frontend/src/App.tsx` 删的是**两处**：`-import JourneyTimeline`(23 行) 与 `-      <JourneyTimeline`(660 行)。**是干净卸载，不是重构挪位。**
- `20a3c57` = "feat: 课设第一遍可走完，开发停在这一版"
- `devlog-2026-08-18.md:27` 原文：**"右栏不再摊八站旅程，写出一章后这里是评审。"**
- `git show 20a3c57:frontend/src/lib/i18n.tsx | grep -c "bench.journey"` → **0**（08-18 时该键不存在）

**我在验证时发现的一刀**：08-18 清空的是**右栏**；08-27 的 `PAPER_NODES` 装回的也是**右栏**（`App.tsx:585` `agent={` → `ThreeColumn.tsx:25` `right={agent}`）。

→ 不是"重建了被删的东西"，是**把 08-18 特意清空的那个位置，用 08-18 明确否决过的东西（八站旅程）重新填满了**，只是换成了 8 个英文节点名。

**定性（采纳 pm2 的措辞，我加最后一刀）**：
不是"13 天漂移留下三层化石"，是 **"一次有意的删除，九天后一次无意的重建"**。
漂移至少每次都是当下的决定；**失忆是 08-18 的教训已执行过一次，然后被彻底遗忘**——08-27/29 建三套新 UI 时，没有任何一次提交负责确认"这个我们删过"。

#### 取证方法陷阱（三轮错误的共同根因，记录在案）

| 轮次 | 谁 | 错因 | 教训 |
|---|---|---|---|
| 1 | pm | `head_limit=20` 的全仓 grep 被截断 → 误判 spec_curve 是死代码 | 不能从"没看到"推"不存在" |
| 2 | pm2 | `sed -n '10,549p' \| grep -n` → 行号相对切片，整体偏移 9 | 管道取号要核对基准 |
| 3 | 双方 | **`git log -L 353,353` 同时返回 `0f1b382`(08-27) 与 `20a3c57`(08-18)**——`-L` 跟踪**行位置**而非键身份，08-18 时占那个位置的是另一个键 | **位置 ≠ 身份** |

第 3 条由 pm2 发现。我这次因用了 `-1`（只取最近一条）侥幸得到正确答案，但方法是脆的——不记下来下次会踩。
**正确做法：按键验证**（`git show <rev>:<file> | grep <key>`），不按行号。

**pm2 的方向 B 成本估算需要再修正一次**（不是"接上已有文案"，是"先裁决哪套算数"）：
- ✅ 中文命名确实已经存在，且 #3/#5 的质量都不错——**命名不用新写**，这点 pm2 对；
- ❌ 但存在**两套已经上线、互相冲突的中文 4 步**，直接"复用"任一套都会静默抹掉另一套的语义：
  - 采纳 #4 → **8 步清洗从用户心智里消失**（它是 #5 的第二步）；
  - 采纳 #5 → 丢失"上传"起点，且 #5 用的是 `deskSteps.*`（Phase B Agent 循环语境，如"估计门 · 估计 Agent"），与 #4/#3 的 `bench`/`journey` 语境不同源。
- 所以 B 的前置动作是**一次裁决 + 一次删除**，不是一次接线。工作量仍是 3–5 天量级，但性质从"改组件"变成"定权威 + 拆掉其余四套"。

**判据收紧（pm2 提法 + 我按证据 8 再收一档）**：
> 当产品层存在时，同一个概念只会有一个权威表述。现在"研究旅程"这个概念有 **5 个表述**，其中 **2 个同时在线且互斥**，没有一个被标为权威。

---

## 二、解法方向（代价摆清，不排序）

### 方向 A：把识别站做成真正的诊断工作台

- **做什么**：DiD 补事件研究/前趋势检验；IV 补过度识别检验；`identification_verify` 从"一次性打分"改成"可重复运行 + 保留历次 diagnostic 快照"。
- **架构冲击**：中。节点是纯函数，加检验不改 state 契约；但**星级语义必须重定义**（补检验后"平行趋势 fail"算 1 星还是 0 星，要重新划线）。
- **⚠️ 隐含坑（pm2 补，我已验证）**：**补了检验也不会自动拦人。** 必须同时改两处，否则新增的失败照样放行：
  - `identification_verify.py:501-507`：`passes and fails` → **1 星**（不拦）
  - `graph.py:56` `route_after_identification`：只认 `star_rating == 0`

  即：星级语义 + 路由阈值**必须同批改**，只补检验是无效投入。
- **开发量**：2–4 周。每个检验要 StatsPAI 支持 + 降级路径 + 单测；StatsPAI 缺函数得 upstream 加。路由与星级重划约 +3 天。
- **UX 改变**：识别站从"看一个星级 + 一段报告"变成"看检验清单 + 逐条结论 + 换设定重跑"。主路径变长。

### 方向 B：给 state 加失效传播（堵最危险的洞）

- **做什么**：`research_direction` / 识别方法变更时，级联清空或标记 `stale`：`estimate`、`robustness_results`、`body_chapters`。stale 的产物禁止写入新章、禁止导出。
- **架构冲击**：小。加一个 `invalidate_downstream(state, from_node)`，在 `run_prewrite` / `run_identification_verify` 入口调用；state 加 `stale_keys`。
- **开发量**：3–5 天 + 改一批直接灌 state 的测试。
- **UX 改变**：换方法会提示"以下章节将失效需重写"。**用户体验是倒退的**——但现在的体验（拿 DiD 主表写 IV 结论）是错的。
- **代价要摆清**：这个改动不让产品更聪明，只让它更诚实。对面试官是加分，对使用者是重写成本。

### 方向 C：修设定表的"谎报"，不是"接线"（**工作量已更正**）

> pm2 更正：接线已完成（`robustness_check.py:671`）。原估 1–2 周作废，真实工作量约 **半天–1 天**。

- **做什么**：
  1. 跳过时显式留痕——`method in {"iv","rd","scm"} or cs_main` 分支写一条 `diagnostics`（`status="skipped"`, `reason="method_not_supported"`），而不是留 `None`。
  2. 节点状态改为由产物决定：`spec_curve` 存在才 `completed`，否则 `skipped` 并有文案。
- **架构冲击**：极小。改一处 if + 一处前端推导。
- **开发量**：UI 半天 + 后端跳过提示半天。
- **UX 改变**：用户第一次会看到"你的方法不支持设定表"——这是把已有的沉默变成明示。
- **边界**：它解决**规格震荡**，不解决**识别策略震荡**。不能替代 A。**优先级应下调**——它现在是"低投入的诚实性修补"，不是"探索能力建设"。

---

## 三、比线性流程更致命的问题（Sun 没提到）

**「验真报告的保质期」。**

产品核心卖点是"机器先交出可引用的数字，再写正文"。但没有任何机制保证这些数字与方法在用户中途改动后仍然成立。

完整失效链：

```
改方法 → 旧 estimate 仍 produced_by="estimate"
       → 结果章照样开写 → 导出照样出 PDF → 评审照样给分
```

整个防编造体系（readiness / grounding / structure_checks / claim_mode）**都建立在"state 里的产物是当前的"这个假设上，而这个假设没有一行代码保证**。

这不是流程形状问题，是**信任模型问题**。
**不修 B，A 和 C 的投入会让更多过期产物更快地流进论文。**

---

## 四、面试作品集：怎么讲 + 最容易被问倒的点

### 主线（不要讲"AI 写论文工具"）

红海，且立即被质疑学术不端。改讲：

> **「我把『不能编造』做成了一条可执行的工程约束。」**

- 问题：LLM 写实证论文最致命的不是文笔，是编系数、编文献、把 OLS 写成因果。
- 解法（都是可指的代码）：
  - 数字先于正文：`estimate` 产出 `treatment_row` 才允许开写
  - 按章就绪检查：results 章缺主表/稳健性 → 409，模型不许补
  - 接地检查：`treatment_row` 必须是正文子串，另造系数表判 `invented_number`
  - 主张只降不升：`claim_mode`，用户写 association 就永远是 association
  - 假审必须可见：`review_source == "mock_fallback"`
- **产品判断点**：你定义了「什么情况下机器必须拒绝干活」，而不只是让机器干得更快。
- 数字：8 站 / 5 介入点 / 6 章 / 4 套 LaTeX 模板 / 38 种计量方法 / 4 种代码导出。

### 最容易被问倒的 4 问（按危险度）

| # | 问题 | 为什么答不好 | 建议 |
|---|---|---|---|
| 1 | **「你的识别验真到底验了什么？」** | 一追问就露：DiD 无平行趋势检验，IV 无过度识别检验；而方法章被**强制要求写"平行趋势"**。追问"那句'平行趋势成立'是谁证明的"——答不上来 | **最危险的一问**，必须先自查 |
| 2 | **「用户中途改方法，之前写的章节怎么办？」** | 没有失效传播。答"会重新生成"是错的，代码里没有 | 如实说已知缺口 + 讲 B 方案 |
| 3 | **「有真实用户跑通过吗？论文什么水平？」** | 唯一证据是 2026-08-28 你自己一次走查（UX-BACKLOG.md），且是**无 LLM key 的降级路径**。无外部研究者、无投稿、无第三方评价 | 这问答不好，前面所有工程细节都打折 |
| 4 | **「这是不是学术不端工具？」** | 落地页第 8 站叫"降AIGC"且未实现，正好坐实疑虑 | 定位改"研究工作台 / 可复现分析"，把"降AIGC"从叙事里拿掉 |

次要点：简历写"8 站"会被追问第 8 站（空壳）；测试质量待 QA 结果。
