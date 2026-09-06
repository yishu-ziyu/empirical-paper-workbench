# 验收契约：Card UX Coherence（证据优先、上下文明确、直接操作优先）

Status: closed

Baseline（2026-09-06，分支 `review/card-ux-coherence`，从已合并 PR #28 的 `main` 检出）：
- frontend：53 test files / 348 tests passed；`npm run build` 通过
- backend：389 passed / 8 skipped
- agent：805 passed / 1 skipped
- `make check-api-drift` 绿
- 端口 5173 / 8000 活跃运行中

不改变范围（硬约束）：
- 不改 Card 统计逻辑与真实统计值（0.0747、0.1315、F=14.14、N=3010 保持真实计算与后端持有）
- 不改 provenance / Claim revision / canonical semantics
- 不引入新模型或新 UI 框架
- 不改变 semantic-target architecture

## Change

将 Card canonical journey 从“功能完整”收敛为一条 evidence-first、context-aware、direct-manipulation-first 的高质量体验：
1. **Evidence Lab 视觉重排**：Surprise → Results Space → Compare / Why did it move? → Next-best Challenge → Claim Ledger；未 review 前只显轻量提示“Draft claim ready · 已可以整理结论”，完成 Compare / Challenge 或点击 Review claim 后 Claim Ledger 展开为主区域。
2. **Agent Rail 上下文感知**：Question 态只显示 Question/Expectation/Design 相关动作，不泄漏 Evidence 的“IV > OLS / Show me”；Evidence 态才显示 Unexpected result / Show me / Challenge / Cursor controls；Paper 态只保留 Linked Evidence 与当前写作审批；任意时刻最多 1 个 primary decision card。
3. **Agent Cursor 编排升级**：固定 10 步 Card script（OLS定位高亮 → IV定位高亮 → 自动对比选择 → Compare 面板即时 0.0747→0.1315 Δ/% → unchanged 淡化 → estimator/identification 高亮 → intent 识别策略变化 → 约 3-4s 收束“This is the main change. / 主要变化来自这里”）；Cursor label 始终贴紧 target，不被 sticky header 裁切，scroll/resize 重新定位，用户 pointer/keyboard 操作 yield。
4. **Specification runs UI 去重**：同一 spec_id 多 runs 默认只展示当前/最新有效 run；提供轻量历史入口（如 Preview · 2 runs / History 2）；表格与散点图无无标识同名行；Compare 可切换 run history。
5. **中文 Canonical 体验**：中文模式下 11 个核心词带中文解释（Research Question（研究问题）、Expectation（预期）、Admissible Space（合理规格空间）、Evidence Lab（证据实验室）、Surprise（意外）、Compare（比较）、Next-best Challenge（下一步最有价值的检验）、Claim Ledger（结论账本）、Supported（当前证据支持）、Conditionally supported（有条件支持）、Unsupported（当前证据不支持））。
6. **Challenge 文案中性修正**：不把 effective F=14.14 称为“may be a weak instrument”，改为中性、可验证的“Instrument strength deserves inspection / 工具变量强度值得检查 · Effective F = 14.14 · Strength diagnostics alone do not establish instrument validity / 强度诊断本身不能证明工具变量有效”。
7. **Paper 聚焦正文**：Paper Writing 第一视觉焦点是当前章节正文与 evidence anchor；现有方向凝练/清洗八步/估计门/WriteLoop 等降级为“Research trace / 研究记录”可折叠区域；Linked Evidence 在右栏；打开 Results 第一眼看到正文、关键数字、“基于证据”与回到 Evidence 入口。
8. **5 张 1440px 截图与 Walkthrough 留档**：Question、Evidence before Claim review、Agent Cursor mid-demonstration、Claim Ledger、Paper Results。

## Not this

- 不算：为了过审修改统计数值或 backend truth contract。
- 不算：全局 i18n 翻修或引入 heavy i18n 库；只针对 Card 核心体验。
- 不算：删掉过程台账（必须收进“Research trace / 研究记录”）。
- 不算：Agent Cursor 回退到坐标、CSS 自由 selector 或破坏 semantic-target 架构。
- 不算：同时向用户推 4 个下一步。
- 不算：向 PR #28 增加代码（必须在 `review/card-ux-coherence` 分支独立开 PR）。

## Evaluator

