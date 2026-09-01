"""Frame 5: atomic, evidence-grounded paper draft read model."""
from __future__ import annotations

from copy import deepcopy
import importlib
from pathlib import Path

from facade import AgentFacade

from agent.nodes.estimate import estimate
from conftest import make_six_chapter_outline


CFPS_CSV = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "cfps_association"
    / "sanitized_sample.csv"
)


def _estimated_state() -> dict:
    direction = {
        "question": "CFPS 中父母教育与子女工资的条件关联是什么？",
        "dv": "ln_wage",
        "iv": "parent_education",
        "controls": ["age", "female", "urban", "edu_last", "experience"],
        "method": "OLS",
        "claim": "association",
    }
    specification = {
        "produced_by": "set_direction",
        "method": "OLS",
        "formula": (
            "ln_wage ~ parent_education + age + female + urban + "
            "edu_last + experience"
        ),
        "outcome": "ln_wage",
        "treatment": "parent_education",
        "controls": ["age", "female", "urban", "edu_last", "experience"],
    }
    state = {
        "session_id": "paper-draft-test",
        "csv_path": str(CFPS_CSV),
        "uploaded_datasets": [
            {
                "name": CFPS_CSV.name,
                "path": str(CFPS_CSV),
                "format": "csv",
            }
        ],
        "research_direction": direction,
        "main_specification": specification,
        "claim": "association",
        "identification_diag": {
            "strategy": None,
            "diagnostics": [],
            "passed": True,
            "report": "OLS 仅支持条件关联表述。",
            "star_rating": None,
        },
        "star_rating": None,
        "robustness_results": {
            "produced_by": "robustness_check",
            "diagnostics": [],
            "robustness": [],
            "heterogeneity": [],
            "placebos": [],
            "degraded": True,
            "reason": "no_cluster_or_groups",
            "summary_table": "# 稳健性\n\n未提供可验证的额外规格。",
        },
        "literature_source": "crossref",
        "literature_produced_by": "search_literature",
        "literature_query": "parental education wages China",
        "literature_entries": [
            {
                "title": "Intergenerational Education and Earnings",
                "authors": ["Researcher, A."],
                "year": 2022,
                "abstract": "A metadata abstract returned by Crossref.",
                "doi": "10.1234/example.2022.1",
                "source": "crossref",
                "relevance_score": 0.9,
            }
        ],
        "outline": make_six_chapter_outline(),
        "current_chapter_index": 0,
    }
    state.update(estimate(state))
    return state


def _facade_with_state(state: dict) -> tuple[AgentFacade, str]:
    paper_facade = AgentFacade()
    session_id = "paper-draft-test"
    paper_facade._store.seed(session_id, deepcopy(state))
    return paper_facade, session_id


def _install_success_nodes(
    monkeypatch,
    module_name: str = "backend.services.paper_draft",
) -> None:
    service = importlib.import_module(module_name)

    monkeypatch.setattr(
        service,
        "generate_title_node",
        lambda state: {
            "title_chapter": {
                "type": "title",
                "title": "父母教育与子女工资的条件关联",
                "content": "\\title{父母教育与子女工资的条件关联}",
                "status": "done",
                "generation_source": "llm",
                "generation_degraded": False,
            }
        },
    )

    def generate(state: dict) -> dict:
        idx = state["current_chapter_index"]
        spec = state["outline"][idx]
        content = f"{spec['title']}短稿。"
        if spec["type"] == "results":
            content += "\n\n" + state["estimate"]["treatment_row"]
        chapters = list(state.get("body_chapters") or [])
        while len(chapters) < 6:
            chapters.append({})
        chapters[idx] = {
            **spec,
            "content": content,
            "status": "generated",
            "versions": [content],
            "chapter_index": idx,
            "generation_source": "llm",
            "generation_degraded": False,
        }
        return {"body_chapters": chapters, "current_chapter_index": idx + 1}

    def review(state: dict, *, structured_retries: int = 2) -> dict:
        idx = state["current_chapter_index"] - 1
        scores = list(state.get("review_scores") or [])
        while len(scores) <= idx:
            scores.append(0.0)
        scores[idx] = 0.9
        return {
            "review_scores": scores,
            "review_chapter_index": idx,
            "review_iteration": 0,
            "review_source": "llm",
            "review_degraded": False,
            "review_typed": True,
            "grounding_failures": [],
            "structure_failures": [],
            "review_rubrics": [
                {
                    "endogeneity": 0.9,
                    "identification": 0.9,
                    "robustness": 0.9,
                    "contribution": 0.9,
                    "readability": 0.9,
                }
                for _ in range(idx + 1)
            ],
        }

    monkeypatch.setattr(service, "generate_chapter_node", generate)
    monkeypatch.setattr(service, "review_chapter_node", review)
    monkeypatch.setattr(
        service,
        "resolve_doi",
        lambda doi: {"DOI": doi, "title": ["verified"]},
    )


