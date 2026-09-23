# econpaper Task State

- Task ID: CORE-PRODUCT-CONTRACT-1
- Status: complete（文档整理完成；P0 范围待确认，业务接线与完整 QA 未完成）
- Git context: `feat/progressive-research-flow` @ `2d83c2c9c716` + existing uncommitted progressive-flow fixes
- Goal: 从现有已确认原则与当前入口/业务代码整理短版核心产品契约，附现有页面映射与后续验收顺序。
- Hard bar: 不改产品代码、不创建第二套业务状态机、不放宽已冻结闸门；保留已有未提交改动；不 commit/push；不调用 Pi 或其他模型。
- Session / run ID: none
- Current research stage: product contract / source audit
- Current review / approval gate: 已授权整理契约；新增范围取舍单列为建议，不冒充已验收能力。
- Verified facts: 冻结的正式依赖是设计提出/确认先于数据匹配与挂接；挂接、Table 1、具体设定确认独立。AttachPanel 正式挂载未接 onConfirmAttach，组件本地却先置 confirmed。设计/估计前确认存在后端接口但当前页面未串联。七对象均按既有承载位置整理，没有新建业务状态机。
- Current hypothesis: 先闭合正式入口的确认链，再统一证据采用与失效传播，最后做展示迭代；非 Card CSV + OLS 建议作为第一条新增正式验收路径。
- Changed files: `docs/product/core-product-contract.md`、`docs/product/core-flow-map.md`、本任务文件、`runtime/STATE.md`、`agent-learning/raw/2026-09-17_core-product-contract.md`。产品代码未改。
- Failed paths: 截图期间 /auth/me 代理 ECONNREFUSED（后端未启动）；未将此记为无错误浏览器验收。
- Data / output evidence locations: 仓库外 `../.devspace-evidence/econpaper-core-20260917/current-empty-desk.png`，1440×900，来自当前 Vite 页面而非设计原型。
- Test evidence: 六节结构与全部本地 Markdown 来源链接校验通过；源文件关键行号已核对；git diff --check 通过。Playwright/Chrome 截图后 DevSpace.read 成功返回图片，完成一次真实截图读取。未改产品代码，未重跑单元/全量测试。
- Pending external state: P0 范围待产品确认；全程浏览器、非 Card 研究与 VoiceOver 待后续验收；本轮未启动 Pi，也没有 commit/push。
- Next action: 确认短契约的 P0 范围；以可见用户动作建立失败测试，再补设计/挂接/估计前确认接线。QA 必须针对包含未提交修复的同一版本，不能仅从旧 HEAD 建 worktree。
- Updated at: 2026-09-17
