# 11. Concurrent write-sets (stay out)

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


| External slice | Lives at | This contract must not touch |
|---|---|---|
| **INFER-DESIGN** | `docs/contracts/infer-design-contract.md`; `session.design`; INF-BE-propose / INF-BE-confirm | Propose/confirm ownership, DiD permission rewrite, catalog-token `allow_did` revival. **Cite and defer** on CK title→propose DiD. |
| **DATA-COMPLETE** | `docs/contracts/data-completion-contract.md`; `dataAttached`; DC-BE-attach / DC-FE-\* | Confirm-attach, upload readiness, attach-panel chrome. Suggest **alignment** is named only (§10). **Do not merge** those branches in G0. |
| **PREWRITE-PAUSE** | `table1Confirmed` + `specConfirmed`; `blockingDecision`; `docs/api/prewrite-confirm.md` | Implementing those flags, freeze/reveal, estimate-prep UI |
| **DID-NARROW / DID-BE-\*** | `docs/contracts/did-narrow-exception-contract.md`; infer-design §7 | Merging those branches; setting DiD from a FIND candidate |
| **CLASSIC-FIXTURES** | `fixtures/classic-5/` CSV / DTA / XLSX **content** and hashes | Adding, editing, or renaming catalog **bytes**. Ranking ids are cited only. |
| **OLS lock** | `agent/engine/ols_lock.py`; generate-chapter / estimate / prompts; issue #24 | Rewriting the lock into general TWFE; sanitizer / prompt-lock edits |
| **HET-CODE-EXPORT** | Heterogeneity × interaction hard-block | `educ×region` policy ownership, results-chapter lock |
| **WORD-FIX** | docx math export samples | Export nodes, math samples, chapter body fill |
| **Card canonical** | `/demos/card`, ADR-0015 | Teaching seed, Evidence Lab |
| **ADR-0004 / 0009 / 0011 literature nodes** | `search_literature`, citation graph, Apodex bypass | Replacing those modules in G0; treating mock/Apodex as R-lit-bar success |

Also do not reopen: generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `session.design`, `dataAttached`, snapshot `dataset`, PREWRITE-PAUSE flag names, existing Crossref/S2 adapters as **implementation targets**. Add `session.find_data` and `session.find_lit` — do not replace `session.design` or `dataAttached`, and do not treat catalog id as a real candidate.

---
