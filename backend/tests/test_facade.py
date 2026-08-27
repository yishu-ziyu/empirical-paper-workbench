"""Unit tests for AgentFacade (ADR-0003 Stage B).

Tests the facade in isolation by mocking the module-level node/graph/cleaning
names that the facade looks up at call time. This verifies:

1. Session lifecycle (create / has / get / save / update / seed / drop).
2. Graph invocation (run_upload_pipeline) stores final state + csv_path.
3. Single-node calls (set_direction_and_outline, resume_outline,
   generate_chapter, regenerate_chapter, rollback_chapter, export_document)
   call the right node, persist state, and return the new state / result.
4. Cleaning step calls (transform_variables, filter_sample, balance_panel)
   delegate to the step class with the right config.
5. CSV path management (get_csv_path, set_csv_path, get_datasets, save_datasets).
6. Error handling: 404 for unknown sessions, 503 when agent deps are missing.
7. CHARLS detect / confirm flow.

The facade is a module-level singleton (``facade = AgentFacade()``). Each test
uses ``facade.seed_state`` / ``facade.drop_session`` to isolate itself; no
shared state leaks across tests.
"""
from __future__ import annotations

import pytest

from facade import facade, AgentFacade, public_literature_entries


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------
def test_create_session_returns_id_and_has_session():
    """create_session returns a non-empty id; has_session True after create."""
    sid = facade.create_session()
    assert isinstance(sid, str) and len(sid) > 0
    assert facade.has_session(sid) is True


def test_create_session_with_explicit_id():
    """create_session accepts an explicit session_id."""
    sid = facade.create_session("my-fixed-id")
    assert sid == "my-fixed-id"
    assert facade.has_session("my-fixed-id")
    facade.drop_session("my-fixed-id")


def test_has_session_false_for_unknown():
    assert facade.has_session("no-such-session") is False


def test_get_state_returns_empty_for_new_session():
    """A freshly created session has an empty state dict."""
    sid = facade.create_session()
    state = facade.get_state(sid)
    assert state == {}
    facade.drop_session(sid)


def test_get_state_returns_seeded_state():
    """seed_state injects state that get_state reads back."""
    sid = "test-seed-state"
    facade.seed_state(sid, {"foo": "bar"})
    assert facade.get_state(sid) == {"foo": "bar"}
    facade.drop_session(sid)


def test_get_state_404_for_unknown_session():
    """get_state raises HTTPException(404) for unknown session."""
    with pytest.raises(Exception) as exc_info:
        facade.get_state("unknown-sid")
    assert exc_info.value.status_code == 404


def test_save_state_overwrites():
    """save_state overwrites the full state dict."""
    sid = "test-save"
    facade.seed_state(sid, {"old": True})
    facade.save_state(sid, {"new": True})
    assert facade.get_state(sid) == {"new": True}
    facade.drop_session(sid)


def test_save_state_404_for_unknown():
    with pytest.raises(Exception) as exc_info:
        facade.save_state("unknown", {"x": 1})
    assert exc_info.value.status_code == 404


def test_update_state_merges_fields():
    """update_state merges fields into existing state."""
    sid = "test-update"
    facade.seed_state(sid, {"a": 1, "b": 2})
    result = facade.update_state(sid, b=3, c=4)
    assert result == {"a": 1, "b": 3, "c": 4}
    assert facade.get_state(sid) == {"a": 1, "b": 3, "c": 4}
    facade.drop_session(sid)


def test_drop_session_removes_it():
    sid = facade.create_session()
    facade.drop_session(sid)
    assert not facade.has_session(sid)


def test_drop_session_silent_for_unknown():
    """drop_session does not raise for unknown session."""
    facade.drop_session("never-existed")


def test_get_session_entry_returns_raw_entry():
    """get_session_entry returns the raw dict (state + csv_path)."""
    sid = "test-entry"
    facade.seed_state(sid, {"x": 1})
    facade.set_csv_path(sid, "/tmp/test.csv")
    entry = facade.get_session_entry(sid)
    assert entry["state"] == {"x": 1}
    assert entry["csv_path"] == "/tmp/test.csv"
    facade.drop_session(sid)


def test_get_session_entry_404_for_unknown():
    with pytest.raises(Exception) as exc_info:
        facade.get_session_entry("unknown")
    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# CSV path management
