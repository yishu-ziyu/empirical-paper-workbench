# 9. Concurrent write-sets (stay out)

> 上级：[Bryce tools contract (four IN; DECIDE-8)](../bryce-tools-contract.md)


| External slice | Lives at | This contract must not touch |
|---|---|---|
| **INFER-DESIGN** | `docs/contracts/infer-design-contract.md`; `session.design`; INF-BE-propose / INF-BE-confirm | Propose/confirm ownership, DiD permission rewrite, catalog-token `allow_did` revival |
| **FIND-DATA-LIT** | `docs/contracts/find-data-lit-contract.md`; FD / FL / R-lit-bar | Replacing FL sources; generate-as-lit revival. **Cite and reuse** `find_lit`. |
| **DATA-COMPLETE** | `docs/contracts/data-completion-contract.md`; `dataAttached`; DC-BE-attach / DC-FE-\* | Confirm-attach, upload readiness, attach-panel chrome. **Do not merge** those branches in G0. |
| **PREWRITE-PAUSE** | `table1Confirmed` + `specConfirmed`; `blockingDecision`; `docs/api/prewrite-confirm.md` | Implementing those flags, freeze/reveal, estimate-prep UI |
| **DID-NARROW / DID-BE-\*** | `docs/contracts/did-narrow-exception-contract.md`; infer-design §7 | Merging those branches; setting DiD from a Bryce tool |
| **CLASSIC-FIXTURES** | `fixtures/classic-5/` CSV / DTA / XLSX **content** and hashes | Adding, editing, or renaming catalog **bytes**. Ranking ids are cited only. |
| **OLS lock** | `agent/engine/ols_lock.py`; generate-chapter / estimate / prompts; issue #24 | Rewriting the lock into general TWFE |
| **HET-CODE-EXPORT** | Heterogeneity × interaction hard-block | `educ×region` policy ownership |
| **WORD-FIX** | docx math export samples | Export nodes, math samples, chapter body fill |
| **Card canonical** | `/demos/card`, ADR-0015 | Teaching seed, Evidence Lab |
| **ADR-0002 cleaning** | `docs/adr/0002-cleaning-pipeline-step-protocol.md` | Rewriting the protocol in G0; Stata-default swap |
| **AERS / stata-code (rejected deps)** | `docs/dev/dependencies.md` | Re-retaining them as runtime; skill dump |
| **Claude skill runner** | `.agents/skills/` | **NORMS-BE** must not use it as the gate engine |

Also do not reopen: generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `session.design`, `session.find_lit`, `dataAttached`, `cleaning_report`, PREWRITE-PAUSE flag names, `code-export` / `doc-export`. Do not replace those objects with a Bryce-named duplicate.

---
