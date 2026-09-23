# 3. Propose flow

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


## 3.1 Input / output (frozen)

**Input (only):**

1. Session **title** (TITLE/TOPIC / desk title / `shapedQuestion` / `title_topic.title`).
2. Optional user-supplied **research-question** text (`source.question`).

**Output:** a `session.design` object with `status=draft`, `confirmed=false`, `confirmed_at=null`, `catalog_entry_id=null`.

Propose reads title (+ RQ) **first**. It may use those strings to choose `method=ols` vs `method=did` vs other `norm_method` tokens and to name outcome / treatment / interaction **slots**. It must not require a catalog hit to emit a draft.

## 3.2 Must (propose)

- Write a draft only. Do not lock.
- Stamp `proposed_at` and `source.title` / `source.question`.
- If the title/RQ names a 2×2 DiD object, draft `method=did` **and** a treated×period interaction slot (names may be placeholders until data is attached).
- If the title/RQ names an average / levels association (e.g. schooling–wages, Barro growth), draft `method=ols` with no DiD interaction requirement.
- Leave `catalog_entry_id` null.

## 3.3 Must not (propose)

| Refusal | Frozen |
|---|---|
| Attach dataset / ingest | Must not call upload, classic-5 attach, or stamp snapshot `dataset`. |
| `dataAttached` | Must not set true. Propose is pre-attach. |
| Catalog as source of truth | Must not select `ck1994` / `ck1994_long` / `barro1991_growth` / any `classic-5` entry. |
| `allow_did` from catalog id | Must not set `allow_did` because an entry id matched. Catalog → `allow_did` is a **deprecated** win path (§7). |
| Locked spec | Must not write `status=confirmed`, must not treat the draft as `set_direction` / `main_specification` for estimate. |
| Gold / chapter bodies | Must not write chapter text, gold-body fixtures, or six-chapter fill. |
| PREWRITE-PAUSE flags | Must not set `table1Confirmed` or `specConfirmed`. |
| Estimate / export | Must not enqueue estimate or emit code/docx. |

A title that looks like Card–Krueger may produce a **DiD draft**. That draft is not permission to estimate DiD and not `allow_did=true`.

---
