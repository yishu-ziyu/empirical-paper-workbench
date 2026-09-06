"""Research lab blob in ResearchSession.state (backend truth owner).

Objects live under ``state.research_lab``. Snapshot and GET /research
project the same public model. LangGraph raw state is not exposed.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException

from schemas.responses import ResearchLabResponse


CARD_TEACHING_CASE = "card_1995"
CARD_CITATION = (
    "Card, D. (1995). Using Geographic Variation in College Proximity "
    "to Estimate the Return to Schooling."
)
CARD_REDISTRIBUTION = (
    "runtime load from StatsPAI dependency, no second public copy"
)
REQUIRED_CARD_COLUMNS = (
    "lwage",
    "educ",
    "nearc4",
    "exper",
    "expersq",
    "black",
    "smsa",
    "south",
)
REGION_COLUMNS = ("smsa66",) + tuple(f"reg66{i}" for i in range(1, 10))


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _event(kind: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "kind": kind,
        "at": _now(),
        "payload": payload or {},
    }


def _choice(dimension: str, value: str) -> dict[str, str]:
    return {"dimension": dimension, "value": value}


def _definition(
    *,
    spec_id: str,
    label: str,
    rationale: str,
    dimension: str,
    value: str,
    choices: list[dict[str, str]],
    admissible: bool = True,
    user_decision: str = "include",
    unavailable_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "id": spec_id,
        "label": label,
        "rationale": rationale,
        "dimension": dimension,
        "value": value,
        "admissible": admissible,
        "user_decision": user_decision,
        "unavailable_reason": unavailable_reason,
        "choices": choices,
    }


def region_columns_present(columns: list[str]) -> bool:
    present = {str(col) for col in columns}
    return "smsa66" in present or any(col.startswith("reg66") for col in present)


def extract_kind_for(columns: list[str]) -> str:
    return "wooldridge_card_34" if region_columns_present(columns) else "statspai_card_9"


def card_specification_definitions(columns: list[str]) -> list[dict[str, Any]]:
    """6–12 admissible (or explicitly unavailable) Card specifications."""
    region_ok = region_columns_present(columns)
    region_decision = "include" if region_ok else "unavailable"
    region_reason = None if region_ok else "missing_columns"

    def base_choices(
        estimator: str,
        identification: str,
        experience: str,
        demographics: str,
        region: str,
    ) -> list[dict[str, str]]:
        return [
            _choice("estimator", estimator),
            _choice("identification", identification),
            _choice("experience", experience),
            _choice("demographics", demographics),
            _choice("region", region),
        ]

    specs = [
        _definition(
            spec_id="ols_linear_exper",
            label="OLS · linear experience",
            rationale="Baseline association between education and log wages.",
            dimension="estimator",
            value="ols",
            choices=base_choices("ols", "none", "linear", "none", "none"),
        ),
        _definition(
            spec_id="ols_quadratic_exper",
            label="OLS · quadratic experience",
            rationale="Allow diminishing returns to labor-market experience.",
            dimension="experience",
            value="quadratic",
            choices=base_choices("ols", "none", "quadratic", "none", "none"),
        ),
        _definition(
            spec_id="ols_demographics",
            label="OLS · demographic controls",
            rationale="Hold race constant when reading the education association.",
            dimension="demographics",
            value="black",
            choices=base_choices("ols", "none", "quadratic", "black", "none"),
        ),
        _definition(
            spec_id="ols_urban_south",
            label="OLS · urban and South",
            rationale="Location (smsa, south) as coarse geographic controls.",
            dimension="region",
            value="smsa_south",
            choices=base_choices("ols", "none", "quadratic", "black", "smsa_south"),
        ),
        _definition(
            spec_id="ols_full_controls",
            label="OLS · full controls",
            rationale="Association with experience, demographics, and location.",
            dimension="estimator",
            value="ols",
            choices=base_choices("ols", "none", "quadratic", "black", "smsa_south"),
        ),
        _definition(
            spec_id="iv_nearc4_linear",
            label="IV · nearc4, linear experience",
            rationale="College proximity as an instrument; local causal return.",
            dimension="identification",
            value="nearc4",
            choices=base_choices("iv", "nearc4", "linear", "none", "none"),
        ),
        _definition(
            spec_id="iv_nearc4_quadratic",
            label="IV · nearc4, quadratic experience",
            rationale="Same instrument with a quadratic experience profile.",
            dimension="experience",
            value="quadratic",
            choices=base_choices("iv", "nearc4", "quadratic", "none", "none"),
        ),
        _definition(
            spec_id="iv_nearc4_demographics",
            label="IV · nearc4 with demographics",
            rationale="IV local return holding race constant.",
            dimension="demographics",
            value="black",
            choices=base_choices("iv", "nearc4", "quadratic", "black", "none"),
        ),
        _definition(
            spec_id="iv_nearc4_urban_south",
            label="IV · nearc4 with urban and South",
            rationale="IV local return with coarse location controls.",
            dimension="region",
            value="smsa_south",
            choices=base_choices("iv", "nearc4", "quadratic", "black", "smsa_south"),
        ),
        _definition(
            spec_id="iv_nearc4_full",
            label="IV · nearc4, full controls",
            rationale="Primary IV comparison against the full-controls OLS.",
            dimension="identification",
            value="nearc4",
            choices=base_choices("iv", "nearc4", "quadratic", "black", "smsa_south"),
        ),
        _definition(
            spec_id="ols_region_dummies",
            label="OLS · 1966 region dummies",
            rationale="Region of residence in 1966 (smsa66, reg661–reg669).",
            dimension="region",
            value="reg66",
            choices=base_choices("ols", "none", "quadratic", "black", "reg66"),
            admissible=region_ok,
            user_decision=region_decision,
            unavailable_reason=region_reason,
        ),
        _definition(
            spec_id="iv_region_dummies",
            label="IV · nearc4 with 1966 region dummies",
            rationale="IV local return with 1966 region of residence.",
            dimension="region",
            value="reg66",
            choices=base_choices("iv", "nearc4", "quadratic", "black", "reg66"),
            admissible=region_ok,
            user_decision=region_decision,
            unavailable_reason=region_reason,
        ),
    ]
    return specs


def seed_card_lab(
    *,
    columns: list[str],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    now = _now()
    expectation_text = (
        "I expect OLS to be positive. If ability creates upward bias, IV may be smaller."
    )
    expectation_zh = (
        "预计 OLS 为正；如果能力造成向上偏误，IV 可能比 OLS 更小。"
    )
    expectation = {
        "text": expectation_text,
        "text_zh": expectation_zh,
        "confidence": "medium",
        "locale": "en",
        "version": 1,
        "updated_at": now,
        "history": [
            {
                "version": 1,
                "text": expectation_text,
                "confidence": "medium",
                "locale": "en",
                "at": now,
                "kind": "seed",
            }
        ],
    }
    definitions = card_specification_definitions(columns)
    return {
        "teaching_case": CARD_TEACHING_CASE,
        "provenance": provenance,
        "question": {
            "id": "card_1995.question",
            "prompt_en": "Does education increase earnings?",
            "prompt_zh": "教育是否提高工资?",
            "outcome": {
                "name": "lwage",
                "label": "Log wage",
                "gloss": "对数工资",
            },
            "treatment": {
                "name": "educ",
                "label": "Years of education",
                "gloss": "受教育年限",
            },
            "causal_threat": {
                "id": "ability_family",
                "label": "Ability and family background",
                "gloss": "能力与家庭背景",
                "text": (
                    "Ability and family background jointly influence education "
                    "and earnings."
                ),
            },
            "identification": {
                "id": "nearc4",
                "strategy": "instrumental_variable",
                "instrument": "nearc4",
                "label": "College proximity (nearc4)",
                "gloss": "大学邻近",
            },
            "estimand": {
                "ols": (
                    "OLS association: conditional association between education "
                    "and log wages."
                ),
                "iv": (
                    "IV local causal return: local average treatment effect for "
                    "those induced by college proximity."
                ),
            },
        },
        "expectation": expectation,
        "specification_space": {
            "status": "proposed",
            "frozen_at": None,
            "frozen_before_results": False,
            "revealed": False,
            "definitions": definitions,
        },
        "specification_runs": [],
        "decision_events": [
            _event("lab_seeded", {"teaching_case": CARD_TEACHING_CASE}),
        ],
        "canonical_spec_id": None,
        "next_challenge": None,
        "surprise": None,
        "canonical_history": [],
        "evidence_revision": 0,
        "claims": [],
        "current_claim_id": None,
        "claim": None,
    }


def lab_from_state(state: dict[str, Any] | None) -> Optional[dict[str, Any]]:
    if not isinstance(state, dict):
        return None
    lab = state.get("research_lab")
    return dict(lab) if isinstance(lab, dict) and lab else None


def current_claim(lab: dict[str, Any] | None) -> Optional[dict[str, Any]]:
    if not isinstance(lab, dict):
        return None
    claims = [item for item in (lab.get("claims") or []) if isinstance(item, dict)]
    cid = lab.get("current_claim_id")
    if cid:
        for item in claims:
            if item.get("id") == cid:
                return dict(item)
    existing = lab.get("claim")
    if isinstance(existing, dict) and existing.get("id"):
        return dict(existing)
    if claims:
        return dict(claims[-1])
    return None


def public_research(state: dict[str, Any] | None) -> ResearchLabResponse:
    lab = lab_from_state(state)
    if lab is None:
        return ResearchLabResponse()
    projected = dict(lab)
    claims = [dict(item) for item in (projected.get("claims") or []) if isinstance(item, dict)]
    projected["claims"] = claims
    current = current_claim(projected)
    projected["claim"] = current
    if current and not projected.get("current_claim_id"):
        projected["current_claim_id"] = current.get("id")
    return ResearchLabResponse.model_validate(projected)


def require_lab(state: dict[str, Any]) -> dict[str, Any]:
    lab = lab_from_state(state)
    if lab is None:
        raise HTTPException(status_code=404, detail="research lab not found")
    return lab


def update_expectation(
    lab: dict[str, Any],
    *,
    text: str,
    confidence: str,
    locale: str | None,
) -> dict[str, Any]:
    cleaned = text.strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail="expectation text is required")
    if confidence not in {"low", "medium", "high"}:
        raise HTTPException(status_code=422, detail="invalid confidence")
    now = _now()
    current = dict(lab.get("expectation") or {})
    version = int(current.get("version") or 0) + 1
    history = list(current.get("history") or [])
    history.append(
        {
            "version": version,
            "text": cleaned,
            "confidence": confidence,
            "locale": locale or current.get("locale") or "en",
            "at": now,
            "kind": "edit",
        }
    )
    lab["expectation"] = {
        **current,
        "text": cleaned,
        "confidence": confidence,
        "locale": locale or current.get("locale") or "en",
        "version": version,
        "updated_at": now,
        "history": history,
    }
    events = list(lab.get("decision_events") or [])
    events.append(
        _event(
            "expectation_set",
            {"version": version, "confidence": confidence},
        )
    )
    lab["decision_events"] = events
    return lab


def freeze_specification_space(lab: dict[str, Any]) -> dict[str, Any]:
    space = dict(lab.get("specification_space") or {})
    runs = lab.get("specification_runs") or []
    has_runs = isinstance(runs, list) and len(runs) > 0
    if space.get("frozen_at"):
        return lab
    now = _now()
    space["frozen_at"] = now
    space["frozen_before_results"] = not has_runs
    space["status"] = "frozen"
    space["revealed"] = bool(has_runs)
    lab["specification_space"] = space
    events = list(lab.get("decision_events") or [])
    events.append(
        _event(
            "specification_space_freeze",
            {
                "frozen_at": now,
                "frozen_before_results": space["frozen_before_results"],
            },
        )
    )
    lab["decision_events"] = events
    return lab


def reattach_research_lab(result: dict[str, Any], initial_state: dict[str, Any]) -> dict[str, Any]:
    """Put the seeded lab back if the upload pipeline dropped unknown keys."""
    seeded = initial_state.get("research_lab")
    if seeded is None:
        return result
    current = result.get("research_lab") if isinstance(result, dict) else None
    if isinstance(current, dict) and current:
        return result
    return {**result, "research_lab": seeded}


SPEC_RUN_FORBIDDEN_KEYS = (
    "estimate",
    "results",
    "main_specification",
    "body_chapters",
    "claim",
    "outline",
)

OUTCOME = "lwage"
TREATMENT = "educ"
INSTRUMENT = "nearc4"
REG66_CONTROLS = ("smsa", "south", "smsa66") + tuple(f"reg66{i}" for i in range(1, 9))


def strip_spec_run_result(result: dict[str, Any]) -> dict[str, Any]:
    """spec_run must not CAS-write canonical paper/estimate keys."""
    return {key: value for key, value in result.items() if key not in SPEC_RUN_FORBIDDEN_KEYS}


def choices_map(definition: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in definition.get("choices") or []:
        if isinstance(item, dict) and item.get("dimension"):
            out[str(item["dimension"])] = str(item.get("value") or "")
    return out


def _available(columns: list[str] | set[str]) -> set[str]:
    return {str(col) for col in columns}


def controls_for_choices(choices: dict[str, str], columns: list[str] | set[str]) -> list[str]:
    present = _available(columns)
    controls: list[str] = []
    experience = choices.get("experience") or "linear"
    if experience == "quadratic":
        for col in ("exper", "expersq"):
            if col in present:
                controls.append(col)
    elif "exper" in present:
        controls.append("exper")
    if choices.get("demographics") == "black" and "black" in present:
        controls.append("black")
    region = choices.get("region") or "none"
    if region == "smsa_south":
        for col in ("smsa", "south"):
            if col in present:
                controls.append(col)
    elif region == "reg66":
        for col in REG66_CONTROLS:
            if col in present:
                controls.append(col)
    return controls


def formula_for_choices(choices: dict[str, str], columns: list[str] | set[str]) -> str:
    controls = controls_for_choices(choices, columns)
    extra = f" + {' + '.join(controls)}" if controls else ""
    if (choices.get("estimator") or "ols") == "iv":
        return f"{OUTCOME} ~ ({TREATMENT} ~ {INSTRUMENT}){extra}"
    return f"{OUTCOME} ~ {TREATMENT}{extra}"


def temporary_spec(definition: dict[str, Any], columns: list[str] | set[str]) -> dict[str, Any]:
    choices = choices_map(definition)
    estimator = choices.get("estimator") or "ols"
    controls = controls_for_choices(choices, columns)
    formula = formula_for_choices(choices, columns)
    spec: dict[str, Any] = {
        "method": estimator,
        "outcome": OUTCOME,
        "treatment": TREATMENT,
        "controls": controls,
        "formula": formula,
    }
    if estimator == "iv":
        spec["endogenous"] = TREATMENT
        spec["instruments"] = [INSTRUMENT]
        spec["instrument"] = INSTRUMENT
        spec["iv_formula"] = formula
    return spec


def comparable_spec_ids(definitions: list[dict[str, Any]]) -> tuple[str, str]:
    by_id = {item.get("id"): item for item in definitions if isinstance(item, dict)}
    ols = by_id.get("ols_region_dummies") or {}
    iv = by_id.get("iv_region_dummies") or {}
    if ols.get("admissible") and iv.get("admissible"):
        return "ols_region_dummies", "iv_region_dummies"
    return "ols_full_controls", "iv_nearc4_full"


def included_spec_ids(lab: dict[str, Any]) -> list[str]:
    space = lab.get("specification_space") or {}
    ids: list[str] = []
    for item in space.get("definitions") or []:
        if not isinstance(item, dict):
            continue
        if not item.get("admissible"):
            continue
        if item.get("user_decision") not in {None, "include"}:
            continue
        spec_id = item.get("id")
        if spec_id:
            ids.append(str(spec_id))
    return ids


def definition_by_id(lab: dict[str, Any], spec_id: str) -> dict[str, Any]:
    space = lab.get("specification_space") or {}
    for item in space.get("definitions") or []:
        if isinstance(item, dict) and item.get("id") == spec_id:
            return item
    raise HTTPException(status_code=404, detail=f"specification {spec_id} not found")


def require_frozen(lab: dict[str, Any]) -> None:
    space = lab.get("specification_space") or {}
    if not space.get("frozen_at"):
        raise HTTPException(status_code=409, detail="specification space is not frozen")


def _as_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mentions_iv_smaller(text: str) -> bool:
    folded = text.casefold()
    return any(
        token in folded
        for token in (
            "iv may be smaller",
            "iv smaller",
            "iv 可能比 ols 更小",
            "iv可能比ols更小",
        )
    )


def _mentions_iv_larger(text: str) -> bool:
    folded = text.casefold()
    return "iv may be larger" in folded or "iv larger" in folded


def _mentions_similar(text: str) -> bool:
    folded = text.casefold()
    return any(token in folded for token in ("similar", "roughly the same", "大致相当"))


def _mentions_positive(text: str) -> bool:
    return "positive" in text.casefold() or "为正" in text


def evaluate_surprise(
    expectation: dict[str, Any] | None,
    runs: list[dict[str, Any]],
    *,
    ols_spec_id: str,
    iv_spec_id: str,
) -> Optional[dict[str, Any]]:
    """Deterministic surprise. LLM must not generate this object."""
    completed = [
        run
        for run in runs
        if isinstance(run, dict) and run.get("status") in {"ok", "degraded"}
    ]
    if not completed:
        return None
    by_spec: dict[str, dict[str, Any]] = {}
    for run in completed:
        spec_id = run.get("spec_id")
        if spec_id and spec_id not in by_spec:
            by_spec[str(spec_id)] = run
    ols = by_spec.get(ols_spec_id)
    iv = by_spec.get(iv_spec_id)
    text = str((expectation or {}).get("text") or "")
    kinds: list[str] = []
    expected_bits: list[str] = []
    observed_bits: list[str] = []
    ols_coef = _as_float((ols or {}).get("coef")) if ols else None
    iv_coef = _as_float((iv or {}).get("coef")) if iv else None

    if _mentions_positive(text) and ols_coef is not None and ols_coef < 0:
        kinds.append("direction_mismatch")
        expected_bits.append("OLS positive")
        observed_bits.append("OLS negative")
    if _mentions_positive(text) and iv_coef is not None and iv_coef < 0:
        kinds.append("direction_mismatch")
        expected_bits.append("positive return")
        observed_bits.append("IV negative")

    if ols_coef is not None and iv_coef is not None:
        relative = abs(iv_coef - ols_coef) / max(abs(ols_coef), 1e-6)
        ordered = relative > 0.05
        if ordered and _mentions_iv_smaller(text) and iv_coef > ols_coef:
            kinds.append("ordering_mismatch")
            expected_bits.append("IV may be smaller than OLS")
            observed_bits.append("IV > OLS")
        elif ordered and _mentions_iv_larger(text) and iv_coef < ols_coef:
            kinds.append("ordering_mismatch")
            expected_bits.append("IV may be larger than OLS")
            observed_bits.append("IV < OLS")
        if _mentions_similar(text) and relative > 0.25:
            kinds.append("magnitude")
            expected_bits.append("OLS and IV similar")
            observed_bits.append("relative difference > 0.25")

    if not kinds:
        return {
            "status": "Expected",
            "kind": None,
            "kinds": [],
            "expected": text or None,
            "observed": None,
        }
    return {
        "status": "Unexpected",
        "kind": kinds[0],
        "kinds": kinds,
        "expected": "; ".join(dict.fromkeys(expected_bits)) or text,
        "observed": "; ".join(dict.fromkeys(observed_bits)),
    }


def compare_specification_runs(
    run_a: dict[str, Any],
    run_b: dict[str, Any],
) -> dict[str, Any]:
    coef_a = _as_float(run_a.get("coef"))
    coef_b = _as_float(run_b.get("coef"))
    delta_abs = None if coef_a is None or coef_b is None else coef_b - coef_a
    delta_pct = None
    if delta_abs is not None and coef_a is not None:
        delta_pct = (delta_abs / max(abs(coef_a), 1e-6)) * 100
    map_a = {
        item.get("dimension"): item.get("value")
        for item in (run_a.get("choices") or [])
        if isinstance(item, dict)
    }
    map_b = {
        item.get("dimension"): item.get("value")
        for item in (run_b.get("choices") or [])
        if isinstance(item, dict)
    }
    dimensions = list(dict.fromkeys([*map_a.keys(), *map_b.keys()]))
    changed: list[dict[str, Any]] = []
    unchanged: list[dict[str, Any]] = []
    for dim in dimensions:
        left = map_a.get(dim)
        right = map_b.get(dim)
        row = {"dimension": dim, "a": left, "b": right}
        if left != right:
            changed.append(row)
        else:
            unchanged.append(row)
    changed_dims = {item["dimension"] for item in changed}
    if {"estimator", "identification"} & changed_dims:
        why = "Identification strategy changed"
    elif "experience" in changed_dims:
        why = "Experience functional form changed"
    elif "region" in changed_dims:
        why = "Region controls changed"
    elif "demographics" in changed_dims:
        why = "Demographic controls changed"
    else:
        why = "Little changed"
    return {
        "a": {
            "id": run_a.get("id"),
            "spec_id": run_a.get("spec_id"),
            "coef": coef_a,
            "label": run_a.get("label"),
        },
        "b": {
            "id": run_b.get("id"),
            "spec_id": run_b.get("spec_id"),
            "coef": coef_b,
            "label": run_b.get("label"),
        },
        "coef_a": coef_a,
        "coef_b": coef_b,
        "delta_abs": delta_abs,
        "delta_pct": delta_pct,
        "changed": changed,
        "unchanged": unchanged,
        "why_moved": why,
        "intent": why,
    }


def find_run(lab: dict[str, Any], token: str) -> dict[str, Any]:
    runs = [run for run in (lab.get("specification_runs") or []) if isinstance(run, dict)]
    for run in reversed(runs):
        if token in {run.get("id"), run.get("spec_id"), run.get("producer_run_id")}:
            return run
    raise HTTPException(status_code=404, detail=f"specification run {token} not found")


def merge_spec_run_lab(current: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Keep live lab fields; merge immutable runs from a spec_run worker.

    Worker snapshots can lag a concurrent Promote / Claim approve. Never copy
    canonical or claims from the worker. New run ids bump evidence_revision
    against the live lab so an approved Claim becomes stale exactly once.
    """
    merged = dict(current)
    existing = [
        dict(run) for run in (merged.get("specification_runs") or []) if isinstance(run, dict)
    ]
    index = {run.get("id"): i for i, run in enumerate(existing)}
    added = False
    for run in incoming.get("specification_runs") or []:
        if not isinstance(run, dict) or not run.get("id"):
            continue
        rid = run["id"]
        if rid in index:
            existing[index[rid]] = dict(run)
        else:
            index[rid] = len(existing)
            existing.append(dict(run))
            added = True
    merged["specification_runs"] = existing

    events = [
        dict(event)
        for event in (merged.get("decision_events") or [])
        if isinstance(event, dict)
    ]
    seen = {event.get("id") for event in events}
    for event in incoming.get("decision_events") or []:
        if isinstance(event, dict) and event.get("id") not in seen:
            events.append(dict(event))
            seen.add(event.get("id"))
    merged["decision_events"] = events

    for key in ("surprise", "next_challenge"):
        if incoming.get(key) is not None:
            merged[key] = incoming[key]

    if current_claim(merged) is None:
        for key in ("claims", "current_claim_id", "claim"):
            if incoming.get(key) is not None:
                merged[key] = incoming[key]

    space = dict(merged.get("specification_space") or {})
    incoming_space = incoming.get("specification_space") or {}
    if existing or incoming_space.get("revealed"):
        space["revealed"] = True
    merged["specification_space"] = space
    if added:
        merged = bump_evidence_revision(merged)
    return merged


