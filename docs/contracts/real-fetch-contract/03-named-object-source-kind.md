# 2. Named object — `source_kind`

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


## 2.1 Extends DECIDE-7 candidate shape (frozen)

DECIDE-7 (`docs/contracts/find-data-lit-contract.md` §5) still requires a **real candidate**: `source_id`, `title`, `url_or_fixture`, `license`, `suggested_cols`, `design_fit`. A classic-5 **id string alone is not** a real candidate.

DECIDE-10 **adds** a required provenance field on every FIND-DATA candidate:

| Field | Type | Meaning |
|---|---|---|
| `source_kind` | see §2.2 | How this row entered the list. Required. Missing / null **fails closed** (not a real candidate). |

Optional fetch projection (later slices may persist; G0 does not add OpenAPI):

| Field | Type | Meaning |
|---|---|---|
| `fetch.status` | `"into_session"` \| `"link_only"` \| `"not_applicable"` | Session download vs honest link vs teaching shelf |
| `fetch.session_path` | string \| `null` | Workspace-relative path after a successful download; `null` otherwise |
| `fetch.reason` | string | Why link-only / not fetched (login, no public file API, HTTP error, …) |

`teaching_fixture` **must** use `fetch.status = "not_applicable"`. A fixture path in the repo is **not** a session fetch.

G0 does not add these fields to snapshot, OpenAPI, or session state. Later slices may project them. Missing `source_kind` **is** dishonest. Fail closed.

## 2.2 Candidate `source_kind` values (frozen)

| `source_kind` | Meaning | May count as find success? |
|---|---|---|
| `discovered` | Live search / public catalog hit (Dataverse dataset, WDI series, FRED series, Card zip file located as a posted archive, …) | **Yes**, if it is still a §5 real candidate |
| `teaching_fixture` | In-repo classic-5 / named teaching extract | **Never** |
| `external_link` | Followable public landing URL when bytes cannot (yet) enter the session | Honest path; **not** “we found your data” copy; **not** a fixture |
| `fetched` | Bytes from a `discovered` or `external_link` venue **already written** into the session workspace | **Yes** (fetch succeeded). Still **not** `dataAttached` |
| `captain_local_real` | Captain-local **real** `.dta`/CSV panel uploaded via the first-class acquire path (§4.4). Projection: `source=captain-local-real` | **Never as FIND / discovered.** **Yes as acquire** (real panel entered the session). Still **not** `dataAttached` until confirm-attach |

Allowed additional kinds later slices may add **only** if they stay outside find-success copy:

| `source_kind` | Meaning | Find success? |
|---|---|---|
| `user_upload` | Generic honest “upload your own file” (not the named captain-local-real path) | No — fallback, not a find, not captain-local-real |

`source=captain-local-real` **is** `source_kind=captain_local_real`. Later slices must emit both or project one from the other. Do not use `user_upload` to hide a captain-local-real file, and do not use `captain_local_real` for toys / synthetics.

**Must not** invent kinds that launder a fixture or a toy (`builtin_match`, `recommended`, `classic_found`, catalog id as `discovered`, `course-panel` / `minimum_wage` / `sanitized_sample` as `discovered`, `fetched`, or `captain_local_real`).

## 2.3 Example objects (role freeze, not byte hashes)

Discovered Dataverse hit (may then fetch):

```json
{
  "source_id": "dataverse:doi:10.7910/DVN/EXAMPLE",
  "source_kind": "discovered",
  "title": "Example replication package",
  "url_or_fixture": "https://doi.org/10.7910/DVN/EXAMPLE",
  "license": "CC0",
  "suggested_cols": [],
  "design_fit": {
    "method": "did",
    "outcome": "employment",
    "treatment": "min_wage",
    "notes": "Dataverse search hit; not a fixture"
  },
  "fetch": {
    "status": "link_only",
    "session_path": null,
    "reason": "download not yet attempted"
  }
}
```

Teaching fixture (shelf only):

```json
{
  "source_id": "classic-5:ck1994_long",
  "source_kind": "teaching_fixture",
  "title": "Card and Krueger minimum wage",
  "url_or_fixture": "fixtures/classic-5/ck1994_long.csv",
  "license": "public-reproduction",
  "suggested_cols": ["employment", "treated", "period"],
  "design_fit": {
    "method": "did",
    "outcome": "employment",
    "treatment": "min_wage",
    "notes": "teaching-known extract; not a find result"
  },
  "fetch": {
    "status": "not_applicable",
    "session_path": null,
    "reason": "in-repo teaching extract"
  }
}
```

External link + honest upload (no public file API / login wall):

```json
{
  "source_id": "ipums:cps",
  "source_kind": "external_link",
  "title": "IPUMS CPS / USA extracts",
  "url_or_fixture": "https://cps.ipums.org/cps/",
  "license": "registration-required",
  "suggested_cols": [],
  "design_fit": {
    "method": "ols",
    "outcome": "wage",
    "treatment": "educ",
    "notes": "external path; user downloads then uploads"
  },
  "fetch": {
    "status": "link_only",
    "session_path": null,
    "reason": "registration-required; no anonymous file API"
  }
}
```

Captain-local-real acquire (interim; role freeze, not a filename from Desktop):

```json
{
  "source_id": "captain-local-real:upload",
  "source_kind": "captain_local_real",
  "source": "captain-local-real",
  "title": "Captain-local real panel",
  "url_or_fixture": "(session upload; .dta or CSV)",
  "license": "user-provided",
  "suggested_cols": [],
  "design_fit": {
    "method": "did",
    "outcome": "employment",
    "treatment": "min_wage",
    "notes": "captain-local-real acquire; not a find result; not a toy"
  },
  "fetch": {
    "status": "into_session",
    "session_path": "workspace/uploads/captain-local-real.dta",
    "reason": "captain-local-real upload"
  }
}
```

## 2.4 Must not live on these objects as a win path

Catalog id alone, `allow_did`, `dataAttached`, chapter bodies, gold-body hashes, unconfirmed `session.design`, a fixture or toy with `source_kind=discovered`, `fetched`, or `captain_local_real`.

---