主 agent 负责编排和端到端浏览器 1440px 视觉实测与截图录档。
实现主体由 implementer 子代理在自身上下文中迭代实现并跑通测试门禁。
收尾由 validator 子代理独立复核验收契约。

## Checks

- [x] C1 Evidence Lab 顺序与 Claim 折叠 — 程序: `cd frontend && npx vitest run src/components/__tests__/EvidenceLab.test.tsx` + 浏览器 DOM — 预期: Results Space / Compare 排在 Claim 前；未交互前 Claim 呈现为“Draft claim ready · 已可以整理结论”；交互（Compare/Challenge）或主动点击“Review claim”后展示 Claim Ledger 主账本。
- [x] C2 Agent Rail context-aware — 程序: `cd frontend && npx vitest run src/components/__tests__/AgentRail.test.tsx src/__tests__/App.test.tsx` + 浏览器 DOM — 预期: Question 视图不显示“Show me”或“IV > OLS”卡片；Paper 视图只显示 Linked Evidence 与写作审批；Evidence 视图才展示 Show me / Surprise；任何视图最多 1 个 primary decision card。
- [x] C3 Agent Cursor 10 步 Choreography 与粘性定位 — 程序: `cd frontend && npx vitest run src/lib/__tests__/agentCursor.test.ts src/components/__tests__/AgentCursorLayer.test.tsx` + 浏览器 DOM — 预期: Show me 脚本完整覆盖 OLS → IV → Compare (0.0747→0.1315 Δ/%) → fadeUnchanged → estimator highlight → “Identification strategy changed / 识别策略发生变化” → “This is the main change. / 主要变化来自这里。”；cursor 浮层不被 sticky header 裁切，resize/scroll 重新对齐 target，用户交互 yield。
- [x] C4 Spec runs UI 去重与历史入口 — 程序: `cd frontend && npx vitest run src/components/__tests__/EvidenceLab.test.tsx` + 浏览器 DOM — 预期: 同一 spec_id 多 runs 时只渲染 1 行主 entry 并展示 History / Preview runs 标记；Choice matrix 与 scatter plot 不出现同名无法区分重复项；可通过历史切换 Compare 所选 run。
- [x] C5 中文 Canonical 核心概念解释 — 程序: `cd frontend && npx vitest run src/__tests__/cardCanonicalLiterals.test.ts` + 浏览器 DOM — 预期: 中文模式下 11 个核心概念均有明确中文呈现（Research Question, Expectation, Admissible Space, Evidence Lab, Surprise, Compare, Next-best Challenge, Claim Ledger, Supported, Conditionally supported, Unsupported）。
- [x] C6 Challenge 中性文案 — 程序: `pytest backend/tests/test_card_research_lab.py` + `cd frontend && npx vitest run src/components/__tests__/EvidenceLab.test.tsx` — 预期: Effective F=14.14 处不再包含“may be a weak instrument”；展示“Instrument strength deserves inspection / 工具变量强度值得检查”、“Effective F = 14.14”、“Strength diagnostics alone do not establish instrument validity / 强度诊断本身不能证明工具变量有效”。
- [x] C7 Paper 聚焦正文与证据跳转 — 程序: `cd frontend && npx vitest run src/components/__tests__/WorkbenchArtifact.test.tsx` + 浏览器 DOM — 预期: Paper Writing 第一屏显示 ChapterWriter 正文与证据锚点；方向凝练/清洗/估计门台账收进“Research trace / 研究记录”可折叠区；右侧 Linked Evidence 点击可跳回 Evidence。
- [x] C8 全量门禁与 1440px 截图包 — 程序: `make test-frontend && make test-backend && make test-agent && cd frontend && npm run build` + Playwright 截图 — 预期: 所有门禁全绿；产出 5 张 1440px 截图并留档至 `docs/acceptance/evidence-card-ux-coherence/`；独立创建 PR。

## Evidence

### 1. 单元与集成测试输出

- **EvidenceLab**:
  ```
  ✓ src/components/__tests__/EvidenceLab.test.tsx (5 tests)
  Test Files  1 passed (1)
  Tests  5 passed (5)
  ```
- **AgentRail & App context-awareness**:
  ```
  ✓ src/components/__tests__/AgentRail.test.tsx (7 tests)
  ✓ src/__tests__/App.test.tsx (50 tests)
  Test Files  2 passed (2)
  Tests  57 passed (57)
  ```
