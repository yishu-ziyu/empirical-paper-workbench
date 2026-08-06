# What Is a Good Empirical Paper?

Source of truth distilled by **reading** real papers and craft guides, not by user lecturing.

Corpus (local):

| File | Role |
|------|------|
| `corpus/black_apple_frbsf.pdf` | Classic applied micro exemplar (intergenerational education) |
| `corpus/black_devereux_salvanes_apple.pdf` | NBER twin of same paper |
| `corpus/bellemare_how_to_write_applied.pdf` | How to write applied papers (Bellemare 2020) |
| notes under `notes/` | Close-reading extracts |

Related classic line (same design family): Oreopoulos–Page–Stevens compulsory schooling; Holmlund–Lindahl–Plug JEL methods survey.

---

## 0. One sentence

**A good empirical paper is a guided tour: one clear question, a design the reader can attack, numbers bound to tables, and honest limits — never a press release that overpromises causality.**

Bellemare: a good paper makes you forget the scaffolding, the way a good film makes you forget the camera. That only works if the scaffolding is conventional and complete.

---

## 1. What Black et al. actually do (the gold pattern for our topic)

Paper: *Why the Apple Doesn't Fall Far* (Black, Devereux, Salvanes).

### Abstract pattern (steal this)

1. Stylized fact (educated parents → educated children).
2. Two stories: **selection** vs **causation**.
3. Design in one clause (Norwegian compulsory reform, staggered municipalities → IV).
4. Result contrast: **OLS large / IV mostly small**.
5. Interpretation: correlations mainly ability/family, not education spillovers.

### Introduction pattern

1. Puzzle: correlation is not explanation.
2. Policy stake: if causal, education policy has multi-generation spillovers.
3. Design paragraph: reform 7→9 years, staggered 1960–1972, exogenous to parental ability.
4. **Results early**, with honesty: little causal effect; one exception mother→son.
5. LATE scope: instrument only speaks to low end of education.
6. Roadmap by section numbers.

### Literature pattern (not a laundry list)

Three **approaches** with **critiques**:

- twins (Behrman–Rosenzweig) + Antonovics–Goldberger coding critique
- adoptees (Plug) + sample/placement limits
- compulsory schooling IV (Chevalier; Oreopoulos–Page–Stevens) + what prior work could not observe

Then: what **this** paper adds (register data, final attainment after leaving home, staggered reform).

### Empirical body pattern

- Institutional reform detail (who, when, curriculum, funding)
- Why timing can be treated as identifying (municipality FE; appendix timing regression)
- First stage table + OLS/IV side-by-side
- Heterogeneity (mother/father × son/daughter)
- Robustness table (drop ages, windows, early cohorts, education distribution)
- Mechanism probes + what is **ruled out**
- Conclusion: findings + external validity (bottom-tail reform; Norway institutions)

### What “good” means here

| Trait | Black does | Bad paper does |
|-------|------------|----------------|
| Estimand | Explicit LATE of +2 years at low end | Vague “effect of education” |
| OLS vs causal | OLS reported **and** demoted by IV | OLS sold as causal |
| Nulls | Allowed and interpreted | Hidden or spun as “no effect = no relation” |
| Tables | N, SE, sample notes, self-contained | Orphan numbers in prose |
| Limits | Bottom-tail reform; country institutions | Silent |

**For our CFPS OLS package:** we cannot fake Black’s IV. We **can** steal the honesty: report association, state selection story, refuse policy spillover language until design closes.

---

## 2. Bellemare craft rules (executable)

Structure of applied paper (learn before you break it):

```text
Title → Abstract → Introduction
  → Theoretical / conceptual framework
  → Data and descriptives
  → Empirical framework (estimation + identification)
  → Results + robustness + heterogeneity + mechanisms + limitations
  → Conclusion
  → References → Appendix
```

### Introduction (Head formula + Bellemare)

1. **Hook** (1–2 para): real-world stake, not “long literature…”
2. **Research question** (1 para): one sentence question
3. **Antecedents** (story of 5–10 closest papers, not enumeration)
4. **Value added** (1–3 contributions; better not invent three)
5. **Roadmap**

Busy-reader path: title → abstract → intro → **tables** → conclusion. Intro must answer enough that readers rarely hunt.

### Data section must answer

Source, when, by whom, sampling, population, N target vs actual, missing/attrition rules, **every variable used** (and none unused). Outcome/treatment get prose; pure controls live in variable table.

### Results discipline

- Core results first; then robustness (multiple measures, placebos, estimators)
- Heterogeneity after robustness
- Mechanisms only with data/assumptions named
- **Limitations subsection**: internal validity, external validity, proxy variables
- Same estimation sample across nested specs
- Table titles self-explanatory; plain-English var names; significance legend complete

