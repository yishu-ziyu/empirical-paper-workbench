# 8. Acceptance criteria (DECIDE-6; verbatim)

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


G0 does not add tests. Later INF / DID / DC slices **must** implement and show these acceptance criteria. Text below is **verbatim** from Decide (via Firstmate). Do **not** evaluate by reading gold chapter bodies.

1. CK-class title only → engine proposes DiD with treated×period BEFORE any ck attach
2. Rename/remove fixture → still can propose; catalog id alone cannot open DiD
3. Level OLS title → proposes OLS; must not open DiD from catalog
4. Unconfirmed design cannot jump to gold/classic prefilled spec
5. After confirm → suggest matches design → attach → direction/pause continues

## 8.1 How later slices bind those bullets (not substitutes)

| # | Gate reading | Fail (unacceptable substitute) |
|---|---|---|
| 1 | Title/question only. Propose writes `design.method=did` plus a treated×period slot **before** any `ck1994` / `ck1994_long` attach, suggest-select, or `dataAttached`. | Wait for ck attach; catalog → `allow_did`; gold-body read; auto-confirm. |
| 2 | After the fixture is renamed or removed, title/question still proposes. Catalog id (`ck1994`, `ck1994_long`, `minimum-wage-employment`, …) alone cannot open DiD. | `catalog_identity_allows` / `allow_did_for(entry_id=…)` as the win path; propose requires the fixture file. |
| 3 | Level OLS title (schooling–wages, Barro growth, …) proposes `method=ols`. Catalog must not open DiD. | Catalog token flips DiD; OLS title emits `method=did`. |
| 4 | Missing or `status=draft` design cannot jump to gold / classic prefilled spec, gold chapter bodies, or locked `main_specification`. | Unconfirmed → gold-body read; classic prefill as success; `set_direction` from catalog. |
| 5 | After human confirm: suggest matches the **confirmed** design (candidates only, never answer key) → attach (`dataAttached`) → direction / prewrite pauses continue. | Suggest without confirm as authoritative match; skip attach; skip pauses; gold-body read. |

OLS remains the default when DiD is not allowed. Heterogeneity × no-interaction stays a hard block. Missing treated×period when `design.method=did` stays a DID-BE-spec hard block (§7.3).

---
