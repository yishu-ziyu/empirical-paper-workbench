# Structure Audit · Producer Synthesis (pre-critic)

Date: 2026-08-06  
Method: 5 parallel explore agents (book SSOT / loop target / runtime / harness / evidence-eval)  
Status: **AWAITING 5-CRITIC REVIEW** — do not treat as final until critics pass.

## One-line pre-conclusion (to be verified)

**仓库有：线性 10 步 full_pipeline + 部分 Harness 碎片 + evaluate 门禁代码。**  
**仓库没有：单一编排 SSOT + evaluate→learn 回炉环 + 统一 step-graph + package 收口。**  
产品文案已是 Continuous Loop；**框架结构未达标。**

```text
  目标:  propose → run → evaluate → learn↻ → package
  现状:  propose → run → evaluate → [红灯清单] → package(可选平行栈)
                         learn 边 ≈ MISSING
  额外伤:  6+ 编排栈并存撕裂主权
```

---

## A. Book checklist H1–H8 (target)

| ID | Name | Audit use |
|----|------|-----------|
| H1 | Model+Harness 五件套 | modules exist & ablatable |
| H2 | ReAct + stop | loop + max_iter/fuse |
| H3 | Context stage + progressive skills | no full dump |
| H4 | ACI tools | structured full returns |
| H5 | Trace/memory/evidence spine | replayable |
| H6 | Eval-first | harness measurable |
| H7 | Real multi-agent IO | not persona theater |
| H8 | Continuous evolution | propose→verify→ship |

Sources: ai-agent-book ch1–6,8,10.

## B. Loop checklist L1–L14 (target)

Critical spine: **L8 evaluate→learn**. Linear 10-step without L8 = **not** Continuous Loop.

## C. Cross-agent scores (producer)

| Agent | Focus | Readiness (producer) |
|-------|--------|----------------------|
| P1 | Book SSOT checklist | checklist only |
| P2 | Loop target L1–L14 | L8 named as main gap |
| P3 | Runtime/pipeline | **~42%** |
| P4 | Agent harness | **~62%** |
| P5 | Evidence/eval/learn | evaluate PRESENT; learn MISSING |

## D. Unified matrix (producer draft)

| Structure | Status | Evidence anchor |
|-----------|--------|-----------------|
| H1 Harness modules | PARTIAL | empirical_agent tools/policy + full_pipeline parallel |
| H2 ReAct loop | PRESENT (agent) / MISSING (main E2E) | empirical_agent vs full_pipeline |
| H3 Context slicing | PARTIAL | memory_index; no hard stage isolation |
| H4 ACI tools | PRESENT | ToolRegistry ok/error |
| H5 Trace | PARTIAL | multi schemas |
| H6 Eval harness | PARTIAL | paper_quality code; no golden multi-round set |
| H7 Multi-agent | PARTIAL | registry/queue; no independent IO spawn |
| H8 Evolution | PARTIAL stub | trace_learning_service not wired |
| L1 Outer loop orchestrator SSOT | **MISSING** | 6+ stacks |
| L2 Stage contracts 10-step | PARTIAL | registry + full_pipeline; IDs drift elsewhere |
| L3–L5 propose/run | PARTIAL | full_pipeline hardcodes topic |
| L6 Evaluate gates | PRESENT-ish | quality/citation/REPRO code |
| L7 REPRO | PRESENT | replication + step_09 |
| **L8 evaluate→learn** | **MISSING** | linear run; quality red still completed |
| L9 Stop conditions | PARTIAL | not unified / quality not hard stop |
| L10 Package in loop | PARTIAL | delivery/formal parallel |
| L11 Immutable run workspace | PARTIAL | multi run dir shapes |
| L12 Human only intake/accept/steer | PARTIAL narrative | product_control* APIs still in code |
| Dual-stack fracture | **PRESENT (bad)** | full_pipeline / pipeline / 28 / orch / orch_v2 / product_control / run_paper |

## E. Top structural gaps (producer)

1. No single PaperLoopOrchestrator SSOT  
2. No StepGraph single truth (10 vs 13 vs 00–08 vs P-phases)  
3. No EvaluateLearnLoop (gate → target_steps rerun → max_rounds)  
4. No unified RunTrace/Replay  
5. Package not terminal stage of same graph  
6. Main delivery path is linear script, not harness self-heal loop  

## F. Falsifiers for critics

Critics must try to **disprove** any PRESENT claim by finding:
- file/function that implements evaluate→learn auto re-entry
- single entry all CLIs delegate to
- quality red that blocks full_pipeline completed
- multi-agent with separate process/workspace IO

If found, upgrade status and cite path.
