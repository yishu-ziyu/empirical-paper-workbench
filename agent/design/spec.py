"""Normalize a research direction into the fields downstream nodes already read."""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from typing import Any


_METHOD_ALIASES = {
    "ols": "ols",
    "did": "did",
    "difference-in-differences": "did",
    "diff-in-diff": "did",
    "difference_in_differences": "did",
    "iv": "iv",
    "instrumental-variables": "iv",
    "instrumental-variable": "iv",
    "2sls": "iv",
    "rd": "rd",
    "rdd": "rd",
    "regression-discontinuity": "rd",
    "regression-discontinuity-design": "rd",
    "scm": "scm",
    "synthetic-control": "scm",
    "synthetic control": "scm",
    "synthetic_control": "scm",
}


def norm_method(method: Any) -> str | None:
    """Map aliases to ols / did / iv / rd / scm. Unknown → None."""
    if method is None:
        return None
    key = str(method).strip().lower()
    if not key:
        return None
    return _METHOD_ALIASES.get(key)


def slug_for_topic(topic: str) -> str:
    """Stable slug for a research question. Known pilots keep readable names."""
    known = {
        "父母受教育水平对子女工资收入的影响": "parent_education_wage",
        "城乡居民基本医疗保险整合是否降低农村中老年人的住院自付支出？": "charls_did_urb_rur_insurance",
    }
    if topic in known:
        return known[topic]
    digest = hashlib.sha1(topic.encode("utf-8")).hexdigest()[:10]
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "_", topic).strip("_").lower()
    if ascii_part:
        return f"{ascii_part[:24]}_{digest}"
    return f"topic_{digest}"


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [c.strip() for c in value.split(",") if c.strip()]
    return [str(c).strip() for c in value if str(c).strip()]


def _first_str(rd: dict[str, Any], *keys: str) -> str:
    for key in keys:
        raw = rd.get(key)
        if raw is None:
            continue
        text = str(raw).strip()
        if text:
            return text
    return ""


