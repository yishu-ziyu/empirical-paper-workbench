# 产品叙事 · Continuous Empirical Loop

**唯一产品定义文件。** 其它旧愿景 / P 阶段 / product-control / 半成品品牌文案一律作废。

## 这是什么

**empirical-paper-workbench**：本地优先的 **全自动实证论文工作台**。

对标直觉（不是抄功能）：[Discovery Loop](https://www.discoveryloop.com/) 把科学/工程实验环自动化。  
本产品把 **实证论文** 的环自动化：

```text
propose (设计/规格) → run (数据门+估计) → evaluate (质量/claim/复现) → learn (修订/重跑)
```

直到吐出 **论文包**，或触达诚实停止条件（数据不可用、方法不可识别且无法自动降级等）。

## 不是什么

| 禁止身份 | 原因 |
|----------|------|
| 「可审计半成品 + 红标清单」工厂 | 那是失败态与内部诊断，不是产品承诺 |
| P0–P18 人工签到流水线 | 人变成工蚁，Agent 变成表格 |
| 无证据一键假论文 | 学术与产品双重自杀 |
| 通用 chat 套壳 | 没有 harness、没有环、没有证据脊柱 |

## 用户承诺

1. **输入**：研究题目 + 可用数据路径（或仓库内已登记样本）。
2. **过程**：系统自动走设计→文献线索→数据诊断→估计→写作→质量评价→引用诚实门→复现→答辩提纲；失败则 **自动纠正/重规格**，轨迹落盘。
3. **输出**：可打开的 Markdown/DOCX/PDF 初稿 + Results 表图 + claim↔evidence + 复现脚本/报告。
4. **人**：丢料、最终验收、或显式 `HITL` 抢方向盘。日常不逐步点「批准」。

## 内部刹车（不是车标）

这些机制 **必须存在**，但 **不占用首页哲学**：

- 路径沙箱与工具白名单  
- claim register ↔ evidence bank  
- integrity / course-paper quality gate  
- 文献未核验 → 正文降级，禁止假引用 PASS  
- 独立 replication 哈希对齐  
- 轨迹 JSONL 可回放  

红灯触发的是 **下一动作**（补证据、降级主张、换规格、停机），不是「打开确认面板当终局」。

## 能力上限（书级 harness）

材料：`/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book` + `AI-Agents-in-Depth-zh-CN.pdf`。

```text
Agent = Model + Harness
Harness = Context + Tools + Constraints + Verification + Correction
```

必须做到书里要求的硬东西：

- **ReAct 主循环** + 明确停止条件  
- **Context Engineering**：按阶段切片，禁止全库倾倒  
- **ACI 工具**：自包含调用 + 完整结构化回传  
- **Skills 渐进披露**：按需加载，不预载十步全家桶  
- **验证在模型外**：gate 读结构化字段，不信「我觉得做完了」  
- **纠正闭环**：失败码 → 下一动作 / 熔断  
- **真 multi-agent**：独立 IO 与产物合同；禁止 markdown 人设串台  
- **无评估则无进步**：每轮 loop 有可枚举指标  

## 固定 10 步合同（实现层）

**外环 SSOT（主路径）：** `runtime/continuous_loop.py` · CLI：`Product.cli continuous-loop` · `agent-pi --loop`  
**内环 runner：** `runtime/full_pipeline.py`（线性 10 步；L8 子集重跑）

| 步 | 名 | 合同产物方向 |
|----|----|----------------|
| 01 | design | 研究设计 / 风险 |
| 02 | literature | 文献候选（未核验必须标） |
| 03 | paper_reading | 阅读协议 |
| 04 | data_gate | 真实数据诊断 + 描述表 |
| 05 | causal | 真实估计 + 稳健 |
| 06 | writing | 正文 + claim register |
| 07 | revision | 质量门评价与修订信号 |
| 08 | citation | 引用诚实门 |
| 09 | replication | 独立复现 REPRO |
| 10 | defense | 答辩 Q&A |

闸门顺序固定；闸门内 Agent 可多轮工具调用。  
**Continuous** 的含义：07 不通过 → 回 01/04/05/06 再跑，而不是卡在 UI 确认。

## 成功 / 失败判据

**成功（课程论文可用绿）：**

- 用户不盯屏也能拿到正文 + 表 + 复现 OK  
- 关键数值句可指到 Results JSON 或脚本  
- 文献/识别若弱，正文主张已自动降级且说明限制  

**失败：**

- 交付物主要是 gate JSON 与「请人工」  
- 系数/引用无证据  
- 把逐步 human signoff 标榜成产品完成度  

## 仓库入口

- 人读：本文件 · `README.md` · `SOUL.md`  
- 书级能力：`docs/BOOK_HARNESS.md`  
- 跑：`docs/TRY_FULL_PIPELINE.md`  
- Agent：`docs/TRY_EMPIRICAL_AGENT.md` · `AGENTS.md`  
- 状态：`WORKFLOW_STATUS.md` · `docs/loop-status.json`  
- **只认现在**，不记 P 朝代史

## 修订规则

改产品身份只改本文件 + `README.md` + `SOUL.md`。  
禁止复活 `product-control/0x_*.md` 式愿景分册与 P 阶段史诗。
