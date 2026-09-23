# 5. Order vs DATA-COMPLETE and PREWRITE-PAUSE

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


## 5.1 Intended sequence (frozen)

DECIDE-6 order (verbatim):

```
title/question → design propose (Y/X/interactions/method) → human confirm → data candidates → attach → prewrite pauses
```

Mapped onto named gates already in this product line:

```
title/question
    → design propose (Y/X/interactions/method)  ⇒  session.design status=draft
    → human confirm                             ⇒  session.design status=confirmed (locked)
    → data candidates                           (DC-BE-suggest; fixtures = candidates, never answer key)
    → attach                                    ⇒  dataAttached
    → prewrite pauses                           table1Confirmed then specConfirmed
                                                (DID-BE-spec: method=did ⇒ interaction required;
                                                 het interaction hard-block still)
```

Propose → confirm happens **before** DATA-COMPLETE and PREWRITE-PAUSE treat the design as authoritative. No gold body reads on this path.

## 5.2 Rules

1. **Confirm-design first for design authority.** Suggest, DID permission, Table 1, spec confirm, and estimate must not treat a missing or draft design as locked `session.design`.
2. **`dataAttached` still first for data.** Confirm-design does not attach. Table 1 / spec / estimate still require `dataAttached` (`docs/contracts/data-completion-contract.md` §2 / §2a).
3. **PREWRITE-PAUSE still owns `table1Confirmed` and `specConfirmed`.** Infer-design does not implement those flags. Those flags must not become true against a missing or draft design, and must not become true for `method=did` when the interaction is missing (DID-BE-spec).
4. **Fail closed on crossed flags.** If `table1Confirmed` / `specConfirmed` / estimate are requested without a confirmed design, return to infer-design confirm. If they are requested without `dataAttached`, return to confirm-attach. Do not invent the missing gate.
5. **Independence.** `dataAttached` does not confirm a design. Confirming a design does not set `dataAttached`. A catalog highlight does not do either.

## 5.3 What may happen before confirm-design

- Shaping or pinning the title / RQ
- Emitting and editing a **draft**
- Opening an attach panel in a **candidates-only** mode (no ranked-as-authoritative match, no auto-select, no `dataAttached`)

What must not happen before confirm-design:

- DC suggest that claims a confirmed-design match or auto-selects a fixture
- Catalog → `allow_did` or catalog → locked spec
- `table1Confirmed` / `specConfirmed` / estimate / chapter write

---
