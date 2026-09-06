# 验收契约：Generic Research Spine 加固（Expectation → Run → Surprise → Explanation → Recovery）

Status: open

基线：`main @ ac62d4a0457c80e480aa335a362040acc650b3af`，分支 `review/generic-research-spine-hardening`。
事实来源：`card-canonical-research-experience-validator.md` 追加的 J–Q first-user audit（2026-09-06，verdict B）。
本契约实现 M1–M4；Infra follow-up（BrokenPipe）只判定与记录，不在本分支修。

## Change

首次使用者改写自然语言预期、点 Run specifications、看 Cursor 解释、遭遇失败时，研究循环每一步都有真实反馈与出口：Surprise 由结构化判定（不再是关键词白名单）、运行有 busy→完成→自动进 Evidence 的状态转换、Show me 编舞真实贴合目标且 ≤6 秒、失败只有单一可信真相和恢复出口。

## Not this

- 不新增计量方法，不实现 DiD/RD；只保证数据模型与判定层对它们可扩展（命名通用，如 `ExpectationCriterion`，不是 `CardExpectation`）。
- 不改 semantic-target 架构、不引入坐标驱动、不扩新 Cursor 功能（只修运行时缺陷）。
- 不通过给 `_mentions_*` 添加同义词来"修"Surprise。
- 不吞掉 BrokenPipe 进研究节点。
- 不伪造 12-node 百分比；后端只有 run-level 时允许 indeterminate，但完成转场必须真实。
- 不 merge PR、不直推 main。

## Evaluator

主 agent 派 **implementer** 循环实现（代码+单测+集成测试），浏览器实证（M3 时间线、M4 注入、最终 clean journey）由主 agent 在真实浏览器执行并归档证据；收尾由 **validator** 独立复核本契约逐条出 ACCEPT/REJECT。

## Checks

### M1 — Expectation Contract（结构化判定）

- [ ] C1 Card 种子建立结构化判据 — 程序: `cd econpaper && python -m pytest backend/tests -k "seed" -x -q`（含新增测试）— 预期: 新建 Card lab 的 `expectation.criteria` 恰含一条 `source="seed"` 判据：`kind="ordering"`、`operator="lt"`、`left` 指向 IV 系数、`right` 指向 OLS 系数、label 含 "IV estimate < OLS estimate"。
- [ ] C2 PUT 语义：显式修改、绝不暗中重猜 — 程序: `python -m pytest backend/tests -k "expectation" -x -q`（含新增测试）— 预期: ① PUT 带 `criteria` 字段时按提交值原样持久化；② PUT 不带 `criteria` 时现有 criteria 保持不变（text 改成任何自由文本都不触发从文本重解析）；③ criteria 与 version/history 一起进 `ExpectationResponse`。
- [ ] C3 evaluate_surprise 只消费 criteria — 程序: `python -m pytest backend/tests -k "surprise" -x -q`（含新增/改写测试）— 预期: ① 判据 IV<OLS + 真实量级 runs（OLS 0.0747 / IV 0.1315）→ `status="Unexpected"`、observed 表达 IV > OLS、kind 为 ordering mismatch 族；② 判据满足时 `Expected`；③ sign（positive/negative）与 distance（approx + tolerance）算子有确定性测试；④ 无判据（纯文本）→ `Expected` + 不抛错。
- [ ] C4 keyword contract 删除 — 程序: `grep -rn "_mentions_iv\|_mentions_similar\|_mentions_positive" backend/ frontend/src/ ; echo EXIT:$?` — 预期: 无匹配（EXIT:1）。`evaluate_surprise` 不再有任何自由文本短语分支。
- [ ] C5 命名通用 + API drift 门 — 程序: `grep -rn "CardExpectation" backend/ frontend/src/ | wc -l` 为 0；类型名 `ExpectationCriterion` / `EvidenceMetricRef`（或等价通用名）；`make check-api-drift` 绿 — 预期: openapi.json、docs/api/openapi.json、frontend/types/api.ts 同步包含 criteria 模型。
- [ ] C6 UI 显式判定块 — 程序: `cd frontend && npx vitest run src/components/__tests__ -t expectation -q`（含新增断言）+ 浏览器抽查 — 预期: Expectation 编辑器在 textarea 下方渲染 `Surprise condition · 意外判定` 块，显示当前判据（如 "IV estimate < OLS estimate"）；改 textarea 文本不改变该块；提供显式控件修改判据（改后保存即生效），无任何"从文本重猜"路径。
- [ ] C7 真实数据验收 — 程序: 浏览器走 Card 真实会话：把预期原文改成 `我觉得 IV 应该会更小一些，但并不确定。`，判据块仍显式为 IV<OLS；Freeze→Run→查看后端 `GET /research` — 预期: `surprise.status="Unexpected"`、`observed` 表达 IV > OLS（真实系数 0.0747/0.1315 量级）。证据归档。