def next_card_challenge(lab: dict[str, Any]) -> Optional[dict[str, Any]]:
    runs = [run for run in (lab.get("specification_runs") or []) if isinstance(run, dict)]
    if not runs:
        return None
    definitions = (lab.get("specification_space") or {}).get("definitions") or []
    ols_id, iv_id = comparable_spec_ids(definitions)
    iv_run = next((run for run in reversed(runs) if run.get("spec_id") == iv_id), None)
    if iv_run:
        diag = iv_run.get("diagnostics") or {}
        f_stat = diag.get("F_eff")
        if f_stat is None:
            f_stat = diag.get("first_stage_F")
        f_text = f"{float(f_stat):.2f}" if _as_float(f_stat) is not None else "unavailable"
        return {
            "id": "challenge.instrument_strength",
            "target": "instrument_strength",
            "rationale": (
                "College proximity may be a weak instrument after the "
                f"comparable controls (effective F={f_text})."
            ),
            "proposed_specification_change": {
                "spec_id": iv_id,
                "mode": "preview",
                "note": "Re-run the comparable IV spec as a preview and inspect first-stage strength.",
            },
            "expected_information_gain": (
                "Whether the instrument remains informative once experience, "
                "demographics, and region are held constant."
            ),
            "status": "proposed",
            "resulting_runs": [],
        }
    linear = next(
        (
            item
            for item in definitions
            if isinstance(item, dict)
            and item.get("admissible")
            and choices_map(item).get("experience") == "linear"
            and choices_map(item).get("estimator") == "ols"
        ),
        None,
    )
    if linear is None:
        return None
    return {
        "id": "challenge.experience_form",
        "target": "experience",
        "rationale": "Experience may enter linearly or as a quadratic.",
        "proposed_specification_change": {
            "spec_id": linear.get("id"),
            "mode": "preview",
        },
        "expected_information_gain": "Whether the education coefficient moves with the experience profile.",
        "status": "proposed",
        "resulting_runs": [],
    }


