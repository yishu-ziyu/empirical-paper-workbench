"""set_direction 节点。

确认用户的研究方向，并写出 ``main_specification``，
给识别验真 / 稳健性 / 设定表使用。
"""
from __future__ import annotations

from typing import Any

from ..design.spec import DirectionSpec
from ..protocols import SetDirectionOutput
from ..state import EconPaperState


_CHARLS_ID_KEYS = {"pid", "id"}
_CHARLS_TIME_KEYS = {"wave", "year"}
_CSV_TIME_NAMES = ("year", "wave")
_CSV_ID_NAMES = ("id", "pid", "state")


def _filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, tuple)) and not value:
        return False
    return True


def _set_if_empty(rd: dict[str, Any], key: str, value: Any) -> bool:
    if _filled(rd.get(key)) or not _filled(value):
        return False
    rd[key] = value
    return True


def _charls_id_time(cfg: Any) -> tuple[str, str]:
    if not isinstance(cfg, dict):
        return "", ""
    mapping = cfg.get("variable_mapping") or {}
    if not isinstance(mapping, dict):
        return "", ""
    id_col = ""
    time_col = ""
    for raw, mapped in mapping.items():
        key = str(raw).strip().lower()
        dest = str(mapped).strip() if mapped is not None else ""
        if not dest:
            continue
        if key in _CHARLS_ID_KEYS and not id_col:
            id_col = dest
        if key in _CHARLS_TIME_KEYS and not time_col:
            time_col = dest
    return id_col, time_col


def _guess_columns_from_csv(csv_path: str) -> tuple[str, str]:
    try:
        import pandas as pd

        columns = {str(c) for c in pd.read_csv(csv_path, nrows=0).columns}
    except Exception:
        return "", ""
    time_col = next((name for name in _CSV_TIME_NAMES if name in columns), "")
    id_col = next((name for name in _CSV_ID_NAMES if name in columns), "")
    return id_col, time_col


def project_method_columns(
    state: EconPaperState, rd: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Fill method columns. First source wins; never overwrite a user value.

    1. DirectionRequest fields already on ``rd``
    2. ``charls_config.variable_mapping`` (pid → id_col, wave → time_col)
    3. ``state.panel_id`` / ``state.time_col``
    4. CSV columns exactly named year/wave/id/pid/state
    """
    out = dict(rd)
    degradations: list[dict[str, Any]] = []

    if not out.get("instruments"):
        one = out.get("instrument") or out.get("instrument_col")
        if _filled(one):
            out["instruments"] = [one] if isinstance(one, str) else list(one)
    if not _filled(out.get("endogenous")) and not _filled(out.get("endogenous_col")):
        if _filled(out.get("iv") or out.get("treatment")):
            # endogenous defaults later in DirectionSpec; leave blank here
            pass
    if not _filled(out.get("running_var")):
        _set_if_empty(out, "running_var", out.get("running") or out.get("running_variable"))

    charls_id, charls_time = _charls_id_time(state.get("charls_config"))
    _set_if_empty(out, "id_col", charls_id)
    _set_if_empty(out, "time_col", charls_time)

    _set_if_empty(out, "id_col", state.get("panel_id"))
    _set_if_empty(out, "time_col", state.get("time_col"))

    if (not _filled(out.get("id_col")) or not _filled(out.get("time_col"))) and state.get(
        "csv_path"
    ):
        guessed_id, guessed_time = _guess_columns_from_csv(str(state.get("csv_path")))
        if _set_if_empty(out, "id_col", guessed_id):
            degradations.append(
                {
                    "node": "set_direction",
                    "reason": "column_guessed",
                    "field": "id_col",
                    "value": guessed_id,
                    "visible": True,
                }
            )
        if _set_if_empty(out, "time_col", guessed_time):
            degradations.append(
                {
                    "node": "set_direction",
                    "reason": "column_guessed",
                    "field": "time_col",
                    "value": guessed_time,
                    "visible": True,
                }
            )
    return out, degradations


def set_direction(state: EconPaperState) -> SetDirectionOutput:
    """确认研究方向，必要时写出 main_specification。

    backend POST /sessions/{id}/direction 已把
    {question, dv, iv, controls, method, template, 方法列} 写入
    state.research_direction。无有效方向时仍透传原字段，保持旧调用方行为。
    """
    rd = state.get("research_direction")
    spec = DirectionSpec.from_direction(rd)
    if spec is None:
        return {"research_direction": rd}

    rd_dict = dict(rd) if isinstance(rd, dict) else {"question": rd}
    projected, degradations = project_method_columns(state, rd_dict)
    spec = DirectionSpec.from_direction(projected) or spec
    enriched = spec.enrich_direction(projected)
    out: SetDirectionOutput = {"research_direction": enriched}
    main_spec = spec.to_main_specification()
    if main_spec:
        out["main_specification"] = main_spec
    if degradations:
        out["degradations"] = list(state.get("degradations") or []) + degradations  # type: ignore[typeddict-unknown-key]
    return out
