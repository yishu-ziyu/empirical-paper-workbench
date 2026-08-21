"""跑三位审稿人 × 两组对照，并把标签落到文件。

两组：
- see_auto：能看见机器打分（容易跟着机器走）
- blind：只看正文（独立判断）

用法：
    python -m eval.ab_review
    python -m eval.ab_review --no-llm
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# 允许直接 python agent/eval/ab_review.py
_AGENT_DIR = Path(__file__).resolve().parents[1]
if str(_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENT_DIR))

from eval.judge import judge
from eval.packets import all_packets
from eval.personas import persona_ids
from nodes.label_store import (
    ARM_BLIND,
    ARM_SEE_AUTO,
    REVIEWER_PERSONA,
    append_event,
    event_from_decision,
    summarize,
)


def run_ab(
    *,
    allow_llm: bool = True,
    persist: bool = True,
) -> Dict[str, Any]:
    events: List[Dict[str, Any]] = []
    for packet in all_packets():
        for persona in persona_ids():
            for see_auto in (False, True):
                verdict = judge(
                    persona,
                    packet,
                    see_auto=see_auto,
                    allow_llm=allow_llm,
                )
                state = {
                    **packet,
                    "hitl_decision": verdict["decision"],
                    "hitl_reviewer": f"persona:{persona}",
                    "hitl_comment": verdict["comment"],
                }
                event = event_from_decision(
                    state,
                    decision=verdict["decision"],
                    reviewer=f"persona:{persona}",
                    comment=verdict["comment"],
                    reviewer_kind=REVIEWER_PERSONA,
                    persona=persona,
                    ab_arm=ARM_SEE_AUTO if see_auto else ARM_BLIND,
                )
                event["packet_id"] = packet.get("packet_id")
                event["judge_source"] = verdict["judge_source"]
                if persist:
                    append_event(event)
                events.append(event)
    report = summarize(events)
    report["events"] = events
    see = report.get("by_arm", {}).get(ARM_SEE_AUTO, {})
    blind = report.get("by_arm", {}).get(ARM_BLIND, {})
    see_agree = see.get("agree_with_auto")
    blind_agree = blind.get("agree_with_auto")
    report["rubber_stamp"] = None
    if see_agree is not None and blind_agree is not None:
        report["rubber_stamp"] = round(see_agree - blind_agree, 3)
    return report


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="三位审稿代理对照")
    parser.add_argument("--no-llm", action="store_true", help="只用规则，不打模型")
    parser.add_argument("--no-persist", action="store_true", help="只打印，不落盘")
    parser.add_argument(
        "--report",
        default="",
        help="把摘要写到这个 json 文件",
    )
    args = parser.parse_args(argv)
    report = run_ab(allow_llm=not args.no_llm, persist=not args.no_persist)
    printable = {k: v for k, v in report.items() if k != "events"}
    printable["n_events"] = len(report["events"])
    text = json.dumps(printable, ensure_ascii=False, indent=2)
    print(text)
    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
