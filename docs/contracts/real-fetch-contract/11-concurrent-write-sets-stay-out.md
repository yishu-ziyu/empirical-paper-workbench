# 10. Concurrent write-sets (stay out)

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


| External slice | Lives at | This contract must not touch |
|---|---|---|
| **INFER-DESIGN** | `docs/contracts/infer-design-contract.md`; `session.design`; INF-BE-propose / INF-BE-confirm | Propose/confirm ownership, DiD permission rewrite, catalog-token `allow_did` revival. **Cite and defer** on CK title→propose DiD. |
| **FIND-DATA / FIND-LIT (DECIDE-7)** | `docs/contracts/find-data-lit-contract.md`; FD-BE-plan; FL-BE-\*; R-lit-bar | Replacing the where/how plan; generate-as-lit revival; OpenAlex/Crossref/S2 ownership. Honesty **recuts** candidate presentation only. |
| **DATA-COMPLETE** | `docs/contracts/data-completion-contract.md`; `dataAttached`; DC-BE-attach / DC-FE-\* | Confirm-attach, upload readiness, attach-panel chrome. Fetch staging is **not** attach. **Do not merge** those branches in G0. |
| **PREWRITE-PAUSE** | `table1Confirmed` + `specConfirmed`; `blockingDecision`; `docs/api/prewrite-confirm.md` | Implementing those flags, freeze/reveal, estimate-prep UI |
| **DID-NARROW / DID-BE-\*** | `docs/contracts/did-narrow-exception-contract.md`; infer-design §7 | Merging those branches; setting DiD from a fetch or fixture |
| **CLASSIC-FIXTURES** | `fixtures/classic-5/` CSV / DTA / XLSX **content** and hashes | Adding, editing, or renaming catalog **bytes**. Ranking ids are cited only. |
| **OLS lock** | `agent/engine/ols_lock.py`; generate-chapter / estimate / prompts; issue #24 | Rewriting the lock into general TWFE |
| **HET-CODE-EXPORT** | Heterogeneity × interaction hard-block | `educ×region` policy ownership |
| **WORD-FIX** | docx math export samples | Export nodes, math samples, chapter body fill |
| **Card canonical** | `/demos/card`, ADR-0015 | Teaching seed, Evidence Lab |
| **flow-sketch** | `econpaper-ui-temp/flow-sketch` (Design FIND-1) | Shipping sketch chrome; using it as other than a **draft sketch** for FD-FE-honesty labels |

Also do not reopen: generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `session.design`, DECIDE-7 candidate fields, `dataAttached`, snapshot `dataset`, PREWRITE-PAUSE flag names, R-sources families. Add `source_kind` (including `captain_local_real`) and optional `source=captain-local-real` — do not replace `session.design` or `dataAttached`, and do not treat catalog id, a toy CSV, or captain-local-real as discovered.

G0 does **not** delete the banned toy files, move them under `tests/`, change `/demos/card`, or copy Desktop/经济学论文 panels into the repo. Later slices own those write-sets against this freeze.

---
