# 4. Four picks IN (detail)

> 上级：[Bryce tools contract (four IN; DECIDE-8)](../bryce-tools-contract.md)


## 4.1 lit-review thin into `find_lit` — **FL-BE-reuse**

**IN.** Thin/reuse. Implementation target is a **thin wrap** of `fetch_papers.py` (OpenAlex + Crossref + S2, DOI dedupe) into `agent/find_lit/` + R-lit-bar chapter gate — not a new package.

Must:

- Thin wrap `fetch_papers.py` into existing `find_lit` (same three sources + DOI dedupe)
- Checkbox **before write**; ≥5 verifiable cards before literature chapter write
- Export **checked** cards only to `refs.bib` or CSL-JSON
- Fail closed if fewer than five verifiable cards (do not pad with generate-as-lit)

Must not:

- Stand up a parallel lit pipeline, Paper-WorkFlow lit dump, or second `literature_entries` writer
- Skip confirm-design
- Write chapters from unchecked cards
- Call Elicit / 知网 / Consensus as V1 success

## 4.2 pywinsor2 cleaning — **CL-BE-winsor**

**IN.** Named Python cleaning tool.

Must:

- pip-install **`pywinsor2`** (Python; not Stata `winsor2` as runtime)
- Named step **`clean_winsor`** on the ADR-0002 pipeline
- **`cuts=(1,99)`**; **continuous columns only**
- Keep before/after stats and sidecar **audit** (`cleaning_report.steps`)
- Protect research-design columns and binaries (do not winsorize treated/period/id/time as a silent default)

Must not:

- Require `stata-code` or a `.do` winsor2 as the default cleaner
- Replace the whole 8-step pipeline with a Paper-WorkFlow clean dump
- Run before `dataAttached`
- Present Card teaching extract vs winsor sidecar confusion as a win (ADR-0015 extract path stays teaching-only)

G0 does not add the pip pin or the step module. Later **CL-BE-winsor** does.

## 4.3 AER-Skills distilled gates — **NORMS-BE**

**IN.** Distill into product yaml + hooks. **No Claude skill runner.**

Must (V1 distilled set — this is the dump ceiling, not a floor to expand):

1. Encode distilled AER rules in **`design_gates.yaml`** and **`chapter_gates.yaml`** (files owned by **NORMS-BE**, not G0)
2. Hook **`design_gates.yaml`** on infer-design **propose** (draft still unconfirmed until human confirm)
3. Hook **`chapter_gates.yaml`** on chapter **write**
4. Confirmed `session.design` before estimate / spec lock
5. Required interactions present (DiD treated×period; HET interaction) or **hard block**
6. `dataAttached` + auditable `clean_winsor` recorded before Table 1 / spec confirm
7. `table1Confirmed` then `specConfirmed` before estimate admission
8. Identification / robustness results recorded when those nodes run; do not invent
9. Literature chapter write only through R-lit-bar (checkbox before write)
10. Export only tex/pdf/docx + code-export languages already in product; no ppt/xhs

Must not:

- Copy AER-Skills / AERS / Paper-WorkFlow into `.agents/skills/` as V1
- Run a **Claude skill runner** as the gate engine
- Add a parallel “AER reviewer” that bypasses PREWRITE-PAUSE
- Treat a skill-file presence test as acceptance
- Add p-hack / spec-search as an “AER robustness” feature (that pick is **OUT**)

## 4.4 top-5 eval only — **EVAL-top5**

**IN.** Scope cap.

Must:

- Keep V1 Bryce evaluation/benchmark to **EVAL-top5**
- Ship it as an **optional submodule** only
- Never use it as a product catalog **answer key**
- Evaluate later BE slices by the §7 bullets, **not** by gold-body reads
- Allow the product to run when the submodule is absent

Must not:

- Add a sprawling eval farm (`agent/eval/tasks/*` growth, extra personas, extra gold packets)
- Use Card 1995 or `undergrad_did_01` as a substitute for the named set
- Use classic-5 catalog identity as the eval answer key
- Vendor EVAL-top5 into `fixtures/classic-5/`
- Treat “more tasks” as a quality improvement in V1

---