def test_real_cfps_estimate_is_projected_exactly(monkeypatch):
    from backend.services.paper_draft import build_paper_draft

    state = _estimated_state()
    expected = deepcopy(state["estimate"])
    paper_facade, session_id = _facade_with_state(state)
    _install_success_nodes(monkeypatch)

    response = build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "ready"
    assert response["readiness"] == "ready"
    evidence = response["evidence"]
    for key in ("formula", "n", "coef", "se", "p", "treatment_row"):
        assert evidence["analysis"][key] == expected[key]
    assert evidence["claim_type"] == "association"
    assert "不构成因果" in evidence["limitation"]
    assert response["paper"]["sections"][4]["content"].endswith(
        expected["treatment_row"]
    )
    assert [section["type"] for section in response["paper"]["sections"]] == [
        "intro",
        "lit_review",
        "data_desc",
        "methods",
        "results",
        "conclusion",
    ]
    assert response["paper"]["references"][0]["doi"] == "10.1234/example.2022.1"
    assert any(
        item["source"].startswith("state.robustness_results")
        and item["severity"] == "warning"
        for item in response["open_questions"]
    )


def test_mock_literature_and_failed_doi_block_ready_without_mutation(monkeypatch):
    from backend.services.paper_draft import build_paper_draft

    state = _estimated_state()
    state["literature_source"] = "mock_degraded"
    state["literature_entries"][0]["source"] = "mock"
    paper_facade, session_id = _facade_with_state(state)
    before = deepcopy(paper_facade.get_state(session_id))

    blocked = build_paper_draft(session_id, state_facade=paper_facade)

    assert blocked["status"] == "not_ready"
    assert "literature_source_not_crossref" in blocked["gaps"]
    assert paper_facade.get_state(session_id) == before

    state = _estimated_state()
    paper_facade.save_state(session_id, deepcopy(state))
    monkeypatch.setattr(
        "backend.services.paper_draft.resolve_doi",
        lambda doi: (_ for _ in ()).throw(RuntimeError("resolve failed")),
    )
    blocked = build_paper_draft(session_id, state_facade=paper_facade)
    assert blocked["status"] == "not_ready"
    assert "doi_resolve_failed" in blocked["gaps"]
    assert paper_facade.get_state(session_id) == state


