# 3. FD — design facets → Dataverse + fixture candidates

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


## 3.1 Design facets (frozen)

**FD** reads **only** a confirmed `session.design` (plus the title/RQ already stored on `session.design.source`). Facets used to search:

| Facet | From | Used for |
|---|---|---|
| `method` | confirmed `session.design.method` | Route + `design_fit` |
| `outcome` / `treatment` | confirmed Y / X slots | Query terms + `suggested_cols` |
| `controls` / DiD slots | confirmed controls, `treated`, `period`, interactions | Column suggestions |
| `qType` | confirmed | Do not weaken HET hard-block |
| `source.title` / `source.question` | infer-design source | Query text; **not** a confirm substitute |

Unconfirmed or missing design: FD **must not** rank as an authoritative match. Fail closed or stay silent. Infer-design §5.3 still holds: before confirm, the attach panel may open in **candidates-only** mode with **no** ranked-as-authoritative FIND-DATA plan.

## 3.2 What FD must do

After confirm:

1. Classify **R-sources** `route_family` from the confirmed facets (§4).
2. Emit a **find-data plan**: **where** (venue) and **how** (query / landing path).
3. Search **Dataverse** with those facets (Harvard Dataverse catalog search or equivalent public Dataverse API). Hits become candidates with URLs.
4. List matching **fixture** candidates from `classic-5` / named teaching extracts (**candidates only**, never answer key).
5. Return **≥1 real candidate** in the §5 shape. Not only a classic-5 id.

Dataverse is the **default external catalog** for `else` and the **always-on backup** when a named fixture id is missing.

## 3.3 What FD must not do

| Refusal | Frozen |
|---|---|
| Run before confirm-design | No authoritative plan; no “matched ck1994” as success. |
| Attach / ingest | Must not call upload, classic-5 attach, or stamp snapshot `dataset`. |
| `dataAttached` | Must not set true. FIND-DATA is pre-attach. |
| Catalog as answer key | Must not auto-select `ck1994` / `ck1994_long` / `barro1991_growth` / `schooling-wages` / any `classic-5` entry. |
| Classic-5 id as the only candidate | A candidate must have `url_or_fixture` (and the rest of §5). An id token is not enough. |
| DiD from catalog | Must not set `allow_did` or propose `method=did`. Defer to infer-design. |
| Gold / chapter bodies | Must not write chapter text, gold-body fixtures, or six-chapter fill. |
| Restricted microdata commit | Must not vendor IPUMS extracts, CHARLS, or other restricted files into the repo. External path only. |

---
