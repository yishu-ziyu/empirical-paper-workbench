# 3. Order vs DECIDE-6 / DECIDE-7

> 上级：[Bryce tools contract (four IN; DECIDE-8)](../bryce-tools-contract.md)


## 3.1 Intended sequence (frozen)

DECIDE-6 (verbatim): `title/question → design propose (Y/X/interactions/method) → human confirm → data candidates → attach → prewrite pauses`

DECIDE-7 (verbatim relative to infer-design): `title → propose → confirm → find-data plan + candidates → attach → prewrite`

DECIDE-8 **does not change that order**. Mapped:

```
title/question
    → design propose                         ⇒  session.design status=draft          (infer-design)
    → human confirm                           ⇒  session.design status=confirmed
    → find-data plan + candidates            ⇒  session.find_data (FD + R-sources)
    → find-lit (FL + R-lit-bar)            ⇒  session.find_lit   (FL-BE-reuse: fetch_papers.py THINS HERE)
    → attach                                 ⇒  dataAttached
    → clean_winsor (pywinsor2, 1/99, cont.) ⇒  cleaning_report.steps (CL-BE-winsor; after attach)
    → prewrite pauses                        table1Confirmed then specConfirmed
                                                + NORMS-BE design_gates / chapter_gates
                                                + identification / robustness
    → chapter write / export                 chapter_gates.yaml on write; doc: tex/pdf/docx; code: py default, Stata option
```

FIND-LIT remains **after design confirm** and **before any literature chapter write**, as in find-data-lit §6. It does not sit in the attach slot. Cleaning does not sit before confirm-design.

## 3.2 Rules

1. **Confirm-design first.** Bryce tools must not treat missing or draft `session.design` as locked.
2. **FIND-DATA still does not attach.** `dataAttached` still first for data.
3. **`clean_winsor` runs after attach**, on the session dataset, as a named `CleaningStep` (`cuts=(1,99)`, continuous only, pip `pywinsor2`). It does not attach, does not confirm design, and does not set PREWRITE-PAUSE flags.
4. **PREWRITE-PAUSE still owns** `table1Confirmed` and `specConfirmed`. **NORMS-BE** yaml **reads** those flags and hooks propose/write; it does not replace them and does not run a Claude skill runner.
5. **CK DiD propose stays on infer-design.** Title/question only → propose DiD + treated×period **before** ck attach. `design_gates.yaml` hooks propose; it does not unlock DiD from catalog.
6. **Fixtures never answer key.** classic-5 is not **EVAL-top5** and not gold. EVAL-top5 is an optional submodule only.
7. **Independence.** Checking lit cards does not set `dataAttached`. Cleaning does not confirm spec. Export does not skip pauses. Missing eval submodule is not a product failure.

## 3.3 What may happen before confirm-design

- Infer-design draft propose / edit
- Opening an attach panel in **candidates-only** mode (no FD plan as authoritative match)

What must not happen before confirm-design:

- Authoritative FIND-DATA / FIND-LIT / Bryce lit-review as a confirmed-design match
- pywinsor2 presented as having cleaned “the study dataset” when nothing is attached
- AER gates treated as passed (yaml missing or skipped is fail-closed, not a Claude-skill pass)
- Catalog → `allow_did` or catalog → locked spec
- `table1Confirmed` / `specConfirmed` / estimate / gold biblio paste / eval-farm gold bodies
- Catalog identity treated as **EVAL-top5** answer key

---
