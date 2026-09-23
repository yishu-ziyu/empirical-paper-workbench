# 6. Order vs infer-design, DATA-COMPLETE, PREWRITE-PAUSE

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


## 6.1 Intended sequence (frozen)

DECIDE-7 order (verbatim relative to infer-design):

```
title → propose → confirm → find-data plan + candidates → attach → prewrite
```

Mapped onto named gates already in this product line:

```
title/question
    → design propose                         ⇒  session.design status=draft     (infer-design)
    → human confirm                          ⇒  session.design status=confirmed
    → find-data plan + candidates            ⇒  session.find_data (FD + R-sources)
    → attach                                 ⇒  dataAttached                    (data-completion)
    → prewrite pauses                        table1Confirmed then specConfirmed
```

FIND-LIT (**FL** + **R-lit-bar**) is **after design confirm** and **before any literature chapter write**. It does **not** skip attach, PREWRITE-PAUSE, or estimate. It does **not** sit in the attach slot.

```
confirm-design
    → FL search (OpenAlex + Crossref + S2) + DOI dedupe
    → ≥5 checkbox cards
    → user checks → refs.bib or CSL-JSON
    → (only then) write checked entries into chapters
```

Estimate / robustness may still run before chapter write (existing paper-engine order). R-lit-bar forbids writing literature chapters from generate-as-lit even if estimate already ran.

## 6.2 Rules

1. **Confirm-design first.** FD must not emit an authoritative plan against missing or draft `session.design`.
2. **FIND-DATA does not attach.** `dataAttached` still first for data (`docs/contracts/data-completion-contract.md`).
3. **PREWRITE-PAUSE still owns** `table1Confirmed` and `specConfirmed`. FIND-DATA / FIND-LIT do not set them.
4. **CK DiD propose stays on infer-design.** Title/question only → propose DiD + treated×period **before** any ck attach (infer-design §8 bullet 1). This file lists ck / Card zip **after** that confirm, as candidates.
5. **Fixtures never answer key.** Suggest / FIND list is not success, not gold, not auto-attach.
6. **Independence.** `dataAttached` does not complete FIND-LIT. Checking lit cards does not set `dataAttached`. A catalog highlight does not do either.

## 6.3 What may happen before confirm-design

- Infer-design draft propose / edit
- Opening an attach panel in **candidates-only** mode (no FD plan as authoritative match)

What must not happen before confirm-design:

- FD plan that claims a confirmed-design match
- Catalog → `allow_did` or catalog → locked spec
- R-lit-bar chapter write
- `table1Confirmed` / `specConfirmed` / estimate / gold biblio paste

---
