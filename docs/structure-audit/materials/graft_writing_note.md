# Graft Writing Note — step_06 WritingAgent prompts

Date: 2026-08-06  
Scope: surgical prompt-only change in `runtime/full_pipeline.py` · `step_06_writing`  
Sources: `awesome_skills_graft.md` (§3 academic_writing + econ_intro; Wave B writing thickness)  
and reliability/veto spirit from `book_ch4-6.md` (hallucination veto, complete=verified facts)

---

## What changed

| Piece | Before | After |
|-------|--------|--------|
| Base `system` | 4 short rules (facts-only, no fake lit, no causal OLS, evidence path) | Structured prompt: hard red lines + econ section order + paragraph discipline + course-paper length floors |
| `degrade_mode` suffix | One line on unverified lit + OLS association | Explicit degrade block: verified status, no fake cites, claim-bound conclusions, no soft causal upgrade |
| `expand_mode` suffix | “写厚 >10000，禁注水/编造” | Expand contract: which sections to thicken, keep numbers/paths, convert outline→claim–support–implication prose, ban new unfacted quantities |
| `user` instruction | Thin “课程论文级…facts=” | Explicit: full Chinese paragraphs, align numbers/paths, association language, no padding fabrications |
| Prior-body handoff | “扩写/降级改写，保留证据数字” | Same + forbid new magnitudes not in facts; expand bullets into paragraphs |

**Not changed:** facts JSON shape, claim register, `_fallback_paper` / `_expand_fallback` deterministic bodies, step order, quality gates, LLM client.

---

## Mechanisms grafted (checklist → prompt text)

From **27 academic_writing / econ_intro** (`awesome_skills_graft.md`):

1. Paragraph = claim → support → implication; 3–7 sentences; no bullet finals in main body.  
2. Intro skeleton: puzzle → question → design → magnitudes (facts only) → contribution/limits → roadmap; no lit dump first.  
3. Results: introduce table → walk coef/se/p/n → economic reading → limits; insignificant ≠ zero effect wording.  
4. Causal language matched to design (`causal_claim_allowed=false` → association only).  
5. Placeholders: `[待绑定证据]` / `[CITATION NEEDED]` instead of inventing.  
6. Course-paper density targets (summary/intro/data+method/results/conclusion floors) without fluff padding.

From **dont-lie / integrity spirit** (same graft doc + book Ch5–6 veto):

- Numbers only from facts; no silent re-round; evidence path on every numeric sentence.  
- No invented authors/years/journals when `literature_verified_count=0`.  
- Hallucinated cites/magnitudes are hard fail language in the system prompt (map to integrity gate, not soft style advice).

From **book_ch4-6** (reliability, not tool ACI):

- Constraint over style: red lines first, then structure, then length.  
- “Complete” prose still cannot invent unverified claims; thickness via honest boundaries and next steps.

---

## File touch

```text
runtime/full_pipeline.py          # step_06_writing system / expand / user strings only
docs/structure-audit/materials/
  graft_writing_note.md           # this note (new)
```

---

## Acceptance / falsifiers

| Claim | Falsifier |
|-------|-----------|
| Longer honest prose | Expand run still ships outline-only or pure bullet main body |
| No invented numbers | Draft contains coef/se/n not present in step_06 `facts` |
| No fake literature | `verified_count=0` but author-year-journal rows appear as if published |
| Causal honesty | OLS-only run uses 导致/提高/LATE without design flag |
| Surgical | Unrelated steps, stats engine, or fallback tables rewritten without need |

---

## Follow-ups (out of this diff)

- Wave B skill file `.claude/skills/econ-academic-writing/SKILL.md` still not on disk.  
- Bind results magnitudes to `verification_manifest` claim IDs when that artifact lands.  
- Optionally thicken `_fallback_paper` only if LLM-off path still fails `too_thin` after prompt graft.
