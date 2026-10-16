# Deferred checks after branch consolidation

The user requested repository consolidation and local removal on 2026-10-17,
then explicitly deferred functional checking and fixes until development resumes.
The seven previously unmerged fixes were preserved in main without new product
code changes. These are review hypotheses, not reproduced failures.

Independent Claude review of `786ef4e5..0480d15` returned REJECT with two concerns:

- In `agent/engine/did_spec.py`, generic columns such as `did`, `treat`, or
  `period` may override a confirmed design's explicitly named treated/period
  columns. Reproduce with both generic and explicitly selected columns and
  inspect the actual estimation formula.
- In `agent/design/propose_data.py` and `backend/routers/design.py`, failed model
  mapping can clear the DiD slots and reject the draft before the user can
  choose real columns. The frontend currently does not submit design overrides.
  Reproduce with an unavailable generate model and inspect the visible recovery
  path before deciding on a fix.

Full provider behavior, analysis, writing, and export were not verified in this
cleanup session. Review output and the exact reviewed diff are in the private
local recovery directory; no provider credentials were read.
