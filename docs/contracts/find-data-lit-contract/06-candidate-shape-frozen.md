# 5. Candidate shape (frozen)

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


A **real candidate** is an object with **all** of:

| Field | Type | Meaning |
|---|---|---|
| `source_id` | string | Stable id. Examples: `classic-5:ck1994_long`, `dataverse:doi:10.7910/DVN/…`, `fred:UNRATE`, `wdi:NY.GDP.PCAP.KD.ZG`, `ipums:cps`, `card-zip:njmin`, `wage1`. |
| `title` | string | Human title of the dataset / extract. |
| `url_or_fixture` | string | Followable URL **or** in-repo fixture path. Empty / id-only **fails** the real-candidate test. |
| `license` | string | Declared license or access class (`CC0`, `public`, `registration-required`, …). Unknown → say `unknown`; do not invent CC0. |
| `suggested_cols` | string[] | Columns that bind to confirmed Y / X / DiD slots when known; empty allowed. |
| `design_fit` | object | Why this candidate matches the **confirmed** design (`method`, outcome, treatment, short note). |

```json
{
  "source_id": "classic-5:ck1994_long",
  "title": "Card and Krueger minimum wage",
  "url_or_fixture": "fixtures/classic-5/ck1994_long.csv",
  "license": "public-reproduction",
  "suggested_cols": ["employment", "treated", "period"],
  "design_fit": {
    "method": "did",
    "outcome": "employment",
    "treatment": "min_wage",
    "notes": "matches confirmed minwage DiD; candidate only"
  }
}
```

A second minwage candidate **without** that fixture id still required when the id is missing:

```json
{
  "source_id": "card-zip:njmin",
  "title": "Card–Krueger NJ–PA fast-food data (author zip)",
  "url_or_fixture": "https://davidcard.berkeley.edu/data_sets.html",
  "license": "author-posted",
  "suggested_cols": [],
  "design_fit": {
    "method": "did",
    "outcome": "employment",
    "treatment": "min_wage",
    "notes": "external path; fixture id absent"
  }
}
```

(Exact author URL may resolve to the current Card data-sets page. G0 freezes the **role**, not a byte hash.)

## 5.1 Real vs not real

| Object | Real candidate? |
|---|---|
| Full §5 object with URL or fixture path | Yes |
| classic-5 id string (`ck1994_long`) with no `url_or_fixture` | **No** |
| Catalog highlight / chip with only `entry_id` | **No** |
| Dataverse hit with dataset URL | Yes |
| IPUMS / FRED / WDI / Card zip landing URL | Yes |
| “use your own file” action | Allowed extra action; does not replace the ≥1 real candidate |

Fixture **may** appear as a candidate. Absence of that fixture id **must not** empty the list: show the R-sources external path (Dataverse etc.).

---
