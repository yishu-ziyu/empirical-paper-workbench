#!/usr/bin/env python3
"""Require the human-only parts of the econpaper PR handoff.

Machine facts such as SHAs and changed files are emitted by CI itself. This
check only guards the four fields that require a person/agent to state what was
done, what was actually run, and what remains uncertain.
"""

from __future__ import annotations

import os
import re
import sys


FIELDS = {
    "what_changed": "What changed",
    "runtime_evidence": "Runtime evidence",
    "known_gaps": "Known gaps or disagreements",
    "facts_vs_requests": "Facts vs requests",
}


def _content(body: str, key: str) -> str | None:
    pattern = re.compile(
        rf"<!--\s*handoff:{re.escape(key)}\s*-->(.*?)"
        rf"<!--\s*/handoff:{re.escape(key)}\s*-->",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(body)
    if match is None:
        return None
    value = re.sub(r"<!--.*?-->", "", match.group(1), flags=re.DOTALL).strip()
    return value if re.search(r"[\w\u3400-\u9fff]", value) else ""


def main() -> int:
    body = os.environ.get("PR_BODY", "")
    missing = [label for key, label in FIELDS.items() if not _content(body, key)]
    if missing:
        print("PR handoff is incomplete. Fill these marked sections:")
        for label in missing:
            print(f"- {label}")
        return 1
    print("PR handoff fields are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
