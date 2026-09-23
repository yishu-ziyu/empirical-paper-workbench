# 0. Product-line lock — DECIDE-8

> 上级：[Bryce tools contract (four IN; DECIDE-8)](../bryce-tools-contract.md)


**DECIDE-8 (frozen; Decide via Firstmate).** Encode the following **IN / OUT**:

**Four picks IN:**

1. **lit-review thin into `find_lit`** — do not stand up a parallel lit pipeline; thin/reuse the existing `find_lit` (OpenAlex+Crossref+S2 cards, checkbox, bib) path.
2. **pywinsor2 cleaning** — winsorize/clean step as a named cleaning tool (Python `pywinsor2`), not a Stata-only default.
3. **AER-Skills distilled gates** — distill AER-Skills into product gates/checks (acceptance-style), not a full skill dump.
4. **top5 eval only** — evaluation/benchmark scope limited to a top-5 set; no sprawling eval farm in V1.

**Explicitly OUT:**

- Paper-WorkFlow dump (do not import wholesale workflow dump)
- p-hack feature (no p-hacking helper)
- stata-code default (Stata is export option, not the default cleaning/codegen path for this slice)
- ppt / 小红书 (xhs) outputs

## 0.1 Research INTEGRATE pointers (frozen; `FM-E-BUILD-BRYCE-1`)

Research INTEGRATE + `FM-E-BUILD-BRYCE-1` freeze these **pointer names**. They must appear. They do **not** change DECIDE-8 IN/OUT. G0 does not add the files or code they name.

| Token | Frozen meaning | DECIDE-8 pick | Retired G0 alias |
|---|---|---|---|
| **FL-BE-reuse** | Thin wrap `fetch_papers.py` (OpenAlex + Crossref + S2, DOI dedupe) into existing `find_lit`. Checkbox before write. | lit-review thin into `find_lit` | `BRYCE-BE-lit-thin` |
| **CL-BE-winsor** | pip `pywinsor2`; named `clean_winsor`; `cuts=(1,99)`; **continuous only**; auditable. | pywinsor2 cleaning | `BRYCE-BE-winsor` |
| **NORMS-BE** | Distill AER rules into `design_gates.yaml` + `chapter_gates.yaml`; hook **propose** and **write**. **No** Claude skill runner. | AER-Skills distilled gates | `BRYCE-BE-aer-gates` |
| **EVAL-top5** | Optional **submodule** eval only. Never a product catalog answer key. | top5 eval only | `BRYCE-BE-top5-eval` |

`fetch_papers.py`, `clean_winsor`, `design_gates.yaml`, and `chapter_gates.yaml` are **later-slice implementation targets**. Their absence from this G0 tree is not a defect. Claude skill runner / `.agents/skills/` dump remains **OUT**.

**Order relative to DECIDE-6 / DECIDE-7 (do not reorder):**

```
title → design → confirm → find data/lit → attach → prewrite
```

Bryce tools **do not** insert a new station before confirm-design. They **do not** skip attach. They **do not** replace PREWRITE-PAUSE. Cleaning sits on the existing post-attach clean path. Distilled AER gates fire on confirm / prewrite / identification / robustness / literature-write / export — they are checks, not a second workflow.

In scope: the formal econpaper paper path — the same product line as `docs/contracts/infer-design-contract.md` and `docs/contracts/find-data-lit-contract.md`.

Out of product line for this contract (do not extend, re-label, or treat as Bryce V1 success):

- Card teaching case (`POST /demos/card`, `research.teaching_case=card_1995`, ADR-0015)
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`)
- CHARLS wizard, CFPS fixture, spike CSVs, eval datasets **outside** the named top-5 set (including `agent/eval/tasks/undergrad_did_01` as a farm seed)
- Agent spike (`/spike`), first-value marketing review, flow-sketch / draft-product chrome
- Sketch-only sample names (`sample_wage.csv`, `sample_panel_mini.csv`, `wage_panel.csv`)
- Catalog identity alone (`ck1994`, `ck1994_long`, `minimum-wage-employment`, `barro1991_growth`, …) as an answer key **or** as the eval set
- Unconfirmed `session.design` (`missing` / `draft`)
- A second literature agent beside `session.find_lit` / **FL** / **R-lit-bar**
- AERS / AER-Skills file dump into `.agents/skills/` or a Claude skill runner
- Paper-WorkFlow / stata-code / p-hack / ppt / xhs as V1 surfaces

`session.design` (infer-design), `session.find_data` / `session.find_lit` (FIND), `dataAttached` (data-completion), and `table1Confirmed` / `specConfirmed` (PREWRITE-PAUSE) stay **different** gates. This contract does not propose or confirm a design, does not attach a dataset, does not skip confirm-attach, and does not replace those flags. It **does** freeze how the four IN picks sit on those surfaces.

DiD permission stays in `docs/contracts/infer-design-contract.md` §7. R-lit-bar stays in `docs/contracts/find-data-lit-contract.md` §7–§8. This file must not reopen catalog-token `allow_did`, must not contradict title-first CK propose, and must not replace generate-as-lit with a second lit dump.

---
