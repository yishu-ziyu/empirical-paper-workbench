# FORMAL-CONFIRMATION-CHAIN-3 收尾验收

日期：2026-09-18。结论：**ACCEPT（S1–S5 与 run 重领问题已闭合）**。

本文件不改写 CHAIN-2 的 REJECT 历史。它只记录用户授权当前 Chat 直接修复后的新代码事实与验收证据。

## 修复结果

| 问题 | 结果 |
|---|---|
| S1 用户看见 A、请求到达时却批准 B | 所有正式确认/运行入口消费 snapshot 的 opaque confirmation target；后端原子校验用户所见 design / dataset / preview / diagnosis。旧对象返回 409，不给当前对象盖章。 |
| S2 两个草稿共用秒级时间戳 | 草稿新增唯一 revision；确认必须携带 revision，比较与 lock 在同一 SessionStore 写事务里完成。 |
| S3 已确认方法参数可被请求替换 | 设计执行投影扩到方法特有字段与序列字段；正式方向请求只能等价表达已批准设计，不能改 cutoff / instrument / cluster / time 等含义。 |
| S4 换数据后旧结果仍是“当前结果” | 上游版本变化会归档旧证据并清空 live estimate/results/diagnostics；Evidence API 暴露历史摘要与 stale 状态。前端当前结果为空，旧数值只从“历史结果”进入。 |
| S5 同 key 可跨方向/估计阶段复用 | durable run 保存完整 intent；重放校验 kind + intent，语义不同返回 `idempotency_conflict`；同意图仍返回原 run。 |

## 异步与运行安全

确认命令统一携带 session ownership、对象版本和持久投递凭证。未知投递结果先回读；服务端已经接收的 200/202 请求复用原 key，不以新 UUID 再投。

之前小屏验收出现约 200 秒、同一 run 多次领取。根因链是短暂数据库争用触发 authority probe 误取消后，旧 worker 仍占着 60 秒 lease。现在：

- 慢但成功的 probe 有有限容忍时间；连续不可用仍在原有约 1 秒安全界限内触发停止；
- worker 真正停止后，仅当 owner + lease_epoch 仍属于自己时将 run 还回 PENDING；
- 新 claim 增加 epoch，旧 worker 不能 progress / complete；terminal run 也不会被 revive；
- 最终浏览器链所有 durable run 均为 attempt=1。

## 验证

- 全量：agent 1072 passed / 2 skipped；backend 712 passed / 8 skipped / 13 subtests；frontend 554 passed；OpenAPI drift 通过。
- 恢复后聚焦复跑：backend 78 / frontend 48 / LLM router 22，全部通过。
- `git diff --check` 通过；frontend lint 0 errors（6 条既有 Fast Refresh warnings）；production build 通过（既有大 chunk warning）。
- 真实 backend + runner + frontend、mock 模型、合成数据：桌面与 320×568 均完成设计确认 → 同会话 attach → 挂接确认 → 真实预览 → 样本/设定确认 → 真实估计 → 刷新恢复。
- 第一份数据 β=31.9631147541；替换数据后旧结果退出当前证据，只留历史；重新确认并估计后 β=94.9631147541。
- 故障注入：丢弃一次 sample 确认响应和一次 estimate 202 响应，客户端均用原 intent key 核对/接回，没有重复 run。

证据根目录：`../empirical-paper-workbench-evidence/formal-confirmation-chain-3/`。

## 未包含在本任务

真人 VoiceOver、证据页执行代码溯源层，以及下一阶段“研究意图 → 数据可行性 → 可执行设计”的产品化不属于 S1–S5 修复。下一阶段按 `docs/specs/research-intent-to-design.md` 继续，不恢复已经废弃的“数据前先确认设计”默认顺序。

