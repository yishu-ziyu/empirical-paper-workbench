# Structure Audit · FINAL（5 producer + 5 critic · APPROVED）

Date: 2026-08-06  
Gate: **APPROVE_SYNTHESIS**（Meta-critic + 4 domain critics）  
Method: 5 explore producers → synthesis → 5 independent critics  
Scope: **structure only**（书级 Harness + Continuous Empirical Loop）  
Not in scope: feature wishlist, paper quality polish, UI.

---

## 结论（先读这三行）

1. **框架结构未达标。** Continuous Loop + 书级 harness 最低线 = **FAIL**。  
2. **现有能力：** 线性 10 步 `full_pipeline` 可跑通（含真估计 + REPRO）；`empirical_agent` 有 ReAct 碎片；evaluate 门禁代码存在。  
3. **致命缺口：** 无单一编排 SSOT；**无 L8 evaluate→learn 回炉边**；质量红灯仍可 `completed`；多栈撕裂。

```text
目标:  propose → run → evaluate → learn↻ → package
现状:  propose → run → evaluate → [红灯清单] → completed
       learn 边 = MISSING
       编排主权 = 6+ 栈并行
```

**因此：现在不能谈「功能往下做」；只能谈结构收敛。**

---

## Review gate 记录

| Critic | Focus | Verdict |
|--------|--------|---------|
| C1 | Book + Loop checklist 忠实性 | PASS_WITH_FIXES（已并入下文） |
| C2 | Runtime 审计准确性 | PASS_WITH_FIXES（已并入） |
| C3 | Harness 审计准确性 | **PASS** |
| C4 | Evidence/learn 脊柱 | **PASS** |
| C5 | Meta overall | **APPROVE_SYNTHESIS** · 结构线 FAIL |

Falsifiers tried and **failed** (no counter-evidence found):

- evaluate→learn auto stage re-entry on quality red  
- single orchestrator all CLIs delegate to  
- quality red blocking full_pipeline `completed`  
- multi-agent independent process/workspace IO on main path  

Hard evidence of coexistence:

- `Results/json/parent_education_wage_full_pipeline_latest.json`：`status=completed` + `quality_verdict` includes `too_thin` / `evidence_integrity_blocked`  
- `runtime/full_pipeline.py`：`step_07` writes quality, does not raise; `run()` marks completed if no exception  

---

## Book checklist（H · 修正后）

| ID | Name | Status | Confidence | Notes |
|----|------|--------|------------|-------|
| H1 | Model + Harness modules | PARTIAL | high | agent 碎片有；主路径是脚本 |
| H1b | Constrain（沙箱/白名单/无证据否决） | PARTIAL | high | policy + tool jail 有；写稿路径未强制 bind-or-block |
| H2 | ReAct + stop | **PARTIAL** | high | **仅** `empirical_agent`；主 E2E = 线性 |
| H3 | Context stage + progressive skills | PARTIAL | med | memory_index/load_skill；无硬隔离 |
| H4 | ACI tools | PRESENT | med | ToolRegistry ok/error + path jail |
| H5 | Trace + claim↔evidence spine | PARTIAL | high | 多 schema；claim 多层未统一强制 |
| H6 | Eval-first（可测 Model+Harness） | PARTIAL | high | paper_quality 有；无多轮 golden |
| L6b | Verify out-of-model | PARTIAL | high | gate 读字段；**不主导 completed** |
| H7 | Real multi-agent IO | PARTIAL→偏 MISSING | med | registry/队列；同进程 reviewer |
| H8 | Cross-run evolution (ch8) | **MISSING** | high | `trace_learning_service` 未接主环；≠ L8 |
| L8b | Correct ladder（retry/degrade/respec/fuse） | **MISSING** | high | 仅清单 |

H8 ≠ L8：H8 = 跨 run 写回 Skill/Harness + canary；L8 = **单次论文 run 内** 红灯回炉。不得互相顶替。

---

## Loop checklist（L · Continuous Empirical Loop）

| ID | Name | Status | Confidence |
|----|------|--------|------------|
| L1 | Outer loop orchestrator SSOT | **MISSING** | high |
| L2 | Stage contracts 10-step single graph | PARTIAL | high |
| L3 | Propose/design consumable by run | PARTIAL | high |
| L4 | Data gate real | PARTIAL/PRESENT on demo | high |
| L5 | Estimate real + consistent method claim | PARTIAL | high |
| L6 | Evaluate quality/claim/citation | PRESENT（产物）/ PARTIAL（主权） | high |
| L7 | REPRO independent | **PRESENT** | high |
| **L8** | **evaluate→learn re-entry** | **MISSING** | **high** |
| L9 | Unified stop (green / honest halt / fuse) | PARTIAL | high |
| L10 | Package terminal of **same** graph | PARTIAL | med |
| L11 | Immutable run workspace + replay | PARTIAL | med |
| L12 | Human only intake / accept / steer | PARTIAL | high |