# ---------------------------------------------------------------------------
def test_get_csv_path_from_explicit_field():
    """get_csv_path returns the csv_path stored on the entry."""
    sid = "test-csv-explicit"
    facade.seed_state(sid, {})
    facade.set_csv_path(sid, "/tmp/data.csv")
    assert facade.get_csv_path(sid) == "/tmp/data.csv"
    facade.drop_session(sid)


def test_get_csv_path_falls_back_to_uploaded_datasets():
    """When csv_path is not set, get_csv_path reads from state.uploaded_datasets."""
    sid = "test-csv-fallback"
    facade.seed_state(sid, {"uploaded_datasets": [{"path": "/tmp/fallback.csv"}]})
    assert facade.get_csv_path(sid) == "/tmp/fallback.csv"
    facade.drop_session(sid)


def test_get_csv_path_400_when_no_dataset():
    """get_csv_path raises 400 when no path is available."""
    sid = "test-csv-none"
    facade.seed_state(sid, {})
    with pytest.raises(Exception) as exc_info:
        facade.get_csv_path(sid)
    assert exc_info.value.status_code == 400
    facade.drop_session(sid)


def test_set_csv_path_creates_entry_if_missing():
    """set_csv_path creates a session entry if it doesn't exist."""
    sid = "test-set-csv-new"
    facade.set_csv_path(sid, "/tmp/new.csv")
    assert facade.has_session(sid)
    assert facade.get_csv_path(sid) == "/tmp/new.csv"
    facade.drop_session(sid)


def test_get_datasets_from_csv_path():
    """get_datasets wraps csv_path into a [{path}] list."""
    sid = "test-ds-csv"
    facade.seed_state(sid, {})
    facade.set_csv_path(sid, "/tmp/d.csv")
    ds = facade.get_datasets(sid)
    assert ds == [{"path": "/tmp/d.csv"}]
    facade.drop_session(sid)


def test_get_datasets_from_state_when_no_csv_path():
    """get_datasets falls back to state.uploaded_datasets."""
    sid = "test-ds-state"
    facade.seed_state(
        sid, {"uploaded_datasets": [{"path": "/a.csv"}, {"path": "/b.csv"}]}
    )
    ds = facade.get_datasets(sid)
    assert len(ds) == 2
    facade.drop_session(sid)


def test_save_datasets_persists_into_state():
    """save_datasets writes the dataset list into state.uploaded_datasets."""
    sid = "test-save-ds"
    facade.seed_state(sid, {})
    facade.save_datasets(sid, [{"path": "/new.csv"}])
    assert facade.get_state(sid)["uploaded_datasets"] == [{"path": "/new.csv"}]
    facade.drop_session(sid)


# ---------------------------------------------------------------------------
# Graph invocation (run_upload_pipeline)
# ---------------------------------------------------------------------------
def test_run_upload_pipeline_invokes_graph_and_stores_state(monkeypatch):
    """run_upload_pipeline calls graph.invoke and stores final state + csv_path."""
    captured = {}

    class FakeGraph:
        def invoke(self, initial_state, config=None):
            captured["initial_state"] = initial_state
            captured["config"] = config
            return {"title_chapter": {"content": "\\title{T}"}, "final": True}

    monkeypatch.setattr("facade._graph", FakeGraph())

    sid = "test-upload"
    result = facade.run_upload_pipeline(sid, "/tmp/upload.csv")

    # graph.invoke was called with the right initial_state
    assert captured["initial_state"]["session_id"] == sid
    assert captured["initial_state"]["csv_path"] == "/tmp/upload.csv"
    assert captured["initial_state"]["uploaded_datasets"] == [
        {"path": "/tmp/upload.csv", "format": "csv"}
    ]
    assert captured["config"]["configurable"]["thread_id"] == sid
    # final state + csv_path persisted on the session entry
    assert result["title_chapter"]["content"] == "\\title{T}"
    assert result["final"] is True
    entry = facade.get_session_entry(sid)
    assert entry["csv_path"] == "/tmp/upload.csv"
    facade.drop_session(sid)


def test_run_upload_pipeline_503_when_graph_missing(monkeypatch):
    """run_upload_pipeline raises 503 when _graph is None."""
    monkeypatch.setattr("facade._graph", None)
    with pytest.raises(Exception) as exc_info:
        facade.run_upload_pipeline("sid", "/tmp/x.csv")
    assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# Single-node calls
