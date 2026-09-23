# 6. Named objects (reuse, do not fork)

> 上级：[Bryce tools contract (four IN; DECIDE-8)](../bryce-tools-contract.md)


G0 adds **no** new snapshot / OpenAPI objects and **no** yaml / `fetch_papers.py` files.

| Object | Owner | Bryce G0 |
|---|---|---|
| `session.design` | infer-design | Read after confirm. Do not write. **NORMS-BE** later hooks propose via `design_gates.yaml`. |
| `session.find_data` | find-data-lit | Untouched (not a Bryce pick). |
| `session.find_lit` | find-data-lit | **Reuse.** **FL-BE-reuse** thin-wraps `fetch_papers.py` here. |
| `fetch_papers.py` | later **FL-BE-reuse** | Pointer only. Not added in G0. |
| `dataAttached` / snapshot `dataset` | data-completion | Read after attach for cleaning. Do not set. |
| `clean_winsor` / `cleaning_report.steps` | ADR-0002; later **CL-BE-winsor** | pip `pywinsor2`; `cuts=(1,99)`; continuous only; auditable. |
| `table1Confirmed` / `specConfirmed` | PREWRITE-PAUSE | **NORMS-BE** reads; does not own. |
| `design_gates.yaml` / `chapter_gates.yaml` | later **NORMS-BE** | Pointer only. Hook propose / write. No Claude skill runner. |
| `find_lit.export` | FL-BE-export | Bib/CSL only from checked cards. |
| **EVAL-top5** submodule | later **EVAL-top5** | Optional. Never catalog answer key. |
| code-export / doc-export | existing routers | Python default; Stata option; no ppt/xhs. |

Must not live on a Bryce object as a win path: catalog id, `allow_did`, gold-body hashes, gold biblio, Paper-WorkFlow dump, p-hack payloads, ppt/xhs blobs, Claude skill-runner output, unconfirmed `session.design`.

---
