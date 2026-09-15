# Real-fetch contract (after design confirm; DECIDE-10)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-REAL-FETCH-1` · slice **G0** (DECIDE-10)  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `feat/fm-e-build-did-spec-recut-1` @ `bf6957150713d9d8ff3ae72379d4233e5bd9b253`  
Design input: **DECIDE-10** acceptance from Decide (via Firstmate / Captain) — **real fetch first**; find-data must not present fixtures as discovered / found data; fixtures = **teaching-known only**, never find success; optional teaching shelf with explicit label; prefer actual download into session when the API allows  
Sister contracts (cited, not merged): `docs/find-data-lit-contract.md` (`FM-E-BUILD-FIND-DATA-LIT` FD-G0 / DECIDE-7), `docs/infer-design-contract.md` (`FM-E-BUILD-INFER-DESIGN-1` INF-G0 / DECIDE-6), `docs/data-completion-contract.md` (`FM-E-BUILD-DATA-COMPLETE-1` G0), `docs/did-narrow-exception-contract.md` (`FM-E-BUILD-DID-NARROW-1` G0)  
Authority: this file freezes the DECIDE-10 **order**, **locks**, **`source_kind`**, and **slice accept bullets** below. Later slices implement against it. G0 adds **this markdown only**.

This is not an ADR. It is the serial write-set freeze so FD-BE-honesty / FD-BE-fetch-\* / FD-FE-honesty can run without colliding with infer-design confirm, FIND-DATA plan authorship, FIND-LIT / R-lit-bar, DATA-COMPLETE attach, PREWRITE-PAUSE flags, classic-5 CSV authorship, or gold chapter bodies. Acceptance is the DECIDE-10 bullets in §8 — **not** gold-body reads and **not** fixture-as-found.

---

## 0. Product-line lock — DECIDE-10

**DECIDE-10 (frozen; Decide via Firstmate / Captain).** Encode the following **verbatim**:

**Real fetch first.** find-data must not present fixtures as discovered/found data.

**Locks:**

- Fixtures = **teaching-known only**, never find success. Optional teaching shelf with explicit label.
- Prefer actual download into session when API allows: Dataverse, Card zip, WDI (and FRED/IPUMS per existing routes).
- Else: show link + honest upload path.
- Align with infer-design + find-data-lit contracts; fixtures ≠ answer key.

**Order after design confirm:** confirmed `session.design` → **real fetch / discovered candidates first** → optional teaching shelf (`teaching_fixture`, labeled) → attach → prewrite.

Product-object names in this file: `session.find_data.candidates[]` with required **`source_kind`**, plus optional **`session.find_data.teaching_shelf`**. They are **not** `session.design`, **not** `dataAttached`, and **not** chapter bodies. Later slices must not evaluate by reading gold chapter bodies or treating a classic-5 id as a find.

In scope: the formal econpaper paper path **after** infer-design confirm — the same product line as `docs/find-data-lit-contract.md` and `docs/infer-design-contract.md`. This contract **recuts FIND-DATA honesty and fetch**. It does **not** reopen FIND-LIT / R-lit-bar.

Out of product line for this contract (do not extend, re-label, or treat as FIND / fetch success):

