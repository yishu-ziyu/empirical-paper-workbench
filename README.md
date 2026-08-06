# empirical-paper-workbench

**全自动实证论文工作台 · Continuous Empirical Loop**

远程：https://github.com/yishu-ziyu/empirical-paper-workbench.git  
本地：本目录

## 一句话

题目 + 数据进来 → 系统无人值守转 **设计 → 估计 → 成文 → 复现 → 修订** 环 → 吐出可打开的论文包。

人只在三处出现：丢料、验收、抢方向盘。  
审计、哈希、claim 门、质量门是 **loop 内部的刹车**，不是产品口号，不是每一步签到台。

## 成功标准

| 算成功 | 不算成功 |
|--------|----------|
| 课程/本科题目 + 可用数据 → 多轮自动跑 → 论文可打开 + 复现脚本可跑 | 只剩 JSON 门禁、红标清单、「请人工确认第 N 步」 |
| 轨迹可回放；无证据 claim 进不了 PASS | 漂亮 PDF 但系数/文献捏造 |
| 证据不够时 **降级诚实输出**，然后 **自动改设计/重跑**，不是停成半成品剧场 | 用「半成品 + 缺口」当品牌身份 |

## 一次跑通（主路径 = Continuous Loop）

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
set -a; source .env.local; set +a
export MINIMAX_CN_API_KEY="${MINIMAX_API_KEY}"

# **主路径** evaluate→learn 回炉（默认 Grok 4.5）
PYTHONPATH=. python3 -m Product.cli continuous-loop --llm --max-rounds 3

# Pi 能拍多少拍多少（写稿默认 Grok；Pi 仅助攻）
PYTHONPATH=. python3 -m Product.cli agent-pi --loop --max-rounds 3 "跑通父母教育工资 Continuous Loop"
```

LLM 默认：`provider=grok` · `model=grok-4.5`（见 `docs/SETUP_GROK.md`）。开发/测试真实调用一律 Grok 4.5。

内环线性 10 步（调试用，不是产品主身份）：

```bash
PYTHONPATH=. python3 -m Product.cli full-pipeline --llm --provider grok --model grok-4.5
```

详见 `docs/TRY_CONTINUOUS_LOOP.md`。

产品壳（可选 UI）：

```bash
python3 Product/serve_product.py   # http://127.0.0.1:8765
```

## Continuous Empirical Loop

```text
        ┌─────────────────────────────────────────┐
        │                                         │
  题目+数据 → design → lit → data → estimate       │
        │         │                │              │
        │         ▼                ▼              │
        │      evaluate ←── write ← results       │
        │         │                │              │
        │         ▼                ▼              │
        │   revise / re-spec ──► reproduce ──► package
        │         │                               │
        └─────────┴───────────────────────────────┘
              内部：claim↔evidence · quality gate · REPRO
```

固定闸门管 **阶段合同**；闸门内 Agent 可多轮 ReAct。  
质量门红灯 → 纠正动作（改规格/补数据/重估/重写），不是把「请人点确认」当终局。

## 仓库结构（落地，不是叙事）

| 路径 | 职责 |
|------|------|
| `runtime/full_pipeline.py` | 全流程编排 SSOT |
| `Product/` | CLI、Agent、API、可选 React 壳 |
| `Program/` | 可复现分析代码 |
| `Data/` | Raw / Interim / Final |
| `Results/` | 表图 JSON 证据 |
| `Manuscripts/` | 正文与生成稿 |
| `evidence/` | claim register / integrity audit |
| `replication/` | 独立复现脚本 |
| `docs/PRODUCT.md` | **产品叙事唯一入口** |
| `SOUL.md` | Agent 身份 |

旧 P0–P18 门禁剧场、半成品品牌稿、product-control 阶段叙事 **已删除**。  
历史 run 产物可在 `Results/`、`Reviews/`、`state/` 里当证据考古，不再当产品定义。

## 已验证 demo

- 题目：父母受教育水平对子女工资收入的影响（CFPS 修复样本）
- 例：`full_pipeline_parent_education_wage_20260806_212153` · 10/10 · `REPRO_OK`
- 论文：`Manuscripts/generated/parent_education_wage_full_pipeline_paper.md`
- 复现：`python3 replication/reproduce_parent_education_wage_full_pipeline.py`

## 能力标尺

生产 Agent 以 [ai-agent-book](file:///Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book) 为上限参考：

```text
Demo:  Agent = LLM + 上下文 + 工具
Prod:  Agent = Model + Harness
Harness = 上下文 + 工具 + 约束 + 验证 + 纠正
Loop:  思考 → 行动 → 观察 → … → 停止条件
```

无评估则无进步。工具自包含、完整回传。Skills 渐进披露。Multi-agent 要有独立 IO，禁止人设串戏。

## 文档

- **产品叙事**：`docs/PRODUCT.md`（只认这一份）
- **试用**：`docs/TRY_FULL_PIPELINE.md` · `docs/TRY_EMPIRICAL_AGENT.md`
- **Agent 约束**：`AGENTS.md` · `SOUL.md`
- **术语**：`CONTEXT.md`
- **当前状态**：`WORKFLOW_STATUS.md`