### M2 — Run specifications 完整状态转换

- [ ] C8 点击即有反馈、不可重复提交 — 程序: vitest（新增）+ 浏览器 — 预期: 点击后按钮立即进入运行态（label 变为 "Running specifications…" 或 "Running k/12"）且 disabled；运行中再次点击不发出第二个 POST（前端禁用即可，409 SessionBusy 分支有处理不崩）。
- [ ] C9 Agent Rail 显示真实运行任务 — 程序: vitest + 浏览器 — 预期: 运行期间右栏"当前任务"显示 spec_run 进行中（进度来自真实 run 事件：`Running k/12`（逐 spec 事件可得）或 indeterminate 文案），不得显示"空闲"、不得虚构数字。
- [ ] C10 完成转场 — 程序: vitest + 浏览器 — 预期: run 成功终止后 ① 运行态解除并出现明确完成反馈；② workbenchTab 自动切到 Evidence Lab；③ 若 `surprise.status="Unexpected"`，Evidence 侧 rail 出现 Show me。
- [ ] C11 失败不假成功 — 程序: vitest（mock run FAILED）+ 浏览器注入 — 预期: spec_run FAILED 时 Design 页显示明确失败信息（含稳定错误类别），提供 Retry（重新发起 run）入口；无 unhandledrejection；按钮恢复可点。
- [ ] C12 无陈旧运行态 — 程序: vitest — 预期: run 终态后 `activeRun` 清空，Agent Rail 不再显示"后台运行监控中/run 仍在进行"。

### M3 — Agent Cursor Runtime Conformance（semantic-target 架构不动）

- [ ] C13 菱形跟随目标 — 程序: 真实浏览器 Show me 全程采样（每 point/compare 步截样），归档 timeline JSON — 预期: 每步采样时 cursor 菱形中心落在目标元素 rect 外扩 ≤24px 内；scroll/resize 后重采样仍成立。机器可测：菱形中心坐标 vs `registry.rect(id)`。
- [ ] C14 总时长 ≤6 秒 — 程序: 同上 timeline — 预期: Show me（无用户确认等待、非 reduced-motion）从 play 到 done 的墙钟时间 ≤6000ms；timeline 给出逐步时间戳。
- [ ] C15 用户输入即时 yield + 低摩擦继续 — 程序: 浏览器注入真实 pointerdown/keydown — 预期: 运行中输入立即暂停（状态可见）；提供继续控件（Resume）从当前步续播而非重播整个脚本；空闲 ≥3s 自动恢复亦可接受（二选一，均需证据）；Cancel/Replay 仍在。
- [ ] C16 Cancel 清理 — 程序: 浏览器 — 预期: Cancel 后 highlight 方框从 DOM 移除、cursor 不可见（opacity 0 或卸载），无可见残留。
- [ ] C17 reduced-motion 可用 — 程序: 浏览器 emulate reduced motion — 预期: 脚本完成、位置瞬移贴合目标、无时长违约。
- [ ] C18 架构不退化 — 程序: `grep -rn "gsap\|clientX\|pageX" frontend/src/lib/agentCursor/ frontend/src/components/AgentCursorLayer.tsx | wc -l` 为 0（现有语义拒绝测试不动）+ `frontend && npx vitest run src/lib/agentCursor src/components/__tests__/AgentCursorLayer.test.tsx -q`（如存在）— 预期: 全过；scripts.ts 仍全语义 id。
- [ ] C19 challenge experience 脚本仍工作 — 程序: vitest + 浏览器 smoke — 预期: point(experience)→preview→awaitConfirm→(确认)→runPreview→compare 链路可走完，语义不变。

