# Research material decision ledger

This ledger separates research value from product dependency. None of these
directories is required to run econpaper; U1 preserves all of them while the
owner resolves the genuinely research-specific decisions.

## Papers

| Candidate | Evidence | Risk | Executor recommendation |
|-----------|----------|------|-------------------------|
| `CGSS_Internet_Happiness` (13 MB; 41 retained files) | Finished eight-page Chinese paper, reproducible pipeline, 26/26 hash verification, explicit association-only claim boundary | Includes an 11.9 MB harmonized 79,014-row respondent dataset; must remain private and outside product Git | **Owner approved and applied:** moved to `materials/papers/`; reproducible build logs, LaTeX auxiliaries, and Python cache removed |
| `StatspAI_第二个样例_最低工资消费效应` (20 MB, 83 files) | Contains a manuscript and workflow artifacts | The stated 2012 DID uses only 2018 and 2022 observations, both post-treatment; the two main pickle artifacts are identical-size generated data and the causal claim is not identified | **Owner approved and applied:** entire sample deleted; it was not promoted as a fixture or research result |
| `StatspAI_跑通一次_CHARLS_DID` (42 MB, 508 files) | Substantial manuscript, scripts, tables, policy timing material, and honest limitation that insurer-type differences are not a full provincial rollout design | Dirty local Git repo with 29 modified and extensive untracked content; sample pickles may contain restricted respondent-level data; no remote exists | **Owner approved and applied:** deleted because there is no current paper-continuation or private product-acceptance use; U1 recovery carries the dormant history |

## Non-paper containers

| Candidate | Decision reason | Recommendation |
|-----------|-----------------|----------------|
| `agent_paper/` | Generated method-demo papers and a parallel server/CLI; product behavior is covered by U3 | Delete |
| root `docs/product/`, `CODE_WIKI.md`, `DEVLOG.md` | Describe the retired legacy product and absolute paths; current product docs and ADRs supersede them | Delete |
| root `docs/memory/` | Tool/user preference notes belong to the agent memory system, not this workspace | Delete |
| root `docs/how-to-read-a-paper.md` | Near-verbatim copy of a third-party paper, unrelated to product operation | Delete |
| root `scratch/`, `.workbuddy/` | Temporary planning/prototype artifacts with no current product consumer | Delete after stale-reference scan |

## Product-owned items already consolidated

- Root `DESIGN.md` moved to `econpaper/DESIGN.md`.
- The current product landscape moved to
  `econpaper/docs/strategy/product-landscape-2026-08-13.md`.
- The recent journey image moved to
  `econpaper/docs/assets/econpaper-journey-step-1.png` after visual review found
  no credentials or personal data.
