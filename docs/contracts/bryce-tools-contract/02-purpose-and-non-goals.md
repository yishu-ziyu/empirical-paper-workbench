# 1. Purpose and non-goals

> 上级：[Bryce tools contract (four IN; DECIDE-8)](../bryce-tools-contract.md)


## 1.1 Purpose (frozen)

On the formal path, DECIDE-8 only:

1. **Thins** any Bryce “lit-review” capability into existing **`session.find_lit`** (**FL-BE-reuse**: thin wrap `fetch_papers.py` into **FL** + **R-lit-bar**). OpenAlex + Crossref + S2, DOI dedupe, checkbox **before write**, checked → `refs.bib` or CSL-JSON.
2. **Names** winsorize/clean as **`clean_winsor`** (**CL-BE-winsor**: pip `pywinsor2`, `cuts=(1,99)`, continuous only, auditable) on the existing `CleaningStep` path. Stata `winsor2` / `stata-code` is not the default.
3. **Distills** AER-Skills into **`design_gates.yaml` + `chapter_gates.yaml`** (**NORMS-BE**), hooked on **propose** and **write**. Not a skill dump. **No** Claude skill runner.
4. **Limits** V1 evaluation/benchmark to **EVAL-top5**: optional submodule eval only. Never a product catalog answer key. No eval farm.

## 1.2 Non-goals (frozen)

This contract does **not**:

- Propose or confirm `session.design` (INF-BE-propose / INF-BE-confirm)
- Replace **FD** / **R-sources** / candidate shape / **FL** / **R-lit-bar**
- Attach a dataset or set `dataAttached`
- Set PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Run estimate, robustness, `generate_title` / `state.title_chapter`, or export as G0 work
- Import Paper-WorkFlow wholesale (prompts, graphs, agents, PPT/xhs emitters, p-hack helpers)
- Dump AER-Skills / AERS into `.agents/skills/` or run a **Claude skill runner**
- Make Stata the default cleaning or codegen path
- Add ppt / pptx / 小红书 (xhs) export
- Add a p-hacking / specification-search / star-hunting helper
- Grow `agent/eval/tasks/` into a farm; treat `undergrad_did_01` or Card 1995 as the V1 Bryce eval set
- Treat `classic-5` catalog ids as **EVAL-top5** or as gold bodies; vendor the eval set into the product catalog
- Merge DATA-COMPLETE / DID / INF / FD / FL implementation branches
- Implement application code, API routes, OpenAPI shapes, fixtures, yaml gates, `fetch_papers.py`, or frontend chrome (BRYCE-G0 is markdown only)
- Land **FL-BE-reuse** / **CL-BE-winsor** / **NORMS-BE** / **EVAL-top5** in this G0 write-set

`TITLE/TOPIC` here is the session-start title already consumed by infer-design. Bryce tools read **confirmed** `session.design` and the FIND / clean / prewrite / export surfaces that already exist. They do not invent a Bryce station that jumps the DECIDE-6/7 order.

---
