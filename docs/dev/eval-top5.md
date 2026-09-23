# EVAL-top5 — optional offline eval (not product catalog)

Status: optional scaffold (`FM-E-BUILD-BRYCE-1` / **EVAL-top5**)  
Product line: formal econpaper only  
Contract: `docs/contracts/bryce-tools-contract.md` §2.4, §4.4, §7.4 (this file does not rewrite that contract)

## What landed

A repo-root `eval/` harness and a **submodule stub**. The product does not
register this as a git submodule, does not vendor a set into
`fixtures/classic-5/`, and does not grow `agent/eval/tasks/`.

| Object | Role |
|---|---|
| `eval/harness.py` | Offline CLI. Default is skip. |
| `eval/slots.json` | Five opaque slot names. Not catalog ids. |
| `eval/top5-set.submodule` | Pointer for a future `git submodule add`. |
| `eval/top5-set/manifest.json` | Present only after optional checkout. |

`classic-5` stays FIND/DATA-COMPLETE **candidates**. EVAL-top5 is a different
object. Catalog identity is never an answer key and never a session gold unlock.

## Keep it off the product path

- `make dev`, `make test`, `make verify`, and session boot **do not** run this
  harness and **do not** require `eval/top5-set/`.
- `pytest.ini` `testpaths` remain `agent/tests backend/tests`.
- Enable only with an explicit flag:

```bash
python eval/harness.py
# status=skipped

ECONPAPER_EVAL_TOP5=1 python eval/harness.py --offline
# status=set_absent  if the submodule is not checked out (not a product failure)
# status=ok          if eval/top5-set/manifest.json is present and in scope
```

Harness tests (optional; not `make test`):

```bash
cd eval && python -m pytest -q
```

## When the set exists

```bash
git submodule add <EVAL-top5-remote-url> eval/top5-set
```

The checkout must ship `manifest.json` with **at most five** slots. It must
not include gold chapter bodies, classic-5 catalog ids as gold, p-hack
helpers, or ppt / 小红书 (xhs) outputs.

## Refusals (unacceptable substitutes)

- Using `ck1994`, `ck1994_long`, `barro1991_growth`, or other classic-5 ids
  as EVAL-top5 gold
- Treating Card 1995 or `agent/eval/tasks/undergrad_did_01` as the V1 set
- Vendoring the set into `fixtures/classic-5/`
- Making the submodule required for product boot
- Scoring by gold-body reads
