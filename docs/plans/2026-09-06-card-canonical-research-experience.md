# Execution plan — Card Canonical Research Experience

规格：`docs/specs/card-canonical-research-experience.md`
契约：`docs/acceptance/card-canonical-research-experience.md`

本文件只记本轮路线、进度、决策、证据。产品真相在规格里。

## Baseline

- git: `review/workbench-v2` @ `226546b`，工作树干净
- frontend 322 / backend 389+8skip / agent 805+1skip / build / api-drift 绿
- 不 reset / stash / 覆盖用户改动

## 已做决策

1. 不建新库。对象进 `state.research_lab`，Snapshot 投影 `research`，专用 `GET /sessions/{id}/research`。
2. `state.estimate` 仍是 canonical。Preview 走新 run kind `spec_run`，禁止 `run_prewrite`。
3. Card 数据不进 `frontend/public/`。Loader：sibling `papers/data_card1995.csv`（34 列）→ `statspai.datasets.card_1995(simulated=False)`（9 列）。
4. 空桌 CTA，不是 wizard。CHARLS wizard 当反模式。
5. Surprise 纯确定性规则。Cursor 第一版 scripted + semantic targets + `motion`。
6. Claim 是写作输入契约；Results 消费 approved claim，不重写六章。
7. Card comparable spec 必须带 `smsa66` + `reg661`–`reg668`。短公式（无 region）会对上 StatsPAI 9 列 pinned 0.0740/0.1323，但对不上用户 anchor 0.0747/0.1315 与 F≈14.2。`iv_diag` 无控制 F≈63.9 不得当 instrument strength。

## 实现顺序（depth-first）

M1 对象 + boot → M2 spec runs + lab → M3 cursor → M4 claim/paper → M5 浏览器全程。

每个 milestone：implementer 实现并留证据 → 主 agent 浏览器实弹 → 再进下一里程碑。不并行改同一 state 模型。

## 进度

- 2026-09-06 侦察 + 立契。Investigator / planner 已回。与规格一致的要点：单 `state.estimate`、complete() CAS 会吞顶层 estimate、IV 已在 estimate 节点、无 Expectation/SpecRun 对象。
- 未采纳：把 Card CSV vendoring 进 `frontend/public/samples/`（许可未单独立项；boot 从 StatsPAI 加载）；planner 的 bivariate/nearc2 网格（第一版以 comparable full-controls 八条为准）。
- M1 完成（程序 + 浏览器空桌→freeze→刷新恢复）。session `3f785f7f-6243-4579-814c-64e35fa4cd0c`。证据 `docs/acceptance/evidence-card-canonical/`。
- M2 implementer 完成：`spec_run` + Evidence Lab + Surprise + Challenge。摘要 `docs/acceptance/card-canonical-m2-implementer.md`。浏览器 C9–C16 仍待主 agent。
- M3 implementer 完成：semantic Agent Cursor（Show me / experience preview）。摘要 `docs/acceptance/card-canonical-m3-implementer.md`。浏览器 C17–C20 仍待主 agent。
- 下一步：主 agent 浏览器实弹 M2+M3；然后 M4 Claim Ledger。
