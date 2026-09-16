"""Guard: every backend runtime install path must declare pydantic-ai.

Why this test exists (issue #37): the typed review channel is reached through
``agent/nodes/review_chapter.py:build_review_agent``, which does a *lazy*
``from pydantic_ai import Agent`` inside a ``try`` and turns any exception into
``review_source="mock_fallback"`` + ``review_degraded=True``. A missing
dependency therefore never raises: the backend/runner process silently swaps
the real LLM review for mock output, even when a real key is configured.

``backend/runner`` and the container both run on the backend venv, so the
dependency has to be declared on every backend install path. A working local
venv cannot falsify the gap (the package is already installed here — that is
precisely why the degradation is invisible), so this guard asserts the
*declarations* instead: if any of the three places drops the pin, the test
fails and the silent downgrade cannot come back unnoticed.

Wired into `make test` through the regular `backend/tests` collection.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

DIST = "pydantic-ai-slim"
PIN = "2.35.3"
PINNED = f"{DIST}[openai]=={PIN}"


def _read(relative: str) -> str:
    path = REPO_ROOT / relative
    assert path.is_file(), f"expected {relative} in the checkout"
    return path.read_text(encoding="utf-8")


def _declared_pins(text: str) -> tuple[set[str], list[str]]:
    """(pinned versions, unpinned mentions) of pydantic-ai-slim in a file.

    Comments are stripped first, so a prose mention in a comment is not a
    declaration. An unpinned mention (``pydantic-ai-slim`` without ``==``) is
    reported separately: it would float the version past the pin.
    """
    pattern = re.compile(
        rf"^{re.escape(DIST)}(?:\[[^\]]*\])?==([0-9][^\s#]*)", re.IGNORECASE
    )
    pins: set[str] = set()
    unpinned: list[str] = []
    for line in text.splitlines():
        stripped = line.split("#", 1)[0].strip()
        if not stripped.lower().startswith(DIST):
            continue
        match = pattern.match(stripped)
        if match:
            pins.add(match.group(1))
        else:
            unpinned.append(stripped)
    return pins, unpinned


def _makefile_target(name: str) -> str:
    """Recipe body of a Makefile target (up to the next target definition)."""
    lines = _read("Makefile").splitlines()
    body: list[str] = []
    inside = False
    for line in lines:
        if re.match(rf"^{re.escape(name)}\s*:", line):
            inside = True
            body.append(line)
            continue
        if not inside:
            continue
        if line.strip() and not line[0].isspace():
            break
        body.append(line)
    assert body, f"Makefile target {name!r} not found"
    return "\n".join(body)


def test_backend_requirements_declares_the_pin():
    pins, unpinned = _declared_pins(_read("backend/requirements.txt"))
    assert pins == {PIN}, (
        f"backend/requirements.txt must declare {PINNED} (found pins: {sorted(pins)})"
    )
    assert unpinned == [], (
        f"backend/requirements.txt has an unpinned {DIST} mention: {unpinned}"
    )


def test_agent_pin_matches_backend_pin():
    agent_pins, unpinned = _declared_pins(_read("agent/requirements.txt"))
    assert agent_pins == {PIN}, f"agent/requirements.txt drift: {sorted(agent_pins)}"
    assert unpinned == [], (
        f"agent/requirements.txt has an unpinned {DIST} mention: {unpinned}"
    )


def test_makefile_install_backend_installs_the_dependency():
    target = _makefile_target("install-backend")
    install_lines = [line for line in target.splitlines() if "pip install" in line]
    assert any(PINNED in line for line in install_lines), (
        f"`make install-backend` must install {PINNED}; "
        f"pip lines seen: {install_lines}"
    )


def test_dockerfile_dependency_layer_installs_the_dependency():
    text = _read("backend/Dockerfile")
    source_copy = "COPY backend/ ./backend/"
    assert source_copy in text, (
        "Dockerfile source-copy anchor moved; update this guard so the "
        "dependency layer is still the slice inspected here"
    )
    dependency_layer = text.split(source_copy)[0]
    pip_lines = [
        line for line in dependency_layer.splitlines() if "pip install" in line
    ]
    assert pip_lines, "Dockerfile dependency layer no longer installs anything"
    assert any(PINNED in line for line in pip_lines), (
        f"backend/Dockerfile dependency layer must install {PINNED}; "
        f"pip lines seen: {pip_lines}"
    )


@pytest.mark.parametrize("relative", ["Makefile", "backend/Dockerfile"])
def test_no_unpinned_mention_on_the_install_paths(relative: str):
    """No second, unpinned spelling of the distribution on the same paths."""
    text = _read(relative)
    mentions = [
        line.strip()
        for line in text.splitlines()
        if DIST in line and not line.strip().startswith("#")
    ]
    assert mentions, f"{relative} never mentions {DIST}"
    for mention in mentions:
        assert PINNED in mention, f"{relative} has an unpinned {DIST} mention: {mention}"


def test_review_channel_still_degrades_silently():
    """The rationale of this guard, pinned to the code it protects.

    If review_chapter.py stops swallowing the ImportError (or stops importing
    pydantic_ai lazily), this test should be revisited together with the guard
    set above — a loud failure would make a missing declaration visible.
    """
    source = _read("agent/nodes/review_chapter.py")
    assert "from pydantic_ai import Agent" in source
    assert '"review_source": "mock_fallback"' in source
    assert "except Exception" in source