# ---------------------------------------------------------------------------
def _patch_prewrite_nodes(monkeypatch, calls, *, star_rating=3):
    """run_prewrite imports node functions at call time."""

    def fake_set_direction(state):
        calls.append("set_direction")
        return {"research_direction": state["research_direction"]}

    def fake_identify(state):
        calls.append("identification_verify")
        return {
            "identification_diag": {"report": "ok", "star_rating": star_rating},
            "identification_failed": star_rating == 0,
            "star_rating": star_rating,
        }

    def fake_estimate(state):
        calls.append("estimate")
        return {
            "results": "# 主结果",
            "estimate": {
                "produced_by": "estimate",
                "status": "ok",
                "treatment_row": "| x | 1 |",
            },
        }

    def fake_robustness(state):
        calls.append("robustness_check")
        return {
            "robustness_results": {
                "produced_by": "robustness_check",
                "diagnostics": [],
            }
        }

    def fake_search(state):
        calls.append("search_literature")
        return {
            "literature_entries": [],
            "literature_query": "q",
            "literature_source": "mock",
            "literature_produced_by": "search_literature",
        }

    def fake_citation(state):
        calls.append("build_citation_graph")
        return {"citation_graph": {}, "citation_indices": {}}

    def fake_title(state):
        calls.append("generate_title")
        return {"title_chapter": {"type": "title", "title": "T"}}

    def fake_outline(state):
        calls.append("generate_outline")
        return {"outline": [{"type": "intro"}]}

    monkeypatch.setattr("nodes.set_direction.set_direction", fake_set_direction)
    monkeypatch.setattr(
        "nodes.identification_verify.identification_verify", fake_identify
    )
    monkeypatch.setattr("nodes.estimate.estimate", fake_estimate)
    monkeypatch.setattr(
        "nodes.robustness_check.robustness_check", fake_robustness
    )
    monkeypatch.setattr(
        "nodes.search_literature.search_literature", fake_search
    )
    monkeypatch.setattr(
        "nodes.citation_graph.build_citation_graph", fake_citation
    )
    monkeypatch.setattr("nodes.generate_title.generate_title", fake_title)
    monkeypatch.setattr("nodes.generate_outline.generate_outline", fake_outline)


def test_set_direction_and_outline_calls_both_nodes(monkeypatch):
    """预写顺序：识别 → 估计 → 稳健性 → 文献 → 标题 → 大纲。"""
    calls = []
    _patch_prewrite_nodes(monkeypatch, calls)

    sid = "test-direction"
    facade.seed_state(sid, {})
    rd = {"question": "q", "method": "OLS"}
    result = facade.set_direction_and_outline(sid, rd)

    assert calls == [
        "set_direction",
        "identification_verify",
        "estimate",
        "robustness_check",
        "search_literature",
        "build_citation_graph",
        "generate_title",
        "generate_outline",
    ]
    assert result["research_direction"] == rd
    assert result["outline"] == [{"type": "intro"}]
    assert result["star_rating"] == 3
    assert result["estimate"]["produced_by"] == "estimate"
    assert facade.get_state(sid)["outline"] == [{"type": "intro"}]
    facade.drop_session(sid)


def test_set_direction_and_outline_skips_outline_on_zero_star(monkeypatch):
    """0 星识别：写回诊断，不生成大纲，也不跑估计。"""
    calls = []
    _patch_prewrite_nodes(monkeypatch, calls, star_rating=0)

    sid = "test-zero-star"
    facade.seed_state(sid, {})
    result = facade.set_direction_and_outline(
        sid, {"question": "q", "method": "did"}
    )
    assert calls == ["set_direction", "identification_verify"]
    assert result.get("outline") is None
    assert result["star_rating"] == 0
    assert result["identification_failed"] is True
    facade.drop_session(sid)


def test_set_direction_and_outline_503_when_nodes_missing(monkeypatch):
    """set_direction_and_outline raises 503 when node functions are None."""
    monkeypatch.setattr("facade.set_direction_node", None)
    monkeypatch.setattr("facade.generate_outline_node", None)
    facade.seed_state("test-503", {})
    with pytest.raises(Exception) as exc_info:
        facade.set_direction_and_outline("test-503", {})
    assert exc_info.value.status_code == 503
    facade.drop_session("test-503")


