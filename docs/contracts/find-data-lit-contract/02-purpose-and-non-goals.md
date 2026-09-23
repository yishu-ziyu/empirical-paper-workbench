# 1. Purpose and non-goals

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


## 1.1 Purpose (frozen)

Given a formal-path session whose **`session.design.status === "confirmed"`**, this flow only:

1. **FD** — Builds a **find-data plan** (where / how) from **design facets**, then lists **candidates**: Dataverse search hits **plus** matching fixture candidates (R-sources may add a named external path).
2. Requires **≥1 real candidate**. A classic-5 **id string alone is not** a real candidate (§5).
3. Lets DATA-COMPLETE **attach** a chosen candidate later. FIND-DATA still lists candidates; it never auto-selects, never confirm-attaches, never writes gold chapter bodies.
4. **FL** — Searches **OpenAlex + Crossref + S2**, **DOI-dedupes**, and shows **≥5 checkbox cards** with verifiable title / author / year / DOI or link.
5. Exports **checked** cards to `refs.bib` **or** CSL-JSON. Only checked entries may be written into chapters (**R-lit-bar**).

## 1.2 Non-goals (frozen)

This contract does **not**:

- Propose or confirm `session.design` (INF-BE-propose / INF-BE-confirm)
- Treat catalog → locked spec, catalog → `allow_did`, or catalog → gold biblio as a win path
- Auto-succeed, auto-select, or prefill a fixture as the user’s study
- Attach a dataset or set `dataAttached`
- Set PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Run estimate, robustness, `generate_title` / `state.title_chapter`, or export docx
- Write `lit_review` / References from an LLM memory dump (**generate-as-lit**)
- Paste a gold bibliography, gold chapter body, or classic-5 answer key
- Crawl 知网, call Elicit, or treat Consensus output as a chapter
- Merge `feat/fm-e-build-data-complete-1`, `feat/fm-e-build-infer-design-1` implementation slices, `feat/fm-e-build-did-narrow-1`, or other DC / DID / INF code branches
- Implement application code, API routes, OpenAPI shapes, or frontend chrome (FD-G0 is markdown only)

`TITLE/TOPIC` here is the session-start title / topic string already consumed by infer-design. FIND-DATA / FIND-LIT read the **confirmed** `session.design`, not the title as a substitute for confirm.

---
