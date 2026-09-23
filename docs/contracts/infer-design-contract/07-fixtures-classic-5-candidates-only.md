# 6. Fixtures / classic-5 — candidates only

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


## 6.1 What catalog is after DECIDE-6

DECIDE-6 lock (verbatim): **Fixtures/catalog = candidates only, never answer key.**

`classic-5` remains the named built-in catalog for formal-path find/select (`docs/contracts/data-completion-contract.md` §3). Landed ranking tokens include `ck1994_long` (Card–Krueger minwage) and `barro1991_growth` (Barro growth), plus the other `fixtures/classic-5/catalog.json` ids. They are never an answer key, never a gold-body source, and never a DiD key.

After infer-design confirm, DC-BE-suggest **may list** those entries as **candidates matching the confirmed design** (method + topic / outcome / treatment slots, plus title/RQ text). Example: a confirmed DiD minwage design may list `ck1994_long`; a confirmed OLS growth design may list `barro1991_growth`.

## 6.2 How catalog must not be used

- Not auto-selected
- Not prefilled as success / as the user’s own study
- Not `dataAttached` by mere suggest or highlight
- Not a locked spec (`catalog → session.design.confirmed`)
- Not a DiD key (`catalog → allow_did`)
- Not a gold-body / six-chapter fill
- Not Card 1995 (`/demos/card`) and not `teaching_case=card_1995`
- Not committed private / restricted microdata

Suggest **must not** attach. Attach **must not** invent ranking. Selecting a candidate **must not** set `dataAttached` or confirm a design.

`session.design.catalog_entry_id` stays `null`. Provenance after a later confirm-attach may record `source: "classic-5"` + entry id on the **dataset**, not as the design lock.

---
