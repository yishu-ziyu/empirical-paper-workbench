# 8. Later parallel slices (`FM-E-BUILD-BRYCE-1`; do not implement in G0)

> 上级：[Bryce tools contract (four IN; DECIDE-8)](../bryce-tools-contract.md)


G0 owns **only** `docs/contracts/bryce-tools-contract.md`.

INTEGRATE pointer names have landed. **Do not start, merge, or partially land these slices in G0.** Implementation is `FM-E-BUILD-BRYCE-1`, write-set-disjoint, after this contract.

| Slice (INTEGRATE id) | Owns (when started) | Must not write |
|---|---|---|
| **FL-BE-reuse** | Thin wrap `fetch_papers.py` into `session.find_lit` / `agent/find_lit`; checkbox before write | Parallel lit pipeline, generate-as-lit, FD ownership, attach, PREWRITE-PAUSE flags |
| **CL-BE-winsor** | pip `pywinsor2`; `clean_winsor` `cuts=(1,99)` continuous only; auditable report | Stata-default cleaner, classic-5 CSV bytes, infer-design, ppt/xhs |
| **NORMS-BE** | `design_gates.yaml` + `chapter_gates.yaml`; hook propose + write | Claude skill runner, AER-Skills dump, p-hack feature, DID unlock rewrite, gold bodies |
| **EVAL-top5** | Optional submodule eval only | Eval farm; catalog or Card as answer key; required submodule for product boot |

Slices stay **write-set-disjoint** when they eventually run. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

Optional FE chrome (labels on FIND-LIT cards, a named `clean_winsor` step in the clean wizard, a gate checklist) does not waive backend gates. Absence of that chrome does not change the IN/OUT set.

---