def test_resume_outline_calls_generate_outline(monkeypatch):
    """resume_outline re-runs generate_outline with user_adjusted_outline."""
    captured = {}

    def fake_generate_outline(state):
        captured["user_adjusted_outline"] = state.get("user_adjusted_outline")
        return {"outline": state["user_adjusted_outline"]}

    monkeypatch.setattr("facade.generate_outline_node", fake_generate_outline)

    sid = "test-resume"
    facade.seed_state(sid, {})
    adjusted = [{"type": "intro", "title": "自定义"}]
    result = facade.resume_outline(sid, adjusted)

    assert captured["user_adjusted_outline"] == adjusted
    assert result["outline"] == adjusted
    facade.drop_session(sid)


def test_generate_chapter_calls_node_and_persists(monkeypatch):
    """generate_chapter writes chapter into state and calls the node."""
    captured = {}

    def fake_generate_chapter(state):
        captured["current_chapter"] = state.get("current_chapter")
        return {"body_chapters": [state["current_chapter"]]}

    monkeypatch.setattr("facade.generate_chapter_node", fake_generate_chapter)
    monkeypatch.setattr("facade.review_chapter_node", lambda state: {})

    sid = "test-gen-chapter"
    facade.seed_state(sid, {})
    chapter = {"type": "intro", "title": "引言"}
    result = facade.generate_chapter(sid, chapter)

    assert captured["current_chapter"] == chapter
    assert result["body_chapters"] == [chapter]
    assert facade.get_state(sid)["body_chapters"] == [chapter]
    facade.drop_session(sid)


def test_generate_chapter_merges_render_kwargs(monkeypatch):
    """非真值 render_kwargs 可补空键；TRUTH_KEYS（如 results）必须忽略。"""
    def fake_generate_chapter(state):
        return {"body_chapters": [{"content": state.get("research_question")}]}

    monkeypatch.setattr("facade.generate_chapter_node", fake_generate_chapter)
    monkeypatch.setattr("facade.review_chapter_node", lambda state: {})

    sid = "test-gen-kwargs"
    facade.seed_state(sid, {})
    facade.generate_chapter(
        sid,
        {"type": "intro"},
        render_kwargs={
            "research_question": "Q1",
            "data_summary": "D1",
            "results": "FAKE TABLE",
        },
    )
    state = facade.get_state(sid)
    assert state["research_question"] == "Q1"
    assert state["data_summary"] == "D1"
    assert state.get("results") != "FAKE TABLE"
    facade.drop_session(sid)


def test_generate_chapter_calls_review_after_write(monkeypatch):
    """写章成功后必须调用 review_chapter。"""
    calls = []

    def fake_generate_chapter(state):
        return {
            "body_chapters": [
                {"type": "intro", "content": "x", "status": "generated"}
            ]
        }

    def fake_review(state):
        calls.append("review_chapter")
        return {"review_scores": [0.8]}

    monkeypatch.setattr("facade.generate_chapter_node", fake_generate_chapter)
    monkeypatch.setattr("facade.review_chapter_node", fake_review)

    sid = "test-gen-review"
    facade.seed_state(sid, {})
    result = facade.generate_chapter(sid, {"type": "intro", "title": "引言"})
    assert calls == ["review_chapter"]
    assert result["review_scores"] == [0.8]
    facade.drop_session(sid)


def test_generate_chapter_does_not_overwrite_existing_kwargs(monkeypatch):
    """generate_chapter does not overwrite existing state fields with render_kwargs."""
    def fake_generate_chapter(state):
        return {"body_chapters": []}

    monkeypatch.setattr("facade.generate_chapter_node", fake_generate_chapter)
    monkeypatch.setattr("facade.review_chapter_node", lambda state: {})

    sid = "test-gen-nooverwrite"
    facade.seed_state(sid, {"research_question": "original"})
    facade.generate_chapter(
        sid,
        {"type": "intro"},
        render_kwargs={"research_question": "should-not-overwrite"},
    )
    assert facade.get_state(sid)["research_question"] == "original"
    facade.drop_session(sid)


def test_generate_chapter_400_on_value_error(monkeypatch):
    """generate_chapter translates ValueError from node into 400."""
    def fake_generate_chapter(state):
        raise ValueError("bad chapter type")

    monkeypatch.setattr("facade.generate_chapter_node", fake_generate_chapter)

    sid = "test-gen-400"
    facade.seed_state(sid, {})
    with pytest.raises(Exception) as exc_info:
        facade.generate_chapter(sid, {"type": "bad"})
    assert exc_info.value.status_code == 400
    facade.drop_session(sid)