@dataclass
class DirectionSpec:
    """Normalized view of the user's research direction."""

    topic: str
    slug: str
    outcome: str = ""
    treatment: str = ""
    controls: list[str] = field(default_factory=list)
    method: str = ""
    template: str = "cn_journal"
    claim: str = "association"
    notes: str = ""
    time_col: str = ""
    id_col: str = ""
    first_treat_col: str = ""
    instruments: list[str] = field(default_factory=list)
    endogenous: str = ""
    running_var: str = ""
    cutoff: Any = None
    unit_col: str = ""
    treated_unit: Any = None
    treatment_time: Any = None
    cluster: str = ""
    cluster_levels: list[str] = field(default_factory=list)
    heterogeneity_groups: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def _ols_formula(self) -> str:
        rhs = [self.treatment, *[c for c in self.controls if c and c != self.treatment]]
        return f"{self.outcome} ~ {' + '.join(rhs)}"

    def _iv_formula(self) -> str:
        endog = self.endogenous or self.treatment
        z = " + ".join(self.instruments)
        extra_terms = [
            c
            for c in self.controls
            if c and c != endog and c not in self.instruments
        ]
        extra = f" + {' + '.join(extra_terms)}" if extra_terms else ""
        return f"{self.outcome} ~ ({endog} ~ {z}){extra}"

    def to_main_specification(self) -> dict[str, Any]:
        """Project into the spec estimate / robustness already read."""
        method = norm_method(self.method) or (self.method.strip().lower() if self.method else "")
        if method == "rd":
            if not self.outcome or not self.running_var:
                return {}
            return {
                "method": "rd",
                "outcome": self.outcome,
                "treatment": self.treatment,
                "controls": list(self.controls),
                "running_var": self.running_var,
                "cutoff": 0.0 if self.cutoff is None else self.cutoff,
                "cluster": self.cluster,
                "cluster_levels": list(self.cluster_levels),
                "heterogeneity_groups": list(self.heterogeneity_groups),
                "produced_by": "set_direction",
            }
        if method == "scm":
            if not self.outcome:
                return {}
            return {
                "method": "scm",
                "outcome": self.outcome,
                "treatment": self.treatment,
                "controls": list(self.controls),
                "unit": self.unit_col,
                "unit_col": self.unit_col,
                "time": self.time_col,
                "time_col": self.time_col,
                "treated_unit": self.treated_unit,
                "treatment_time": self.treatment_time,
                "cluster": self.cluster,
                "cluster_levels": list(self.cluster_levels),
                "heterogeneity_groups": list(self.heterogeneity_groups),
                "produced_by": "set_direction",
            }
        if method == "iv":
            if not self.outcome or not (self.endogenous or self.treatment):
                return {}
            endog = self.endogenous or self.treatment
            payload = {
                "method": "iv",
                "outcome": self.outcome,
                "treatment": endog,
                "endogenous": endog,
                "instruments": list(self.instruments),
                "controls": list(self.controls),
                "cluster": self.cluster,
                "cluster_levels": list(self.cluster_levels),
                "heterogeneity_groups": list(self.heterogeneity_groups),
                "produced_by": "set_direction",
            }
            if self.instruments:
                iv_formula = self._iv_formula()
                payload["iv_formula"] = iv_formula
                payload["formula"] = iv_formula
            return payload
        if not self.outcome or not self.treatment:
            return {}
        formula = self._ols_formula()
        payload = {
            "method": method or "ols",
            "formula": formula,
            "outcome": self.outcome,
            "treatment": self.treatment,
            "controls": list(self.controls),
            "cluster": self.cluster,
            "cluster_levels": list(self.cluster_levels),
            "heterogeneity_groups": list(self.heterogeneity_groups),
            "produced_by": "set_direction",
        }
        if method == "did":
            payload["time_col"] = self.time_col
            payload["id_col"] = self.id_col
            payload["first_treat_col"] = self.first_treat_col
            if self.id_col and self.time_col:
                payload["feols_formula"] = (
                    f"{formula} | {self.id_col} + {self.time_col}"
                )
        return payload

    def enrich_direction(self, rd: dict[str, Any]) -> dict[str, Any]:
        """Fill identification_verify aliases without dropping user fields."""
        out = dict(rd)
        if self.outcome:
            out.setdefault("dv", self.outcome)
            out.setdefault("outcome", self.outcome)
            out.setdefault("outcome_col", self.outcome)
        if self.treatment:
            out.setdefault("iv", self.treatment)
            out.setdefault("treatment", self.treatment)
            out.setdefault("treatment_col", self.treatment)
        if self.method:
            out.setdefault("method", self.method)
        if self.controls and not out.get("controls"):
            out["controls"] = list(self.controls)
        if self.topic and not out.get("question"):
            out["question"] = self.topic
        if self.time_col:
            out.setdefault("time_col", self.time_col)
            out.setdefault("time", self.time_col)
        if self.id_col:
            out.setdefault("id_col", self.id_col)
            out.setdefault("id", self.id_col)
        if self.first_treat_col:
            out.setdefault("first_treat_col", self.first_treat_col)
        if self.instruments:
            out.setdefault("instruments", list(self.instruments))
            out.setdefault("instrument", self.instruments[0])
            out.setdefault("instrument_col", self.instruments[0])
        if self.endogenous:
            out.setdefault("endogenous", self.endogenous)
            out.setdefault("endogenous_col", self.endogenous)
        if self.running_var:
            out.setdefault("running_var", self.running_var)
            out.setdefault("running", self.running_var)
        if self.cutoff is not None:
            out.setdefault("cutoff", self.cutoff)
        if self.unit_col:
            out.setdefault("unit_col", self.unit_col)
            out.setdefault("unit", self.unit_col)
        if self.treated_unit is not None:
            out.setdefault("treated_unit", self.treated_unit)
        if self.treatment_time is not None:
            out.setdefault("treatment_time", self.treatment_time)
        if self.cluster:
            out.setdefault("cluster", self.cluster)
        if self.cluster_levels and not out.get("cluster_levels"):
            out["cluster_levels"] = list(self.cluster_levels)
        if self.heterogeneity_groups and not out.get("heterogeneity_groups"):
            out["heterogeneity_groups"] = list(self.heterogeneity_groups)
        return out

    @classmethod
    def from_direction(cls, rd: Any) -> "DirectionSpec | None":
        """Build from the direction form payload.

        Accepts dict ``{question, dv, iv, controls, method, template}``
        plus method columns (instrument / running / time_col / ...).
        Or a plain question string. Returns None if there is nothing to use.
        """
        if isinstance(rd, str):
            topic = rd.strip()
            if not topic:
                return None
            return cls(topic=topic, slug=slug_for_topic(topic))
        if not isinstance(rd, dict):
            return None
        topic = str(rd.get("question") or rd.get("topic") or "").strip()
        outcome = str(rd.get("dv") or rd.get("outcome") or rd.get("outcome_col") or "").strip()
        treatment = str(
            rd.get("iv") or rd.get("treatment") or rd.get("treatment_col") or ""
        ).strip()
        if not topic and not outcome and not treatment:
            return None
        controls = _as_str_list(rd.get("controls"))
        instruments = _as_str_list(rd.get("instruments"))
        if not instruments:
            one = _first_str(rd, "instrument", "instrument_col")
            if one:
                instruments = [one]
        cutoff = rd.get("cutoff")
        if cutoff is not None and cutoff != "":
            try:
                cutoff = float(cutoff)
            except (TypeError, ValueError):
                pass
        else:
            cutoff = None
        treated_unit = rd.get("treated_unit")
        if treated_unit == "":
            treated_unit = None
        treatment_time = rd.get("treatment_time")
        if treatment_time == "":
            treatment_time = None
        return cls(
            topic=topic or f"{treatment} → {outcome}".strip(" →"),
            slug=slug_for_topic(topic or f"{treatment}_{outcome}"),
            outcome=outcome,
            treatment=treatment,
            controls=controls,
            method=str(rd.get("method") or "").strip(),
            template=str(rd.get("template") or "cn_journal").strip() or "cn_journal",
            claim=str(rd.get("claim") or "association"),
            notes=str(rd.get("notes") or ""),
            time_col=_first_str(rd, "time_col", "time"),
            id_col=_first_str(rd, "id_col", "id"),
            first_treat_col=_first_str(rd, "first_treat_col", "treatment_group_col"),
            instruments=instruments,
            endogenous=_first_str(rd, "endogenous", "endogenous_col") or treatment,
            running_var=_first_str(rd, "running_var", "running", "running_variable"),
            cutoff=cutoff,
            unit_col=_first_str(rd, "unit_col", "unit"),
            treated_unit=treated_unit,
            treatment_time=treatment_time,
            cluster=_first_str(rd, "cluster", "cluster_col"),
            cluster_levels=_as_str_list(rd.get("cluster_levels")),
            heterogeneity_groups=_as_str_list(rd.get("heterogeneity_groups")),
        )
