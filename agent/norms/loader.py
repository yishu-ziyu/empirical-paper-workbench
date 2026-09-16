"""Load NORMS-BE yaml gates and evaluate them. Missing yaml fails closed.

Not a Claude skill runner. Unknown gate ids fail closed.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

import yaml

from agent.design.spec import norm_method
from agent.find_lit.chapter_gate import literature_write_blockers
from agent.find_lit.query import design_is_confirmed, session_design

GATES_DIR = Path(__file__).resolve().parent
DESIGN_GATES_FILE = "design_gates.yaml"
CHAPTER_GATES_FILE = "chapter_gates.yaml"
GATES_MISSING = "gates_missing"

# Distilled ceiling (DECIDE-8 §4.3). Tests pin these ids so the yaml
# cannot silently shrink. Not a floor to expand.
DESIGN_GATE_IDS = (
    "draft_not_locked",
    "did_requires_treated_period",
    "het_requires_interaction",
    "catalog_not_design_lock",
    "no_skill_runner",
)
CHAPTER_GATE_IDS = (
    "did_requires_treated_period",
    "het_requires_interaction",
    "data_attached",
    "clean_winsor_audit",
    "table1_confirmed",
    "spec_confirmed",
    "identification_recorded",
    "robustness_recorded",
    "r_lit_bar",
    "export_allowed_formats",
    "no_skill_runner",
    "no_phack",
)

_DEFAULT_EXPORT = ("tex", "pdf", "docx", "py", "do", "R", "m")
_FORBIDDEN_EXPORT = frozenset({"ppt", "pptx", "xhs", "小红书"})

SKILL_RUNNER = False


class GatesMissing(FileNotFoundError):
    """Yaml gate file is absent. Fail closed; do not skip."""

    code = GATES_MISSING


def load_gates(filename: str, *, gates_dir: Path | None = None) -> dict[str, Any]:
    path = (gates_dir or GATES_DIR) / filename
    if not path.is_file():
        raise GatesMissing(filename)
    with path.open(encoding="utf-8") as fh:
        payload = yaml.safe_load(fh) or {}
    if not isinstance(payload, dict) or not payload.get("gates"):
        raise GatesMissing(filename)
    return payload


def assert_propose_gates(
    design: Mapping[str, Any] | None,
    *,
    extra: Mapping[str, Any] | None = None,
    gates_dir: Path | None = None,
) -> None:
    """Propose hook. Yaml missing or hard-block → ValueError (fail closed)."""
    try:
        blockers = design_gate_blockers(design, extra=extra, gates_dir=gates_dir)
    except GatesMissing as exc:
        raise ValueError(GATES_MISSING) from exc
    if blockers:
        raise ValueError(blockers[0])


def design_gate_blockers(
    design: Mapping[str, Any] | None,
    *,
    extra: Mapping[str, Any] | None = None,
    gates_dir: Path | None = None,
) -> list[str]:
    spec = load_gates(DESIGN_GATES_FILE, gates_dir=gates_dir)
    ctx = _context(design=design, extra=extra)
    return _evaluate(spec, ctx, _DESIGN_CHECKS)


def chapter_write_blockers(
    state: Mapping[str, Any] | None,
    chapter_type: str = "",
    *,
    extra: Mapping[str, Any] | None = None,
    gates_dir: Path | None = None,
) -> list[str]:
    """Write hook. Yaml missing → ``gates_missing`` (fail closed, no skip)."""
    try:
        spec = load_gates(CHAPTER_GATES_FILE, gates_dir=gates_dir)
    except GatesMissing:
        return [GATES_MISSING]
    ctx = _context(state=state, chapter_type=chapter_type, extra=extra)
    return _evaluate(spec, ctx, _CHAPTER_CHECKS)


def _context(
    *,
    design: Mapping[str, Any] | None = None,
    state: Mapping[str, Any] | None = None,
    chapter_type: str = "",
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    extra = dict(extra or {})
    state_map = state if isinstance(state, dict) else {}
    if design is None:
        design = session_design(state_map) or {}
    design = design if isinstance(design, dict) else {}
    return {
        "design": design,
        "state": state_map,
        "chapter_type": str(chapter_type or extra.get("chapter_type") or ""),
        "export_format": extra.get("export_format", state_map.get("export_format")),
        "skill_runner": extra.get("skill_runner", SKILL_RUNNER),
        "phack": extra.get("phack", state_map.get("phack")),
        "allowed_export": None,
        "forbidden_export": None,
    }


def _evaluate(
    spec: Mapping[str, Any],
    ctx: dict[str, Any],
    checks: Mapping[str, Callable[[dict[str, Any]], list[str]]],
) -> list[str]:
    ctx["allowed_export"] = tuple(spec.get("allowed_export_formats") or _DEFAULT_EXPORT)
    ctx["forbidden_export"] = frozenset(
        str(item) for item in (spec.get("forbidden_export_formats") or _FORBIDDEN_EXPORT)
    )
    blockers: list[str] = []
    seen: set[str] = set()
    for gate in spec.get("gates") or []:
        if not isinstance(gate, dict):
            blockers.append("gates_malformed")
            continue
        gate_id = str(gate.get("id") or "")
        if not gate_id:
            blockers.append("gates_malformed")
            continue
        if not _when_matches(gate.get("when"), ctx):
            continue
        fn = checks.get(gate_id)
        if fn is None:
            code = f"unknown_gate:{gate_id}"
            if code not in seen:
                blockers.append(code)
                seen.add(code)
            continue
        for code in fn(ctx) or []:
            text = str(code or gate.get("blocker") or "")
            if text and text not in seen:
                blockers.append(text)
                seen.add(text)
    return blockers


def _when_matches(when: Any, ctx: dict[str, Any]) -> bool:
    if not when:
        return True
    if not isinstance(when, dict):
        return True
    design = ctx["design"]
    if "method" in when:
        if norm_method(design.get("method")) != str(when["method"]):
            return False
    if "qType" in when:
        if str(design.get("qType") or "").strip().lower() != str(when["qType"]):
            return False
    if when.get("confirmed_design") is True:
        if not design_is_confirmed(design):
            return False
    if "chapter" in when:
        if ctx["chapter_type"] != str(when["chapter"]):
            return False
    if when.get("export_format") == "present":
        if not str(ctx.get("export_format") or "").strip():
            return False
    return True


def _has_did_interaction(design: Mapping[str, Any]) -> bool:
    from services.allow_did import has_treated_period_interaction

    return has_treated_period_interaction(design)


def _has_het_interaction(design: Mapping[str, Any]) -> bool:
    groups = [
        str(item).strip()
        for item in (design.get("heterogeneity_groups") or [])
        if str(item).strip()
    ]
    if groups:
        return True
    for item in design.get("interactions") or []:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind") or "").strip().lower()
        if kind == "het":
            return True
        if kind == "did":
            continue
        term = str(item.get("term") or "")
        if any(mark in term for mark in (":", "*", "×", "x")):
            return True
        left = str(item.get("left") or "").strip()
        right = str(item.get("right") or "").strip()
        if left and right:
            return True
    return False


def _clean_winsor_recorded(state: Mapping[str, Any]) -> bool:
    report = state.get("cleaning_report")
    if not isinstance(report, dict):
        return False
    for step in report.get("steps") or []:
        if not isinstance(step, dict):
            continue
        if str(step.get("name") or "").strip() == "clean_winsor":
            return True
    return False


def _identification_recorded(state: Mapping[str, Any]) -> bool:
    diag = state.get("identification_diag")
    if not isinstance(diag, dict):
        return False
    if diag.get("report") not in (None, ""):
        return True
    if diag.get("diagnostics"):
        return True
    return bool(diag.get("produced_by"))


def _robustness_recorded(state: Mapping[str, Any]) -> bool:
    rob = state.get("robustness_results")
    if not isinstance(rob, dict):
        return False
    if rob.get("produced_by") == "robustness_check":
        return True
    return "diagnostics" in rob


def _check_draft_not_locked(ctx: dict[str, Any]) -> list[str]:
    design = ctx["design"]
    status = str(design.get("status") or "").strip().lower()
    if status != "draft" or design.get("confirmed") is True:
        return ["design_treated_as_locked"]
    return []


def _check_did_interaction(ctx: dict[str, Any]) -> list[str]:
    if _has_did_interaction(ctx["design"]):
        return []
    return ["did_missing_interaction"]


def _check_het_interaction(ctx: dict[str, Any]) -> list[str]:
    if _has_het_interaction(ctx["design"]):
        return []
    return ["het_missing_interaction"]


def _check_catalog_not_lock(ctx: dict[str, Any]) -> list[str]:
    if ctx["design"].get("catalog_entry_id"):
        return ["catalog_as_locked_spec"]
    return []


def _check_no_skill_runner(ctx: dict[str, Any]) -> list[str]:
    if ctx.get("skill_runner") or SKILL_RUNNER:
        return ["skill_runner_not_allowed"]
    return []


def _check_data_attached(ctx: dict[str, Any]) -> list[str]:
    if ctx["state"].get("dataAttached") is True:
        return []
    return ["data_not_attached"]


def _check_clean_winsor(ctx: dict[str, Any]) -> list[str]:
    if _clean_winsor_recorded(ctx["state"]):
        return []
    return ["clean_winsor_not_recorded"]


def _check_table1(ctx: dict[str, Any]) -> list[str]:
    if ctx["state"].get("table1Confirmed") is True:
        return []
    return ["table1_not_confirmed"]


def _check_spec(ctx: dict[str, Any]) -> list[str]:
    if ctx["state"].get("specConfirmed") is True:
        return []
    return ["spec_not_confirmed"]


def _check_identification(ctx: dict[str, Any]) -> list[str]:
    if _identification_recorded(ctx["state"]):
        return []
    return ["identification_not_recorded"]


def _check_robustness(ctx: dict[str, Any]) -> list[str]:
    if _robustness_recorded(ctx["state"]):
        return []
    return ["robustness_not_recorded"]


def _check_r_lit_bar(ctx: dict[str, Any]) -> list[str]:
    return list(literature_write_blockers(ctx["state"]))


def _check_export(ctx: dict[str, Any]) -> list[str]:
    raw = str(ctx.get("export_format") or "").strip()
    if not raw:
        return []
    allowed = {str(item) for item in (ctx.get("allowed_export") or _DEFAULT_EXPORT)}
    forbidden = ctx.get("forbidden_export") or _FORBIDDEN_EXPORT
    if raw in forbidden or raw not in allowed:
        return ["export_format_not_allowed"]
    return []


def _check_no_phack(ctx: dict[str, Any]) -> list[str]:
    if ctx.get("phack"):
        return ["phack_not_allowed"]
    return []


_DESIGN_CHECKS: dict[str, Callable[[dict[str, Any]], list[str]]] = {
    "draft_not_locked": _check_draft_not_locked,
    "did_requires_treated_period": _check_did_interaction,
    "het_requires_interaction": _check_het_interaction,
    "catalog_not_design_lock": _check_catalog_not_lock,
    "no_skill_runner": _check_no_skill_runner,
}

_CHAPTER_CHECKS: dict[str, Callable[[dict[str, Any]], list[str]]] = {
    "did_requires_treated_period": _check_did_interaction,
    "het_requires_interaction": _check_het_interaction,
    "data_attached": _check_data_attached,
    "clean_winsor_audit": _check_clean_winsor,
    "table1_confirmed": _check_table1,
    "spec_confirmed": _check_spec,
    "identification_recorded": _check_identification,
    "robustness_recorded": _check_robustness,
    "r_lit_bar": _check_r_lit_bar,
    "export_allowed_formats": _check_export,
    "no_skill_runner": _check_no_skill_runner,
    "no_phack": _check_no_phack,
}
