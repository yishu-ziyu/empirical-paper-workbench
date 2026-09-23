# 3. Honesty — fixtures are teaching-known only

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


## 3.1 Never fixture-as-found (frozen)

FIND-DATA **must not** present a fixture as discovered / found data. Frozen refusals:

| Surface | Forbidden |
|---|---|
| `source_kind` | `teaching_fixture` emitted as `discovered` or `fetched` |
| Ordering | Fixture listed in the **discovered / fetch** list as if it were a search hit |
| Copy | “找到了数据”, “discovered dataset”, “matched your study”, “recommended data”, “we found ck1994” on a fixture |
| Padding | Empty or failed real fetch filled with classic-5 so the list is non-empty |
| Success | Treating a teaching shelf row as FIND success, attach success, or DiD unlock |

DECIDE-7 still allows a fixture to **appear** as a candidate. DECIDE-10 **narrows how**: only as `teaching_fixture`, never as find success, never unlabeled next to Dataverse hits.

## 3.2 Optional teaching shelf (frozen)

`session.find_data.teaching_shelf` (name frozen) is **optional**.

| Rule | Frozen |
|---|---|
| Contents | Zero or more `source_kind=teaching_fixture` real candidates |
| Label | **Explicit**. Product copy must say this is a **teaching-known** extract / 教学已知样本, **not** a find result |
| Absence | Missing shelf is fine. FIND does not fail because no fixture exists |
| Presence | Does **not** satisfy “≥1 real candidate” as a **find**. The ≥1 real candidate owed after confirm must still be `discovered`, `fetched`, or `external_link` (DECIDE-7 §9 bullet 1, recut by honesty) |
| Separation | Shelf is a distinct list / region. Do not interleave unlabeled with discovered cards |

Rename or remove `ck1994_long` / `barro1991_growth` / wage1: the shelf may empty. Real fetch / external path **must** still show (same as DECIDE-7 bullet 2).

**DATA-RIGOR recut of the shelf:** banned toys (§3.4) **must not** appear on the shelf, in suggest, or in find-data UI. A 4–24-row synthetic is not a `teaching_fixture` candidate. Real classic-5 **reproduction extracts** (not toys) may still sit on the shelf as teaching-known, never as found data.

## 3.3 Copy rules (FD-BE-honesty; frozen)

| `source_kind` | Allowed copy family | Forbidden copy family |
|---|---|---|
| `discovered` / `fetched` | “检索到 / Dataverse 命中 / 已下载到本会话” | Calling it a teaching sample as the primary label |
| `teaching_fixture` | “教学已知样本 / teaching-known extract — not a find result” | found / discovered / matched / recommended / 为你找到 |
| `external_link` | “公开链接；请下载后上传” / link + honest upload | found dataset; silent fixture substitution |
| `user_upload` | “上传你自己的文件” | presented as a search hit |
| `captain_local_real` | “船长本地真实面板 / captain-local-real — not a find result” | found / discovered / Dataverse hit / teaching toy |

Chinese and English surfaces obey the same distinctions. A translation that calls a fixture 发现 / 检索结果 **fails** FD-BE-honesty.

## 3.4 Teaching toys — banned on the product path (DATA-RIGOR; frozen)

**NO synthetic / invented / toy sample data on the product path.** Fake small CSVs that pass demos then die on real panels are forbidden.

**BANNED as product "found data"** (paths frozen; row counts are data rows, excluding header):

| File | Path | Rows | Why banned |
|---|---|---|---|
| `minimum_wage.csv` | `agent/spike/fixtures/minimum_wage.csv` | 4 | Spike toy 2×2; not a panel |
| `course-panel.csv` | `frontend/public/samples/course-panel.csv` | 24 | Guide / legacy course sample |
| `sanitized_sample.csv` | `fixtures/cfps_association/sanitized_sample.csv` | 24 | CFPS-shaped **synthetic** (fixture README) |

Same ban covers aliases, copies, and UI sample entries that load those bytes (`SAMPLE_CSV` / “了解产品” guide-sample, spike min-wage CSV, CFPS sanitized sample). Later slices must not add new n≈4–24 invented CSVs to `frontend/public/`, `fixtures/` (outside `tests/`), or suggest/find-data.

**Never present teaching toys as found data.** Not as `discovered`, `fetched`, `external_link` padding, `captain_local_real`, unlabeled shelf rows, or “we found your data”.

## 3.5 Tiny fixtures — tests only (DATA-RIGOR; frozen)

Tiny / synthetic fixtures **ONLY** under `tests/` (including `backend/tests/`, `agent/tests/`, `frontend/src/__tests__/`), and they **must be labeled synthetic** in the file or the test that owns them.

They **never** appear in:

- suggest / FIND-DATA / FIND UI
- teaching shelf
- product sample buttons
- session fetch staging presented as a find

pytest HTTP mocks remain test doubles. They are not found data and not a product demo.

## 3.6 n<200 honesty gate (DATA-RIGOR; frozen)

On **attach** or **estimate**, if attached / analysis `n` (row count) **< 200**:

| Surface | Frozen |
|---|---|
| Demo / found-data / “product works” claim | **Fail closed.** Must not treat the run as a passing product demo, FIND success, or teaching-toy win. |
| Honesty warning | **Required.** User-visible: this file is too small to stand in for a real panel; it is not a demo success. |
| Attach itself | A user may still attach their own small file. Attach ≠ demo claim. |
| Estimate itself | May run for the user’s own file. Estimate ≠ “the product was proven on real data”. |
| Write-loops | Smoke / rehearsal / classic write-loops **must not** use n<200 toys as the proving path. |

Threshold name (later slices may project; G0 does not add OpenAPI): **`N_DEMO_CLAIM_MIN = 200`**. Missing row count **fails closed** for demo claims (do not assume n≥200).

## 3.7 Smoke / rehearsal / classic write-loops (DATA-RIGOR; frozen)

Product-path smoke, rehearsal, and classic write-loops **must** use **≥ real Card 1995 extract** (wooldridge / StatsPAI `card_1995`, n≈3010 in-repo evidence) **or other real panels** (live public fetch, or captain-local-real `.dta`/CSV upload).

**Not allowed** as that proving path: 4–24-row toys, CFPS `sanitized_sample.csv`, `course-panel.csv`, `minimum_wage.csv`, or any unlabeled synthetic under `fixtures/` / `frontend/public/`.

`/demos/card` chrome stays out of FIND success. Real Card 1995 **bytes** may back a write-loop; the teaching-case UI is still not FIND-DATA.

---