### M4 — Failure / Recovery UX

- [ ] C20 (A) Expectation 保存失败 — 程序: 浏览器注入 PUT /research/expectation → 503 — 预期: ① 编辑器内显示保存失败（不用全局一闪而过 toast 独扛）；② textarea 保留用户未保存文本；③ REST 复核后端 version/text 未变；④ console 无 unhandledrejection；⑤ 解除注入后 Retry 保存成功。
- [ ] C21 (B) Card boot 终态失败单一真相 — 程序: 浏览器注入 boot run FAILED — 预期: 同屏只有**一个** terminal failure surface（含稳定失败原因），提供 Retry Card（重开教学案例）与 Back to desk / New study；同屏不再出现"数据处理失败"+"run 仍在进行"+"下一步 Freeze"两类以上矛盾信号；rail 当前任务不宣称终态 run 仍在进行。
- [ ] C22 (C) 会话内导航 — 程序: 浏览器 — 预期: 已有研究会话视图内存在明确 New study / 回工作台入口，单击回到空桌（Try Card 可见）；不清 localStorage 即可开始新研究（Try Card boot 新会话）。
- [ ] C23 (D) History 行 / 矩阵行 — 程序: 真实浏览器以原生 el.click() 独立复现 `evidence-matrix-*` 行点击与 `evidence-history-*` — 预期: 二选一并记录：真实可复现 → 修复（点 OLS 行 + IV 行能重建 0.0747→0.1315 compare；History 能切换 run 且视觉有反馈）；无法复现 → 在 audit supplement 记录复现程序与结论，不为过审乱改代码。

### Infra follow-up（独立，不阻塞本 PR）

- [ ] C24 BrokenPipe 判定与记录 — 程序: 用 repo-owned launcher（make dev-runner / uvicorn 启动 runner）尝试稳定复现 stdout 断管 → run 误标 FAILED；结果二选一归档：① 可稳定复现 → 开独立 GitHub issue（附复现程序与 runner logging lifecycle 修复方向，URL 记录于此）；② 不可稳定复现 → 在 `docs/dev/`（或等价处）记录本地运行前置条件与安全启动方式 + audit supplement。— 预期: 研究节点代码无任何 BrokenPipe 吞噬（`grep -rn "BrokenPipe" backend/ agent/ --include="*.py" | grep -v tests | grep -v raise` 为空或仅出现在与本研究循环无关的既有位置）。

### 收尾

- [ ] C25 clean first-user journey 全程 — 程序: 真实浏览器，从清空状态走 Empty desk→Try Card→改自然语言预期→验证显式 Surprise Criterion→Freeze→Run（有反馈）→自动进 Evidence→Unexpected→Show me（真实 ≤6s 编舞）→Compare→Challenge→stale Claim→Review new evidence→Approve→显式 Promote→Results→Linked Evidence — 预期: 每步有 primary 且不假成功；全程 console 无 uncaught/unhandledrejection；证据归档 `docs/acceptance/assets/generic-spine-hardening-*/`。
- [ ] C26 三个失败注入 — 程序: 浏览器注入 Expectation 503、spec_run FAILED、Card boot FAILED — 预期: 各自不假成功、无矛盾状态、有恢复出口（对应 C20/C11/C21）。
- [ ] C27 原语义不退化 — 程序: `make test` 全绿（含 check-api-drift）；journey 中核对 evidence_revision 递增、Claim stale→redraft→approve、显式 Promote 改 canonical、Results grounded 门（批准≠grounded）、provenance 存在 — 预期: 全部保持。
- [ ] C28 质量门 — 程序: `make test`；`cd frontend && npx tsc --noEmit && npm run lint && npm run build` — 预期: 全部 0 退出；无新增 skip。

## Evidence

（浏览器实证由主 agent 于 2026-09-07 完成并归档；逐条摘要如下，完整时间线/截图见 `docs/acceptance/assets/generic-spine-hardening-2026-09-07/`，复核记录见 `card-canonical-research-experience-validator.md` 末尾 Audit Supplement。）

