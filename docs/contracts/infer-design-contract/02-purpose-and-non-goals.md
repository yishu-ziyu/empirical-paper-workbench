# 1. Purpose and non-goals

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


## 1.1 Purpose (frozen)

Given a formal-path **session title** and optional research-question text, this flow only:

1. **Proposes** a research-design **draft** (`session.design.status = draft`).
2. Requires the user to **confirm** that draft before any downstream gate treats the design as locked.
3. On confirm, writes **`session.design`** as the authoritative design object (`status = confirmed`).
4. Lets DATA-COMPLETE **suggest** classic-5 entries that **match the confirmed design**. Suggest still lists candidates; it never auto-selects, never confirm-attaches, never writes gold chapter bodies.
5. Lets the DiD narrow exception proceed **only** from confirmed `method=did` (or equivalent) **plus** the required treated×period interaction. Missing interaction stays a **hard block** (DID-BE-spec).

## 1.2 Non-goals (frozen)

This contract does **not**:

- Generate, fill, lock, or **read** six-chapter / gold chapter bodies (acceptance is §8, not gold-body reads)
- Treat catalog → locked spec as a win path
- Treat catalog → `allow_did` as a win path
- Auto-succeed, auto-select, or prefill a fixture as the user’s study
- Attach a dataset or set `dataAttached`
- Set PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Run estimate, robustness, literature, `generate_title` / `state.title_chapter`, or export
- Merge `feat/fm-e-build-data-complete-1`, `feat/fm-e-build-did-narrow-1`, or other DC / DID implementation branches
- Implement application code, API routes, OpenAPI shapes, or frontend chrome (INF-G0 is markdown only)

`TITLE/TOPIC` here is the session-start title / topic string (desk `onConfirm(title)`, `shapedQuestion`, later `title_topic`). It is **not** `generate_title` / `state.title_chapter` (paper `\title{...}` after estimate / literature / robustness). Infer-design must not move, rename, or gate that node.

---
