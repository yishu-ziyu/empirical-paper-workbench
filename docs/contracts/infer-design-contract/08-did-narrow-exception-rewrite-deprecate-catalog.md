# 7. DiD narrow-exception rewrite — deprecate catalog-token `allow_did`

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


## 7.1 What DECIDE-5 A froze, and what DECIDE-6 changes

`docs/contracts/did-narrow-exception-contract.md` (DECIDE-5 A) froze `allow_did` default false and allowed **only** a title/catalog gate (Card–Krueger / minwage TITLE/TOPIC or catalog identity `minimum-wage-employment` / `ck1994` / `ck1994_long`) to set true. Form `method=did` was **not** the setter.

**DECIDE-6 withdraws catalog identity (and catalog-token `allow_did`) as the source of truth.** Later DID-BE-gate slices must stop treating those tokens as a DiD unlock.

Unchanged from DECIDE-5 A (still frozen):

- Formal path stays OLS-locked **unless** this exception applies
- The exception is still **narrow 2×2 DiD**, not general TWFE / event-study / staggered / Callaway–Sant'Anna / Goodman-Bacon
- Card 1995 teaching case is **not** this exception
- `barro1991_growth` / schooling–wages / other classic-5 ids are **not** a DiD unlock
- When DiD is in play, treated×period (or equivalent) is required or **hard block**
- OLS lock elsewhere stays in `agent/engine/ols_lock.py` (issue #24); this file does not rewrite that module into a general TWFE unlock

## 7.2 New DiD permission (frozen)

DiD is allowed iff **all** of:

1. `session.design.status === "confirmed"`
2. Confirmed `design.method=did` (or an existing `norm_method` equivalent)
3. The confirmed design includes the required **treated×period** interaction (§2.4)

Otherwise DiD is not allowed. Fail closed.

| Input | DiD allowed? |
|---|---|
| Catalog `ck1994` / `ck1994_long` / `minimum-wage-employment` alone | No |
| Title/RQ matcher hit, design still draft | No |
| Confirmed `method=ols` (even if a minwage CSV is later attached) | No |
| Confirmed `method=did` **without** treated×period | No — **hard block** (DID-BE-spec) |
| Confirmed `method=did` **with** treated×period; catalog none / `barro1991_growth` / user file | Yes (narrow 2×2 only), still needs `dataAttached` + PREWRITE-PAUSE |
| Form / `research_direction.method=did` while design unconfirmed | No |
| `id_col` + `time_col` / `| entity + time` without confirmed DiD + interaction | No |

`allow_did` as a **derived projection** of the three conditions above is optional for later slices. Catalog-token `allow_did` (`catalog_identity_allows`, `MINWAGE_ENTRY_IDS`, `entry.allow_did` in `catalog.json`) is **deprecated** and must not be the setter.

## 7.3 Hard block — DID-BE-spec (unchanged duty, new trigger)

If confirmed `method=did` (or equivalent) and the spec / design has no treated×period (or equivalent) main term:

| Surface | Frozen refusal |
|---|---|
| Spec confirm (`specConfirmed`) | Must not become true. Return to equation / 题型→设定. |
| `POST /sessions/{id}/direction` that would run estimate | Refuse. Do not start estimate. |
| Estimate / `mainResults` | Do not run. Do not invent a coefficient. |
| Generate-chapter / six-chapter write | Do not write as if DiD ran. |
| Code export | Do not emit feols / xtreg / reghdfe / TWFE for this session. |

Fail closed. Same family as heterogeneity × no-interaction. Missing required interaction **blocks**; it does not degrade to silent OLS or silent TWFE.

DID-BE-spec owns the check. Trigger = **confirmed DiD design**, not catalog `allow_did`. G0 does not add the error code.

## 7.4 When DiD is not allowed

OLS lock holds. Direction, estimate, prompts, generate-chapter, and export stay on OLS / regress / lm. They must not inject or claim 双向固定效应 / TWFE / feols / xtreg / reghdfe / felm.

A user who typed DiD on the form, attached `ck1994_long`, or has a panel CSV, still does not get TWFE without a **confirmed** DiD design **and** the interaction.

IV / RD / SCM stay on their existing non-OLS paths. This file does not reopen them.

---
