# Main and worktree consolidation

Status: content consolidated; remote verification precedes local removal

## Observable result

GitHub retains one branch, `main`, containing the previous local changes, the
current GitHub main, all eight remote branch tips, and the equivalent DevSpace
history. The user subsequently requested deletion of the local project after
verifying that GitHub contains the final commit and tree. Local-only research
materials, evidence, configuration, and state go into a private local recovery
directory before removing the project and the unused DevSpace worktree.

## Evaluation

- Save and verify a Git bundle plus a hash manifest and archive of the 32 local
  changed/untracked files before merging.
- Verify every original commit tip is an ancestor of final main before deleting
  its branch or worktree. Keep historical archive tags.
- Preserve the independent review findings for the next development session.
  The user explicitly deferred functional checking and fixes on 2026-10-17.
- After pushing, verify GitHub main and its branch list independently. Remove the
  local project and unused, clean DevSpace worktree only after verifying their
  committed content is preserved and no active processes use them. Record the
  final filesystem state and disk usage outside the removed project.

## Boundaries

No force push, rewritten history, dependency upgrade, provider credential access,
production deployment, or loss of research/user data. Do not treat mock model
responses as proof of a live model provider.

## Evidence

Local recovery bundle and original file hashes:
`~/Archives/disk-cleanup-records/20261017-empirical-main-consolidation/`.

Before scope was narrowed, documentation checks and the frontend build passed.
A real browser uploaded a generated Stata file (120 rows); ingestion reached
ready. No full functional acceptance was completed or claimed. Temporary
application services were stopped. Review follow-ups are recorded in
`docs/notes/20261017-consolidation-followups.md`.

Final remote checks and local deletion measurements are recorded in the recovery
directory because the local project itself is removed after verification.
