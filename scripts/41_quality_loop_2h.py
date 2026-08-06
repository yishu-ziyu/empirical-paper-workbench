#!/usr/bin/env python3
"""2-hour quality-first Continuous Loop runner.

propose → run continuous-loop → score evaluator → keep best → repeat until end time.
Uses Grok 4.5 by default. Does not stop on soft reds; keeps pushing.

Usage:
  PYTHONPATH=. python3 scripts/41_quality_loop_2h.py --hours 2 --max-inner-rounds 3
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=2.0)
    ap.add_argument("--max-inner-rounds", type=int, default=3)
    ap.add_argument("--provider", default="grok")
    ap.add_argument("--model", default="grok-4.5")
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--pi-assist", action="store_true")
    ap.add_argument("--sleep-between", type=float, default=5.0)
    args = ap.parse_args()

    hour_dir = ROOT / ".hour-loop"
    hour_dir.mkdir(parents=True, exist_ok=True)
    archive = ROOT / "state" / "evolve_archive"
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=float(args.hours))
    meta = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "provider": args.provider,
        "model": args.model,
    }
    (hour_dir / "quality_loop_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log_path = hour_dir / "quality_loop_2h.jsonl"
    print(f"⏱ Quality loop until {end.isoformat()}  provider={args.provider} model={args.model}")

    iteration = 0
    while datetime.now(timezone.utc) < end:
        iteration += 1
        remaining = (end - datetime.now(timezone.utc)).total_seconds()
        print(f"\n======== OUTER ITER {iteration}  remaining={remaining/60:.1f}min ========")
        row: dict = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "iteration": iteration,
            "remaining_sec": remaining,
        }
        try:
            from runtime.continuous_loop import ContinuousEmpiricalLoop
            from runtime.evolve_evaluator import maybe_update_best, score_package

            loop = ContinuousEmpiricalLoop(
                max_rounds=int(args.max_inner_rounds),
                use_llm=not args.no_llm,
                provider_id=args.provider,
                model=args.model,
                use_pi_assist=bool(args.pi_assist),
            )
            result = loop.run()
            state = {
                "status": result.status,
                "loop_id": result.loop_id,
                "final_verdict": result.final_verdict,
                "package": result.package,
            }
            sc = score_package(loop_state=state)
            sc = maybe_update_best(sc, archive)
            row.update(
                {
                    "ok": True,
                    "loop_id": result.loop_id,
                    "status": result.status,
                    "score": sc.score,
                    "better_than_best": sc.better_than_best,
                    "components": sc.components,
                    "package": result.package,
                    "pdf": result.package.get("pdf"),
                }
            )
            print(
                f"→ status={result.status} score={sc.score} better={sc.better_than_best} pdf={result.package.get('pdf')}"
            )
        except Exception as exc:  # noqa: BLE001
            row.update({"ok": False, "error": str(exc), "trace": traceback.format_exc()[-2000:]})
            print(f"→ FAIL {exc}")

        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        (hour_dir / "quality_loop_latest.json").write_text(
            json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        if datetime.now(timezone.utc) >= end:
            break
        time.sleep(max(0.0, float(args.sleep_between)))

    print(f"\n⏹ Quality loop finished after {iteration} outer iterations. Log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
