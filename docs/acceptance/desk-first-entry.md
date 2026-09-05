# 验收契约：入口改为「空桌直入 · 对话先行」（用户选定方案 A）

Status: closed

## Change

打开 econpaper 首页（无会话、无论是否看过落地页）直接进入对话工作台 DeskPage，可立即输入/上传；
GuidePage（纸上扉页落地页）不再强制拦截首次访问，降级为页眉「了解产品」可选入口，且从落地页
始终能回到空桌；顺带修复 GuidePage hero 在 1280px 视口下的横向溢出。

设计方向 = 选型稿 `econpaper/sketches/entry-redesign.html` 方案 A 的**结构语义**
（进门即对话工作台、营销层不拦路），不是该草图的像素复刻；DeskPage 保持现有三栏结构
（聊天 + 起步 chips + 上传 + agent 面板）。

## Not this

- 不重做 GuidePage 的海报视觉，不新增营销内容。
- 不改后端 / agent 管线。
- 不引入新的 npm 依赖。
- 不把「只在 dev server 看一眼」当完成；每个检查项要有程序输出或截图证据。
- 不允许通过删除/改写仍成立的现有测试断言来让门禁变绿（按新入口语义**更新**用例可以）。

## Evaluator

- C1–C5、C7（代码类）：validator 子代理独立跑程序复核，只认契约输出。
- C6（真实视口布局）：jsdom 无法测布局，由主 agent 在内置浏览器走查并留截图/取值证据，
  validator 复核证据文件存在性与结论一致性。

## Checks

- [ ] C1 首次访问直接进空桌：localStorage 无 `econpaper_seen_guide`、无会话时挂载 App，
      渲染 `data-testid="desk-page"`，空态输入框 `data-testid="desk-paper"` 可见，且不出现
      GuidePage 的 hero 标题「用数据写实证论文」与「四步写出论文」分区。
      程序: `cd econpaper/frontend && npx vitest run src/__tests__/App.test.tsx`（含按本条新增的用例）— 预期: 全绿
- [ ] C2 seenGuide 不再是进门条件：`localStorage['econpaper_seen_guide']='1'` 与删除该键两种
      初始化，首屏都是 `desk-page`。
      程序: `cd econpaper/frontend && npx vitest run src/__tests__/App.test.tsx`（新增参数化用例）— 预期: 全绿
- [ ] C3 空桌可操作不回退：starter chip 点击把文本填入输入框、`desk-upload-inline` 触发上传入口、
      `desk-paper` 可输入后出现 desk-thread（沿用现有 DeskPage 语义）。
      程序: `cd econpaper/frontend && npx vitest run src/__tests__/DeskPage.test.tsx` — 预期: 全绿
- [ ] C4 落地页降级为可选入口且有回路：空桌页眉有「了解产品」入口（新 `data-testid="desk-open-guide"`），
      点击后出现 GuidePage；从 GuidePage 有可见途径（现有 CTA 或返回按钮）回到 `desk-page`。
      程序: `cd econpaper/frontend && npx vitest run src/__tests__/App.test.tsx`（新增两条用例）— 预期: 全绿
- [ ] C5 工作台侧入口不产生死端：无会话工作台（desk 确认方向后）点「再看一次产品页」能看 GuidePage，
      且能回到工作台；有会话时工作台行为不回归。
      程序: `cd econpaper/frontend && npx vitest run src/__tests__/App.test.tsx src/__tests__/integration.test.tsx` — 预期: 全绿
- [ ] C6 GuidePage 无横向溢出：1280×800 视口打开 GuidePage，
      `document.documentElement.scrollWidth <= document.documentElement.clientWidth`。
      程序（主 agent 浏览器走查）: 打开开发服 → 经「了解产品」进入 GuidePage → evaluate 取值 + 全页截图。
      预期: 比较式成立；实现侧以响应式约束（clamp/max-w/允许换行）落地。
- [ ] C7 回归门禁：前端全量测试与构建通过。
      程序: `cd econpaper && make test-frontend && cd frontend && npm run build` — 预期: 退出码 0

## Evidence

- C1 PASS — `npx vitest run src/__tests__/App.test.tsx`：`Test Files 1 passed (1), Tests 49 passed (49)`，
  含新增用例「C1 首次访问直接进空桌：无 seen_guide 无会话时首屏是 DeskPage，无落地页内容」。
  真实浏览器复核（1280×800，`localStorage.clear()` 后 reload）：`hasDesk=true, hasPaper=true, paperVisible=true,
  leakedGuideHero=false, leakedFourSteps=false, hasGuideEntry=true, seenGuideKey=null`。
  截图：`/Users/mahaoxuan/.zcode/cli/artifacts/sess_749e940a-a6e6-498e-a272-24d8d1faf6b5/call_fc7d443ef090498d8f07368e-tool-result-504c3751-fb4b-49d0-9763-6ec2afc4f27a.png`
- C2 PASS — 同命令，新增参数化用例「C2 seenGuide 不再是进门条件：seen_guide 键存在与否首屏都是 desk-page」。
- C3 PASS — `npx vitest run src/__tests__/DeskPage.test.tsx`：`Test Files 1 passed (1), Tests 11 passed (11)`，
  新增 starter chip 填入 / desk-upload-inline 触发 / desk-paper 输入出 thread 三用例，原 7 用例保留全绿。
- C4 PASS — App.test.tsx 新增「C4 空桌页眉『了解产品』进入 GuidePage，CTA 再回到空桌」等两用例；
  真实浏览器复核：原生点击 `desk-open-guide` → 落地页出现（h1=用数据写实证论文…），
  `guide-back-desk` 存在，点击后 `deskBack=true, guideGone=true`。
- C5 PASS — `npx vitest run src/__tests__/App.test.tsx src/__tests__/integration.test.tsx`：
  `Test Files 2 passed (2), Tests 52 passed (52)`，含新增「C5 无会话工作台点『再看一次产品页』能看 GuidePage，
  且能回到工作台不丢方向」。
- C6 PASS — 主 agent 浏览器走查：1280×800 视口打开 GuidePage，
  `scrollWidth=1265 <= clientWidth=1265`（overflow=false）；hero 大标题完整显示无裁切。
  截图：`/Users/mahaoxuan/.zcode/cli/artifacts/sess_749e940a-a6e6-498e-a272-24d8d1faf6b5/call_28e9407f2a51404b8cf7eca6-tool-result-fe1d2f3b-6065-4111-8789-62a0d6e10016.png`
- C7 PASS — `make test-frontend`：`Test Files 45 passed (45), Tests 322 passed (322)`；
  `npm run build` 退出码 0（`✓ built in 1.48s`，>500kB chunk 警告为改造前已有）。

## Named relaxations

无。
