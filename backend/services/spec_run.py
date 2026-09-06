"""Execute admissible specifications without touching canonical estimate."""
from __future__ import annotations

from typing import Any, Callable

import pandas as pd

from agent.nodes.estimate import (
    _estimate_iv,
    _estimate_ols,
    analysis_dataset_identity,
)
from services.research_lab import (
    _as_float,
    _event,
    _now,
    bump_evidence_revision,
    comparable_spec_ids,
    definition_by_id,
    evaluate_surprise,
    included_spec_ids,
    maybe_draft_card_claim,
    next_card_challenge,
    strip_spec_run_result,
    temporary_spec,
)

ProgressFn = Callable[[str, str, dict], None]


class SpecRunRejected(RuntimeError):
    """Stable worker failure; not an HTTP 500 / NameError."""

    def __init__(self, code: str, message: str | None = None):
        self.code = code
        super().__init__(message or code)


def _num(value: Any) -> float | None:
    return _as_float(value)


def _covariance(estimator: str) -> str:
    if estimator == "statspai.ivreg":
        return "nonrobust"
    return "HC1"


def _iv_diagnostics(df: pd.DataFrame, controls: list[str]) -> dict[str, Any]:
    """First-stage strength from THIS spec's controls, not uncontrolled iv_diag."""
    import statspai

    try:
        result = statspai.effective_f_test(
            df,
            endog="educ",
            instruments=["nearc4"],
            exog=list(controls) or None,
            vcov="HC1",
        )
        f_eff = _num(result.get("F_eff"))
        first_stage = _num(result.get("first_stage_F"))
        return {
            "test": "effective_f_test",
            "F_eff": f_eff,
            "first_stage_F": first_stage,
            "strength": result.get("strength"),
            "covariance": "HC1",
            "controls": list(controls),
        }
    except Exception as exc:
        return {
            "test": "effective_f_test",
            "status": "error",
            "error": str(exc),
            "controls": list(controls),
        }


def _run_one(
    *,
    df: pd.DataFrame,
    state: dict[str, Any],
    definition: dict[str, Any],
    relation: str,
    producer_run_id: str,
) -> dict[str, Any]:
    columns = [str(col) for col in df.columns]
    spec = temporary_spec(definition, columns)
    formula = str(spec["formula"])
    estimator_kind = spec.get("method") or "ols"
    if estimator_kind == "iv":
        output = _estimate_iv(df, spec, formula)
        diagnostics = _iv_diagnostics(df, list(spec.get("controls") or []))
    else:
        output = _estimate_ols(df, spec, formula)
        diagnostics = None
    estimate = output.get("estimate") if isinstance(output.get("estimate"), dict) else {}
    estimator = str(estimate.get("estimator") or "")
    identity = analysis_dataset_identity(state, state.get("csv_path"))
    status = str(estimate.get("status") or "ok")
    return {
        "id": f"{producer_run_id}:{definition.get('id')}",
        "spec_id": definition.get("id"),
        "spec_version": 1,
        "label": definition.get("label"),
        "choices": list(definition.get("choices") or []),
        "estimator": estimator,
        "method": estimator_kind,
        "formula": estimate.get("formula") or formula,
        "covariance": _covariance(estimator),
        "analysis_dataset": identity,
        "producer_run_id": producer_run_id,
        "coef": _num(estimate.get("coef")),
        "se": _num(estimate.get("se")),
        "p": _num(estimate.get("p")),
        "n": int(estimate["n"]) if estimate.get("n") is not None else None,
        "diagnostics": diagnostics,
        "status": status,
        "provenance": {
            "produced_by": "estimate",
            "producer_run_id": producer_run_id,
            "formula": estimate.get("formula") or formula,
        },
        "created_at": _now(),
        "relation": relation,
    }


def execute_spec_run(
    session_id: str,
    run_id: str,
    payload: dict[str, Any],
    progress_callback: ProgressFn | None = None,
) -> dict[str, Any]:
    from facade import facade

    def progress(node: str, status: str, detail: dict | None = None) -> None:
        if progress_callback is not None:
            progress_callback(node, status, detail or {})

    state = facade.get_state(session_id)
    lab = state.get("research_lab")
    if not isinstance(lab, dict) or not lab:
        raise RuntimeError("research lab not found")
    extract_path = lab.get("extract_csv_path") if lab.get("teaching_case") else None
    csv_path = extract_path or state.get("csv_path")
    if not csv_path:
        raise RuntimeError("spec_run missing csv_path")
    df = pd.read_csv(str(csv_path))
    state = {**state, "csv_path": str(csv_path)}
    requested = list(payload.get("spec_ids") or included_spec_ids(lab))
    relation = str(payload.get("relation") or "exploratory")
    allowed = set(included_spec_ids(lab))
    spec_ids = [spec_id for spec_id in requested if spec_id in allowed]
    if not spec_ids:
        raise SpecRunRejected(
            "no_admissible_specifications",
            "no admissible specifications to run",
        )

    new_runs: list[dict[str, Any]] = []
    for spec_id in spec_ids:
        progress("spec_run", "running", {"spec_id": spec_id})
        definition = definition_by_id(lab, spec_id)
        new_runs.append(
            _run_one(
                df=df,
                state=state,
                definition=definition,
                relation=relation,
                producer_run_id=run_id,
            )
        )

    existing = [run for run in (lab.get("specification_runs") or []) if isinstance(run, dict)]
    combined = existing + new_runs
    definitions = (lab.get("specification_space") or {}).get("definitions") or []
    ols_id, iv_id = comparable_spec_ids(definitions)
    surprise = evaluate_surprise(
        lab.get("expectation"),
        combined,
        ols_spec_id=ols_id,
        iv_spec_id=iv_id,
    )
    space = dict(lab.get("specification_space") or {})
    space["revealed"] = True
    events = list(lab.get("decision_events") or [])
    events.append(
        _event(
            "specification_space_run",
            {
                "producer_run_id": run_id,
                "spec_ids": spec_ids,
                "relation": relation,
            },
        )
    )
    updated = {
        **lab,
        "specification_runs": combined,
        "specification_space": space,
        "surprise": surprise,
        "decision_events": events,
    }
    challenge_id = payload.get("challenge_id")
    if challenge_id:
        challenge = dict(updated.get("next_challenge") or {})
        if challenge.get("id") == challenge_id:
            challenge["status"] = "accepted"
            challenge["resulting_runs"] = [run.get("id") for run in new_runs]
            updated["next_challenge"] = challenge
            events.append(_event("challenge_accept", {"id": challenge_id}))
            updated["decision_events"] = events
    elif updated.get("next_challenge") is None:
        updated["next_challenge"] = next_card_challenge(updated)

    updated = bump_evidence_revision(updated)
    updated = maybe_draft_card_claim(updated)
    progress("spec_run", "done", {"count": len(new_runs)})
    return strip_spec_run_result({"research_lab": updated})
