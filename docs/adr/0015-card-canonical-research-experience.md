# ADR 0015 — Card Canonical Research Experience：SpecificationRun、preview 边界、Cursor 与 Claim Ledger

- **Status:** Accepted（2026-09-06，随验收契约 `docs/acceptance/card-canonical-research-experience.md` 实施）
- **Date:** 2026-09-06
- **Related:** ADR-0013（snapshot 真相）、ADR-0014（Workbench shell）、规格 `docs/specs/card-canonical-research-experience.md`

---

## Context

Workbench v2 只有一个 `state.estimate`。Card 教学案例需要 OLS 与 IV 共存、preview 不得偷改正式结果、Agent 只能指语义目标、Paper 必须消费有边界的 Claim。不能为此新建数据库或平行研究引擎。

## Decision

### 1. SpecificationRun 如何建模

对象进既有 `ResearchSession.state["research_lab"]`。每次真实执行追加一条不可变 SpecificationRun（spec id、choices、formula、estimator、covariance、analysis dataset identity、producer `spec_run` run_id、coef/se/p/n、diagnostics）。`GET /sessions/{id}` 投影 `research`；完整 lab 走 `GET /sessions/{id}/research`。`GET /sessions/{id}/evidence` 仍只描述 canonical estimate。

Card 教学数字读 `research_lab.extract_csv_path`（原始 extract），不用清洗 winsorize 后的 sidecar，否则 OLS 会从 ≈0.0747 漂到 ≈0.069。

### 2. preview vs canonical

`state.estimate` 仍是唯一正式估计。新 run kind `spec_run` 只调用既有 `_estimate_ols` / `_estimate_iv`，result **不得**含顶层 `estimate`/`results`/`main_specification`/`body_chapters`/`claim`。`RunRepository.complete()` 对 spec_run 剥离这些键并结构性合并 `research_lab`。只有 `Promote`（及既有 prewrite）可写 canonical estimate。Revert 从 `canonical_history` 恢复。

### 3. Agent Cursor semantic-target contract

Agent 只操作 semantic id（`evidence.spec.ols`、`evidence.spec.iv`、`evidence.choice.estimator`、…）。`SemanticTargetRegistry` 把 id 解析成 DOM rect。禁止坐标、CSS selector、XPath 作为控制面。Cursor layer 挂在 Workbench Shell，`pointer-events: none`，`motion` transform，用户 pointer/keyboard 让路。第一版 scripted，不接 LLM。Point 不改研究状态；Demonstrate 只 enqueue preview `spec_run`。

### 4. Claim Ledger 真相边界

Claim 是写作输入契约，不是 LLM 先写再检查。Card 主张的 supported / conditionally supported / unsupported 措辞由规则从 OLS/IV runs 填入。用户 `Approve` 之前 Results 不得 grounded（`claim_unapproved`）。正文绑定 Claim wording + SpecificationRun 系数；出现 unsupported 句则不得标 grounded。canonical / claim 变更后旧 Results 标 stale。`prepare-paper` 把已批准的 comparable IV run 提升为 canonical 并补 identification/robustness/outline，供既有六章门写 Results——不是第二套写作引擎。

## Consequences

- 教学案例与 course-panel 共用 SessionStore / RunRepository / estimate 节点。
- 活着的 `python -m runner` 不会随 uvicorn `--reload` 加载新 kind；加 `spec_run` 后必须重启 runner。
- Paper 其他五章仍走原门；本 ADR 只打通 Results ← Claim。

## Out of scope

LLM 自主科研、组合爆炸、38 methods UI、GSAP、新 Agent framework、把 Card CSV vendoring 进 `frontend/public/`。