def bump_evidence_revision(lab: dict[str, Any]) -> dict[str, Any]:
    """New completed evidence. Existing claims keep their text and become stale."""
    current = int(lab.get("evidence_revision") or 0) + 1
    lab["evidence_revision"] = current
    claims = []
    for item in lab.get("claims") or []:
        if not isinstance(item, dict):
            continue
        updated = dict(item)
        based = updated.get("based_on_evidence_revision")
        try:
            stale = based is None or int(based) != current
        except (TypeError, ValueError):
            stale = True
        if stale:
            updated["stale"] = True
        claims.append(updated)
    lab["claims"] = claims
    current_id = lab.get("current_claim_id")
    if current_id:
        lab["claim"] = next((item for item in claims if item.get("id") == current_id), lab.get("claim"))
    elif claims:
        lab["claim"] = claims[-1]
    return lab


def promote_run(lab: dict[str, Any], run: dict[str, Any], estimate: dict[str, Any] | None) -> dict[str, Any]:
    history = list(lab.get("canonical_history") or [])
    history.append(
        {
            "at": _now(),
            "estimate": estimate,
            "canonical_spec_id": lab.get("canonical_spec_id"),
        }
    )
    lab["canonical_history"] = history[-8:]
    runs = []
    for item in lab.get("specification_runs") or []:
        if not isinstance(item, dict):
            continue
        updated = dict(item)
        if updated.get("id") == run.get("id"):
            updated["relation"] = "canonical"
        elif updated.get("relation") == "canonical":
            updated["relation"] = "exploratory"
        runs.append(updated)
    lab["specification_runs"] = runs
    lab["canonical_spec_id"] = run.get("spec_id")
    events = list(lab.get("decision_events") or [])
    events.append(
        _event(
            "preview_promote",
            {
                "run_id": run.get("id"),
                "spec_id": run.get("spec_id"),
                "producer_run_id": run.get("producer_run_id"),
            },
        )
    )
    lab["decision_events"] = events
    return bump_evidence_revision(lab)


