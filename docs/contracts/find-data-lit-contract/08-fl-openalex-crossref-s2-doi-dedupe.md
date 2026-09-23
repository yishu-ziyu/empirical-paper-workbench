# 7. FL — OpenAlex + Crossref + S2, DOI dedupe

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


## 7.1 Sources (frozen)

**FL** V1 search set is exactly:

| Source | Role |
|---|---|
| **OpenAlex** | Works search from confirmed design facets + title/RQ |
| **Crossref** | Works search (existing `literature_sources/crossref.py` is a later-slice implementation target, not a G0 edit) |
| **S2** | Semantic Scholar works search |

All three are searched in V1. Missing key / network failure on one source **does not** license generate-as-lit. Remaining sources still feed the card list. If the merged, deduped list cannot fill **≥5** verifiable cards, **do not write** literature into chapters. Fail closed.

**Not V1 sources:** Elicit, 知网爬, Consensus, Google Scholar scrape, Apodex, mock corpus as a success path, gold biblio fixtures.

ADR-0004 mock and ADR-0011 Apodex stay out of the V1 win path. pytest may still mock HTTP; that is a test double, not generate-as-lit and not a gold biblio.

## 7.2 Query (frozen)

Build the query from **confirmed** `session.design` facets (method, outcome, treatment, title/RQ). Do not require `dataAttached`. Do not let the model free-write the only query without those facets.

## 7.3 DOI dedupe (frozen)

Merge hits across OpenAlex, Crossref, and S2.

1. Normalize DOI (lowercase, strip `https://doi.org/` prefix).
2. Same DOI → one card. Prefer the record that has the fullest title/author/year.
3. No DOI → fallback key `normalized(title) + year + first author`. Do not drop a verifiable link-only hit solely for missing DOI.
4. One checkbox card per surviving work.

## 7.4 Verifiable card fields (frozen)

Each card **must** expose:

| Field | Rule |
|---|---|
| `title` | From a search hit, not LLM memory |
| `authors` | From a search hit |
| `year` | From a search hit |
| `doi` **or** `url` | At least one followable identifier. DOI preferred. |

Missing all of DOI and URL → **not** a V1 card. Do not fill gaps from gold biblio or generate-as-lit.

---
