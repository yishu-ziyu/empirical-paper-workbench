# Private pilot auth focused evidence

Date: 2026-09-08. Worktree: `deploy/private-pilot`, based on main `c02eb05a12b99a435def10ba613eb99c5ac18201`. These runs exercised uncommitted pilot changes; the final deployment source SHA is recorded separately at delivery.

## Environment and commands

Working directory: `/Users/mahaoxuan/Desktop/经济学论文/econpaper-private-pilot`.

Interpreter: `/Users/mahaoxuan/Desktop/经济学论文/econpaper/backend/.venv/bin/python` (Python 3.12). The existing interpreter was used only for focused development tests, not as a deployment/image dependency. Repository root pytest configuration imports the pilot worktree's source. The test configuration uses temporary state and database paths. No real provider request was made.

Before the auth implementation changes, after adding the initial four regression tests:

```sh
../econpaper/backend/.venv/bin/python -m pytest backend/tests/test_private_pilot_auth.py -q --tb=short
```

Observed: **4 failed in 1.59s**. All four failures were expected status `401`, actual status `200`:

| Regression | Failing behavior observed |
|---|---|
| Production anonymous `POST /sessions` | Created an empty session without an authenticated owner |
| Refresh token used as Bearer on `/auth/me` | Authenticated as an access token |
| Rotated refresh token after clearing process revocation memory | Old token renewed successfully |
| Logged-out refresh token after clearing process revocation memory | Logged-out token renewed successfully |

After the auth implementation changes, with the same four regressions plus existing auth suites:

```sh
../econpaper/backend/.venv/bin/python -m pytest backend/tests/test_private_pilot_auth.py backend/tests/test_auth.py backend/tests/test_auth_upgrade.py -q --tb=short --show-capture=no
```

Observed: **40 passed, 38 warnings in 18.21s**.

After adding four further focused checks:

```sh
../econpaper/backend/.venv/bin/python -m pytest backend/tests/test_private_pilot_auth.py -q --tb=short --show-capture=no
```

Observed: **8 passed, 7 warnings in 2.88s**. Warnings were the existing `python-jose` use of deprecated `datetime.utcnow()`.

## What the additional checks establish

- WebSocket token resolver rejects a refresh token with `401` before a user database lookup.
- DEBUG anonymous session creation remains available.
- Six concurrent sessions using separate connections to one temporary SQLite database attempt to consume the same refresh identifier: exactly one succeeds and five are rejected by the database uniqueness constraint.
- Two separately launched Python processes use one temporary SQLite database: the first consumes and commits a token identifier, and the second rejects it. This establishes persistence beyond Python process memory, without retaining or printing raw tokens.

`git diff --check` passed after the changes. Refresh Cookie path remained `/auth`; these tests do not reproduce or accept the Nginx/browser cookie-path fix.

## Limits and deployment implications

These are focused route/database checks, not real browser acceptance, a full research journey, PostgreSQL concurrency evidence, or service/container restart acceptance. Those remain separate checks in the deployment contract.

The new `refresh_revocations` table is additive and registered with existing `create_tables` bootstrap. Raw JWTs and API credentials are not stored in it. Old revocations held only in a previous version's process memory cannot be recovered into this table. An upgrade retaining previously issued credentials must account for that gap by invalidating old JWTs or waiting for their expiry; a fresh isolated pilot has no such old credential population.

Logout retains the existing short-lived access-token semantics: clearing browser cookies and persistently preventing refresh renewal does not revoke an already copied access token before its expiry.
