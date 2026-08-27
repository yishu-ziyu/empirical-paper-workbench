"""CSV describe for the data_desc chapter. No invented CHARLS rows."""
from __future__ import annotations

from engine.bind import bind_chapter_kwargs
from engine.data_eda import compute_csv_eda


def test_compute_csv_eda_missing_path_is_empty():
    assert compute_csv_eda({}) == ("", "")
    assert compute_csv_eda({"csv_path": ""}) == ("", "")


def test_compute_csv_eda_missing_file_is_empty(tmp_path):
    assert compute_csv_eda({"csv_path": str(tmp_path / "gone.csv")}) == ("", "")


def test_compute_csv_eda_from_castle_like_csv(tmp_path):
    csv_path = tmp_path / "castle.csv"
    csv_path.write_text(
        "l_homicide,post,sid,year\n"
        "1.2,0,1,1980\n"
        "1.4,0,1,1981\n"
        "2.1,1,2,1980\n"
        "2.4,1,2,1981\n",
        encoding="utf-8",
    )
    summary, table = compute_csv_eda({"csv_path": str(csv_path)})
    assert summary.startswith("4 行 × 4 列")
    assert "l_homicide, post, sid, year" in summary
    assert "表 1 描述统计" in table
    assert "| l_homicide |" in table
    assert "| post |" in table
    assert "CHARLS" not in summary
    assert "CHARLS" not in table


def test_bind_chapter_kwargs_uses_csv_eda(tmp_path):
    csv_path = tmp_path / "castle.csv"
    csv_path.write_text(
        "l_homicide,post\n1.2,0\n1.4,1\n",
        encoding="utf-8",
    )
    bound = bind_chapter_kwargs(
        {"csv_path": str(csv_path), "research_direction": {}},
        {"type": "data_desc"},
    )
    assert "2 行 × 2 列" in bound["data_summary"]
    assert "| l_homicide |" in bound["eda_results"]
