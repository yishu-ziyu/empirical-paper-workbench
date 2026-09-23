# 2. How the four picks map onto existing surfaces

> 上级：[Bryce tools contract (four IN; DECIDE-8)](../bryce-tools-contract.md)


Product surfaces named in DECIDE-6/7 and this file:

| Surface | Contract / object | INTEGRATE slice | Bryce pick |
|---|---|---|---|
| **infer-design** | `docs/contracts/infer-design-contract.md`; `session.design` | **NORMS-BE** `design_gates.yaml` hooked on **propose** | AER distilled gates. Not a new design engine. |
| **find-data-lit** | `docs/contracts/find-data-lit-contract.md`; `session.find_data`; **`session.find_lit`** | **FL-BE-reuse** thin wrap `fetch_papers.py` into `find_lit`; checkbox before write. **NORMS-BE** literature write via R-lit-bar | lit-review thin. No parallel pipeline. |
| **prewrite** | PREWRITE-PAUSE `table1Confirmed` then `specConfirmed`; `run_prewrite`; `identification_verify`; `robustness_check` | **NORMS-BE** `chapter_gates.yaml` hooked on **write**; **CL-BE-winsor** `clean_winsor` **before** prewrite, after attach | AER distilled gates + named Python clean. |
| **export** | `GET /code-export` (`py` / `do` / `R` / `m`); `GET /doc-export` (`tex` / `pdf` / `docx`); FL bib export | (no new Bryce export slice) | Python default; Stata **option**. **No** ppt / xhs. |
| **eval** | not the product catalog | **EVAL-top5** optional submodule | top5 eval only; never catalog answer key. |

## 2.1 lit-review thin → `find_lit` — **FL-BE-reuse** (frozen)

| Must reuse | Must not create |
|---|---|
| `session.find_lit` (`hits[]`, `cards[]`, `checked_ids[]`, `export`) | `session.bryce_lit`, a second search agent, Paper-WorkFlow lit node, generate-as-lit |
| **FL**: OpenAlex + Crossref + S2, DOI dedupe | Elicit / 知网爬 / Consensus-as-chapter / Apodex-as-V1 |
| Thin wrap **`fetch_papers.py`** (same three sources + DOI dedupe) **into** existing `find_lit` | A standalone fetch-papers product path beside `agent/find_lit/` |
| **R-lit-bar**: checkbox cards **before write**; checked → `refs.bib` or CSL-JSON; mailto polite pool | Auto-check-all; gold biblio paste; mock corpus as user bibliography; write without checkbox |
| Query from **confirmed** `session.design` facets | Title-only search that skips confirm-design |

A “lit-review” Bryce tool in V1 **is** FL + R-lit-bar, with `fetch_papers.py` as a **thin wrap** inside `find_lit`. It is not a parallel pipeline.

## 2.2 pywinsor2 cleaning → `clean_winsor` — **CL-BE-winsor** (frozen)

| Must reuse | Must not create |
|---|---|
| ADR-0002 `CleaningStep` protocol; `clean_data` orchestrator; `cleaning_report.steps` | A Stata-only cleaner as the default |
| Named step **`clean_winsor`** (outliers / winsor family) | Silent rewrite of design / binary columns; undocumented cuts |
| pip **`pywinsor2`** as the named V1 runtime | `stata-code` / Stata `winsor2` as the required runtime |
| **`cuts=(1,99)`**; **continuous only** | Winsorizing treated/period/id/time or 0/1 indicators as a silent default |
| Sidecar + before/after stats (auditable) | A second cleaning graph imported from Paper-WorkFlow |

Attach (`dataAttached`) still happens **before** this tool runs on the session dataset. Confirm-design does not clean. FIND-DATA does not clean.

## 2.3 AER-Skills distilled gates → yaml + hooks — **NORMS-BE** (frozen)

Distill, do not dump. V1 gates are **YAML check lists** plus **hooks**, not a copy of AERS skill files, AERS Stage 04 prose, an AER handbook, or a **Claude skill runner**.

| Artifact | Hook | Existing surface | Fail closed if |
|---|---|---|---|
| `design_gates.yaml` | **propose** (infer-design propose → draft; confirm still required to lock) | `session.design` | Draft / missing design treated as locked spec; propose skips yaml |
| `design_gates.yaml` | confirmed method + required interactions | infer-design §2.4; DID-BE-spec; HET hard-block | Confirmed `method=did` without treated×period; `qType=heterogeneity` without interaction |
| `chapter_gates.yaml` | **write** (chapter generate / literature write) | PREWRITE-PAUSE; R-lit-bar; generate-chapter | Estimate / chapter write without `table1Confirmed` / `specConfirmed`; generate-as-lit |
| Distilled checks (same ceiling as before) | prewrite / identification / robustness / export | `dataAttached` + `clean_winsor` audit; `identification_verify`; `robustness_check`; code/doc export | Invented diagnostics; p-hack helper; ppt/xhs; Stata as the only codegen |

G0 does not add the yaml files. Later **NORMS-BE** owns them. Absence of a dedicated “AER panel” UI or a Claude skill does not waive the checks. A skill-runner presence test is **not** acceptance.

## 2.4 top-5 eval only → optional submodule — **EVAL-top5** (frozen)

| Is | Is not |
|---|---|
| An **optional submodule** eval/benchmark for V1 | Product catalog (`classic-5`) used as an **answer key** |
| Scope cap: **only** that top-5 set in V1 | An eval farm under `agent/eval/tasks/` |
| Optional: product runs without the submodule | Vendoring the eval set into `fixtures/classic-5/` |
| Out of line: Card 1995 teaching case; `undergrad_did_01` as farm seed | Gold-body reads as the eval metric |

`classic-5` remains FIND/DATA-COMPLETE **candidates** (DECIDE-6/7). **EVAL-top5** is a different object. Do not conflate them. Never treat catalog identity as the eval answer key.

---