def test_chapter_or_grounding_failure_is_atomic(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    state["body_chapters"] = [
        {
            **spec,
            "content": f"旧稿 {index}",
            "versions": [f"旧稿 {index}", f"更旧稿 {index}"],
            "status": "approved",
            "chapter_index": index,
        }
        for index, spec in enumerate(state["outline"])
    ]
    paper_facade, session_id = _facade_with_state(state)
    before = deepcopy(paper_facade.get_state(session_id))
    _install_success_nodes(monkeypatch)

    def fail_on_methods(working: dict) -> dict:
        if working["current_chapter_index"] == 3:
            raise RuntimeError("chapter provider unavailable")
        return {}

    monkeypatch.setattr(service, "generate_chapter_node", fail_on_methods)
    blocked = service.build_paper_draft(session_id, state_facade=paper_facade)
    assert blocked["status"] == "not_ready"
    assert "chapter_generation_failed" in blocked["gaps"]
    assert paper_facade.get_state(session_id) == before


def test_missing_treatment_existing_grounding_and_review_failure_are_refusals(monkeypatch):
    import backend.services.paper_draft as service

    for mutation, expected_gap in (
        (lambda state: state["estimate"].update(treatment_row=""), "treatment_row_missing"),
        (lambda state: state.update(grounding_failures=["invented_number"]), "grounding_failure"),
    ):
        state = _estimated_state()
        mutation(state)
        paper_facade, session_id = _facade_with_state(state)
        before = deepcopy(paper_facade.get_state(session_id))
        response = service.build_paper_draft(session_id, state_facade=paper_facade)
        assert response["status"] == "not_ready"
        assert expected_gap in response["gaps"]
        assert paper_facade.get_state(session_id) == before

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    before = deepcopy(paper_facade.get_state(session_id))
    _install_success_nodes(monkeypatch)

    def failed_review(working: dict, *, structured_retries: int = 2) -> dict:
        idx = working["current_chapter_index"] - 1
        return {
            "review_scores": [0.4] * (idx + 1),
            "review_chapter_index": idx,
                "review_source": "llm",
                "review_degraded": False,
                "review_typed": True,
                "grounding_failures": [],
                "structure_failures": [],
                "review_rubrics": [{
                    "endogeneity": 0.4,
                    "identification": 0.4,
                    "robustness": 0.4,
                    "contribution": 0.4,
                    "readability": 0.4,
                } for _ in range(idx + 1)],
            }

    monkeypatch.setattr(service, "review_chapter_node", failed_review)
    response = service.build_paper_draft(session_id, state_facade=paper_facade)
    assert response["status"] == "not_ready"
    assert "chapter_review_failed" in response["gaps"]
    assert paper_facade.get_state(session_id) == before


def test_state_external_number_is_blocked_even_when_review_claims_pass(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    before = deepcopy(paper_facade.get_state(session_id))
    _install_success_nodes(monkeypatch)
    successful_generate = service.generate_chapter_node

    def invent_number(working: dict) -> dict:
        result = successful_generate(working)
        idx = working["current_chapter_index"]
        if idx == 4:
            result["body_chapters"][idx]["content"] += "\n额外结果为 999。"
        return result

    monkeypatch.setattr(service, "generate_chapter_node", invent_number)
    response = service.build_paper_draft(session_id, state_facade=paper_facade)
    assert response["status"] == "not_ready"
    assert "invented_number" in response["gaps"]
    assert paper_facade.get_state(session_id) == before


def test_data_desc_invented_numbers_are_rewritten_once_then_ready(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    _install_success_nodes(monkeypatch)
    successful_generate = service.generate_chapter_node
    calls = {"data_desc": 0}
    retry_suggestions: list[str] = []
    save_calls = 0
    original_save = paper_facade.save_state

    def generate(working: dict) -> dict:
        chapter_type = working["outline"][working["current_chapter_index"]]["type"]
        result = successful_generate(working)
        if chapter_type == "data_desc":
            calls["data_desc"] += 1
            if calls["data_desc"] == 1:
                working["failed_attempt_poison"] = True
                result["body_chapters"][2]["content"] += (
                    "\n未绑定的比例分别为 28.9% 和 48.6%。"
                )
            else:
                assert "failed_attempt_poison" not in working
                retry_suggestions.append(working["revision_suggestions"][2])
        return result

    def save_once(sid: str, saved: dict) -> None:
        nonlocal save_calls
        save_calls += 1
        original_save(sid, saved)

    monkeypatch.setattr(service, "generate_chapter_node", generate)
    monkeypatch.setattr(paper_facade, "save_state", save_once)

    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "ready"
    data_desc = response["paper"]["sections"][2]
    assert "28.9" not in data_desc["content"]
    assert "48.6" not in data_desc["content"]
    assert calls["data_desc"] == 2
    assert save_calls == 1
    assert data_desc["versions"] == [data_desc["content"]]
    assert "failed_attempt_poison" not in paper_facade.get_state(session_id)
    assert "28.9%" in retry_suggestions[0]
    assert "48.6%" in retry_suggestions[0]
    assert "未绑定的比例分别为 28.9% 和 48.6%。" in retry_suggestions[0]
    assert "允许的分析事实" in retry_suggestions[0]
    assert "允许的文献事实" in retry_suggestions[0]
    assert "数据描述安全重写方案（必须采用）" in retry_suggestions[0]
    assert "特别不得添加千位逗号" in retry_suggestions[0]
    assert [item["status"] for item in paper_facade.get_state(session_id)["paper_draft_attempts"] if item["chapter"] == "data_desc"] == [
        "retry",
        "passed",
    ]


def test_retry_sentence_evidence_uses_numeric_tokens_not_substrings():
    from backend.services.paper_draft import _offending_sentences

    assert _offending_sentences("已绑定 34315。未绑定 3。", ["3"]) == ["未绑定 3。"]


def test_lit_review_unbound_year_is_rewritten_then_ready(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    _install_success_nodes(monkeypatch)
    successful_generate = service.generate_chapter_node
    calls = {"lit_review": 0}
    retry_suggestions: list[str] = []

    def generate(working: dict) -> dict:
        chapter_type = working["outline"][working["current_chapter_index"]]["type"]
        result = successful_generate(working)
        if chapter_type == "lit_review":
            calls["lit_review"] += 1
            if calls["lit_review"] == 1:
                result["body_chapters"][1]["content"] += "\n该研究发表于 2021 年。"
            else:
                retry_suggestions.append(working["revision_suggestions"][1])
        return result

    monkeypatch.setattr(service, "generate_chapter_node", generate)

    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "ready"
    assert calls["lit_review"] == 2
    assert "2021" not in response["paper"]["sections"][1]["content"]
    assert "未绑定数字/年份：2021" in retry_suggestions[0]
    assert "year=2022" in retry_suggestions[0]


def test_invented_number_retry_exhaustion_is_structured_and_atomic(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    before = deepcopy(paper_facade.get_state(session_id))
    _install_success_nodes(monkeypatch)
    successful_generate = service.generate_chapter_node
    data_desc_calls = 0
    data_desc_review_calls = 0
    retry_suggestions: list[str] = []
    save_calls = 0
    original_save = paper_facade.save_state
    successful_review = service.review_chapter_node

    def generate(working: dict) -> dict:
        nonlocal data_desc_calls
        chapter_type = working["outline"][working["current_chapter_index"]]["type"]
        result = successful_generate(working)
        if chapter_type == "data_desc":
            data_desc_calls += 1
            if data_desc_calls > 1:
                retry_suggestions.append(working["revision_suggestions"][2])
            invented = ("28.9%", "32715", "44.4%")[data_desc_calls - 1]
            result["body_chapters"][2]["content"] += f"\n虚构值为 {invented}。"
        return result

    def count_save(sid: str, saved: dict) -> None:
        nonlocal save_calls
        save_calls += 1
        original_save(sid, saved)

    def review(working: dict, *, structured_retries: int = 2) -> dict:
        nonlocal data_desc_review_calls
        idx = working["current_chapter_index"] - 1
        if working["outline"][idx]["type"] == "data_desc":
            data_desc_review_calls += 1
        return successful_review(working, structured_retries=structured_retries)

    monkeypatch.setattr(service, "generate_chapter_node", generate)
    monkeypatch.setattr(service, "review_chapter_node", review)
    monkeypatch.setattr(paper_facade, "save_state", count_save)

    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "not_ready"
    assert "grounding_failure" in response["gaps"]
    assert "invented_number" in response["gaps"]
    assert any(
        gap.startswith(
            "chapter_retry_exhausted:data_desc:attempt=3:failures=invented_number"
        )
        for gap in response["gaps"]
    )
    assert any("values=44.4%" in gap for gap in response["gaps"])
    retry_questions = [
        item
        for item in response["open_questions"]
        if item["code"].startswith("chapter_retry_attempt_")
    ]
    assert len(retry_questions) == 3
    assert all("chapter=data_desc" in item["message"] for item in retry_questions)
    assert all("failures=invented_number" in item["message"] for item in retry_questions)
    assert "28.9%" in retry_suggestions[1]
    assert "32715" in retry_suggestions[1]
    assert "本轮禁止输出任何百分比" in retry_suggestions[1]
    assert data_desc_calls == 3
    assert data_desc_review_calls == 3
    assert save_calls == 0
    assert paper_facade.get_state(session_id) == before


def test_passing_chapters_are_generated_and_reviewed_once(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    _install_success_nodes(monkeypatch)
    successful_generate = service.generate_chapter_node
    successful_review = service.review_chapter_node
    generate_calls: list[str] = []
    review_calls: list[str] = []

    def generate(working: dict) -> dict:
        generate_calls.append(
            working["outline"][working["current_chapter_index"]]["type"]
        )
        return successful_generate(working)

    def review(working: dict, *, structured_retries: int = 2) -> dict:
        assert structured_retries == 0
        review_calls.append(
            working["outline"][working["current_chapter_index"] - 1]["type"]
        )
        return successful_review(working, structured_retries=structured_retries)

    monkeypatch.setattr(service, "generate_chapter_node", generate)
    monkeypatch.setattr(service, "review_chapter_node", review)

    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "ready"
    assert generate_calls == list(service._CHAPTER_TYPES)
    assert review_calls == list(service._CHAPTER_TYPES)


def test_repairable_structure_review_rewrites_only_failed_chapter(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    _install_success_nodes(monkeypatch)
    successful_generate = service.generate_chapter_node
    successful_review = service.review_chapter_node
    generated: list[str] = []
    data_desc_reviews = 0

    def generate(working: dict) -> dict:
        generated.append(
            working["outline"][working["current_chapter_index"]]["type"]
        )
        return successful_generate(working)

    def review(working: dict, *, structured_retries: int = 2) -> dict:
        nonlocal data_desc_reviews
        idx = working["current_chapter_index"] - 1
        if working["outline"][idx]["type"] != "data_desc":
            return successful_review(working, structured_retries=structured_retries)
        data_desc_reviews += 1
        if data_desc_reviews == 2:
            assert "keyword_stuffed" in working["revision_suggestions"][idx]
            return successful_review(working, structured_retries=structured_retries)
        scores = [0.9] * (idx + 1)
        scores[idx] = 0.5
        suggestions = [""] * (idx + 1)
        suggestions[idx] = "结构层失败：keyword_stuffed。不得只堆关键词。"
        return {
            "review_scores": scores,
            "review_chapter_index": idx,
            "review_source": "llm",
            "review_degraded": False,
            "review_typed": True,
            "grounding_failures": [],
            "structure_failures": ["keyword_stuffed"],
            "review_rubrics": [{
                "endogeneity": 0.9,
                "identification": 0.9,
                "robustness": 0.9,
                "contribution": 0.9,
                "readability": 0.9,
            } for _ in range(idx + 1)],
            "revision_suggestions": suggestions,
        }

    monkeypatch.setattr(service, "generate_chapter_node", generate)
    monkeypatch.setattr(service, "review_chapter_node", review)

    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "ready"
    assert generated.count("data_desc") == 2
    assert all(generated.count(chapter) == 1 for chapter in service._CHAPTER_TYPES if chapter != "data_desc")


def test_review_provider_error_is_not_retried_or_persisted(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    before = deepcopy(paper_facade.get_state(session_id))
    _install_success_nodes(monkeypatch)
    successful_generate = service.generate_chapter_node
    generated: list[str] = []

    def generate(working: dict) -> dict:
        generated.append(
            working["outline"][working["current_chapter_index"]]["type"]
        )
        return successful_generate(working)

    def provider_error(working: dict, *, structured_retries: int = 2) -> dict:
        assert structured_retries == 0
        raise RuntimeError("review provider unavailable")

    monkeypatch.setattr(service, "generate_chapter_node", generate)
    monkeypatch.setattr(service, "review_chapter_node", provider_error)

    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "not_ready"
    assert "chapter_review_failed" in response["gaps"]
    assert generated == ["intro"]
    assert paper_facade.get_state(session_id) == before


def test_claim_read_model_reuses_saved_analysis_and_honest_source_excerpt(monkeypatch):
    from backend.services.paper_draft import build_paper_draft, get_claim_evidence

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    _install_success_nodes(monkeypatch)
    built = build_paper_draft(session_id, state_facade=paper_facade)

    evidence = get_claim_evidence(
        session_id,
        built["main_claim"]["id"],
        state_facade=paper_facade,
    )

    assert evidence["analysis"] == built["evidence"]["analysis"]
    assert evidence["sources"][0]["abstract"] == state["literature_entries"][0]["abstract"]
    assert evidence["sources"][0]["excerpt"] is None
    assert evidence["sources"][0]["excerpt_status"] == "unavailable"
    assert "关联" in evidence["limitation"]


def test_development_api_is_typed_and_uses_only_facade_state(client, monkeypatch):
    from facade import facade as global_facade

    state = _estimated_state()
    session_id = "paper-draft-api-test"
    state["session_id"] = session_id
    global_facade._store.seed(session_id, deepcopy(state))
    _install_success_nodes(monkeypatch, "services.paper_draft")
    try:
        response = client.post(f"/sessions/{session_id}/paper-draft")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ready"
        assert len(payload["paper"]["sections"]) == 6

        claim = client.get(
            f"/sessions/{session_id}/paper-draft/claims/{payload['main_claim']['id']}"
        )
        assert claim.status_code == 200
        assert claim.json()["analysis"] == payload["evidence"]["analysis"]

        saved = global_facade.get_state(session_id)
        for spike_only_key in (
            "messages",
            "pending_decision",
            "last_tool_result",
            "current_status",
        ):
            assert spike_only_key not in saved
    finally:
        global_facade._store.drop(session_id)


def test_mock_fallback_review_cannot_enter_ready(monkeypatch):
    """A high mock score never satisfies the formal-draft review gate."""
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    before = deepcopy(paper_facade.get_state(session_id))
    _install_success_nodes(monkeypatch)

    def fallback_review(working: dict, *, structured_retries: int = 2) -> dict:
        idx = working["current_chapter_index"] - 1
        scores = list(working.get("review_scores") or [])
        while len(scores) <= idx:
            scores.append(0.0)
        scores[idx] = 0.99
        return {
            "review_scores": scores,
            "review_chapter_index": idx,
            "review_iteration": 0,
            "review_source": "mock_fallback",
            "review_degraded": True,
            "grounding_failures": [],
        }

    monkeypatch.setattr(service, "review_chapter_node", fallback_review)
    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "not_ready"
    assert "chapter_review_degraded" in response["gaps"]
    assert paper_facade.get_state(session_id) == before


def test_mock_title_and_chapter_generation_cannot_enter_ready(monkeypatch):
    import backend.services.paper_draft as service

    for failed_part in ("title", "chapter"):
        state = _estimated_state()
        paper_facade, session_id = _facade_with_state(state)
        before = deepcopy(paper_facade.get_state(session_id))
        _install_success_nodes(monkeypatch)

        if failed_part == "title":
            monkeypatch.setattr(
                service,
                "generate_title_node",
                lambda working: {
                    "title_chapter": {
                        "type": "title",
                        "title": "占位标题",
                        "content": "\\title{占位标题}",
                        "status": "done",
                        "generation_source": "mock",
                        "generation_degraded": True,
                    }
                },
            )
        else:
            successful_generate = service.generate_chapter_node

            def mock_chapter(working: dict) -> dict:
                result = successful_generate(working)
                idx = working["current_chapter_index"]
                result["body_chapters"][idx]["generation_source"] = "mock"
                result["body_chapters"][idx]["generation_degraded"] = True
                return result

            monkeypatch.setattr(service, "generate_chapter_node", mock_chapter)

        response = service.build_paper_draft(session_id, state_facade=paper_facade)

        assert response["status"] == "not_ready"
        assert "generation_not_authentic" in response["gaps"]
        assert paper_facade.get_state(session_id) == before


def test_high_scoring_mock_review_cannot_enter_ready(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    before = deepcopy(paper_facade.get_state(session_id))
    _install_success_nodes(monkeypatch)
    calls = 0

    def mock_review(working: dict, *, structured_retries: int = 2) -> dict:
        nonlocal calls
        calls += 1
        idx = working["current_chapter_index"] - 1
        return {
            "review_scores": [0.99] * (idx + 1),
            "review_rubrics": [{
                "endogeneity": 0.99,
                "identification": 0.99,
                "robustness": 0.99,
                "contribution": 0.99,
                "readability": 0.99,
            } for _ in range(idx + 1)],
            "review_chapter_index": idx,
            "review_source": "mock",
            "review_degraded": False,
            "review_typed": False,
            "grounding_failures": [],
            "structure_failures": [],
        }

    monkeypatch.setattr(service, "review_chapter_node", mock_review)
    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "not_ready"
    assert "chapter_review_not_authentic" in response["gaps"]
    assert calls == 1
    assert paper_facade.get_state(session_id) == before


def test_ready_sections_expose_complete_provenance_and_new_initial_versions(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    state["body_chapters"] = [
        {
            **spec,
            "content": f"旧稿 {index}",
            "versions": [f"旧稿 {index}", f"更旧稿 {index}"],
            "status": "approved",
            "chapter_index": index,
        }
        for index, spec in enumerate(state["outline"])
    ]
    paper_facade, session_id = _facade_with_state(state)
    _install_success_nodes(monkeypatch)

    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "ready"
    assert len(response["paper"]["sections"]) == 6
    for section in response["paper"]["sections"]:
        assert section["generation_source"] == "llm"
        assert section["generation_degraded"] is False
        assert section["review_source"] == "llm"
        assert section["review_degraded"] is False
        assert section["review_typed"] is True
        assert section["review_status"] == "passed"
        assert section["grounding_failures"] == []
        assert section["structure_failures"] == []
        assert section["versions"] == [section["content"]]


def test_malformed_typed_review_stops_after_one_outer_attempt(monkeypatch):
    import backend.services.paper_draft as service

    state = _estimated_state()
    paper_facade, session_id = _facade_with_state(state)
    before = deepcopy(paper_facade.get_state(session_id))
    _install_success_nodes(monkeypatch)
    generate_calls = 0
    review_calls = 0
    successful_generate = service.generate_chapter_node

    def generate(working: dict) -> dict:
        nonlocal generate_calls
        generate_calls += 1
        return successful_generate(working)

    def malformed_review(working: dict, *, structured_retries: int = 2) -> dict:
        nonlocal review_calls
        review_calls += 1
        assert structured_retries == 0
        idx = working["current_chapter_index"] - 1
        return {
            "review_scores": [0.99] * (idx + 1),
            "review_rubrics": [{"readability": 0.99}],
            "review_chapter_index": idx,
            "review_source": "llm",
            "review_degraded": False,
            "review_typed": False,
            "grounding_failures": [],
            "structure_failures": [],
        }

    monkeypatch.setattr(service, "generate_chapter_node", generate)
    monkeypatch.setattr(service, "review_chapter_node", malformed_review)
    response = service.build_paper_draft(session_id, state_facade=paper_facade)

    assert response["status"] == "not_ready"
    assert "chapter_review_not_authentic" in response["gaps"]
    assert generate_calls == 1
    assert review_calls == 1
    assert paper_facade.get_state(session_id) == before