def revert_canonical(lab: dict[str, Any]) -> tuple[dict[str, Any], Optional[dict[str, Any]]]:
    history = list(lab.get("canonical_history") or [])
    if not history:
        raise HTTPException(status_code=409, detail="no canonical estimate to revert")
    previous = history.pop()
    lab["canonical_history"] = history
    restored = previous.get("estimate")
    previous_spec = previous.get("canonical_spec_id")
    runs = []
    for item in lab.get("specification_runs") or []:
        if not isinstance(item, dict):
            continue
        updated = dict(item)
        if previous_spec and updated.get("spec_id") == previous_spec:
            updated["relation"] = "canonical"
        elif updated.get("relation") == "canonical":
            updated["relation"] = "exploratory"
        runs.append(updated)
    lab["specification_runs"] = runs
    lab["canonical_spec_id"] = previous_spec
    events = list(lab.get("decision_events") or [])
    events.append(_event("preview_revert", {"canonical_spec_id": previous_spec}))
    lab["decision_events"] = events
    lab = bump_evidence_revision(lab)
    return lab, restored if isinstance(restored, dict) else None


def estimate_payload_from_run(run: dict[str, Any]) -> dict[str, Any]:
    coef = run.get("coef")
    se = run.get("se")
    p_value = run.get("p")
    treatment_row = run.get("treatment_row") or (
        f"| {TREATMENT} | {coef} | {se} | {p_value} |" if coef is not None else ""
    )
    return {
        "status": run.get("status") or "ok",
        "produced_by": "estimate",
        "estimator": run.get("estimator"),
        "method": run.get("method") or choices_map({"choices": run.get("choices") or []}).get("estimator"),
        "formula": run.get("formula"),
        "treatment": TREATMENT,
        "treatment_row": treatment_row,
        "n": run.get("n"),
        "coef": coef,
        "se": se,
        "p": p_value,
        "source_run_id": run.get("producer_run_id"),
        "analysis_dataset": run.get("analysis_dataset"),
        "diagnostics": run.get("diagnostics"),
    }


