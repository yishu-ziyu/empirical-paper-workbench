# StatsPAI 方法论吸收记录

日期：2026-05-12

来源：

- `https://www.statspai.com/zh/blog/statspai-agent-era-statistics-ecosystem`
- `https://www.statspai.com/`
- `https://www.statspai.com/zh/blog`
- `https://www.copaper.ai/`
- `https://github.com/brycewang-stanford/StatsPAI`

## 核心判断

StatsPAI 的关键价值不是“多一个统计包”，而是给 AI Agent 时代的实证研究提供稳定的方法引擎底座。它把 Stata 的一致命令体系、R 的因果推断覆盖、Python 的 AI/数据工程生态统一到 agent-native API 里。

对本项目的直接启发：

- Skill / Agent 编排层回答“做什么”：研究问题、变量选择、识别策略、模型路径、稳健性和写作顺序。
- StatsPAI / 方法引擎层回答“怎么做”：统一函数签名、统一结果对象、统一导出、统一引用。
- 产品层必须把“AI 正在做什么”和“统计引擎产出了什么”分开展示，不能把静态阶段状态伪装成真实执行。

## 可落地设计原则

1. 可观察执行优先。

   每一次 run 都要暴露 `run_id`、`steps`、`events`、`gates`、`artifacts` 和 `evidence_level`。用户看到的不是“完成 100%”，而是哪个 Agent 在哪个阶段调用了什么方法、生成了什么产物。

2. Agent-native 方法调用。

   后续 StatsPAI adapter 不应返回脆弱字符串，而应返回结构化结果：方法名、公式、输入变量、诊断、表格路径、图表路径、引用信息和导出格式。

3. 人在环中是产品主路径。

   CoPaper/StatsPAI 页面强调大纲、变量、模型设定、结果解读处都要暂停等待用户判断。本项目的 gate 也应覆盖这些节点，P0 先展示，P1 再写入 resolve API。

4. 证据等级必须可见。

   `mock`、`local_file`、`local_execution` 应直接显示在 UI 上。尤其是 mock 数据不能被 promote 为正式研究证据。

5. 出版输出与复现同等重要。

   用户最终需要 Word/LaTeX/Excel/HTML/Markdown 产物，但每个数字、图表和表格都应能回溯到代码、数据和方法调用。

## 对 P0 的约束

P0 不引入新统计方法，也不伪装 StatsPAI 已接入。P0 只做一件事：让真实执行轨迹变成产品可见对象。

必须展示：

- run_id、mode、status、started_at、finished_at
- step id/title/status/actor/summary/metadata
- event sequence/timestamp/type/actor/message/evidence_level
- gate id/title/status/blocking/options/metadata
- artifact_written 事件和 step artifacts 聚合出的产物路径
- 顶层和条目级 evidence_level

暂不实现：

- gate confirm/reject 写入
- 本地数据集上传启动真实 run
- StatsPAI adapter 的真实方法调用
