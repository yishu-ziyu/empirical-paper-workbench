# econpaper Run Record

- Date: 2026-09-17
- Task ID / state file: CORE-PRODUCT-CONTRACT-1 / runtime/tasks/20260917-core-product-contract.md
- Commit / Git context: feat/progressive-research-flow @ 2d83c2c9c716 + existing uncommitted fixes; no new commit or push
- Model and tool environment: Chat via DevSpace; existing Playwright CLI and Google Chrome; no delegated agent
- Dataset class / research method: none; no research/model run
- Task: 整理核心业务契约与当前页面映射，并核实截图文件能否直接用于视觉检查。
- Result: 文档交付完成；产品范围确认、正式接线与端到端验收另行推进。
- Session / run ID: none
- Verification commands: source reads and symbol searches; local Markdown link/section validation; git diff --check; Vite on 127.0.0.1:5189; playwright screenshot --channel chrome --viewport-size 1440,900; DevSpace.read PNG
- Output evidence locations: docs/product/core-product-contract.md; docs/product/core-flow-map.md; ../.devspace-evidence/econpaper-core-20260917/current-empty-desk.png

## 可复核发现

- 正式设计、数据挂接、Table 1 与具体设定的确认是四件独立事实。已冻结先设计后匹配数据，不能因为聊天画了另一个顺序就覆盖原规则。
- 后端存在确认 API 不代表前端接好了。AttachPanel 的正式挂载缺少确认回调，却会本地显示 confirmed；接线缺口与证据位置已登记。
- 已有 claims 的写作门与无 claims 的历史回退不同，教学案例证据不能证明任意自带数据都有同等采用链路。
- DevSpace.read 可以直接返回 PNG 图像。本轮已对当前前端完成截图再读取，不需要另一个模型才能做视觉核对。

## 限制与收尾

- 后端未启动，截图时 /auth/me 代理连接被拒绝；只验证了空桌渲染和图像读取，不是完整研究路径或无错误控制台验收。
- 已停止本轮 Vite 进程，确认 5189 无监听。没有修改产品代码、原有未提交修复或临时 HTML。
- 未执行 Pi、模型调用、全量测试、VoiceOver 或文稿导出验收。没有读取用户原始数据、金标准正文或凭据。

## 后续验证原则

- 核心确认必须通过可见用户动作走通；API 预置不能掩盖缺失按钮。
- 未提交修复不在 HEAD 中；独立 QA 必须核对完整待验版本，而非只核分支名。
- 文档草案完成与产品能力已可用是两个不同结论。
