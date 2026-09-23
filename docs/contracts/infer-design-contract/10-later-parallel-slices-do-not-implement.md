# 9. Later parallel slices (do not implement in G0)

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


G0 owns **only** `docs/contracts/infer-design-contract.md`.

| Slice | Owns | Must not write |
|---|---|---|
| **INF-BE-propose** | Title (+ optional RQ) → `session.design` **draft**. Title-first. | Confirm lock, attach / `dataAttached`, catalog auto-select, `allow_did` from entry id, chapter bodies, FE chrome, PREWRITE-PAUSE flags |
| **INF-BE-confirm** | User confirm → lock `session.design`. Project onto direction/spec **only** as a confirmed object. | Propose ranking ownership, attach, catalog CSV bytes, estimate, gold bodies, `table1Confirmed` / `specConfirmed` |
| **INF-FE-review** (optional) | Show draft fields and the confirm CTA. | Second product line, sketch chrome, backend routes, attach-panel ownership, Table1 / equation pause UI |
| **DID-BE-gate** (rewrite) | DiD permission from **confirmed** `method=did` + interaction. Remove catalog-token `allow_did` as source of truth. | General TWFE unlock, classic-5 CSV bytes, FE beyond an optional one-line hint, WORD-FIX |
| **DID-BE-spec** | Confirmed DiD ⇒ require treated×period. Missing → hard block. | Catalog matcher ownership, staggered / CS / Bacon, export/docx |
| **DC-BE-suggest** (align) | Rank classic-5 **candidates** against the **confirmed** design. Without confirm: fail or candidates-only. | Confirm-attach, `dataAttached` writes, auto-select, gold bodies |

Slices stay **write-set-disjoint**. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

**INF-FE-review alignment (frozen):** optional. Absence of the review chrome does not change the backend gates. Confirm is still required.

---