def test_regenerate_chapter_sets_index_and_calls_node(monkeypatch):
    """regenerate_chapter writes current_chapter_index before calling node."""
    captured = {}

    def fake_generate_chapter(state):
        captured["current_chapter_index"] = state.get("current_chapter_index")
        return {"body_chapters": [{"content": "new"}]}

    monkeypatch.setattr("facade.generate_chapter_node", fake_generate_chapter)
    monkeypatch.setattr("facade.review_chapter_node", lambda state: {})

    sid = "test-regen"
    facade.seed_state(sid, {})
    result = facade.regenerate_chapter(sid, 2)

    assert captured["current_chapter_index"] == 2
    assert result["body_chapters"] == [{"content": "new"}]
    facade.drop_session(sid)


def test_rollback_chapter_passes_indices_to_node(monkeypatch):
    """rollback_chapter writes rollback_chapter_index + rollback_version_index."""
    captured = {}

    def fake_rollback(state):
        captured["chapter_index"] = state.get("rollback_chapter_index")
        captured["version_index"] = state.get("rollback_version_index")
        return {"body_chapters": [{"status": "rolled_back"}]}

    monkeypatch.setattr("facade.rollback_chapter_node", fake_rollback)

    sid = "test-rollback"
    facade.seed_state(sid, {})
    result = facade.rollback_chapter(sid, 1, 2)

    assert captured["chapter_index"] == 1
    assert captured["version_index"] == 2
    assert result["body_chapters"] == [{"status": "rolled_back"}]
    facade.drop_session(sid)


def test_rollback_chapter_400_on_index_error(monkeypatch):
    """rollback_chapter translates IndexError into 400."""
    def fake_rollback(state):
        raise IndexError("out of range")

    monkeypatch.setattr("facade.rollback_chapter_node", fake_rollback)

    sid = "test-rollback-400"
    facade.seed_state(sid, {})
    with pytest.raises(Exception) as exc_info:
        facade.rollback_chapter(sid, 99, 99)
    assert exc_info.value.status_code == 400
    facade.drop_session(sid)


def test_rollback_chapter_503_when_node_missing(monkeypatch):
    """rollback_chapter raises 503 when rollback_chapter_node is None."""
    monkeypatch.setattr("facade.rollback_chapter_node", None)
    facade.seed_state("test-rb-503", {})
    with pytest.raises(Exception) as exc_info:
        facade.rollback_chapter("test-rb-503", 0, 0)
    assert exc_info.value.status_code == 503
    facade.drop_session("test-rb-503")


def test_export_document_calls_node_and_persists_template(monkeypatch):
    """export_document writes template into state and calls export_docx_node."""
    captured = {}

    def fake_export_docx(state):
        captured["export_template"] = state.get("export_template")
        return {
            "latex_source": "\\title{T}",
            "pdf_path": None,
            "docx_path": None,
            "degraded": False,
        }

    monkeypatch.setattr("facade.export_docx_node", fake_export_docx)

    sid = "test-export"
    facade.seed_state(sid, {})
    result = facade.export_document(sid, "master_thesis")

    assert captured["export_template"] == "master_thesis"
    assert result["latex_source"] == "\\title{T}"
    # template + result persisted into state
    assert facade.get_state(sid)["export_template"] == "master_thesis"
    facade.drop_session(sid)


def test_export_document_503_when_node_missing(monkeypatch):
    """export_document raises 503 when export_docx_node is None."""
    monkeypatch.setattr("facade.export_docx_node", None)
    facade.seed_state("test-exp-503", {})
    with pytest.raises(Exception) as exc_info:
        facade.export_document("test-exp-503", "cn_journal")
    assert exc_info.value.status_code == 503
    facade.drop_session("test-exp-503")


# ---------------------------------------------------------------------------
# Cleaning step calls
# ---------------------------------------------------------------------------
def test_transform_variables_runs_transform_step(monkeypatch):
    """transform_variables calls TransformStep.run with workspace + order."""
    captured = {}

    class FakeTransformStep:
        def run(self, datasets, config):
            captured["datasets"] = datasets
            captured["config"] = config
            return [{"path": "/tmp/transformed.csv"}], {"report": "ok"}

    monkeypatch.setattr("facade.TransformStepCls", FakeTransformStep)

    sid = "test-transform"
    facade.seed_state(sid, {})
    facade.set_csv_path(sid, "/tmp/original.csv")

    result = facade.transform_variables(sid, {"column": "income"})
    assert result == [{"path": "/tmp/transformed.csv"}]
    assert captured["datasets"] == [{"path": "/tmp/original.csv"}]
    assert captured["config"]["column"] == "income"
    assert captured["config"]["workspace"] == "/tmp"
    assert captured["config"]["order"] == 0
    # datasets persisted into state
    assert facade.get_state(sid)["uploaded_datasets"] == [
        {"path": "/tmp/transformed.csv"}
    ]
    facade.drop_session(sid)