def card_paper_outline() -> list[dict[str, str]]:
    return [
        {"type": "intro", "title": "引言"},
        {"type": "lit_review", "title": "文献综述"},
        {"type": "data_desc", "title": "数据描述"},
        {"type": "methods", "title": "方法", "method": "IV"},
        {"type": "results", "title": "结果"},
        {"type": "conclusion", "title": "结论"},
    ]


def _claim_required_spec_id(claim: dict[str, Any] | None) -> str | None:
    if not isinstance(claim, dict):
        return None
    required = (claim.get("provenance") or {}).get("iv_spec_id")
    return str(required) if required else None


def require_claim_ready_for_paper(lab: dict[str, Any]) -> dict[str, Any]:
    claim = current_claim(lab)
    if not claim or not claim.get("approved_by_user"):
        raise HTTPException(status_code=409, detail="claim_unapproved")
    based = claim.get("based_on_evidence_revision")
    revision = lab.get("evidence_revision")
    stale = bool(claim.get("stale"))
    try:
        stale = stale or based is None or int(based) != int(revision or 0)
    except (TypeError, ValueError):
        stale = True
    if stale:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "claim_stale",
                "message": "New evidence available · 结论需要重新审视",
            },
        )
    required = _claim_required_spec_id(claim)
    if required and lab.get("canonical_spec_id") != required:
        iv_run = _latest_completed_run(
            [item for item in (lab.get("specification_runs") or []) if isinstance(item, dict)],
            required,
        )
        raise HTTPException(
            status_code=409,
            detail={
                "code": "canonical_mismatch",
                "message": "当前 Claim 依赖 IV specification，但正式主规格不是该 IV。",
                "canonical_spec_id": lab.get("canonical_spec_id"),
                "required_spec_id": required,
                "promote_run_id": (iv_run or {}).get("id"),
            },
        )
    return claim


