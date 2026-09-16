"""Optional EVAL-top5 offline harness.

Not a product runtime module. Session boot, FIND, attach, estimate, and
export must not import this file. classic-5 catalog ids are never gold.

Enable (offline; default product path never does this):

    ECONPAPER_EVAL_TOP5=1 python eval/harness.py --offline

Absent submodule checkout is not a product failure (status=set_absent).
This harness does not read gold chapter bodies and does not unlock sessions.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

EVAL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EVAL_ROOT.parent
SLOTS_PATH = EVAL_ROOT / "slots.json"
SET_DIR = EVAL_ROOT / "top5-set"
POINTER_PATH = EVAL_ROOT / "top5-set.submodule"
FLAG = "ECONPAPER_EVAL_TOP5"
ENABLE_VALUES = frozenset({"1", "true", "yes", "on"})
MAX_SLOTS = 5

# Catalog / farm identities that must never unlock EVAL-top5 gold.
FORBIDDEN_GOLD_IDS = frozenset(
    {
        "classic-5",
        "ck1994",
        "ck1994_long",
        "barro1991_growth",
        "schooling-wages",
        "trade-local-labor",
        "fiscal-output",
        "health-labor-supply",
        "minimum-wage-employment",
        "undergrad_did_01",
        "card_1995",
        "card1995",
    }
)

FORBIDDEN_MANIFEST_KEYS = frozenset(
    {
        "gold_body",
        "gold_bodies",
        "gold_biblio",
        "answer_key",
        "catalog_id",
        "catalog_entry_id",
        "p_hack",
        "phack",
        "ppt",
        "pptx",
        "xhs",
    }
)


class CatalogGoldError(ValueError):
    """Raised when classic-5 / farm identity is offered as eval gold."""


class ScopeError(ValueError):
    """Raised when the set exceeds the top-5 cap or carries OUT surfaces."""


def flag_enabled(environ: Mapping[str, str] | None = None) -> bool:
    env = os.environ if environ is None else environ
    return str(env.get(FLAG, "")).strip().lower() in ENABLE_VALUES


def refuse_catalog_gold(identity: str | None) -> None:
    token = (identity or "").strip()
    if not token:
        return
    lowered = token.lower()
    for forbidden in FORBIDDEN_GOLD_IDS:
        needle = forbidden.lower()
        if lowered == needle or lowered.startswith(needle + "/"):
            raise CatalogGoldError(
                f"{token!r} is not EVAL-top5 gold "
                "(catalog/farm identity cannot unlock sessions)"
            )


def load_slots(path: Path | None = None) -> dict[str, Any]:
    data = json.loads((path or SLOTS_PATH).read_text(encoding="utf-8"))
    if data.get("eval_id") != "EVAL-top5":
        raise ScopeError("scaffold eval_id must be EVAL-top5")
    if data.get("catalog_answer_key") is not False:
        raise ScopeError("scaffold must declare catalog_answer_key=false")
    if data.get("gold_body_reads") is not False:
        raise ScopeError("scaffold must declare gold_body_reads=false")
    if data.get("product_runtime") is not False:
        raise ScopeError("scaffold must declare product_runtime=false")
    slots = data.get("slots")
    if not isinstance(slots, list) or len(slots) != MAX_SLOTS:
        raise ScopeError(f"EVAL-top5 scaffold must declare exactly {MAX_SLOTS} slots")
    for slot in slots:
        if not isinstance(slot, str):
            raise ScopeError("scaffold slots must be opaque string ids")
        refuse_catalog_gold(slot)
    return data


def set_present(set_dir: Path | None = None) -> bool:
    """True only when the optional submodule left a manifest in place."""
    return (set_dir or SET_DIR).joinpath("manifest.json").is_file()


def load_set_manifest(set_dir: Path | None = None) -> dict[str, Any] | None:
    manifest_path = (set_dir or SET_DIR) / "manifest.json"
    if not manifest_path.is_file():
        return None
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ScopeError("EVAL-top5 manifest must be an object")
    bad = FORBIDDEN_MANIFEST_KEYS.intersection(data)
    if bad:
        raise ScopeError(f"EVAL-top5 manifest must not carry {sorted(bad)}")
    eval_id = data.get("eval_id")
    if eval_id is not None and eval_id != "EVAL-top5":
        refuse_catalog_gold(str(eval_id))
        raise ScopeError(f"unexpected eval_id {eval_id!r}")
    slots = data.get("slots")
    if not isinstance(slots, list) or not 1 <= len(slots) <= MAX_SLOTS:
        raise ScopeError(f"EVAL-top5 set must have 1..{MAX_SLOTS} slots, not a farm")
    for item in slots:
        if isinstance(item, str):
            refuse_catalog_gold(item)
            continue
        if not isinstance(item, dict):
            raise ScopeError("slot must be a string id or object")
        bad_item = FORBIDDEN_MANIFEST_KEYS.intersection(item)
        if bad_item:
            raise ScopeError(f"slot must not carry {sorted(bad_item)}")
        for key in ("id", "gold", "catalog_id", "entry_id"):
            value = item.get(key)
            if value is not None:
                refuse_catalog_gold(str(value))
    return data


def run(
    *,
    offline: bool = False,
    environ: Mapping[str, str] | None = None,
    set_dir: Path | None = None,
) -> dict[str, Any]:
    if not (offline or flag_enabled(environ)):
        return {
            "status": "skipped",
            "reason": "EVAL-top5 is optional and off the product runtime path",
            "how": f"{FLAG}=1 python eval/harness.py --offline",
            "product_runtime": False,
            "catalog_answer_key": False,
        }
    load_slots()
    manifest = load_set_manifest(set_dir)
    if manifest is None:
        return {
            "status": "set_absent",
            "reason": "optional submodule not checked out; product is fine",
            "pointer": str(POINTER_PATH.relative_to(REPO_ROOT)),
            "product_runtime": False,
            "catalog_answer_key": False,
        }
    return {
        "status": "ok",
        "eval_id": "EVAL-top5",
        "slots": len(manifest["slots"]),
        "gold_body_reads": False,
        "catalog_answer_key": False,
        "product_runtime": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Optional EVAL-top5 offline harness. Not product runtime."
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help=(
            f"Run the optional check (same as {FLAG}=1). "
            "Missing set is not a product failure."
        ),
    )
    args = parser.parse_args(argv)
    try:
        result = run(offline=args.offline)
    except (CatalogGoldError, ScopeError, json.JSONDecodeError, OSError) as exc:
        json.dump({"status": "refused", "reason": str(exc)}, sys.stdout)
        sys.stdout.write("\n")
        return 2
    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