- C1/C2/C3/C5/C9(后端)/C18/C24(静态)：implementer 循环内 `make test` 全绿（agent 819 passed/1 skip，backend 433 passed/8 既有环境 skip，frontend 384 passed），check-api-drift 三段 ✅，`_mentions_*` grep 空，CardExpectation 零命中。
- C6/C7：真实会话改写 `我觉得 IV 应该会更小一些，但并不确定。` → 判据块保持 "IV estimate < OLS estimate"（ja01-expectation-zh-criterion.png）；真实 specs → `surprise.status=Unexpected`、`observed="IV estimate 0.1315 > OLS estimate 0.0747"`（REST 双向核对）。
- C8/C9/C10：runLog 采样 `D Running 0/12 → 1/12 → 8/12`（按钮 disabled + rail "正在运行规格 k/12"）；完成后自动转 Evidence、Show me 出现（ja02-evidence-unexpected-showme.png）。
- C11：注入 run FAILED → Design 页 `spec_run_failed` 失败卡 + Retry（m2-spec-run-failure-card.png，6s 出现）；解除注入 Retry → 真实跑完自动转 Evidence；无 unhandledrejection。
- C12：终态后 rail 回"空闲"、无"后台运行监控中"。
- C13/C14：Show me 时间线（120ms 采样）：keyFrames OLS(122ms)→IV(962ms)→compare+intent(1922ms)→estimator(2761ms)→"This is the main change."(4803ms)，done ≈5.8s ≤6s；每步 cursor 中心（+6,+8 偏移）与高亮框中心差 ≈1px ≤24px；scroll 后重采样仍贴合。
- C15：真实 pointerdown 注入 → "已暂停" + Resume 控件；1.5s 后仍暂停（不自动丢失）；Resume 后续播至末步（"This is the main change."），非重播。
- C16：Cancel 后 `agent-cursor-highlight-*` 0 个、cursor opacity 0。
- C17：matchMedia patch 模拟 reduced motion → 全脚本 ≈0.4s 完成、data-reduced-motion=true、位置贴合。
- C19：challenge experience 脚本（Show preview→awaitConfirm→Run Preview→compare）vitest 全过；旅程内 Accept challenge 链路真实走通。
- C20：503 注入：编辑器错误卡（m4a-expectation-save-failure.png）、textarea 保留、后端 version/text 不变（REST 复核）、无 unhandledrejection、Retry 成功。
- C21：boot 注入 FAILED（4s 出现）：单一 "Boot failed · 启动失败" 卡 + Retry Card + Back to desk（m4b-boot-failure-single-surface.png）；programmatically 验证同屏无 "仍在进行"/"确认 Admissible Space"/"重新选择文件"。
- C22：`new-study-entry` 单击回空桌、localStorage 会话清除、Try Card 可见（m4c-new-study-empty-desk.png）；New study→Try Card 落 Question 页。
- C23：矩阵行与 History 均可交互（见 supplement 判定表）——死交互不可复现，机理记录于 Audit Supplement，未改交互语义。
- C24：repo-owned launcher 确定性复现 BrokenPipe→run 误标 FAILED；独立 issue https://github.com/yishu-ziyu/empirical-paper-workbench/issues/30 ；docs/local-runner.md 记录前置条件；研究节点无 BrokenPipe 吞噬。
- C25/C26/C27：clean first-user journey 全程走通（ supplement 方法附注），全程 console 零错误；evidence_revision 1→2、claim v1→v2、stale→redraft→approve、explicit Promote（canonical=iv_region_dummies）、grounded 门（Results 基于证据）、provenance 均保持。
- C28：`make test`、`tsc --noEmit`、`npm run lint`、`npm run build` 全部 0 退出（最终提交后复跑记录见 PR 描述）。

## Named relaxations

- M2 进度：若逐 spec 进度事件经 SSE 到达前端不可靠，允许 indeterminate "Running specifications…"（目标原文明示）；完成转场与失败真相不得放宽。
- C23：目标原文明示"可复现则修 / 确认 automation artifact 则记录"二选一，由复现证据裁决。
- C14 的 6s 在本地 dev（ECONPAPER_LLM=mock、本机 Chrome/IAB）实测为准；不在 CI 环境复测时长。
- 种子判据 label 允许中英双语文案变体，断言针对算子语义（iv lt ols）而非精确字符串字面。