**L8 定义（产品硬线）：** gate 红 → 可解析 `next_action` + `target_steps` 重跑 + `max_rounds`/熔断。  
线性 01→10 且 07 只写 notes = **不是 Continuous Loop**（`docs/PRODUCT.md`）。

---

## 多栈撕裂（#1 主权风险，与 L8 并列致命）

| Stack | Path / entry | Role today |
|-------|----------------|------------|
| A | `runtime/full_pipeline.py` · `Product.cli full-pipeline` · `scripts/40_*` | **主 E2E 线性 10 步** |
| B | `runtime/pipeline.py` · registry | contract 引擎；rollback **不执行** |
| C | `scripts/28_agent_orchestrator.py` | adapter 策略执行 |
| D | `Product/backend/orchestrator.py` | workbench 00–08 |
| E | `Product/backend/orchestrator_v2.py` | **13 步** STEP_ORDER，ID 漂移 |
| F | `product_control_*.py` × ~21 | 旧 P 相位 API 尸体仍 import 可得 |
| G | `Program/run_paper` / formal_package 旁路 | Phase A / 交付平行线 |

`workflows/registry.json`：`status: "contract-only"`。

---

## 结构就绪度（诚实表述，不用虚 % 当真理）

| 层 | 判断 |
|----|------|
| 线性产线可跑 | **有**（demo 10/10 + REPRO） |
| 书级 Harness 主路径 | **未** |
| Continuous Loop（含 L8） | **未** |
| 单一编排主权 | **未** |
| 能否开功能产品会 | **否** |

若非要一个分母清晰的分：在上表 12 个 L 项中，PRESENT 仅 L7（及 L6 半项），**Continuous 结构项达标率远低于一半**。不把 ~42%/62% 当验收数字。

---

## 最低结构 bar（过线前禁止功能扩面）

必须全部为 PRESENT 且可证伪：

1. **唯一** PaperLoop 图 + 唯一 CLI/API 委托入口（其余栈标 legacy 或不被主入口调用）。  
2. **L8**：quality/citation/claim 红 → 自动 `target_steps` 有限回炉或 hard stop（禁止红灯 `completed`）。  
3. **L9**：完成判据 = 绿或诚实停；模型 `FINAL ANSWER` / 步数跑完 ≠ 成功。  
4. **L6b+H1b**：无证据 claim 不能 PASS；gate 读结构化字段。  
5. **H5**：单一 run 轨迹 schema 可回放 evaluate/learn 决策。  

未过线前，任何「加功能 / 加 UI / 加 multi-agent 人数」视为跑偏。

---

## 与书、产品文案的对齐

| 来源 | 要求 | 仓库 |
|------|------|------|
| Book | Agent = Model + Harness | 碎片有，主路径无 |
| Book | 可靠 = 检测/恢复/终止 | 检测有，恢复/终止未接主路径 |
| Book ch8 | 跨 run 进化有门槛 | stub，未接 |
| PRODUCT | Continuous Loop | **文案先行，结构未达** |
| SOUL | 刹车触发纠正 | 刹车写清单，纠正边缺失 |

---

## 文件索引

| File | Role |
|------|------|
| `docs/structure-audit/00_PRODUCER_SYNTHESIS.md` | 预审合成（已被本文件取代为最终） |
| `docs/structure-audit/01_FINAL_APPROVED.md` | **本文件 · 审查通过终稿** |
| `docs/PRODUCT.md` | 产品身份（目标） |
| `docs/BOOK_HARNESS.md` | 书级能力摘要 |
| `runtime/full_pipeline.py` | 当前主 E2E（线性） |
| `Product/backend/empirical_agent/` | ReAct 旁路 |

---

## 审查通过后的唯一允许讨论题

> 如何把结构收到「唯一环图 + L8 回炉 + 硬停」？  
> 不讨论：新功能、UI 妆点、再砍文档、再跑一题 demo 装完成。

*Critics approved synthesis with listed fixes applied. Structure bar remains FAIL.*
