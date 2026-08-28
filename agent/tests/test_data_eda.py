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


def test_compute_csv_eda_caps_wide_columns(tmp_path):
    from engine.data_eda import _EDA_COL_CAP

    n_cols = _EDA_COL_CAP + 5
    names = [f"c{i}" for i in range(n_cols)]
    csv_path = tmp_path / "wide.csv"
    csv_path.write_text(
        ",".join(names) + "\n" + ",".join("1" for _ in names) + "\n",
        encoding="utf-8",
    )
    summary, table = compute_csv_eda({"csv_path": str(csv_path)})
    assert f"1 行 × {n_cols} 列" in summary
    assert f"上限 {_EDA_COL_CAP}" in summary
    assert "| c0 |" in table
    assert f"| c{_EDA_COL_CAP} |" not in table
    assert "CHARLS" not in summary


def test_bind_skips_csv_eda_unless_data_desc(monkeypatch):
    called = []

    def fake_eda(_state):
        called.append(1)
        return "S", "T"

    monkeypatch.setattr("engine.bind.compute_csv_eda", fake_eda)
    intro = bind_chapter_kwargs({"csv_path": "/tmp/x.csv"}, {"type": "intro"})
    assert called == []
    assert intro["data_summary"] == ""
    assert intro["eda_results"] == ""
    desc = bind_chapter_kwargs({"csv_path": "/tmp/x.csv"}, {"type": "data_desc"})
    assert called == [1]
    assert desc["eda_results"] == "T"


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
