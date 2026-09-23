# 0. Product-line lock — DECIDE-6

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


**DECIDE-6 (frozen; Decide via Firstmate).** Encode the following **verbatim**:

**Order:** title/question → design propose (Y/X/interactions/method) → human confirm → data candidates → attach → prewrite pauses.

**Locks:**

- Fixtures/catalog = candidates only, never answer key.
- DiD only from confirmed `design.method=did` + treated×period; NO catalog-id `allow_did`.
- OLS default elsewhere; het interaction hard-block still.

Product-object name in this file is `session.design` (same object as `design` above). `Y` / `X` are outcome / treatment. Later slices must not evaluate by reading gold chapter bodies.

The engine proposes a research design from the **session title** (and any user-supplied research-question text) **first**. Classic fixtures / catalog entries are **candidates only**, never an answer key. The user must **confirm** a design before downstream gates treat it as locked (`session.design`). DiD is allowed only from that **confirmed** design (`design.method=did` or `norm_method` equivalent **and** the required treated×period interaction). Catalog id is never the DiD source of truth. OLS is the default elsewhere; the heterogeneity interaction hard-block still holds.

In scope: the formal econpaper paper path after TITLE/TOPIC — the same product line as `docs/contracts/data-completion-contract.md`.

Out of product line for this contract (do not extend, re-label, or treat as a confirmed design):

- Card teaching case (`POST /demos/card`, `research.teaching_case=card_1995`, ADR-0015)
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`)
- CHARLS wizard, CFPS fixture, spike CSVs, eval datasets (including `agent/eval/tasks/undergrad_did_01`)
- Agent spike (`/spike`), first-value marketing review, flow-sketch / draft-product chrome
- Sketch-only sample names (`sample_wage.csv`, `sample_panel_mini.csv`, `wage_panel.csv`)
- Catalog identity alone (`ck1994`, `ck1994_long`, `minimum-wage-employment`, `barro1991_growth`, …)
- Unconfirmed `MethodSelector` / `DirectionForm` picks, including a typed `DiD`
- Presence of `id_col` + `time_col`, `| entity + time` formula syntax, or `first_treat_col` without a confirmed DiD design + interaction

`dataAttached` (data-completion) and `table1Confirmed` / `specConfirmed` (PREWRITE-PAUSE) are **different** gates. This contract does not attach data, does not skip confirm-attach, and does not replace those flags. It **does** rewrite who may unlock DiD: confirmed `session.design`, not catalog-token `allow_did`.

---
