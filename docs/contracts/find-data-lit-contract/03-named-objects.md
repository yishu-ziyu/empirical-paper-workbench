# 2. Named objects

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


## 2.1 `session.find_data` (frozen)

Product object name: **`session.find_data`**.

This is the formal-path FIND-DATA record emitted **after** design confirm. It is **not** a catalog entry, **not** `dataAttached`, and **not** `session.design`.

G0 does not add the object to snapshot, OpenAPI, or session state. Later slices may project it. Missing / null / absent **is** “no FIND-DATA yet.” Fail closed: do not treat a classic-5 id highlight as a plan.

## 2.2 Plan vs candidates (frozen)

| Field | Meaning | Downstream may treat as attached? |
|---|---|---|
| `plan` | Where / how to look, derived from confirmed design facets + **R-sources** | No |
| `candidates[]` | Real candidate objects (§5). Fixtures may appear. | No — still candidates |
| `status` | `missing` / `planned` | No |

| Flag | Meaning |
|---|---|
| `planned_at` | When the current plan + candidate list was written |
| `route_family` | R-sources family: `educ_wage` / `minwage` / `growth` / `macro` / `else` |
| `primary_venue` | Where the plan sends the user first (Dataverse, IPUMS, FRED, WDI, fixture+Card zip, …) |

Selecting a candidate still requires DATA-COMPLETE confirm-attach. FIND-DATA never sets `dataAttached`.

## 2.3 `session.find_lit` (frozen)

Product object name: **`session.find_lit`**.

This is the formal-path FIND-LIT record. It is **not** `literature_entries` filled by generate-as-lit, **not** a gold biblio, and **not** a chapter body.

| Field | Meaning |
|---|---|
| `hits[]` | Deduped FL hits (OpenAlex + Crossref + S2) |
| `cards[]` | Checkbox cards shown to the user. V1 requires **≥5** before any chapter write |
| `checked_ids[]` | Cards the user checked |
| `export` | `refs.bib` and/or CSL-JSON built **only** from checked cards |
| `polite_pool` | mailto identity used in User-Agent (§8.5) |

G0 does not add the object. Missing / null / absent **is** “no FIND-LIT yet.” Chapter write of literature **fails closed**.

## 2.4 Must not live on these objects as a win path

Catalog id alone, `allow_did`, `dataAttached`, chapter bodies, gold-body hashes, gold biblio blobs, Elicit/知网/Consensus payloads, unconfirmed `session.design`.

---
