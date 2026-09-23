# 10. Later parallel slices (do not implement in G0)

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


G0 owns **only** `docs/contracts/find-data-lit-contract.md`.

| Slice | Owns | Must not write |
|---|---|---|
| **FD-BE-plan** | Confirmed design facets → find-data **plan** (where/how) + R-sources `route_family` | Attach / `dataAttached`, catalog auto-select, `allow_did`, chapter bodies, FL ownership |
| **FD-BE-candidates** | Dataverse search + fixture candidates + R-sources external paths; emit §5 objects; ≥1 real candidate | Confirm-attach, classic-5 CSV bytes, infer-design propose/confirm, gold bodies |
| **FD-FE-cards** (optional) | Show plan + candidate cards (not as the user’s study) | Backend routes, Table1 / equation pause UI, auto-check attach |
| **FL-BE-search** | OpenAlex + Crossref + S2 query from confirmed design; mailto polite pool | generate-as-lit, Elicit/知网/Consensus, mock-as-success, chapter write |
| **FL-BE-dedupe** | DOI dedupe across the three sources | Ranking ownership of FD, attach, gold biblio |
| **FL-FE-cards** | ≥5 checkbox cards before write; checked set | Backend search ownership, PREWRITE-PAUSE flags, estimate |
| **FL-BE-export** | checked → `refs.bib` or CSL-JSON; chapter write may consume **only** this export | Inventing extra works; docx math (WORD-FIX); six-chapter fill from unchecked hits |

Slices stay **write-set-disjoint**. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

**FD-FE-cards / FL-FE-cards alignment (frozen):** optional chrome. Absence of the cards UI does not waive backend gates (plan + real candidates; ≥5 verifiable hits + checked export before literature write).

DC-BE-suggest (data-completion) may still rank classic-5 against the confirmed design. FIND-DATA **extends** that list with Dataverse + R-sources external paths. Suggest alignment is named only. **Do not merge** those branches in G0. Classic-5 ranking remains **candidates**, never answer key.

---
