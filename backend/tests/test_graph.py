"""LangGraph graph end-to-end contract tests (T-02, Seam 1 core).

generate_title 节点测试已迁移至 agent/tests/test_generate_title.py
（ADR-0003 Stage C 命名约定）。

本文件保留 graph 结构 + upload_data + clean_data 契约：
- 3 nodes wired: upload_data -> clean_data (detect missing only) -> generate_title (LLM)
- upload_data parses CSV into dataset_meta written into state.uploaded_datasets
- clean_data detects missing values and writes missing_count (does NOT handle them)
"""
from graph import build_graph, graph
from nodes.clean_data import clean_data
from nodes.upload_data import upload_data

from conftest import make_state


def test_graph_has_three_nodes():
    """The graph wires upload_data -> clean_data -> generate_title.

    Beyond node presence, clean_data must actually detect missing values
    (not just be a print-only placeholder). The presence check passes in
    the red stage; the missing-value behavior check fails.
    """
    g = build_graph()
    try:
        node_ids = set(g.get_graph().nodes.keys())
    except Exception as e:  # pragma: no cover - defensive introspection
        assert False, f"could not introspect graph nodes: {e}"
    for name in ("upload_data", "clean_data", "generate_title"):
        assert name in node_ids, f"graph missing node: {name} (have {node_ids})"

    # clean_data must write missing_count into the state — placeholder does not.
    result = graph.invoke(make_state(session_id="t1", uploaded_datasets=[]))
    assert any(
        isinstance(d, dict) and "missing_count" in d
        for d in result.get("uploaded_datasets", [])
    ), "clean_data did not write missing_count into uploaded_datasets"


def test_graph_upload_node_writes_dataset_meta(sample_csv_path):
    """upload_data parses the CSV into dataset_meta (columns/rows/dtypes/missing_count)."""
    state = make_state(
        session_id="t2",
        uploaded_datasets=[{"path": str(sample_csv_path), "format": "csv"}],
    )
    result = upload_data(state)
    datasets = result.get("uploaded_datasets", [])
    assert len(datasets) == 1, f"expected 1 dataset, got {len(datasets)}"
    ds = datasets[0]
    for key in ("columns", "rows", "dtypes", "missing_count"):
        assert key in ds, f"dataset meta missing key: {key} (have {sorted(ds)})"
    assert len(ds["columns"]) == 3, f"expected 3 columns, got {len(ds['columns'])}"
    assert ds["rows"] == 5, f"expected 5 rows, got {ds['rows']}"
    assert ds["missing_count"] == 1, (
        f"expected 1 missing value, got {ds['missing_count']}"
    )


def test_graph_clean_data_detects_missing(sample_csv_path):
    """clean_data detects missing values and writes the count (without handling them)."""
    state = make_state(
        session_id="t3",
        uploaded_datasets=[{"path": str(sample_csv_path), "format": "csv"}],
    )
    # Run upload_data first so dataset_meta is populated, then clean_data.
    after_upload = {**state, **upload_data(state)}
    result = clean_data(after_upload)
    datasets = result.get("uploaded_datasets", after_upload.get("uploaded_datasets", []))
    assert len(datasets) == 1, f"expected 1 dataset, got {len(datasets)}"
    ds = datasets[0]
    assert "missing_count" in ds, (
        f"clean_data did not write missing_count (ds keys: {sorted(ds)})"
    )
    assert ds["missing_count"] == 1, (
        f"expected 1 missing value, got {ds.get('missing_count')!r}"
    )