def prepare_card_paper_state(state: dict[str, Any], lab: dict[str, Any]) -> dict[str, Any]:
    """Fill write-ready fields from the current canonical spec. Never promotes."""
    require_claim_ready_for_paper(lab)
    spec_id = lab.get("canonical_spec_id")
    runs = [item for item in (lab.get("specification_runs") or []) if isinstance(item, dict)]
    run = _latest_completed_run(runs, str(spec_id)) if spec_id else None
    if run is None:
        raise HTTPException(status_code=409, detail="no_specification_run")
    estimate = estimate_payload_from_run(run)
    csv_path = lab.get("extract_csv_path") or state.get("csv_path")
    from pathlib import Path

    if not csv_path or not Path(str(csv_path)).is_file():
        run_path = (run.get("analysis_dataset") or {}).get("path")
        if run_path and Path(str(run_path)).is_file():
            csv_path = str(run_path)
        else:
            import pandas as pd

            from services.card_demo import load_card_extract

            df_extract, _ = load_card_extract()
            sid = state.get("session_id") or "card"
            fallback = Path(str(csv_path) if csv_path else f"/tmp/{sid}-card-extract.csv")
            fallback.parent.mkdir(parents=True, exist_ok=True)
            df_extract.to_csv(fallback, index=False)
            csv_path = str(fallback)
        lab["extract_csv_path"] = csv_path
    columns = list((run.get("analysis_dataset") or {}).get("columns") or [])
    if not columns and csv_path:
        import pandas as pd

        columns = [str(col) for col in pd.read_csv(str(csv_path), nrows=0).columns]
    spec = temporary_spec(definition_by_id(lab, str(run.get("spec_id"))), columns)
    direction = {
        "question": (lab.get("question") or {}).get("prompt_en") or "Does education increase earnings?",
        "dv": OUTCOME,
        "iv": TREATMENT,
        "instrument": INSTRUMENT,
        "method": "iv" if (run.get("method") == "iv" or "ivreg" in str(spec.get("estimator") or "")) else "ols",
        "controls": spec.get("controls") or [],
        "claim": "association",
    }
    working = {
        **state,
        "csv_path": csv_path,
        "research_direction": direction,
        "main_specification": spec,
        "estimate": estimate,
        "research_lab": lab,
    }
    from agent.nodes.identification_verify import identification_verify
    from agent.nodes.robustness_check import robustness_check

    ident = identification_verify(working)
    working.update(ident)
    robust = robustness_check(working)
    working.update(robust)
    row = estimate.get("treatment_row") or ""
    working["results"] = (
        "# 主结果\n\n| 变量 | 系数 | SE | p |\n|------|------|----|---|\n" + row
    )
    if not working.get("outline"):
        working["outline"] = card_paper_outline()
        working["current_chapter_index"] = 4
    working["claim"] = "association"
    return working


