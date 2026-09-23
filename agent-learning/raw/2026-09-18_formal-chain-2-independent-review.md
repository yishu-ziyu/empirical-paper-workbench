# econpaper 独立评审运行记录

- Date: 2026-09-18（评审于本机 2026-09-17 开始）
- Task ID / state file: FORMAL-CHAIN-2-REVIEW / runtime/tasks/20260917-formal-chain-2-review.md
- Commit / Git context: feat/progressive-research-flow @ 2d83c2c9c716c0708eb5303840e76f51749583d1 + CHAIN-1/2 未提交交付，未改产品实现
- Model and tool environment: ChatGPT Chat → DevSpace 本机；现有 Python venv、Vitest、Playwright/Chrome；无模型委派或真实模型调用
- Dataset class / method: 隔离合成状态与 60 行合成 CSV / OLS，非真实研究数据验收
- Task: 独立核验 CHAIN-2 指纹、确认对象版本、幂等恢复及真实页面路径
- Result: fail（实施验收 REJECT，独立评审完成）
- Session / run ID: 小屏估计 c89cd75a-1507-4da6-ac12-d5c4ce93cd49；其余去敏运行索引见证据目录
- Verification commands: 安全环境下 targeted pytest、Vitest --mode review；review/api_probes.py；review/browser_path.mjs、browser_replace.mjs、browser_recover.mjs；make verify；npm run lint/build --mode review
- Output evidence: ../empirical-paper-workbench-evidence/formal-confirmation-chain-2/review/；docs/reviews/20260917-formal-confirmation-chain-2-independent-review.md

## 成功动作

评审前 37/37 交付指纹一致。独立既有测试后端 84、router 22、前端 47 通过。真实桌面确认链运行到数值与证据，独立 OLS 复算一致。直接读取 Playwright PNG 核查显示；隔离 make verify 和构建通过。

## 失败动作与根因

确认记录虽存入服务端当前身份，却未核对请求方所见身份；秒级 proposed_at 可碰撞；执行对齐字段不完整；换数据只清预览、不撤销旧结果作为当前的资格；幂等回执未比较动作与输入。五项 API 反例和换数据浏览器反例均可复现。

首次 router 测试全局 mock 与部分配置测试前提冲突；更正测试环境后通过，保留两次日志。小屏浏览器估计 90 秒超时，同一 run 约 201 秒、4 次领取后成功；因果归属尚未知，保留全部时序，不以延长等待或后续成功覆盖首轮失败。

## 可复现条件

以本次受评文件指纹运行证据目录中的脚本。服务使用独立端口 8483/5323 和 /tmp/fcc2-browser-review-rB2ljb，模型 mock，阻止外部连接与读取环境文件；测试进程收尾停止。旧敏感配置副本不得作为测试输入。

## 候选模式

存了版本不等于验证了版本：必须核对“用户所见目标 → 请求目标 → 原子确认/执行”的同一身份。测试应包括跨窗口、同形异内容数据与跨动作幂等反例。单次运行记录不晋升为通用 Skill。