### Abstract

First sentences of hook + question + value-added; intelligible to smart non-economist; no faux rigor via jargon.

### Sins

1. Omission (hide what matters)
2. Forcing reader to hunt for a number/spec

---

## 3. CGDEV / Head intro (dev econ norm)

Common top-journal intro order (consistent with Head/Sahm):

1. Motivate puzzle  
2. State question  
3. Empirical approach  
4. **Detailed results** (3–4 paragraphs)  
5. Value-added vs literature  
6. Optional: robustness / policy / limits  
7. Roadmap  

Implication: **results live in the introduction**, not only at the end.

---

## 4. Product mapping (empirical-paper-workbench)

| Good-paper requirement | Our code/artifact |
|------------------------|-------------------|
| One estimand, honest language | `causal_claim_allowed=false`; claim register |
| OLS vs causal contrast | Main results report association; design wishlist ≠ executed IV |
| Bound numbers | `(证据: tables/... / Results/json/...)` |
| Self-contained tables | `tables/*_table*.csv` + table notes in LaTeX |
| Section order | `course_paper_builder` + quality `REQUIRED_SECTIONS` |
| Intro formula | Writing system prompt + builder intro blocks |
| Integrity > polish | `evidence_integrity_blocked` → score 0 |
| Reproducibility | REPRO_OK script |
| Beautiful PDF | `latex_pdf.py` xelatex/ctexart |

### Explicit non-goals (so we do not Goodhart)

- Do **not** invent compulsory-schooling IV for CFPS demo
- Do **not** paste fake verified cites to look like Black’s bibliography
- Do **not** treat “longer prose” as substitute for first stage / design

### Minimum “good draft” bar for this product

1. Abstract follows Black pattern adapted to **association**  
2. Intro has hook → question → design (OLS+HC1) → main number → limits → roadmap  
3. Literature is approach-based or honest “verified=0” gap (not fake cites)  
4. Data answers Bellemare checklist in Chinese  
5. Empirical strategy states estimand, SE, threats, non-claims  
6. Results: coefficient + se + n + evidence path; no policy causal  
7. Robustness: subgroup table with reading discipline  
8. Conclusion: summary + limits + next design step  
9. LaTeX PDF opens; REPRO_OK  

---

## 5. Evaluator hooks (anti self-praise)

Programmatic signals (to implement / tighten):

- Has 摘要/引言/实证策略/结果/结论  
- Abstract mentions 关联 **and** 非因果/不是 LATE (for association packages)  
- Main coef appears with se or evidence path  
- No LATE/政策效应 without `causal_claim_allowed`  
- `cn_chars` band + section presence (not only global length)  
- Repro + latex + integrity floors already in `evolve_evaluator.py`

---

## 6. Reading queue (continue without user teaching)

Priority:

1. Black–Devereux–Salvanes AER version (if accessible) — already FRBSF/NBER  
2. Oreopoulos–Page–Stevens intergenerational compulsory schooling  
3. Holmlund–Lindahl–Plug JEL 2011 methods comparison  
4. One Chinese applied micro paper with clean design (for local style)  
5. Nikolov *Writing Tips for Economics Research Papers* (IZA DP15057) — **downloaded** as `corpus/nikolov_writing_tips.pdf` (39 pp.)

### Nikolov (extra craft, 2022)

- Clarity > cleverness; present tense; active voice; short sentences; cut thrice.
- Distill **one central contribution** before expanding.
- Intro: hook + motivate importance; surprise intuition; not long lit dump.
- Lit: fold into intro for journals; if separate section, **do not title it “Literature Review”**; topical closest papers + your difference (data/model/ID).
- Results: boring clear phrases OK (“estimated coefficient… not statistically significantly different from zero”); guide attention; **economic magnitude**, not only stars; SE-driven significant digits.
- Conclusion short; restate findings + limits + policy only if supported.
- Appendix for secondary robustness / theory dumps.

Method: full text, not inspectional skim. Notes go to `docs/good-papers/notes/`.

---

## 7. How this changes the next draft of *parent education → wage*

Our topic is close to Black’s **question family** (intergenerational human capital) but different **outcome** (wage not child’s schooling) and different **design** (OLS association, not reform IV).

Therefore a **good** version of our paper:

- Opens like Black: correlation is not causation; selection story first  
- States CFPS sample and OLS+HC1 estimand like a clean empirical framework section  
- Reports parent_education coef with se/n as association  
- Explicitly says: **cannot** support multi-generation policy spillover claims  
- Lists what Black-style design would require next (staggered compulsory education / IV diagnostics)  
- Never upgrades design.json “recommended IV” into executed method  

That is the standard. Length without this structure is still a bad paper.