- **Agent Cursor Layer & Choreography**:
  ```
  ✓ src/lib/__tests__/agentCursor.test.ts (9 tests)
  ✓ src/components/__tests__/AgentCursorLayer.test.tsx (4 tests)
  Test Files  2 passed (2)
  Tests  13 passed (13)
  ```
- **Chinese canonical literals (11 core terms)**:
  ```
  ✓ src/__tests__/cardCanonicalLiterals.test.ts (2 tests)
  Test Files  1 passed (1)
  Tests  2 passed (2)
  ```
- **WorkbenchArtifact (Paper focus)**:
  ```
  ✓ src/components/__tests__/WorkbenchArtifact.test.tsx (2 tests)
  Test Files  1 passed (1)
  Tests  2 passed (2)
  ```
- **Backend Card tests**:
  ```
  tests/test_card_research_lab.py ........ [ 24%]
  tests/test_card_spec_run.py ............... [ 69%]
  tests/test_card_claim_ledger.py .......... [100%]
  ============================= 33 passed in 28.80s ==============================
  ```
- **All Repo Gates**:
  - `make test-frontend`: 53 test files passed, 356 tests passed
  - `cd frontend && npm run build`: 0 errors (dist built in 1.74s)
  - `make check-api-drift`: openapi.json, docs/api/openapi.json, types/api.ts 同步全绿
  - `make test-backend`: 422 passed, 8 skipped in 119.93s
  - `make test-agent`: 819 passed, 1 skipped in 44.72s

### 2. 浏览器 1440x900 真实截屏证据 (Playwright Chromium)

- [01-question-1440x900.png](file:///Users/mahaoxuan/Desktop/经济学论文/econpaper/docs/acceptance/evidence-card-ux-coherence/01-question-1440x900.png)
  - 呈现 Research Question（研究问题）与 Expectation（预期），右侧 Agent Rail 专注当前 Question/Design 决策，无 Evidence “Show me” 或 “IV > OLS” 泄漏。
- [02-evidence-before-claim-1440x900.png](file:///Users/mahaoxuan/Desktop/经济学论文/econpaper/docs/acceptance/evidence-card-ux-coherence/02-evidence-before-claim-1440x900.png)
  - 呈现 Evidence Lab 视觉排布：Surprise (意外) → Results Space (散点图) → Choice matrix；Claim Ledger 处于折叠/提示卡片态，不打扰证据探索；Agent Rail 此时呈现“这个变化值得检查”及“Show me”入口。
- [03-agent-cursor-mid-demo-1440x900.png](file:///Users/mahaoxuan/Desktop/经济学论文/econpaper/docs/acceptance/evidence-card-ux-coherence/03-agent-cursor-mid-demo-1440x900.png)
  - 呈现 Agent Cursor 编排执行中：cursor 指向 Choice matrix 中的 METHOD 列，带悬浮标签“AGENT: Identification strategy changed / 识别策略发生变化”，贴合元素，不被遮挡；右侧提供 Cancel / Replay 控制。
- [04-claim-ledger-1440x900.png](file:///Users/mahaoxuan/Desktop/经济学论文/econpaper/docs/acceptance/evidence-card-ux-coherence/04-claim-ledger-1440x900.png)
  - 呈现展开后的 Claim Ledger 与中性文案 Next-best Challenge：
    “Instrument strength deserves inspection. Effective F = 14.14. Strength diagnostics alone do not establish instrument validity. / 工具变量强度值得检查。Effective F = 14.14。强度诊断本身不能证明工具变量有效。”
    以及 SUPPORTED / CONDITIONALLY SUPPORTED / UNSUPPORTED 双语结论账本与 Approve 按钮。
- [05-paper-results-1440x900.png](file:///Users/mahaoxuan/Desktop/经济学论文/econpaper/docs/acceptance/evidence-card-ux-coherence/05-paper-results-1440x900.png)
  - 呈现 Paper Results 界面：第一屏居中呈现当前生成的 Results 正文；方向凝练/清洗八步/估计门/WriteLoop 过程台账折叠进“Research trace · 研究记录”；右侧呈现 Linked Evidence 栏（β: 0.1315, SE: 0.0550, p: 0.0168, N: 3,010，“查看完整证据 →”跳转回 Evidence）。

## Named relaxations

无。数值与统计逻辑严格守约。
