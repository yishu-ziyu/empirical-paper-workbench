# 7. Acceptance criteria (DECIDE-8 + INTEGRATE pointers)

> 上级：[Bryce tools contract (four IN; DECIDE-8)](../bryce-tools-contract.md)


G0 does not add tests. Later `FM-E-BUILD-BRYCE-1` slices **must** implement and show these acceptance criteria. Do **not** evaluate by reading gold chapter bodies or gold bibliographies. Slice ids are the INTEGRATE tokens in §0.1.

## 7.1 FL-BE-reuse (alias: BRYCE-BE-lit-thin)

- Thin wrap `fetch_papers.py` (OpenAlex + Crossref + S2, DOI dedupe) into existing `find_lit`.
- Checkbox before write. Bib/CSL from **checked** cards only.
- No second literature pipeline. No generate-as-lit. No gold biblio paste.
- Unconfirmed design cannot rank as an authoritative lit-review success.

**Fail (unacceptable substitute):** Paper-WorkFlow lit dump; Elicit/知网/Consensus; a new `session.bryce_lit` that writes chapters; skip R-lit-bar; fetch-papers as a parallel product path.

## 7.2 CL-BE-winsor (alias: BRYCE-BE-winsor)

- pip `pywinsor2`. Named `clean_winsor`. `cuts=(1,99)`. Continuous only. Auditable (`cleaning_report.steps`).
- Stata `winsor2` / `stata-code` is not the default.
- Design / binary columns are not silently winsorized.

**Fail (unacceptable substitute):** Stata-only default cleaner; undocumented pandas one-off presented as the named tool; clean-before-attach; Paper-WorkFlow clean dump; winsorizing binaries.

## 7.3 NORMS-BE (alias: BRYCE-BE-aer-gates)

- Distill AER rules into `design_gates.yaml` + `chapter_gates.yaml`.
- Hook **propose** (design) and **write** (chapters). No Claude skill runner.
- No full skill dump. No p-hack feature dressed as robustness.

**Fail (unacceptable substitute):** `.agents/skills/` dump; Claude skill runner as the gate engine; bypass of `table1Confirmed` / `specConfirmed`; catalog → locked spec; p-hack helper.

## 7.4 EVAL-top5 (alias: BRYCE-BE-top5-eval)

- V1 eval/benchmark is **EVAL-top5** as an **optional submodule** only.
- Never a product catalog answer key. No sprawling eval farm. Card / `undergrad_did_01` are not the V1 set.
- Product still runs if the submodule is absent.

**Fail (unacceptable substitute):** adding many `agent/eval/tasks/*`; gold-body rubric as the only metric; catalog id as answer key; vendoring the submodule into classic-5.

OLS remains the default when DiD is not allowed (**infer-design**). Heterogeneity × no-interaction stays a hard block. Missing treated×period when `design.method=did` stays a DID-BE-spec hard block. This file does not change those rules.

---
