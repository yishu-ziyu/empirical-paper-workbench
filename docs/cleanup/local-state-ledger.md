# Local state provenance and disposition ledger

U1 encrypted every source store before classification. U5 then evaluated the
content rather than relying on directory names.

## Provenance decision

No retained user state was found in the old cohorts:

| Old cohort | Current count | Reproducible provenance | Decision |
|------------|---------------|-------------------------|----------|
| root/product/backend SQLite databases | 103 / 787 / 275 users | Every email or username matches the auth-test generators, including `@example.com`, `@test.com`, `test*`, and the invalid-email cases | Generated test output; delete |
| root/product/backend uploads | 104 / 1,161 / 1,974 files | Every filename is the UUID or UUID-plus-`.cleaned` form emitted by upload tests | Generated test output; delete |
| root/product/backend runs | 307 / 1,930 / 1,468 run directories | UUID sessions, upload-test source names, test-database owner ids, and run-artifact fixtures; no named research source | Generated test output; delete |
| `backend/data/sessions.json` | zero sessions, zero degradations | Empty SessionStore bootstrap payload | Generated empty state; delete |
| `data/learning_labels.jsonl` | 543 events | Test-review session ids and fixed test reviewers/comments (`alice`, `bob`, `carol`, `human`, `ok`, `good`) | Generated test output; delete |

The counts above were taken after U3 verification. U1 preserves the earlier
snapshot; the increase is explained by tests that ran before U5 isolated their
state paths.

## Canonical local layout

```text
econpaper/.local/
├── db/econpaper.db
├── uploads/
├── runs/
├── sessions/sessions.json
├── cache/s3/
└── learning/learning_labels.jsonl
```

`ECONPAPER_LOCAL_STATE_ROOT` can replace the root with an absolute local path.
Individual production overrides remain supported. Docker continues to use
PostgreSQL and `/data/{uploads,runs,sessions}`; it does not inherit host
`.local` paths.

Directories are created or repaired to mode `0700`; written state files are
repaired to `0600`. `.local/` is ignored by Git. Pytest now assigns database,
uploads, runs, sessions, cache, and learning labels to a per-run temporary root,
so rerunning the suite cannot repopulate the workspace.
