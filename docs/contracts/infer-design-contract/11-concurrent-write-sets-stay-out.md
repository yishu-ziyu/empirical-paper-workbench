# 10. Concurrent write-sets (stay out)

> 上级：[Infer-design contract (title-first; DECIDE-6)](../infer-design-contract.md)


| External slice | Lives at | This contract must not touch |
|---|---|---|
| **DATA-COMPLETE** | `docs/contracts/data-completion-contract.md`; `dataAttached`; DC-BE-attach / DC-FE-\* | Confirm-attach, upload readiness, attach-panel chrome. Suggest **alignment** is named only (§9). **Do not merge** those branches in G0. |
| **PREWRITE-PAUSE** | `table1Confirmed` + `specConfirmed`; `blockingDecision`; `docs/api/prewrite-confirm.md` | Implementing those flags, freeze/reveal, estimate-prep UI |
| **DID-NARROW (DECIDE-5 A code)** | `docs/contracts/did-narrow-exception-contract.md`; `backend/services/allow_did.py` on DID-BE-gate branches | Merging that branch; keeping catalog-token `allow_did` as truth. G0 documents the rewrite only. |
| **CLASSIC-FIXTURES** | `fixtures/classic-5/` CSV / DTA / XLSX **content** and hashes | Adding, editing, or renaming catalog **bytes**. Ranking ids are cited only. |
| **OLS lock** | `agent/engine/ols_lock.py`; generate-chapter / estimate / prompts; issue #24 | Rewriting the lock into general TWFE; sanitizer / prompt-lock edits |
| **HET-CODE-EXPORT** | Heterogeneity × interaction hard-block | `educ×region` policy ownership, results-chapter lock |
| **WORD-FIX** | docx math export samples | Export nodes, math samples, chapter body fill |
| **Card canonical** | `/demos/card`, ADR-0015 | Teaching seed, Evidence Lab |

Also do not reopen: generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `norm_method` / `DirectionSpec` field names, `dataAttached`, snapshot `dataset`, PREWRITE-PAUSE flag names. Add `session.design` as the design lock — do not replace `dataAttached`, and do not treat catalog id as `session.design`.

---