def test_transform_variables_503_when_step_missing(monkeypatch):
    """transform_variables raises 503 when TransformStepCls is None."""
    monkeypatch.setattr("facade.TransformStepCls", None)
    facade.seed_state("test-tf-503", {})
    facade.set_csv_path("test-tf-503", "/tmp/x.csv")
    with pytest.raises(Exception) as exc_info:
        facade.transform_variables("test-tf-503", {})
    assert exc_info.value.status_code == 503
    facade.drop_session("test-tf-503")


def test_filter_sample_runs_filter_step(monkeypatch):
    """filter_sample calls FilterStep.run with conditions."""
    captured = {}

    class FakeFilterStep:
        def run(self, datasets, config):
            captured["config"] = config
            return datasets, {"report": "filtered"}

    monkeypatch.setattr("facade.FilterStepCls", FakeFilterStep)

    sid = "test-filter"
    facade.seed_state(sid, {})
    facade.set_csv_path(sid, "/tmp/data.csv")

    facade.filter_sample(sid, [{"col": "age", "op": ">", "val": 18}])
    assert captured["config"]["conditions"] == [
        {"col": "age", "op": ">", "val": 18}
    ]
    facade.drop_session(sid)


def test_balance_panel_returns_report(monkeypatch):
    """balance_panel calls BalanceStep.run and returns the report."""
    class FakeBalanceStep:
        def run(self, datasets, config):
            return datasets, {"balanced": True, "n_panels": 5}

    monkeypatch.setattr("facade.BalanceStepCls", FakeBalanceStep)

    sid = "test-balance"
    facade.seed_state(sid, {})
    facade.set_csv_path(sid, "/tmp/panel.csv")

    report = facade.balance_panel(sid, "pid", "year")
    assert report == {"balanced": True, "n_panels": 5}
    facade.drop_session(sid)


# ---------------------------------------------------------------------------
# CHARLS detect / confirm
# ---------------------------------------------------------------------------
def test_confirm_charls_persists_config():
    """confirm_charls writes charls_config into state + entry."""
    sid = "test-charls-confirm"
    facade.seed_state(sid, {})

    vm = {"income": "INC"}
    waves = [2018, 2020]
    presets = [{"name": "urban"}]
    config = facade.confirm_charls(sid, vm, waves, presets)

    assert config["variable_mapping"] == vm
    assert config["waves"] == waves
    assert config["filter_presets"] == presets
    # persisted in state
    assert facade.get_state(sid)["charls_config"] == config
    # mirrored on entry top-level
    assert facade.get_session_entry(sid)["charls_config"] == config
    facade.drop_session(sid)


# ---------------------------------------------------------------------------
# Fresh instance isolation
# ---------------------------------------------------------------------------
def test_fresh_facade_instance_starts_empty():
    """A new AgentFacade has no sessions."""
    f = AgentFacade()
    assert f._sessions == {}
    assert f.has_session("anything") is False


def test_public_literature_entries_strips_abstract_and_non_doi_url():
    """读数台：有 DOI 才给 doi.org 链接；摘要不外送；立场只三选一。"""
    out = public_literature_entries(
        [
            {
                "title": "Returns",
                "authors": ["Zhang"],
                "year": 2023,
                "abstract": "secret",
                "url": "https://doi.org/10.1016/j.jceco.2023.001",
                "stance": "支持",
            },
            {
                "title": "No DOI",
                "authors": "Solo",
                "year": "2010",
                "url": "https://example.com/paper",
                "stance": "maybe",
            },
        ]
    )
    assert "abstract" not in out[0]
    assert out[0]["url"] == "https://doi.org/10.1016/j.jceco.2023.001"
    assert out[0]["stance"] == "支持"
    assert out[1]["authors"] == ["Solo"]
    assert out[1]["year"] == 2010
    assert out[1]["url"] == ""
    assert "stance" not in out[1]
