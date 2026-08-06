# 书级 Harness 能力上限（读入摘要）

材料 SSOT：`/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book`  
辅：`/Users/mahaoxuan/Desktop/AI产品经理/AI-Agents-in-Depth-zh-CN.pdf`  
产品映射：`docs/PRODUCT.md`

## 公式

```text
Demo:  Agent = LLM + 上下文 + 工具
Prod:  Agent = Model + Harness
Harness = 上下文 + 工具 + 约束 + 验证 + 纠正
Loop:  思考 → 行动 → 观察 → … → 停止条件
```

模型商品化后，竞争力在 Harness。无评估则无进步。评的是 **Model+Harness**，不是裸模型。

## 为什么能很强

1. **可验证任务最先成熟**：回归退出码、表哈希、REPRO、claim↔table 对齐 = 天然评价器。  
2. **可靠 = 每类错有检测/恢复/终止**，不是「少犯错」。  
3. **长任务拆初始化 Agent vs 执行 Agent**，抗上下文耗尽与过早宣称完成。  
4. **propose→run→evaluate→learn**：轨迹不可变 → 三层验（结果/过程/质量）→ 最小 diff 写回 Skill/程序/Harness → canary，禁止自评过门。  
5. **Multi-agent 真增益**只在引入新信息（执行结果/检索/独立审阅）；同文辩论是剧场。  

## 本产品必须建的件

| 件 | 论文环落地 |
|----|------------|
| 工作区状态 | run 目录：设计、估计、表、hash、TODO |
| ACI 工具 | 自包含调用 + 结构化失败回灌 |
| Skills 渐进披露 | 识别/估计/写作/复现按需加载 |
| 约束编码 | 无证据 claim 否决；路径白名单 |
| 验证自动化 | quality gate · claim audit · REPRO |
| 纠正分级 | 重试 → 降级 → 回炉改规格 → 熔断 |
| 停止条件 | 论文包+复现齐，或不可恢复；不是模型自称 done |
| 提议者-审核者 | 成文 vs claim audit 独立上下文 |

## 停止条件（完成判据）

**完成**：可打开论文 + 可复现（或诚实降级说明）+ claim 可追溯。  
**非完成**：gate JSON、「请人工确认」、无证据 PDF。

人只在：丢料、验收、抢方向盘。

## 反模式

- 无 Harness 直接交稿  
- 目标模糊却开自动反馈 → 高效跑偏  
- 无限重试无熔断  
- 把护栏当品牌首页  
- multi-agent 只加角色不改工具/不验  

## 与 Continuous Empirical Loop

```text
design → estimate → write → reproduce → revise
   ↑______________evaluate/learn_______________|
```

闸门顺序可固定；闸门内 ReAct。红灯触发纠正，不触发签到台。
