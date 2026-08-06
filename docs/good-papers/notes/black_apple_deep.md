# Close read: Black, Devereux, Salvanes — Why the Apple Doesn’t Fall Far

Local files: `corpus/black_apple_frbsf.pdf`, `corpus/black_devereux_salvanes_apple.pdf`

## Thesis in one line

Parent–child education correlations are mostly **selection**, not causal education spillovers — shown by OLS vs compulsory-schooling IV in Norway.

## Craft moves to steal

### Abstract

- Fact → two hypotheses → design → result contrast (OLS vs 2SLS) → interpretation.
- JEL codes present (I21, J13, J24).

### Introduction (~pages 1–3)

- Opens with the correlation, not with literature dump.
- Policy paragraph: equality of opportunity + multi-generation spillover claim.
- Design: 1960s reform 7→9 years, staggered municipalities 1960–1972.
- Results early: little causal link; mother–son exception.
- Instrument scope: only identifies effect of increasing education from 7 to 9 years.
- Country comparison honesty: Norway vs US/UK institutions.
- Roadmap with section numbers.

### Literature (Section 2)

Organized as **identification approaches**, each with a critique:

| Approach | Exemplar | Critique they put on the record |
|----------|----------|----------------------------------|
| Twin parents | Behrman–Rosenzweig | Coding sensitivity (Antonovics–Goldberger); twins may differ in non-genetic ways |
| Adoptees | Plug | Tiny N; non-random placement; other unobservables |
| Compulsory schooling IV | Chevalier; Oreopoulos–Page–Stevens | Nationwide law confounds trends; sample only kids at home; US census limited to grade retention |

Then their add: full population register, final attainment after leaving home, staggered reform.

### Identification body

- Reform institutional detail is long and specific (curriculum standardization, funding, cohort 1947–1958).
- Municipality FE so timing need not be random; still check correlates of timing (Appendix Table 1).
- First stage reported separately.
- Main table: OLS and IV side by side for mother/father × all/son/daughter.
- Robustness: drop child’s age, reform window, early cohorts, bottom of education distribution.

### Results communication

- “Despite strong OLS… little causal…”
- Exception mother–son stated with size context.
- Nulls are findings, not failures.

### Conclusion

- Restate findings.
- Mechanisms examined (marriage market, quantity/quality) — some ruled out.
- Policy: limited support for multi-gen spillover from **this** reform.
- External validity: bottom-tail reform; Norway may not generalize to high skill-return countries.
- Agenda sentence without fake certainty.

### Tables

- Table 1 summary stats with sample definition footnote.
- Table 2 education distribution before/after reform (first-stage visual).
- Table 3 OLS/IV with N per cell, robust SE, controls listed.
- Table 3a first stage.
- Table 4 multi-column robustness.

## What this paper is *not*

- It is not “longer prose.”
- It is not OLS sold as policy.
- It does not hide that IV is local to low schooling.

## Mapping to our wage paper

| Black | Our current package | Action |
|-------|---------------------|--------|
| Child education outcome | Child log wage | OK different outcome |
| Reform IV | OLS association only | Keep honest; do not invent IV |
| OLS/IV contrast | Only OLS | Report OLS as association; discuss what IV would need |
| Selection story | Partially present | Strengthen intro/method like Black |
| First stage | N/A | Integrity must not require first_stage for OLS packages |

## Quotes / patterns (paraphrase-safe)

- Selection story vs causation story is the opening frame.
- “High correlations… due primarily to family characteristics and inherited ability and not education spillovers.”
- Instrument only identifies +2 years at low end — always state the LATE window.
