# econpaper 独立评审运行记录

- Date: 2026-09-17
- Task ID: FORMAL-CHAIN-REVIEW-2
- Git context: feat/progressive-research-flow @ 2d83c2c9c716 + 未提交交付
- Environment: Chat 通过 DevSpace 直接读取本机代码；Python 3.12 测试环境；Vitest；读取原浏览器截图
- Result: 评审完成，交付 REJECT；下一批执行规格已写，未修改产品实现
- Evidence: 仓库外 empirical-paper-workbench-evidence/formal-confirmation-chain-1/review/

## 验证事实

受评 17 个源码/测试文件与交付指纹一致。既有后端 42 项、前端 38 项通过，新增独立前端反例 5 项失败，API/配置探针 7 项记录到与契约相反的实际行为。
关键问题是确认缺少真实对象/版本绑定、缺失设计反而放行、旧异步响应跨会话、风险确认未消费。已有规则函数测试通过不能证明新的消费端遵守规则。
global mock 在非 pytest 的 desk 配置分支被覆盖，以无效占位 key 构造配置复现；没有发起真实模型请求或读取真实凭据。
基线副本存在环境文件，仅检查名称，未检查值；已登记不传播、按授权范围脱敏的后续任务。

## 验证失败与适用边界

从 stdin 进入 pytest 不适合当前 macOS spawn 测试，改为文件入口后通过；浏览器测试注入的 React 模块不一致导致 harness 失败，改为同依赖的 Vitest 反例。两项均不是产品回归。
截图证明原 happy path 有可见输出，也暴露正文待确认与侧栏空闲矛盾；不能代替小屏全部确认、运行中刷新或真人读屏验收。
未重跑全套测试或完整浏览器 happy path；临时 Vite 停止、树内临时反例移除、受评产品文件 hash 不变。

## 后续

先修运行隔离与确认完整性，独立复核后进入意图优先流程。新产品决定与旧实现缺陷分开记录；已批准的新顺序已在旧契约入口添加替代说明，历史要求/报告保留可追溯。
