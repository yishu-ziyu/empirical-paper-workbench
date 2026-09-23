# 4. Confirm flow

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


## 4.1 Named transition (frozen)

**Confirm-design** is the only transition that locks `session.design`.

`session.design.status` becomes `confirmed` iff the user confirmed the current draft (or an edited draft) on the formal path.

| State | `session.design` | Downstream treats design as locked? |
|---|---|---|
| Nothing proposed | missing | No |
| Draft only | `status=draft` | No |
| User edited the draft, not confirmed | still `draft` | No |
| Confirm-design succeeded | `status=confirmed`, `confirmed=true`, `confirmed_at` set | Yes |

## 4.2 Must (confirm)

- Require an existing draft. Confirm with no draft fails closed.
- Lock the fields on the confirmed object (`method`, outcome / treatment / controls, DiD/HET slots, `interactions`).
- Stamp `confirmed_at`.
- Keep `catalog_entry_id` null. Confirming a design does **not** pick a fixture.
- After confirm, DATA-COMPLETE suggest / DID permission / estimate admission may proceed **under this contract’s rules**. They still owe their own gates (`dataAttached`, Table 1, spec confirm, DID-BE-spec interaction).

## 4.3 Must not (confirm)

- Attach data or set `dataAttached`
- Auto-select or confirm-attach `ck1994` / `barro1991` / any catalog entry
- Set `allow_did` from a catalog token
- Set `table1Confirmed` / `specConfirmed`
- Write chapter bodies or run estimate
- Skip DID-BE-spec: confirmed `method=did` **without** a treated×period term still **hard-blocks** spec confirm and estimate

Confirm-design is **not** confirm-attach and **not** spec confirm.

## 4.4 Who may consume the locked design

Only after `status=confirmed`:

| Consumer | Allowed use |
|---|---|
| DC-BE-suggest | Rank classic-5 **candidates** that match the confirmed design. Still candidates. |
| DID permission | Read `method` + `interactions` (see §7). Catalog id is irrelevant. |
| PREWRITE-PAUSE / `set_direction` | Project confirmed fields into direction / spec. Still requires `dataAttached` before Table 1 / spec / estimate. |
| Estimate / write / export | Only after `dataAttached` **and** PREWRITE-PAUSE **and** DID-BE-spec (if `method=did`). |

Without a confirmed design, those consumers fail closed or stay on candidates-only (§8).

---