CARD_CLAIM_ID = "claim.card.education-earnings"
CARD_SUPPORTED_WORDING = "Education is positively associated with earnings."
CARD_CONDITIONAL_WORDING = (
    "Under the college-proximity IV assumptions, IV estimates suggest "
    "a positive local causal return to schooling."
)
CARD_UNSUPPORTED_WORDING = (
    "One more year of education raises everyone's wage by 13%."
)
CARD_UNRESOLVED_ASSUMPTIONS = [
    "IV exclusion restriction (college proximity affects wages only through education)",
    "monotonicity (no defiers)",
    "LATE is not ATE",
    "instrument strength",
]


def _latest_completed_run(runs: list[dict[str, Any]], spec_id: str) -> Optional[dict[str, Any]]:
    for run in reversed(runs):
        if run.get("spec_id") == spec_id and run.get("status") in {"ok", "degraded"}:
            return run
    return None


def _claim_run_facts(ols: dict[str, Any] | None, iv: dict[str, Any] | None) -> str:
    lines: list[str] = []
    for label, run in (("OLS", ols), ("IV", iv)):
        if not run:
            continue
        coef = run.get("coef")
        se = run.get("se")
        n = run.get("n")
        lines.append(
            f"{label} spec_id={run.get('spec_id')} coef={coef} se={se} n={n} "
            f"formula={run.get('formula')}"
        )
    return "\n".join(lines) if lines else "未提供"


