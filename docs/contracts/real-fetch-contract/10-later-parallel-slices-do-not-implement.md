# 9. Later parallel slices (do not implement in G0)

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


G0 owns **only** `docs/contracts/real-fetch-contract.md`.

| Slice | Owns | Must not write |
|---|---|---|
| **FD-BE-honesty** | `source_kind` on candidates; never fixture-as-found; never toy-as-found; `captain_local_real` / `source=captain-local-real` label; teaching-shelf projection; DATA-RIGOR copy tokens; n<200 demo-claim fail-closed (warning contract) | Attach implementation, catalog auto-select, `allow_did`, chapter bodies, FE chrome ownership, fetch HTTP clients, moving toys into `tests/` in G0, vendoring Desktop/经济学论文 files |
| **FD-BE-fetch-card** | Card / minwage zip resolve + session download or link+upload | Classic-5 CSV bytes, `/demos/card`, confirm-attach, DiD permission, WDI/Dataverse clients |
| **FD-BE-fetch-dataverse** | Dataverse file download into session when API allows; else URL | Fixture substitution, attach, teaching-shelf copy ownership |
| **FD-BE-fetch-wdi** | WDI public download into session when API allows; else URL | Barro as fetch, attach, Card zip client |
| **FD-FE-honesty** | Labels / grouping (discovered vs teaching-known vs **captain-local-real** vs upload). Sketch = draft only | Backend routes, Table1 / equation pause UI, auto-check attach, shipping flow-sketch |

Slices stay **write-set-disjoint**. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

FRED / IPUMS fetch, if later named, follow §4 and stay off this G0 write-set.

**FD-FE-honesty alignment (frozen):** optional chrome. Absence of the labels UI does not waive backend `source_kind` / never fixture-as-found / never toy-as-found / captain-local-real labeled as acquire.

Existing FD-BE-plan / FD-BE-candidates (DECIDE-7) keep plan + real-candidate shape. This contract **recuts** fixture presentation and adds fetch. **Do not merge** those implementation branches in G0.

---
