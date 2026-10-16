# Main and worktree consolidation

Status: in progress

## Observable result

GitHub and the local repository have one branch, `main`, and the local repository
has one worktree. Main contains the previous local changes, the current GitHub
main, all eight remote branch tips, and the equivalent DevSpace history.
Research materials, evidence, local configuration, and existing environments stay
in the primary directory.

## Evaluation

- Save and verify a Git bundle plus a hash manifest and archive of the 32 local
  changed/untracked files before merging.
- Verify every original commit tip is an ancestor of final main before deleting
  its branch or worktree. Keep historical archive tags.
- Review the exact candidate commit independently; resolve material findings.
- Exercise the running application with isolated state: upload Stata data, edit
  a design using real columns, apply sample operations, and check the resulting
  analysis state. Check affected existing behavior and rejected input.
- Deliberately make the end-to-end check fail once before accepting its result.
- Run documentation and API consistency checks and the frontend build.
- After pushing, verify GitHub main and its branch list independently. Remove the
  unused, clean DevSpace worktree only after verifying preservation and no open
  process handles. Verify the final worktree list and disk usage.

## Boundaries

No force push, rewritten history, dependency upgrade, provider credential access,
production deployment, or deletion of research/user data. Do not treat mock model
responses as proof of a live model provider. Record unverified provider behavior.

## Evidence

Local recovery bundle and original file hashes:
`~/Archives/disk-cleanup-records/20261017-empirical-main-consolidation/`.

Results will be appended after the checks finish.