def draft_card_claim_payload(lab: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Deterministic Card claim from comparable OLS/IV runs. No LLM."""
    runs = [run for run in (lab.get("specification_runs") or []) if isinstance(run, dict)]
    definitions = (lab.get("specification_space") or {}).get("definitions") or []
    ols_id, iv_id = comparable_spec_ids(definitions)
    ols = _latest_completed_run(runs, ols_id)
    iv = _latest_completed_run(runs, iv_id)
    if ols is None or iv is None:
        return None
    ols_coef = _as_float(ols.get("coef"))
    iv_coef = _as_float(iv.get("coef"))
    supporting = [str(ols.get("id")), str(iv.get("id"))]
    counter: list[str] = []
    if ols_coef is not None and iv_coef is not None and ols_coef != iv_coef:
        counter.append(
            "OLS and IV coefficients differ; identification strategy is a sensitive dimension."
        )
    diag = iv.get("diagnostics") or {}
    f_stat = _as_float(diag.get("F_eff") if diag.get("F_eff") is not None else diag.get("first_stage_F"))
    if f_stat is not None and f_stat < 10:
        counter.append("Instrument may be weak after comparable controls.")
    sensitive = ["estimator", "identification"]
    evidence_status = "supported" if ols_coef is not None and ols_coef > 0 else "insufficient"
    return {
        "id": CARD_CLAIM_ID,
        "claim_text": CARD_SUPPORTED_WORDING,
        "claim_type": "association",
        "supported_wording": CARD_SUPPORTED_WORDING,
        "conditionally_supported_wording": CARD_CONDITIONAL_WORDING,
        "unsupported_wording": CARD_UNSUPPORTED_WORDING,
        "supporting_run_ids": supporting,
        "counter_evidence": counter,
        "sensitive_dimensions": sensitive,
        "unresolved_assumptions": list(CARD_UNRESOLVED_ASSUMPTIONS),
        "evidence_status": evidence_status,
        "approved_by_user": False,
        "stale": False,
        "version": 1,
        "based_on_evidence_revision": int(lab.get("evidence_revision") or 0),
        "run_facts": _claim_run_facts(ols, iv),
        "provenance": {
            "ols_run_id": ols.get("id"),
            "iv_run_id": iv.get("id"),
            "ols_spec_id": ols_id,
            "iv_spec_id": iv_id,
            "producer_run_ids": list(
                dict.fromkeys(
                    [
                        str(item)
                        for item in (ols.get("producer_run_id"), iv.get("producer_run_id"))
                        if item
                    ]
                )
            ),
            "ols_coef": ols_coef,
            "iv_coef": iv_coef,
        },
    }


def _store_claim(lab: dict[str, Any], claim: dict[str, Any]) -> dict[str, Any]:
    claims = [dict(item) for item in (lab.get("claims") or []) if isinstance(item, dict)]
    index = next((i for i, item in enumerate(claims) if item.get("id") == claim.get("id")), None)
    if index is None:
        claims.append(claim)
    else:
        claims[index] = claim
    lab["claims"] = claims
    lab["current_claim_id"] = claim.get("id")
    lab["claim"] = claim
    return lab


def maybe_draft_card_claim(lab: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    drafted = draft_card_claim_payload(lab)
    if drafted is None:
        return lab
    existing = current_claim(lab)
    if existing and not force:
        return lab
    if existing and force:
        drafted["id"] = existing.get("id") or drafted["id"]
        drafted["version"] = int(existing.get("version") or 1) + 1
        drafted["approved_by_user"] = False
        drafted["stale"] = False
        drafted["evidence_status"] = "draft"
        drafted["based_on_evidence_revision"] = int(lab.get("evidence_revision") or 0)
    _store_claim(lab, drafted)
    events = list(lab.get("decision_events") or [])
    events.append(
        _event(
            "claim_drafted",
            {
                "claim_id": drafted.get("id"),
                "version": drafted.get("version"),
                "supporting_run_ids": drafted.get("supporting_run_ids"),
            },
        )
    )
    lab["decision_events"] = events
    return lab


def draft_card_claim(lab: dict[str, Any]) -> dict[str, Any]:
    require_frozen(lab)
    drafted = draft_card_claim_payload(lab)
    if drafted is None:
        raise HTTPException(
            status_code=409,
            detail="comparable OLS and IV specification runs are required to draft a claim",
        )
    updated = maybe_draft_card_claim(lab, force=True)
    if current_claim(updated) is None:
        raise HTTPException(status_code=409, detail="claim could not be drafted")
    return updated


def approve_card_claim(lab: dict[str, Any], claim_id: str) -> dict[str, Any]:
    claim = current_claim(lab)
    if claim is None or claim.get("id") != claim_id:
        claims = [item for item in (lab.get("claims") or []) if isinstance(item, dict)]
        claim = next((item for item in claims if item.get("id") == claim_id), None)
    if claim is None:
        raise HTTPException(status_code=404, detail=f"claim {claim_id} not found")
    if not claim.get("supporting_run_ids"):
        raise HTTPException(status_code=409, detail="claim has no supporting specification runs")
    based = claim.get("based_on_evidence_revision")
    revision = lab.get("evidence_revision")
    stale = bool(claim.get("stale"))
    try:
        stale = stale or based is None or int(based) != int(revision or 0)
    except (TypeError, ValueError):
        stale = True
    if stale:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "claim_stale",
                "message": "New evidence available · 结论需要重新审视",
            },
        )
    updated = dict(claim)
    updated["approved_by_user"] = True
    updated["stale"] = False
    updated["evidence_status"] = "approved"
    _store_claim(lab, updated)
    events = list(lab.get("decision_events") or [])
    events.append(
        _event(
            "claim_approved",
            {"claim_id": updated.get("id"), "version": updated.get("version")},
        )
    )
    lab["decision_events"] = events
    return lab


def mark_results_chapters_stale(chapters: list[Any]) -> list[Any]:
    out: list[Any] = []
    for item in chapters:
        if not isinstance(item, dict) or item.get("type") != "results" or not item.get("content"):
            out.append(item)
            continue
        updated = dict(item)
        updated["stale"] = True
        updated["needs_regeneration"] = True
        updated["grounded"] = False
        out.append(updated)
    return out
