# 8. R-lit-bar — replace generate-as-lit (frozen)

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


**R-lit-bar** is the named V1 literature bar. It **replaces generate-as-lit**.

**generate-as-lit** (forbidden win path) = writing `lit_review`, References, `literature_entries`, or citation indices from an LLM’s remembered papers, a gold bibliography paste, or a mock corpus presented as the user’s search.

## 8.1 Five steps (verbatim order)

1. **OpenAlex + Crossref + S2 search** (§7.1)
2. **DOI dedupe** (§7.3)
3. **≥5 checkbox cards** before write into chapters
4. **checked → `refs.bib` or CSL-JSON**
5. **mailto polite pool**

## 8.2 Checkbox cards (frozen)

- Show **at least five** cards that pass §7.4 **before** any literature chapter write.
- Each card has a checkbox. Unchecked cards must not enter `refs.bib`, CSL-JSON, or chapter citations.
- Fewer than five verifiable cards: **block** literature chapter write. Do not pad with generate-as-lit or gold paste.
- Checking is a human action. Auto-check-all is not V1 success.

## 8.3 Export (frozen)

Checked cards export to **either or both**:

- `refs.bib` (BibTeX)
- CSL-JSON

Export contains **only** checked cards. Empty `checked_ids` → empty export; chapter write still blocked.

Later export/docx may render References from this export. It must not invent extra works.

## 8.4 Chapter write gate (frozen)

Literature into chapters is allowed iff **all** of:

1. `session.design.status === "confirmed"`
2. ≥5 checkbox cards were shown
3. The citations being written are in `checked_ids` / the export
4. Each cited work still has verifiable title / author / year / DOI or link

Otherwise do not write `lit_review` / References as if a bibliography existed.

This gate does **not** skip `dataAttached` or PREWRITE-PAUSE for estimate. It is additional for literature text.

## 8.5 mailto polite pool (frozen)

V1 HTTP User-Agent for OpenAlex, Crossref, and S2 **must** include a `mailto:` of a project contact (Crossref / OpenAlex polite-pool rule). Requests share one **polite pool**: identify the product, do not hammer, reuse the same mailto across FD Dataverse and FL searches.

G0 does not pick the address and does not commit secrets. `mailto:dev@local` is **not** the production pool; later slices replace it with a real project contact without putting credentials in git.

## 8.6 V1 refusals (frozen)

| Refusal | Frozen |
|---|---|
| Elicit | Not a V1 source. |
| 知网爬 | Not a V1 source. No crawl. |
| Consensus-as-chapter | Consensus output must not be pasted as a chapter. |
| generate-as-lit | Forbidden. |
| Gold biblio paste | Forbidden as acceptance. |
| Mock corpus as user bibliography | Forbidden as V1 success. |

---