- Card teaching case (`POST /demos/card`, `research.teaching_case=card_1995`, ADR-0015)
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`)
- CHARLS wizard, CFPS fixture, spike CSVs, eval datasets (including `agent/eval/tasks/undergrad_did_01`)
- Agent spike (`/spike`), first-value marketing review, **flow-sketch / draft-product chrome as shipped UI**
- Sketch-only sample names (`sample_wage.csv`, `sample_panel_mini.csv`, `wage_panel.csv`)
- Catalog identity alone (`ck1994`, `ck1994_long`, `minimum-wage-employment`, `barro1991_growth`, `schooling-wages`, …) presented as **discovered / found**
- Unconfirmed `session.design` (`missing` / `draft`)
- Gold-body reads, six-chapter fill from catalog, generate-as-lit

`session.design` (infer-design), `session.find_data` plan (FIND-DATA / DECIDE-7), `dataAttached` (data-completion), and `table1Confirmed` / `specConfirmed` (PREWRITE-PAUSE) are **different** gates. This contract does not propose or confirm a design, does not replace the where/how plan, does not skip confirm-attach, and does not replace those flags. It **does** freeze that fixtures are never “found data”, and that fetch prefers session download when the public API allows.

DiD permission stays in `docs/infer-design-contract.md` §7. FIND-LIT / R-lit-bar stay in `docs/find-data-lit-contract.md` §7–§8. This file must not reopen catalog-token `allow_did`, must not propose DiD from a fixture id, and must not contradict title-first CK propose.

---

## 1. Purpose and non-goals

### 1.1 Purpose (frozen)

Given a formal-path session whose **`session.design.status === "confirmed"`**, this flow only:

1. **Real fetch first** — Searches / fetches **external** sources for the confirmed design (FD + R-sources venues). Hits that come from a live catalog or public download are `source_kind = discovered` (or `external_link` when only a URL can be shown).
2. **Never fixture-as-found** — In-repo classic-5 / teaching extracts must **not** be labeled, ordered, or copied as discovered / found / matched-your-study data.
3. **Teaching-known only** — Those extracts may appear **only** as `source_kind = teaching_fixture`, on an **optional teaching shelf** with an **explicit** label. Their presence is **not** find success.
4. **Download into session when the API allows** — For Dataverse, Card zip, WDI, and FRED/IPUMS per existing R-sources routes: if a public API or posted file can be retrieved, write bytes into the **session workspace** (staging). That is **fetch**, not attach.
5. **Else honest path** — If download is not allowed, fails, or needs login / registration, show a followable **link** plus an **honest upload** path. Do not pad with a fixture.

FIND-DATA still lists candidates; it never auto-selects, never confirm-attaches, never writes gold chapter bodies. Fetch-into-session does **not** set `dataAttached`.

### 1.2 Non-goals (frozen)

This contract does **not**:

- Propose or confirm `session.design` (INF-BE-propose / INF-BE-confirm)
- Own the FIND-DATA **where/how plan** (FD-BE-plan) or FIND-LIT / R-lit-bar
- Treat catalog → locked spec, catalog → `allow_did`, catalog → found dataset, or catalog → gold biblio as a win path
- Auto-succeed, auto-select, or prefill a fixture as the user’s study
- Attach a dataset or set `dataAttached` (download-into-session ≠ confirm-attach)
- Set PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Run estimate, robustness, `generate_title` / `state.title_chapter`, or export docx
- Vendor restricted microdata (IPUMS extracts, CHARLS, …) into the git repo
- Scrape behind login, store user credentials, or treat a teaching shelf as a find
- Ship Design FIND-1 / `econpaper-ui-temp/flow-sketch` as product chrome
- Merge DATA-COMPLETE / DID / INF / FIND-LIT / FIND-DATA implementation branches
- Implement application code, API routes, OpenAPI shapes, or frontend chrome (G0 is markdown only)

`TITLE/TOPIC` is already consumed by infer-design. Real-fetch reads the **confirmed** `session.design`, not the title as a substitute for confirm.

---

## 2. Named object — `source_kind`

### 2.1 Extends DECIDE-7 candidate shape (frozen)

DECIDE-7 (`docs/find-data-lit-contract.md` §5) still requires a **real candidate**: `source_id`, `title`, `url_or_fixture`, `license`, `suggested_cols`, `design_fit`. A classic-5 **id string alone is not** a real candidate.

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

### 2.2 Candidate `source_kind` values (frozen)

| `source_kind` | Meaning | May count as find success? |
|---|---|---|
| `discovered` | Live search / public catalog hit (Dataverse dataset, WDI series, FRED series, Card zip file located as a posted archive, …) | **Yes**, if it is still a §5 real candidate |
| `teaching_fixture` | In-repo classic-5 / named teaching extract | **Never** |
| `external_link` | Followable public landing URL when bytes cannot (yet) enter the session | Honest path; **not** “we found your data” copy; **not** a fixture |
| `fetched` | Bytes from a `discovered` or `external_link` venue **already written** into the session workspace | **Yes** (fetch succeeded). Still **not** `dataAttached` |

Allowed additional kinds later slices may add **only** if they stay outside find-success copy:

| `source_kind` | Meaning | Find success? |
|---|---|---|
| `user_upload` | Honest “upload your own file” action, not a catalog hit | No — it is the fallback path, not a find |

**Must not** invent kinds that launder a fixture (`builtin_match`, `recommended`, `classic_found`, catalog id as `discovered`).

### 2.3 Example objects (role freeze, not byte hashes)

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

### 2.4 Must not live on these objects as a win path

Catalog id alone, `allow_did`, `dataAttached`, chapter bodies, gold-body hashes, unconfirmed `session.design`, a fixture with `source_kind=discovered` or `source_kind=fetched`.

---

## 3. Honesty — fixtures are teaching-known only

### 3.1 Never fixture-as-found (frozen)

FIND-DATA **must not** present a fixture as discovered / found data. Frozen refusals:

| Surface | Forbidden |
|---|---|
| `source_kind` | `teaching_fixture` emitted as `discovered` or `fetched` |
| Ordering | Fixture listed in the **discovered / fetch** list as if it were a search hit |
| Copy | “找到了数据”, “discovered dataset”, “matched your study”, “recommended data”, “we found ck1994” on a fixture |
| Padding | Empty or failed real fetch filled with classic-5 so the list is non-empty |
| Success | Treating a teaching shelf row as FIND success, attach success, or DiD unlock |

DECIDE-7 still allows a fixture to **appear** as a candidate. DECIDE-10 **narrows how**: only as `teaching_fixture`, never as find success, never unlabeled next to Dataverse hits.

### 3.2 Optional teaching shelf (frozen)

`session.find_data.teaching_shelf` (name frozen) is **optional**.

| Rule | Frozen |
|---|---|
| Contents | Zero or more `source_kind=teaching_fixture` real candidates |
| Label | **Explicit**. Product copy must say this is a **teaching-known** extract / 教学已知样本, **not** a find result |
| Absence | Missing shelf is fine. FIND does not fail because no fixture exists |
| Presence | Does **not** satisfy “≥1 real candidate” as a **find**. The ≥1 real candidate owed after confirm must still be `discovered`, `fetched`, or `external_link` (DECIDE-7 §9 bullet 1, recut by honesty) |
| Separation | Shelf is a distinct list / region. Do not interleave unlabeled with discovered cards |

Rename or remove `ck1994_long` / `barro1991_growth` / wage1: the shelf may empty. Real fetch / external path **must** still show (same as DECIDE-7 bullet 2).

### 3.3 Copy rules (FD-BE-honesty; frozen)

| `source_kind` | Allowed copy family | Forbidden copy family |
|---|---|---|
| `discovered` / `fetched` | “检索到 / Dataverse 命中 / 已下载到本会话” | Calling it a teaching sample as the primary label |
| `teaching_fixture` | “教学已知样本 / teaching-known extract — not a find result” | found / discovered / matched / recommended / 为你找到 |
| `external_link` | “公开链接；请下载后上传” / link + honest upload | found dataset; silent fixture substitution |
| `user_upload` | “上传你自己的文件” | presented as a search hit |

Chinese and English surfaces obey the same distinctions. A translation that calls a fixture 发现 / 检索结果 **fails** FD-BE-honesty.

---

## 4. Fetch policy — download vs link + upload

### 4.1 Prefer session download (frozen)

When a **public** API or posted file allows anonymous retrieval, later fetch slices **must** try to write bytes into the **session workspace** (staging under the session run dir). Preferred venues:

| Venue | R-sources family (DECIDE-7 §4) | G0 named slice |
|---|---|---|
| **Dataverse** | `else` primary; **always-on backup** for every family | **FD-BE-fetch-dataverse** |
| **Card zip** | `minwage` (author-posted NJ–PA archive) | **FD-BE-fetch-card** |
| **WDI** | `growth` (World Bank World Development Indicators) | **FD-BE-fetch-wdi** |
| **FRED** | `macro` (existing route) | no extra G0 slice; same prefer-download rule |
| **IPUMS** | `educ_wage` (existing route) | no extra G0 slice; same prefer-download rule |

**Card zip** is the Card–Krueger author-posted reproduction archive. It is **not** `/demos/card` and **not** `allow_did`.

Success: candidate may move to `source_kind=fetched` with `fetch.status=into_session` and a session path. The user still **confirm-attaches** (DATA-COMPLETE) before `dataAttached`.

### 4.2 Else: link + honest upload (frozen)

If any of the following hold, **do not** invent a fixture find:

- No public file API
- Registration / login / ToS wall (typical for IPUMS extracts)
- HTTP / parse / license refusal
- Ambiguous HTML landing page with no resolvable file

Then: `source_kind=external_link` (or keep `discovered` with `fetch.status=link_only` when the row is a live catalog hit), show the **URL**, and offer **upload your own file**. Copy must say the product did **not** ingest that file.

### 4.3 Fetch must not (frozen)

| Refusal | Frozen |
|---|---|
| Set `dataAttached` | Fetch is pre-attach staging. |
| Confirm-attach | User still confirms. |
| Treat fixture bytes as a fetch | Copying `fixtures/classic-5/*.csv` into the session is **not** real fetch and **not** `source_kind=fetched`. |
| Vendor restricted files into git | IPUMS / CHARLS / licensed microdata stay out of the repo. Session staging is per-session, not a catalog commit. |
| Scrape behind login | No password, cookie, or token harvest. |
| Skip confirm-design | No authoritative fetch against missing / draft design. |
| Unlock DiD | Catalog / Card zip / Dataverse fetch does not set `allow_did`. |

---

## 5. Order vs infer-design, FIND-DATA, DATA-COMPLETE

### 5.1 Intended sequence (frozen)

DECIDE-6 / DECIDE-7 spine, with DECIDE-10 honesty:

```
title → propose → confirm → real fetch (discovered first) → optional teaching shelf → attach → prewrite
```

Mapped onto named gates:

```
title/question
    → design propose                         ⇒  session.design status=draft       (infer-design)
    → human confirm                          ⇒  session.design status=confirmed
    → find-data plan (where/how)             ⇒  session.find_data.plan            (DECIDE-7 FD)
    → real fetch / discovered candidates     ⇒  source_kind discovered|fetched|external_link
    → optional teaching shelf                ⇒  source_kind teaching_fixture (labeled; not find success)
    → attach                                 ⇒  dataAttached                      (data-completion)
    → prewrite pauses                        table1Confirmed then specConfirmed
```

FIND-LIT stays after confirm and before literature chapter write (`docs/find-data-lit-contract.md` §6). This file does not move it.

### 5.2 Rules

1. **Confirm-design first.** No authoritative plan, fetch, or “found” list against missing or draft `session.design`.
2. **Real fetch before teaching shelf.** UI and API lists that the user sees as FIND results are discovered / fetched / external_link first. The shelf is secondary and labeled.
3. **FIND / fetch does not attach.** `dataAttached` still first for data.
4. **PREWRITE-PAUSE still owns** `table1Confirmed` and `specConfirmed`.
5. **CK DiD propose stays on infer-design.** Title/question only → propose DiD + treated×period **before** any ck attach (`docs/infer-design-contract.md` §8 bullet 1). This file may fetch Card zip / Dataverse **after** that confirm. It must not propose DiD from a fixture or from a successful fetch.
6. **Fixtures ≠ answer key** (DECIDE-6 / DECIDE-7, unchanged). DECIDE-10 adds: fixtures ≠ found data.
7. **Independence.** A session fetch path does not confirm a design. Checking lit cards does not fetch data. A catalog highlight does neither.

### 5.3 What may happen before confirm-design

- Infer-design draft propose / edit
- Opening an attach panel in **candidates-only** mode (no FD plan as authoritative match, no “we found”)

What must not happen before confirm-design:

- Authoritative fetch / “discovered” ranking
- Fixture-as-found
- Catalog → `allow_did` or catalog → locked spec
- `table1Confirmed` / `specConfirmed` / estimate

---

## 6. Venue notes (later fetch slices)

Exact URLs and API query strings are **implementation** (later slices). G0 freezes **roles**.

| Slice / route | Must | Must not |
|---|---|---|
| **FD-BE-fetch-card** | After confirmed minwage (or equivalent R-sources `minwage`) design, resolve the author-posted Card–Krueger zip and **download into session** when the posted file is retrievable; else link + honest upload | Use `/demos/card`; copy classic-5 CSV as the zip; set `dataAttached`; call it a find of `ck1994` |
| **FD-BE-fetch-dataverse** | Search Dataverse from confirmed facets; **download** a chosen public file into session when the Dataverse API allows; else dataset URL + upload | Treat Dataverse landing HTML as a fetched table; substitute classic-5 on search miss |
| **FD-BE-fetch-wdi** | For `growth`, pull WDI (World Bank indicators API or equivalent public download) into session when allowed; else WDI page + upload | Treat `barro1991_growth` as the WDI fetch |
| **FRED / IPUMS** | Same prefer-download-else-link rule on existing R-sources families (`macro` / `educ_wage`) | Commit IPUMS extracts to git; scrape FRED behind a key if the product has no configured public path — then link + upload |

Dataverse remains the **always-on backup** when a named venue cannot fetch.

---

## 7. FD-FE-honesty — labels (draft sketch only)

**FD-FE-honesty** owns UI labels / grouping so the user can see the §2–§3 distinctions.

**Design FIND-1** at `econpaper-ui-temp/flow-sketch` may be **consulted as a draft sketch only** (label intent: discovered vs teaching-known vs upload). It is **not** product chrome, **not** a second product line, and **not** an accept path. Later FE must not import sketch sample names, Card 1995 teaching-case layout, or treat the sketch as the formal FIND UI.

Absence of the FE chrome does **not** waive backend honesty (`source_kind` + never fixture-as-found).

---

## 8. Acceptance criteria (DECIDE-10; later slices)

G0 does not add tests. Later slices **must** implement and show these acceptance criteria. Do **not** evaluate by reading gold chapter bodies. Do **not** treat a fixture as found data.

**Locks (must remain true on every named slice):** real fetch first; fixtures = teaching-known only, never find success; optional teaching shelf with explicit label; prefer session download when the API allows (Dataverse, Card zip, WDI, FRED/IPUMS per existing routes); else link + honest upload; fixtures ≠ answer key; CK title→propose DiD deferred to infer-design.

### 8.1 Named slice accept bullets

| Slice | Accept (gate reading) | Fail (unacceptable substitute) |
|---|---|---|
| **FD-BE-honesty** | Every FIND-DATA candidate has `source_kind`. Copy and list membership never present a fixture as discovered / found. Teaching extracts only as `teaching_fixture` (optional labeled shelf). Empty real fetch must not be padded with classic-5. | Fixture with `source_kind=discovered` / `fetched`; “找到了 ck1994”; id-only chip as the find; gold-body read; auto-attach. |
| **FD-BE-fetch-card** | Confirmed minwage design: attempt Card zip **download into session** when the posted archive is retrievable; else Card zip **link + honest upload**. Fixture is not the fetch. | `/demos/card`; copy `ck1994_long.csv` into session and call it the zip; skip confirm-design; set `dataAttached`; unlock DiD. |
| **FD-BE-fetch-dataverse** | Confirmed design: Dataverse search from facets; download a public file into session when the API allows; else dataset / search URL + honest upload. Search miss → Dataverse path still shown, **not** a fixture find. | Fixture as the Dataverse hit; hide Dataverse because a catalog id existed; attach without confirm. |
| **FD-BE-fetch-wdi** | Confirmed growth design: WDI download into session when the public API allows; else WDI link + honest upload. `barro1991_growth` stays teaching-known if shown. | Barro fixture as the WDI fetch; skip confirm; set `dataAttached`. |
| **FD-FE-honesty** | UI labels separate discovered / fetched / external_link / teaching shelf / upload. Teaching shelf explicitly **not** a find result. May use Design FIND-1 (`econpaper-ui-temp/flow-sketch`) as **draft sketch only**. | Sketch shipped as the formal UI; fixture cards with “found” copy; mixing unlabeled fixtures into the discovered list. |

OLS remains the default when DiD is not allowed (**infer-design**). Heterogeneity × no-interaction stays a hard block. Missing treated×period when `design.method=did` stays a DID-BE-spec hard block. FIND-LIT / R-lit-bar stay as DECIDE-7. This file does not change those rules.

DECIDE-7 extras still owed by FIND-DATA (not substitutes for the table above): where/how plan; ≥1 **non-fixture** real candidate after confirm (discovered / fetched / external_link); fixture **may** appear only as teaching-known; without that id still show the external path.

---

## 9. Later parallel slices (do not implement in G0)

G0 owns **only** `docs/real-fetch-contract.md`.

| Slice | Owns | Must not write |
|---|---|---|
| **FD-BE-honesty** | `source_kind` on candidates; never fixture-as-found; teaching-shelf projection; copy tokens | Attach / `dataAttached`, catalog auto-select, `allow_did`, chapter bodies, FE chrome ownership, fetch HTTP clients |
| **FD-BE-fetch-card** | Card / minwage zip resolve + session download or link+upload | Classic-5 CSV bytes, `/demos/card`, confirm-attach, DiD permission, WDI/Dataverse clients |
| **FD-BE-fetch-dataverse** | Dataverse file download into session when API allows; else URL | Fixture substitution, attach, teaching-shelf copy ownership |
| **FD-BE-fetch-wdi** | WDI public download into session when API allows; else URL | Barro as fetch, attach, Card zip client |
| **FD-FE-honesty** | Labels / grouping (discovered vs teaching-known vs upload). Sketch = draft only | Backend routes, Table1 / equation pause UI, auto-check attach, shipping flow-sketch |

Slices stay **write-set-disjoint**. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

FRED / IPUMS fetch, if later named, follow §4 and stay off this G0 write-set.

**FD-FE-honesty alignment (frozen):** optional chrome. Absence of the labels UI does not waive backend `source_kind` / never fixture-as-found.

Existing FD-BE-plan / FD-BE-candidates (DECIDE-7) keep plan + real-candidate shape. This contract **recuts** fixture presentation and adds fetch. **Do not merge** those implementation branches in G0.

---

## 10. Concurrent write-sets (stay out)

| External slice | Lives at | This contract must not touch |
|---|---|---|
| **INFER-DESIGN** | `docs/infer-design-contract.md`; `session.design`; INF-BE-propose / INF-BE-confirm | Propose/confirm ownership, DiD permission rewrite, catalog-token `allow_did` revival. **Cite and defer** on CK title→propose DiD. |
| **FIND-DATA / FIND-LIT (DECIDE-7)** | `docs/find-data-lit-contract.md`; FD-BE-plan; FL-BE-\*; R-lit-bar | Replacing the where/how plan; generate-as-lit revival; OpenAlex/Crossref/S2 ownership. Honesty **recuts** candidate presentation only. |
| **DATA-COMPLETE** | `docs/data-completion-contract.md`; `dataAttached`; DC-BE-attach / DC-FE-\* | Confirm-attach, upload readiness, attach-panel chrome. Fetch staging is **not** attach. **Do not merge** those branches in G0. |
| **PREWRITE-PAUSE** | `table1Confirmed` + `specConfirmed`; `blockingDecision`; `docs/api/prewrite-confirm.md` | Implementing those flags, freeze/reveal, estimate-prep UI |
| **DID-NARROW / DID-BE-\*** | `docs/did-narrow-exception-contract.md`; infer-design §7 | Merging those branches; setting DiD from a fetch or fixture |
| **CLASSIC-FIXTURES** | `fixtures/classic-5/` CSV / DTA / XLSX **content** and hashes | Adding, editing, or renaming catalog **bytes**. Ranking ids are cited only. |
| **OLS lock** | `agent/engine/ols_lock.py`; generate-chapter / estimate / prompts; issue #24 | Rewriting the lock into general TWFE |
| **HET-CODE-EXPORT** | Heterogeneity × interaction hard-block | `educ×region` policy ownership |
| **WORD-FIX** | docx math export samples | Export nodes, math samples, chapter body fill |
| **Card canonical** | `/demos/card`, ADR-0015 | Teaching seed, Evidence Lab |
| **flow-sketch** | `econpaper-ui-temp/flow-sketch` (Design FIND-1) | Shipping sketch chrome; using it as other than a **draft sketch** for FD-FE-honesty labels |

Also do not reopen: generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `session.design`, DECIDE-7 candidate fields, `dataAttached`, snapshot `dataset`, PREWRITE-PAUSE flag names, R-sources families. Add `source_kind` (and optional fetch projection) — do not replace `session.design` or `dataAttached`, and do not treat catalog id as discovered.

---

## 11. G0 done rule

- File present: `docs/real-fetch-contract.md`
- Folded: DECIDE-10 **real fetch first**; find-data must not present fixtures as discovered/found data; fixtures = teaching-known only, never find success; optional teaching shelf with explicit label; prefer actual download into session when API allows (Dataverse, Card zip, WDI, and FRED/IPUMS per existing routes); else link + honest upload; align with infer-design + find-data-lit; fixtures ≠ answer key; `source_kind`: `discovered` \| `teaching_fixture` \| `external_link` \| `fetched` (plus optional `user_upload`); order after design confirm; slice accept bullets **FD-BE-honesty**, **FD-BE-fetch-card**, **FD-BE-fetch-dataverse**, **FD-BE-fetch-wdi**, **FD-FE-honesty** (Design FIND-1 / flow-sketch = draft sketch only); **no gold body reads**
- No application code, API routes, frontend, fixtures, OpenAPI, or OLS-lock change in G0
- No merge of DATA-COMPLETE / DID-NARROW / INF / FIND-DATA / FIND-LIT implementation branches
- No pull request from this slice
- Later slices cite this file; they do not rewrite §2–§6 without a new serial contract
