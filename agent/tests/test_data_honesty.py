"""Honesty fail-closed for n<200 demo / found-data claims."""
from agent.data_honesty import DEMO_MIN_ROWS, honesty_for_n, is_found_scale, is_toy_filename


def test_rows_below_200_cannot_claim_demo_success():
    honesty = honesty_for_n(24, name="panel.csv")
    assert honesty["demo_success"] is False
    assert honesty["found"] is False
    assert str(DEMO_MIN_ROWS) in honesty["honesty_warning"]
    assert is_found_scale(24) is False
    assert is_found_scale(200) is True


def test_toy_filenames_are_never_found():
    honesty = honesty_for_n(500, name="course-panel.csv")
    assert honesty["demo_success"] is False
    assert honesty["teaching_fixture"] is True
    assert honesty["found"] is False
    assert is_toy_filename("minimum_wage.csv")
    assert is_toy_filename("sanitized_sample.csv")
    assert is_toy_filename("wage1.csv")


def test_found_scale_real_file_can_claim_demo_success():
    honesty = honesty_for_n(768, name="ck1994_long.csv")
    assert honesty["demo_success"] is True
    assert honesty["found"] is True
    assert honesty["honesty_warning"] is None
    assert honesty["teaching_fixture"] is False
