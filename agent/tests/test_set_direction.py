"""set_direction writes a runnable specification from the direction form."""
from agent.nodes.set_direction import set_direction


def test_set_direction_writes_main_specification():
    result = set_direction(
        {
            "research_direction": {
                "question": "教育回报",
                "dv": "ln_wage",
                "iv": "edu",
                "controls": ["age"],
                "method": "ols",
            }
        }
    )
    assert result["research_direction"]["outcome_col"] == "ln_wage"
    assert result["main_specification"]["formula"] == "ln_wage ~ edu + age"
    assert "design_card" not in result


def test_set_direction_passthrough_when_empty():
    assert set_direction({}) == {"research_direction": None}
    assert set_direction({"research_direction": {}}) == {"research_direction": {}}
