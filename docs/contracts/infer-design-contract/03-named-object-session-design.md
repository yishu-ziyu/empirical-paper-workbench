# 2. Named object — `session.design`

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


## 2.1 Named object (frozen)

Product object name: **`session.design`**.

This is the formal-path research-design record. It is **not** a catalog entry, **not** `dataAttached`, and **not** a chapter body.

Existing engine fields stay readable (`research_direction`, `main_specification`, `DirectionSpec` / `norm_method` in `agent/design/spec.py`). Later slices may **project** a confirmed `session.design` onto those fields. They must not treat an unconfirmed draft, a catalog id, or a form click as `set_direction` / locked spec.

G0 does not add the object to snapshot, OpenAPI, or session state. Later slices may project it. Missing / null / absent **is** unconfirmed. Fail closed.

## 2.2 Draft vs confirmed (frozen)

| `status` | Meaning | Downstream may treat as locked? |
|---|---|---|
| missing / null | No inference yet | No |
| `draft` | Engine proposal from title (+ optional RQ). User has not confirmed. | No |
| `confirmed` | User confirmed. This is `session.design` as used by later gates. | Yes |

| Flag | Meaning |
|---|---|
| `confirmed` | `true` iff `status === "confirmed"` |
| `proposed_at` | When the current draft was written |
| `confirmed_at` | When the user confirmed; `null` while draft / missing |

Re-propose after confirm writes a **new draft** and clears `confirmed` / `confirmed_at`. Downstream gates fall back to unconfirmed until the user confirms again. Confirm is the only transition that locks.

## 2.3 Field shape (frozen)

Normalize `method` with the existing `norm_method` map: display `OLS` / `DiD` / `IV` / `RD` / `SCM` → stored `ols` / `did` / `iv` / `rd` / `scm`. DiD aliases already in-repo (`difference-in-differences`, `diff-in-diff`, `difference_in_differences`) count as `did`.

```json
{
  "status": "draft",
  "confirmed": false,
  "proposed_at": "2026-09-15T12:00:00Z",
  "confirmed_at": null,
  "source": {
    "title": "最低工资对就业的影响",
    "question": ""
  },
  "method": "did",
  "outcome": "employment",
  "treatment": "min_wage",
  "controls": [],
  "group": "treated",
  "treated": "treated",
  "period": "post",
  "time_col": "",
  "id_col": "",
  "first_treat_col": "",
  "interactions": [
    {
      "kind": "did",
      "left": "treated",
      "right": "period",
      "term": "treated:period"
    }
  ],
  "qType": "causal",
  "heterogeneity_groups": [],
  "catalog_entry_id": null
}
```

| Field | Type | Required when | Meaning |
|---|---|---|---|
| `status` | `"draft"` \| `"confirmed"` | always once proposed | Draft vs locked |
| `confirmed` | bool | always once proposed | Must match `status` |
| `proposed_at` | ISO-8601 | once proposed | Draft timestamp |
| `confirmed_at` | ISO-8601 \| `null` | always once proposed | Confirm timestamp; null if draft |
| `source.title` | string | always | Session title / TITLE/TOPIC text used to propose |
| `source.question` | string | optional | User-supplied research-question text; empty if title-only |
| `method` | `ols` \| `did` \| `iv` \| `rd` \| `scm` | always once proposed | Same tokens as `DirectionSpec` / `ENGINE_METHODS` |
| `outcome` | string | preferred; empty allowed on draft | `dv` / `outcome` / `outcome_col` |
| `treatment` | string | preferred; empty allowed on draft | Treatment (form `iv` / `treatment` / `treatment_col` — **not** the IV instrument) |
| `controls` | string[] | optional | Same as `DirectionSpec.controls` |
| `group` / `treated` | string | `method=did` (draft may leave a named slot) | Treated / group indicator |
| `period` | string | `method=did` (draft may leave a named slot) | Post / period indicator |
| `time_col` / `id_col` / `first_treat_col` | string | optional | Existing DiD columns; **not** a substitute for the interaction |
| `interactions` | object[] | required before DiD or HET may pass their hard-blocks | See §2.4 |
| `qType` | `"average"` \| `"heterogeneity"` \| `"causal"` | optional; default from method | Same family as PREWRITE-PAUSE `qType` |
| `heterogeneity_groups` | string[] | when `qType=heterogeneity` | Existing `DirectionSpec.heterogeneity_groups` |
| `catalog_entry_id` | string \| `null` | must be `null` on propose/confirm | Catalog is not part of the locked design |

Method-specific extras already used in-repo stay optional on the object and are **not** confirm substitutes:

| `method` | Optional fields (existing) |
|---|---|
| `iv` | `endogenous`, `instruments` / `instrument` |
| `rd` | `running_var`, `cutoff` |
| `scm` | `unit_col`, `treated_unit`, `treatment_time` |
| any | `cluster`, `cluster_levels` |

**Must not** live on `session.design` as a win path: catalog id, `allow_did`, `dataAttached`, chapter bodies, gold-body hashes, fixture file paths.

## 2.4 Interaction terms (frozen)

`interactions[]` entries:

| Field | Type | Meaning |
|---|---|---|
| `kind` | `"did"` \| `"het"` | DiD 2×2 vs heterogeneity |
| `left` / `right` | string | Factors (e.g. `treated` / `period`, `educ` / `region`) |
| `term` | string | Canonical display: `treated:period`, `educ:region` |

**DiD main term** (`kind=did`) counts as present if any one of:

- Explicit interaction: `treated:period`, `treated * period`, `treat × post`, `treat#post`
- A single constructed dummy that **is** that interaction (`treat_post`, `did`, NJ×after, and the same 2×2 cell)

**Does not count** (still missing):

- Treated main effect alone, or period / post main effect alone
- `id_col` + `time_col` without the interaction
- `| entity + time` / TWFE absorb syntax as a substitute
- `first_treat_col`, staggered timing, Callaway–Sant'Anna, Goodman-Bacon
- Event-study lead/lag dummies without the 2×2 main term
- `method=did` with `y ~ treat` or pooled OLS

**HET term** (`kind=het`) stays the existing PREWRITE-PAUSE rule: `qType === heterogeneity` requires an interaction (`educ×region` / `educ:region` / `educ*region` or the groups named on the design). Infer-design does not own that hard-block; it must not weaken it.

G0 does not freeze column names to a catalog schema. Later slices bind whatever columns the session actually has (user file or a later confirm-attached candidate) to this shape.

---
