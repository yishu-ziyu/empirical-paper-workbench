# econpaper Codex Experience Wiki

这里保存 Codex 开发过程跨任务成立的模式。它不替代论文证据账本、研究设计记录或产品运行数据库。

## Pattern index

| ID | 问题 | 根因 | 已验证处理 | Run records |
|---|---|---|---|---|
| FD-plan-confirm-gate | FIND-DATA plan must not rank as a confirmed-design match before confirm | Unconfirmed `session.design` is missing/draft | POST plan returns 409; GET is `status=missing`; R-sources table is plan-only | `agent-learning/raw/2026-09-15_fd-be-plan.md` |
| FD-honesty-fixture-not-found | Fixtures/toys presented as discovered/found | Suggest listed classic-5 in the same list as Dataverse hits | Required `source_kind`; teaching shelf only; toys quarantined; empty fetch not padded | `agent-learning/raw/2026-09-15_fd-be-honesty.md` |
| FE-honesty-off-openapi | FIND-DATA FE labels must not wait on / rewrite generated `api.ts` | Backend `source_kind` is a later disjoint slice | Local FE types + grouping; fail closed on missing kind; keep OpenAPI untouched | `agent-learning/raw/2026-09-15_fd-fe-honesty.md` |
| FIND-merge-stack-on-infer | FIND G0/plan/suggest + FL search need one tip with INFER confirm lock | Sibling write-sets share G0 `2a663915`; OpenAPI/STATE overlap | Stack on INFER `0ad7e0ae`; union routers/schemas; regen OpenAPI; confirm=`status`+`confirmed is True` | `agent-learning/raw/2026-09-15_fm-e-build-find-merge-1.md` |
| FL-be-reuse-inside-find-lit | Bryce lit-review must not stand up a second pipeline | DECIDE-8 IN is thin wrap into existing `find_lit` | `fetch_papers.py` inside `agent/find_lit`; checkbox/bib stay on `search_find_lit`; mock/synthetic not found | `agent-learning/raw/2026-09-15_fl-be-reuse.md` |
| DID-spec-confirmed-not-catalog | Parked DID-BE-spec forced/blocked on catalog `allow_did` | DECIDE-6 withdrew catalog as DiD SoT | Trigger = `confirmed_did_method`; missing term 409 + estimate/write block; force `y ~ treat * post` without `| FE` | `agent-learning/raw/2026-09-15_did-be-spec-recut.md` |
| CL-BE-winsor-explicit-cuts | Stata/pywinsor2 default call is implicit cuts + replace=False/`_w` | Cleaning must be auditable 1/99 on continuous vars only | `clean_winsor` always passes `cuts=(1, 99)` and `replace=True`; skip binary/design; record engine/cuts/n_changed | `agent-learning/raw/2026-09-15_fm-e-build-cl-be-winsor.md` |
| NORMS-yaml-fail-closed | AER gates treated as passed if yaml missing or skipped | Distill as yaml + hooks, not a skill runner | Missing/unknown gate ids fail closed; propose always evaluates `design_gates.yaml`; write evaluates `chapter_gates.yaml`; unconfirmed design is not a locked spec | `agent-learning/raw/2026-09-15_fm-e-build-norms-be-1.md` |
| DC-attach-routes-on-recut-stack | CK-WRITE-1 attach / confirm-attach 404; `/upload` used as hang workaround | Recut stack had suggest + infer-design but not DC-BE-attach | Restore `/sessions/{id}/attach` + `/confirm-attach`; only confirm-attach sets `dataAttached` | `agent-learning/raw/2026-09-15_fm-e-build-attach-404.md` |
| DC-attach-plus-classic-fixture | Attach routes and `ck1994_long.csv` lived on sibling tips | Catalog already listed CK; CSV/SOURCE restored on a different branch | Merge attach first, then fixture blobs; do not invent CSV | `agent-learning/raw/2026-09-15_fm-e-build-attach-fixture-merge-1.md` |
| DATA-RIGOR-plus-attach | DATA-RIGOR honesty and attach/confirm-attach lived on sibling tips | Rigor recovered found CK + teaching flags; attach restored DC-BE routes on the recut stack | Merge attach onto rigor; keep `teaching_fixture`/`found` and real CK bytes; do not invent CSV | `agent-learning/raw/2026-09-15_fm-e-build-rigor-attach-merge-1.md` |
| BRYCE-fold-on-rigor-attach | FL/CL/NORMS/OLS lived on DATA-RIGOR siblings, not the live attach tip | Product write-sets disjoint; STATE/wiki overlap | Serial-merge onto live PASS rigor+attach; union STATE/wiki; keep found CK; do not fold EVAL-top5 | `agent-learning/raw/2026-09-15_fm-e-build-bryce-fold-1.md` |

## Skill impact

| 日期 | 目标 Skill | 原子修改 | 固定验证集前 → 后 | 决定 | 原因 |
|---|---|---|---|---|---|

## Rejected proposals

记录被拒绝的 diff 摘要、退化指标、数据类型和适用环境，避免重复试错。

## 晋升门槛

- 至少 4 份相关运行记录，并同时包含成功与失败。
- 写清问题、根因、动作协议、适用与不适用条件。
- 一次只 create 或 patch 一个 Skill。
- 在目标模型、数据类型、研究方法和工具环境运行固定验证案例与 `make test`；涉及运行链路时再跑 `make verify` 和真实用户路径。
- 未提高主指标，或造成研究可追溯性、人工审批、恢复门槛退化时回滚 Skill；Wiki 与拒绝记录保留。
