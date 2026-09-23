"""Version binding for the formal confirmation chain (CHAIN-2 R2/R3/R6).

An approval has to name the object it approved. This module owns the smallest
set of identity fields that makes that checkable:

- a *design identity* — the fingerprint of the design's executable projection
  (method / outcome / treatment / controls / method columns). Display wording,
  title or question changes deliberately do not move it;
- a *dataset identity* — dataset revision + upload fingerprint, written when
  the new flow binds (or re-binds) data;
- a *preview identity* — design + dataset + Table 1 + equation. Sample and
  setting confirmations are stored against it, so a moved preview leaves them
  behind;
- a *diagnosis identity* — the #40 diagnostic plus star rating a risk decision
  was made about.

Atomic changes supersede the affected artefacts: the approvals are revoked,
the artefacts are archived into ``formal_chain.history`` (kept readable) and
the live fields are cleared. Runs carry the binding they were admitted under,
so a run that finishes after its version was superseded writes history instead
of the current state.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from fastapi import HTTPException

from services.formal_chain import formal_path_applies, is_design_locked

CHAIN_KEY = "formal_chain"

CODE_PREVIEW_NOT_READY = "preview_not_ready"
CODE_SAMPLE_REQUIRED = "sample_confirmation_required"
CODE_CONFIRMATIONS_STALE = "confirmations_stale"
CODE_DESIGN_EXECUTION_MISMATCH = "design_execution_mismatch"
CODE_RISK_CONFIRMATION_REQUIRED = "risk_confirmation_required"
CODE_RISK_NOT_APPLICABLE = "risk_confirmation_not_applicable"

HISTORY_LIMIT = 50
REQUEST_LIMIT = 50

# Design fields that change what the estimate runs. Everything else in the
# design object (title, question, proposal timestamps) is presentation.
_DESIGN_SCALAR_KEYS = (
    "method",
    "outcome",
    "treatment",
    "group",
    "treated",
    "period",
    "time_col",
    "id_col",
    "first_treat_col",
    "endogenous",
    "running_var",
    "cutoff",
    "unit_col",
    "treated_unit",
    "treatment_time",
    "cluster",
    "qType",
)
_DESIGN_SEQUENCE_KEYS = (
    "controls",
    "interactions",
    "heterogeneity_groups",
    "instruments",
    "cluster_levels",
)

# Live artefacts owned by the current preview. Superseding a design, a dataset
# or a preview clears exactly these; the archive keeps the previous values.
_PREVIEW_FIELDS: dict[str, Any] = {
    "table1": None,
    "specification_equation": None,
    "prewrite_gate": None,
    "table1_confirmed": False,
    "table1Confirmed": False,
    "spec_confirmed": False,
    "specConfirmed": False,
    "blocking_decision": None,
}

# These products depend on the approved data/design, not just the session ID.
_EVIDENCE_FIELDS = {
    "estimate": None, "results": None, "robustness_results": None,
    "identification_diag": None, "identification_failed": False,
    "star_rating": None, "claim": None, "code_translations": [],
    "treatment_row": None,
}


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _digest(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, bool):
        return str(value)
    return value


def _canonical_item(item: Any) -> Any:
    if isinstance(item, Mapping):
        return {str(key): str(value) for key, value in item.items()}
    return str(item).strip()


def _sequence(value: Any) -> list[str]:
    """Order-insensitive canonical form of a list-ish value."""
    if value is None:
        return []
    if isinstance(value, str):
        items: list[Any] = [part.strip() for part in value.split(",")]
    elif isinstance(value, (list, tuple)):
        items = list(value)
    else:
        return []
    canonical = set()
    for item in items:
        if isinstance(item, str) and not item.strip():
            continue
        canonical.add(
            json.dumps(_canonical_item(item), sort_keys=True, ensure_ascii=False)
        )
    return sorted(canonical)


def _is_declared(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple)):
        return True
    return True


# ---------------------------------------------------------------------------
# Identities
# ---------------------------------------------------------------------------


def design_execution_projection(design: Any) -> dict[str, Any] | None:
    """The executable content of a design, without its presentation."""
    if not isinstance(design, dict):
        return None
    projection: dict[str, Any] = {}
    for key in _DESIGN_SCALAR_KEYS:
        value = _text(design.get(key))
        if value is not None:
            projection[key] = value
    for key in _DESIGN_SEQUENCE_KEYS:
        items = _sequence(design.get(key))
        if items:
            projection[key] = items
    return projection or None


def design_identity(design: Any) -> str | None:
    projection = design_execution_projection(design)
    if not projection:
        return None
    return _digest(projection)


def design_revision(design: Any) -> str | None:
    """New drafts have unique revisions; old drafts use content, never a clock."""
    if not isinstance(design, dict):
        return None
    return design.get("revision") or _digest({
        "source": design.get("source"), "proposed_at": design.get("proposed_at"),
        "execution": design_execution_projection(design),
    })


def confirmation_targets(state: Mapping[str, Any]) -> dict[str, str | None]:
    """Opaque identities are public; paths, data and credentials are not."""
    return {
        "design": design_revision(state.get("design")),
        "dataset": dataset_identity(state),
        "preview": preview_identity(state),
        "diagnosis": diagnosis_identity(state),
    }


def require_observed_target(
    state: dict, expected: Any, fields: tuple[str, ...]
) -> None:
    if not formal_path_applies(state):
        return
    if not isinstance(expected, Mapping):
        raise HTTPException(409, detail={"code": "confirmation_target_required"})
    current = confirmation_targets(state)
    if any(key not in expected or expected[key] != current[key] for key in fields):
        raise HTTPException(409, detail={"code": "confirmation_target_mismatch", "current": current})


def chain(state: Mapping[str, Any] | None) -> dict[str, Any]:
    """The formal binding block, normalized (missing fields are filled in)."""
    raw = state.get(CHAIN_KEY) if isinstance(state, Mapping) else None
    block = raw if isinstance(raw, dict) else {}
    confirmations = block.get("confirmations")
    history = block.get("history")
    requests = block.get("requests")
    return {
        "dataset_revision": int(block.get("dataset_revision") or 0),
        "dataset_fingerprint": block.get("dataset_fingerprint"),
        "confirmations": dict(confirmations) if isinstance(confirmations, dict) else {},
        "history": list(history) if isinstance(history, list) else [],
        "requests": dict(requests) if isinstance(requests, dict) else {},
    }


def with_chain(state: dict[str, Any], block: dict[str, Any]) -> dict[str, Any]:
    return {**state, CHAIN_KEY: block}


def dataset_identity(state: Mapping[str, Any] | None) -> str | None:
    block = chain(state)
    fingerprint = block["dataset_fingerprint"]
    revision = block["dataset_revision"]
    if fingerprint is None and not revision:
        return None
    return _digest({"revision": revision, "fingerprint": fingerprint})


def _table1_signature(table1: Any) -> dict[str, Any] | None:
    if not isinstance(table1, dict):
        return None
    rows = table1.get("rows")
    return {
        "n": table1.get("n"),
        "variables": _sequence(table1.get("variables")),
        "rows": [
            _canonical_item(row)
            for row in (rows or [])
            if isinstance(row, Mapping)
        ],
    }


def has_preview(state: Mapping[str, Any] | None) -> bool:
    """True when the generated Table 1 and equation are really on the session."""
    if not isinstance(state, Mapping):
        return False
    table1 = state.get("table1")
    if not isinstance(table1, dict) or "rows" not in table1:
        return False
    if not isinstance(table1.get("columns"), list):
        return False
    equation = state.get("specification_equation")
    return isinstance(equation, str) and bool(equation.strip())


def preview_identity(state: Mapping[str, Any] | None) -> str | None:
    """Identity of the preview a confirmation is about, or None when absent."""
    if not has_preview(state):
        return None
    specification = state.get("main_specification")
    from agent.engine.prewrite_gates import resolve_q_type, resolve_spec_mode
    return _digest(
        {
            "design": design_identity(state.get("design")),
            "dataset": dataset_identity(state),
            "spec": _digest(specification) if isinstance(specification, dict) else None,
            "table1": _table1_signature(state.get("table1")),
            "equation": str(state.get("specification_equation")).strip(),
            "question_type": resolve_q_type(state),
            "spec_mode": resolve_spec_mode(state),
        }
    )


def diagnosis_identity(state: Mapping[str, Any] | None) -> str | None:
    diag = state.get("identification_diag") if isinstance(state, Mapping) else None
    if not isinstance(diag, dict) or not diag:
        return None
    return _digest({"diag": diag, "star": state.get("star_rating")})


# ---------------------------------------------------------------------------
# Confirmation records
# ---------------------------------------------------------------------------


def confirmations(state: Mapping[str, Any] | None) -> dict[str, Any]:
    return chain(state)["confirmations"]


def _record(state: dict[str, Any], kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    block = chain(state)
    records = dict(block["confirmations"])
    records[kind] = {"at": _now_iso(), **payload}
    return with_chain(state, {**block, "confirmations": records})


def sample_is_current(state: Mapping[str, Any] | None) -> bool:
    return _preview_confirm_is_current(state, "sample")


def setting_is_current(state: Mapping[str, Any] | None) -> bool:
    return _preview_confirm_is_current(state, "spec")


def _preview_confirm_is_current(state: Mapping[str, Any] | None, kind: str) -> bool:
    record = confirmations(state).get(kind)
    if not isinstance(record, dict):
        return False
    current = preview_identity(state)
    if not current or record.get("preview") != current:
        return False
    if record.get("design") != design_identity(
        state.get("design") if isinstance(state, Mapping) else None
    ):
        return False
    return record.get("dataset_revision") == chain(state)["dataset_revision"]


def risk_is_current(state: Mapping[str, Any] | None) -> bool:
    record = confirmations(state).get("risk")
    if not isinstance(record, dict):
        return False
    design = design_identity(
        state.get("design") if isinstance(state, Mapping) else None
    )
    diagnosis = diagnosis_identity(state)
    if design is None or diagnosis is None:
        return False
    return record.get("design") == design and record.get("diagnosis") == diagnosis


def bound_confirm_flags(state: Mapping[str, Any] | None) -> dict[str, bool]:
    """The Table 1 / setting flags as *earned* facts, not as stored booleans."""
    return {
        "table1Confirmed": sample_is_current(state),
        "specConfirmed": setting_is_current(state),
    }


def stale_confirmation_present(state: Mapping[str, Any] | None) -> bool:
    """True when the session carries approvals (records or true flags) that no
    longer name the current version — the honest "re-confirm" case."""
    if any(confirmations(state).values()):
        return True
    return bool(state.get("table1Confirmed")) or bool(state.get("specConfirmed"))


# ---------------------------------------------------------------------------
# Recording confirmations (R2 ordering + R6 risk decision)
# ---------------------------------------------------------------------------


def record_confirms(state: dict[str, Any], incoming: Mapping[str, Any]) -> dict[str, Any]:
    """Apply the confirms in ``incoming`` with version checks. Fail closed.

    Order matters: the sample description is confirmed before the setting it
    belongs to, and neither can be recorded without a current preview.
    """
    out = dict(state)
    if not formal_path_applies(out):
        return out
    fields = ("design", "dataset", "preview")
    if incoming.get("riskConfirmed") or incoming.get("risk_confirmed"):
        fields += ("diagnosis",)
    require_observed_target(out, incoming.get("expectedTarget"), fields)
    if preview_identity(out) is None:
        raise HTTPException(
            status_code=409,
            detail={"code": CODE_PREVIEW_NOT_READY},
        )
    current_preview = preview_identity(out)
    design = design_identity(out.get("design"))
    revision = chain(out)["dataset_revision"]

    if incoming.get("table1Confirmed") or incoming.get("table1_confirmed"):
        out = _record(
            out,
            "sample",
            {"preview": current_preview, "design": design, "dataset_revision": revision},
        )

    if incoming.get("specConfirmed") or incoming.get("spec_confirmed"):
        if not sample_is_current(out):
            raise HTTPException(
                status_code=409,
                detail={"code": CODE_SAMPLE_REQUIRED},
            )
        out = _record(
            out,
            "spec",
            {"preview": current_preview, "design": design, "dataset_revision": revision},
        )

    if incoming.get("riskConfirmed") or incoming.get("risk_confirmed"):
        diagnosis = diagnosis_identity(out)
        if design is None or diagnosis is None:
            raise HTTPException(
                status_code=409,
                detail={"code": CODE_RISK_NOT_APPLICABLE},
            )
        out = _record(
            out, "risk", {"design": design, "diagnosis": diagnosis, "level": "confirm"}
        )

    return out


def _supersede_entry(
    state: dict[str, Any], kind: str, **details: Any
) -> dict[str, Any]:
    block = chain(state)
    entry = {
        "at": _now_iso(),
        "kind": kind,
        "table1": state.get("table1"),
        "specification_equation": state.get("specification_equation"),
        "main_specification": state.get("main_specification"),
        "research_direction": state.get("research_direction"),
        "confirmations": block["confirmations"],
        **{key: state[key] for key in _EVIDENCE_FIELDS if key in state},
        **details,
    }
    return entry


def supersede(state: dict[str, Any], kind: str, **details: Any) -> dict[str, Any]:
    """Revoke the current approvals, archive the artefacts, clear the lives.

    Only the formal path is versioned this way; legacy sessions keep their
    existing behavior. Only fields that are actually present are rewritten, so
    a supersede never invents state the session did not have.
    """
    if not formal_path_applies(state):
        return dict(state)
    block = chain(state)
    history = (block["history"] + [_supersede_entry(state, kind, **details)])[
        -HISTORY_LIMIT:
    ]
    cleared = {key: value for key, value in _PREVIEW_FIELDS.items() if key in state}
    updated = {**state, **cleared,
               **{key: value for key, value in _EVIDENCE_FIELDS.items() if key in state}}
    if state.get("estimate") or state.get("evidence_stale"):
        updated["evidence_stale"] = True
    if state.get("body_chapters"):
        updated["body_chapters"] = [
            {**chapter, "stale": True, "needs_regeneration": True}
            if isinstance(chapter, dict) else chapter for chapter in state["body_chapters"]
        ]
    return with_chain(
        updated, {**block, "confirmations": {}, "history": history}
    )


def supersede_design(state: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    """A new draft replaces the locked design; nothing about the old one stays
    live (the archived copy in history stays readable)."""
    if not formal_path_applies(state):
        return {**state, "design": draft}
    updated = supersede(state, "design_superseded", design=state.get("design"))
    for key in ("research_direction", "main_specification"):
        if key in state:
            updated[key] = None
    return {**updated, "design": draft}


def supersede_dataset(state: dict[str, Any], *, fingerprint: str | None) -> dict[str, Any]:
    """New data: revision moves, approvals die, old preview goes to history."""
    block_before = chain(state)
    updated = supersede(
        state,
        "dataset_superseded",
        dataset_revision=block_before["dataset_revision"],
        dataset_fingerprint=block_before["dataset_fingerprint"],
    )
    block = chain(updated)
    if "main_specification" in state:
        updated = {**updated, "main_specification": None}
    return with_chain(
        updated,
        {
            **block,
            "dataset_revision": block_before["dataset_revision"] + 1,
            "dataset_fingerprint": fingerprint,
        },
    )


def supersede_sample_definition(
    state: dict[str, Any], *, reason: str
) -> dict[str, Any]:
    """Cleaning / sample-filter rules changed: the sample identity moved.

    The bound file is the same one, so the fingerprint stays; the revision
    moves (the preview identity includes it) and the previous sample/setting
    approvals die with the preview they were given.
    """
    block_before = chain(state)
    updated = supersede(state, "sample_superseded", reason=reason)
    block = chain(updated)
    return with_chain(
        updated,
        {**block, "dataset_revision": block_before["dataset_revision"] + 1},
    )


def archive_stale_run_result(
    state: dict[str, Any], *, binding: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    """A run admitted for a superseded version writes history, not the state."""
    block = chain(state)
    entry = {
        "at": _now_iso(),
        "kind": "stale_run_result",
        "binding": binding,
        "result": result,
    }
    degradations = list(state.get("degradations") or [])
    degradations.append(
        {
            "node": "prewrite",
            "reason": "stale_run_result",
            "fallback": "kept_history",
            "visible": True,
        }
    )
    return with_chain(
        {**state, "degradations": degradations},
        {**block, "history": (block["history"] + [entry])[-HISTORY_LIMIT:]},
    )


# ---------------------------------------------------------------------------
# Request ledger: one intention, one confirmation
# ---------------------------------------------------------------------------


def request_replay(
    state: Mapping[str, Any] | None, key: str | None, *, action: str, payload: Any
) -> bool:
    """True when this exact intention was already recorded under this key."""
    if not key:
        return False
    record = chain(state)["requests"].get(str(key))
    if not isinstance(record, dict):
        return False
    matches = (
        record.get("action") == action
        and record.get("payload") == _digest(payload)
    )
    if not matches:
        raise HTTPException(409, detail={"code": "idempotency_conflict"})
    return True


def remember_request(
    state: dict[str, Any],
    key: str | None,
    *,
    action: str,
    payload: Any,
) -> dict[str, Any]:
    if not key:
        return dict(state)
    block = chain(state)
    requests = dict(block["requests"])
    requests[str(key)] = {
        "action": action,
        "payload": _digest(payload),
        "at": _now_iso(),
    }
    if len(requests) > REQUEST_LIMIT:
        ordered = sorted(requests.items(), key=lambda item: item[1].get("at") or "")
        requests = dict(ordered[-REQUEST_LIMIT:])
    return with_chain(state, {**block, "requests": requests})


def validate_confirmation_options(state: dict, incoming: Mapping[str, Any]) -> None:
    """Confirmation cannot silently edit the object or its blocking rules."""
    if not formal_path_applies(state):
        return
    from agent.engine.prewrite_gates import (
        public_prewrite_gates, normalize_q_type, normalize_spec_mode,
    )
    current = public_prewrite_gates(state)
    for field, normalize in (("qType", normalize_q_type), ("specMode", normalize_spec_mode)):
        value = incoming.get(field)
        if value is not None and normalize(value) != current[field]:
            raise _mismatch(field, current[field], value)
    interaction = incoming.get("hasInteraction")
    if interaction is not None and interaction != current["blockingDecision"]["hasInteraction"]:
        raise _mismatch("hasInteraction", current["blockingDecision"]["hasInteraction"], interaction)


def apply_confirmation_command(state: dict, incoming: dict, key: str | None) -> dict:
    """Pure confirmation transition; caller holds the session write lock."""
    from agent.engine.prewrite_gates import evaluate_blocking_decision, merge_confirm_flags, persist_gate_fields
    from services.formal_chain import require_confirm_attached, require_design_confirmed

    require_confirm_attached(state)
    require_design_confirmed(state)
    validate_confirmation_options(state, incoming)
    replayed = request_replay(state, key, action="record_confirms", payload=incoming)
    out = persist_gate_fields(state, incoming)
    if formal_path_applies(state):
        if not replayed:
            out = record_confirms(out, incoming)
        flags = bound_confirm_flags(out)
    else:
        flags = merge_confirm_flags(out, incoming)
    decision = evaluate_blocking_decision(out, incoming)
    if flags["specConfirmed"] and decision.get("blocked"):
        raise HTTPException(409, detail={"code": "estimate_blocked", "blockingDecision": decision})
    if not replayed:
        out = remember_request(out, key, action="record_confirms", payload=incoming)
    return persist_gate_fields(out, incoming,
        table1_confirmed=flags["table1Confirmed"], spec_confirmed=flags["specConfirmed"])


# ---------------------------------------------------------------------------
# Run binding
# ---------------------------------------------------------------------------


def run_binding(state: Mapping[str, Any] | None) -> dict[str, Any]:
    block = chain(state)
    return {
        "revision": design_revision(state.get("design") if isinstance(state, Mapping) else None),
        "design": design_identity(
            state.get("design") if isinstance(state, Mapping) else None
        ),
        "dataset_revision": block["dataset_revision"],
        "dataset_fingerprint": block["dataset_fingerprint"],
    }


def binding_is_current(state: Mapping[str, Any] | None, binding: Any) -> bool:
    if not isinstance(binding, dict) or not binding:
        return True
    return binding == run_binding(state)


# ---------------------------------------------------------------------------
# Executed content must match the approved version (R3)
# ---------------------------------------------------------------------------


def _mismatch(field: str, expected: Any, submitted: Any) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={
            "code": CODE_DESIGN_EXECUTION_MISMATCH,
            "field": field,
            "expected": expected,
            "submitted": submitted,
        },
    )


def align_direction(state: Mapping[str, Any] | None, submitted: Mapping[str, Any]) -> dict:
    """Return the direction the confirmed design authorizes.

    The approved design is authoritative for the fields it declares: a
    submitted value that contradicts it is refused instead of executed, and a
    field the caller left out is filled from the design. Sessions without a
    locked design (legacy / direct bind) keep the submitted payload as-is.
    """
    out = dict(submitted)
    design = state.get("design") if isinstance(state, Mapping) else None
    if not is_design_locked(design):
        return out

    from agent.design.spec import DirectionSpec, norm_method

    normalized_design = DirectionSpec.from_direction(design)

    checks = (
        ("iv", design.get("treatment"), _text),
        ("dv", design.get("outcome"), _text),
        ("method", design.get("method"), norm_method),
    )
    for field, expected, norm in checks:
        if not _is_declared(expected):
            if formal_path_applies(state) and _is_declared(out.get(field)):
                raise _mismatch(field, expected, out.get(field))
            continue
        expected_norm = norm(expected)
        incoming = _text(out.get(field))
        if incoming is None:
            out[field] = expected
            continue
        if norm(incoming) != expected_norm:
            raise _mismatch(field, expected, out.get(field))

    if isinstance(design.get("controls"), (list, tuple)):
        expected_controls = _sequence(design.get("controls"))
        if _sequence(out.get("controls")) != expected_controls:
            raise _mismatch("controls", design.get("controls"), out.get("controls"))
        out["controls"] = list(design.get("controls"))

    # Method-specific fields are just as material as Y/X. Resolve aliases
    # before comparing, then emit one canonical value for every alias so a
    # downstream node cannot choose a different spelling with a different value.
    aliases = {
        "instruments": ("instruments", "instrument", "instrument_col"),
        "endogenous": ("endogenous", "endogenous_col"),
        "running_var": ("running_var", "running", "running_variable"),
        "cluster": ("cluster", "cluster_col"),
        "time_col": ("time_col", "time"),
        "id_col": ("id_col", "id"),
        "first_treat_col": ("first_treat_col", "treatment_group_col"),
        "unit_col": ("unit_col", "unit"),
    }
    sequences = set(_DESIGN_SEQUENCE_KEYS) - {"controls"}
    keys = (set(_DESIGN_SCALAR_KEYS) | sequences) - {"method", "outcome", "treatment", "controls"}

    def normalized(key: str, value: Any) -> Any:
        if key == "interactions":
            items = value if isinstance(value, (list, tuple)) else [value] if value else []
            return sorted(str(item.get("term") or f"{item.get('left')}:{item.get('right')}")
                          if isinstance(item, Mapping) else str(item).strip() for item in items)
        if key in sequences:
            return _sequence(value)
        if key == "cutoff" and value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return _text(value)
        return _text(value)

    for key in sorted(keys):
        names = aliases.get(key, (key,))
        expected = next((design[name] for name in names if _text(design.get(name)) is not None), None)
        if expected is None and normalized_design is not None:
            expected = getattr(normalized_design, key, None)
        if key == "cutoff" and norm_method(design.get("method")) == "rd" and expected is None:
            expected = 0.0
        expected_norm = normalized(key, expected)
        provided = [(name, out[name]) for name in names if _text(out.get(name)) is not None]
        for name, value in provided:
            # Empty optional arrays added by request defaults do not override
            # an approved list. Non-empty aliases must all agree.
            if value == []:
                continue
            if normalized(key, value) != expected_norm:
                raise _mismatch(name, expected, value)
        for name in names:
            out.pop(name, None)
        if expected is not None:
            out[key] = expected

    # Alias values for the outcome/treatment cannot contradict the canonical
    # fields when later nodes read those aliases rather than dv/iv.
    for canonical, aliases_for_field in (("dv", ("outcome", "outcome_col")),
                                         ("iv", ("treatment", "treatment_col"))):
        for alias in aliases_for_field:
            supplied = _text(out.get(alias))
            if supplied is not None and supplied != _text(out.get(canonical)):
                raise _mismatch(alias, out.get(canonical), supplied)
            out.pop(alias, None)

    return out


__all__ = [
    "CHAIN_KEY",
    "align_direction",
    "archive_stale_run_result",
    "binding_is_current",
    "bound_confirm_flags",
    "chain",
    "confirmations",
    "dataset_identity",
    "design_execution_projection",
    "design_identity",
    "diagnosis_identity",
    "has_preview",
    "preview_identity",
    "record_confirms",
    "risk_is_current",
    "run_binding",
    "sample_is_current",
    "setting_is_current",
    "stale_confirmation_present",
    "supersede",
    "supersede_dataset",
    "supersede_design",
    "with_chain",
]
