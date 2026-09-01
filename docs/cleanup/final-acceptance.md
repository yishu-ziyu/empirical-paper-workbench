# Workspace cleanup acceptance

Date: 2026-09-01

## Final workspace contract

The workspace now has one product checkout, one proven source dependency, and
one explicit private-material boundary:

```text
经济学论文/
├── README.md
├── econpaper/
├── dependencies/StatsPAI/
├── materials/papers/CGSS_Internet_Happiness/
├── .agents/
├── .claude/
└── skills-lock.json
```

The hidden skill directories remain because the current workspace loader uses
them. The CGSS material remains outside the product Git repository and is
owner-only. All product runtime state now lives under ignored `.local/` paths.

## Removed

- The retired CLI checkout, its four linked worktrees, and nested repositories.
- Duplicate StatsPAI and AERS references, `stata-code`, `agent-skills`, and the
  superseded `agent_paper` prototype.
- The invalid minimum-wage DID case and the no-longer-used CHARLS paper case.
- Root caches, scratch output, stale task state, orphan `node_modules`, old
  workspace documents, and 38 tracked execution-handoff documents.
- Generated root/product/backend databases, uploads, runs, sessions, caches,
  and learning labels after their test provenance was established.

No permanent archive directory was created.

## Acceptance evidence

- StatsPAI retained revision: `a98b6743cc797ddd9cc33de1772c3ea3e3f0c394`.
- Both Python environments import the editable StatsPAI source from
  `dependencies/StatsPAI/`.
- Agent suite: 792 passed, 1 skipped after final review fixes.
- Backend suite: 284 passed, 7 skipped after final review fixes.
- Frontend suite: 269 passed.
- OpenAPI drift check passed.
- A real frontend, backend, and Agent startup passed with removed directories
  absent.
- `make verify` now rejects missing services, an unrelated process on the
  frontend port, a backend with the wrong OpenAPI identity, and an editable
  StatsPAI source that does not match the workspace dependency contract.

## Recovery status

The owner accepted the final layout and retained CGSS material on 2026-09-01.
The encrypted recovery sparsebundle, its Keychain credential, and the now-empty
recovery container directory were permanently deleted. Follow-up checks confirm
that neither the bundle nor the credential remains.
