# 5. Order vs infer-design, FIND-DATA, DATA-COMPLETE

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


## 5.1 Intended sequence (frozen)

DECIDE-6 / DECIDE-7 spine, with DECIDE-10 honesty:

```
title → propose → confirm → real fetch (discovered first) OR captain-local-real acquire → optional teaching shelf → attach → prewrite
```

Mapped onto named gates:

```
title/question
    → design propose                         ⇒  session.design status=draft       (infer-design)
    → human confirm                          ⇒  session.design status=confirmed
    → find-data plan (where/how)             ⇒  session.find_data.plan            (DECIDE-7 FD)
    → real fetch / discovered candidates     ⇒  source_kind discovered|fetched|external_link
       OR captain-local-real acquire         ⇒  source_kind captain_local_real
                                                (source=captain-local-real; not a find)
    → optional teaching shelf                ⇒  source_kind teaching_fixture (labeled; not find success)
    → attach                                 ⇒  dataAttached                      (data-completion)
    → prewrite pauses                        table1Confirmed then specConfirmed
```

FIND-LIT stays after confirm and before literature chapter write (`docs/contracts/find-data-lit-contract.md` §6). This file does not move it.

## 5.2 Rules

1. **Confirm-design first.** No authoritative plan, fetch, or “found” list against missing or draft `session.design`.
2. **Real fetch / captain-local-real before teaching shelf.** FIND results are discovered / fetched / external_link. Captain-local-real is a **parallel acquire**, labeled, not mixed into discovered copy. The shelf is secondary and labeled.
3. **FIND / fetch / captain-local-real does not attach.** `dataAttached` still first for data.
4. **PREWRITE-PAUSE still owns** `table1Confirmed` and `specConfirmed`.
5. **CK DiD propose stays on infer-design.** Title/question only → propose DiD + treated×period **before** any ck attach (`docs/contracts/infer-design-contract.md` §8 bullet 1). This file may fetch Card zip / Dataverse **after** that confirm. It must not propose DiD from a fixture or from a successful fetch.
6. **Fixtures ≠ answer key** (DECIDE-6 / DECIDE-7, unchanged). DECIDE-10 adds: fixtures ≠ found data. DATA-RIGOR adds: **toys ≠ found data** and **toys ≠ product demo**.
7. **Independence.** A session fetch path does not confirm a design. Checking lit cards does not fetch data. A catalog highlight does neither.
8. **Prefer live public fetch OR captain-local-real upload OR honest link+upload** (§4.0). Guide-sample / spike / CFPS synthetic buttons are not that upload path. Captain-local-real does not waive the FIND plan or the external path; Research scouts continue.

## 5.3 What may happen before confirm-design

- Infer-design draft propose / edit
- Opening an attach panel in **candidates-only** mode (no FD plan as authoritative match, no “we found”)

What must not happen before confirm-design:

- Authoritative fetch / “discovered” ranking
- Fixture-as-found or toy-as-found or toy-as-captain-local-real
- Catalog → `allow_did` or catalog → locked spec
- `table1Confirmed` / `specConfirmed` / estimate

---
