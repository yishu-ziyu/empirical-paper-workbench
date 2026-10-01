"""Data-aware design mapping (own-data path)."""
from __future__ import annotations

import json

import pytest

from agent.design.propose import propose_design
from agent.design.propose_data import apply_design_overrides, map_design_to_data


DATASET = {
    "name": "CGSS2023.dta",
    "rows": 100,
    "columns": ["a8a", "a7a", "a2", "a3a", "a18", "isurban", "a69"],
    "dtypes": {c: "float64" for c in ["a8a", "a7a", "a2", "a3a", "a18", "isurban", "a69"]},
    "variable_labels": {
        "a8a": "个人去年全年总收入",
        "a7a": "最高教育程度",
        "a2": "性别",
        "a3a": "年龄",
        "a18": "户口登记状况",
        "isurban": "居委会/村委会",
        "a69": "婚姻状况",
    },
    "value_labels": {
        "a7a": {"-3": "拒绝回答", "13": "大学本科"},
        "isurban": {"1": "居委会", "2": "村委会"},
    },
}


def _llm_ok(prompt: str) -> str:
    return json.dumps(
        {
            "method": "ols",
            "outcome": "a8a",
            "treatment": "a7a",
            "controls": ["a2", "a3a", "a18"],
            "heterogeneity_groups": ["isurban"],
            "instruments": [],
            "group": "",
            "treated": "",
            "period": "",
            "time_col": "",
            "id_col": "",
            "notes": ["a8a 含 9999999 等缺失代码", "a7a 是有序编码不是受教育年限"],
            "question_to_user": "",
        },
        ensure_ascii=False,
    )


def test_map_design_to_data_uses_real_columns():
    draft = propose_design("受教育程度对个人收入的影响", "控制性别年龄户口，看城乡差异")
    assert draft["outcome"] == "wages"  # rule-only still uses generic slots
    mapped = map_design_to_data(
        draft, DATASET, title="受教育程度对个人收入的影响", question="控制性别年龄户口，看城乡差异", llm=_llm_ok
    )
    assert mapped["outcome"] == "a8a"
    assert mapped["treatment"] == "a7a"
    assert mapped["controls"] == ["a2", "a3a", "a18"]
    assert mapped["heterogeneity_groups"] == ["isurban"]
    assert mapped["qType"] == "heterogeneity"
    assert mapped["interactions"] == [
        {"kind": "het", "left": "a7a", "right": "isurban", "term": "a7a:isurban"}
    ]
    assert mapped["proposal"]["source"] == "llm"
    assert "a8a 含" in mapped["proposal"]["notes"][0]


def test_map_design_drops_hallucinated_columns():
    def bad(_prompt: str) -> str:
        return json.dumps(
            {
                "method": "ols",
                "outcome": "income",
                "treatment": "educ",
                "controls": ["gender", "a2"],
                "heterogeneity_groups": ["urban"],
            }
        )

    draft = propose_design("教育与收入", "")
    mapped = map_design_to_data(draft, DATASET, title="教育与收入", llm=bad)
    assert mapped["outcome"] == ""
    assert mapped["treatment"] == ""
    assert mapped["controls"] == ["a2"]
    assert mapped["heterogeneity_groups"] == []
    assert "income" in mapped["proposal"]["dropped"]
    assert "educ" in mapped["proposal"]["dropped"]


def test_map_design_clears_fake_slots_when_llm_fails():
    def boom(_prompt: str) -> str:
        raise RuntimeError("LLM down")

    draft = propose_design("教育与收入", "")
    mapped = map_design_to_data(draft, DATASET, title="教育与收入", llm=boom)
    assert mapped["outcome"] == ""
    assert mapped["treatment"] == ""
    assert mapped["proposal"]["source"] == "rule"
    assert mapped["proposal"]["error"] == "RuntimeError"


def test_apply_overrides_rejects_unknown_column():
    draft = propose_design("教育与收入", "")
    with pytest.raises(ValueError, match="unknown_column:fake"):
        apply_design_overrides(draft, {"outcome": "fake"}, DATASET["columns"])


def test_apply_overrides_rebuilds_het_interaction():
    draft = propose_design("教育与收入", "")
    draft = map_design_to_data(draft, DATASET, title="教育与收入", llm=_llm_ok)
    edited = apply_design_overrides(
        draft,
        {"heterogeneity_groups": ["a69"], "controls": ["a2", "a3a"]},
        DATASET["columns"],
    )
    assert edited["heterogeneity_groups"] == ["a69"]
    assert edited["interactions"] == [
        {"kind": "het", "left": "a7a", "right": "a69", "term": "a7a:a69"}
    ]
    assert edited["qType"] == "heterogeneity"


def test_explicit_iv_method_is_kept():
    draft = propose_design("教育回报的工具变量估计", "用父亲教育作工具变量做 IV")
    assert draft["method"] == "iv"

    def wants_ols(prompt: str) -> str:
        return json.dumps(
            {
                "method": "ols",
                "outcome": "a8a",
                "treatment": "a7a",
                "instruments": ["a89b"] if "a89b" in prompt else [],
                "controls": ["a2"],
            }
        )

    ds = {**DATASET, "columns": DATASET["columns"] + ["a89b"],
          "variable_labels": {**DATASET["variable_labels"], "a89b": "父亲最高教育程度"}}
    mapped = map_design_to_data(draft, ds, title="教育回报的工具变量估计", question="用父亲教育作工具变量做 IV", llm=wants_ols)
    assert mapped["method"] == "iv"
    assert mapped["instruments"] == ["a89b"]
