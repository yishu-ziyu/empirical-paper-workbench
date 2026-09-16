# EVAL-top5 (optional, offline)

V1 evaluation for DECIDE-8 **top5 eval only**. This directory is a harness
plus a submodule stub. It is **not** the product catalog, **not** a session
answer key, and **not** on the default runtime path.

Contract: `docs/bryce-tools-contract.md` §2.4 / §4.4 / §7.4.
How to run: `docs/eval-top5.md`.

## What this is

- Scope cap: five slots (`slots.json`). No eval farm.
- Optional checkout: `eval/top5-set/` via `top5-set.submodule`.
- Offline flag: `ECONPAPER_EVAL_TOP5=1`.

## What this is not

- Not `fixtures/classic-5/` and not `ck1994` / `barro1991_growth` gold.
- Not `agent/eval/tasks/undergrad_did_01` and not Card 1995 as the V1 set.
- Not a p-hack helper, ppt, or 小红书 (xhs) emitter.
- Not imported by `agent/` or `backend/` on product boot.

## Run offline

Default (no flag): skip. Product is unchanged.

```bash
python eval/harness.py
# {"status":"skipped", ...}

ECONPAPER_EVAL_TOP5=1 python eval/harness.py --offline
# {"status":"set_absent", ...}  when the submodule is not checked out (OK)
```

Tests (not part of `make test`):

```bash
cd eval && python -m pytest -q
```

Missing `eval/top5-set/manifest.json` is not a product failure.
