"""Shared pytest rules for the current product surface.

The legacy static frontend under Product/web was removed on 2026-06-19.
Tests in this list inspect deleted shells, retired visual experiments, or old
manuscript snapshots directly, so keeping them in the default pytest collection
would force non-current products back into the product. React/current-surface
tests remain active.

Wrapper service tests still use the project-wide LLM mock below so default
pytest never depends on a real model endpoint.
"""
from __future__ import annotations

import importlib
import os
from unittest.mock import patch

import pytest

collect_ignore = [
    "test_agent_cluster_frontend_interactions.py",
    "test_agent_task_dispatch_audit.py",
    "test_agent_task_queue.py",
    "test_archive_interface_visual_contract.py",
    "test_clean_workbench_visual_contract.py",
    "test_dataset_frontend.py",
    "test_dataset_quality_profile.py",
    "test_design_run_plan_state_machine.py",
    "test_dual_gap_fix_spec.py",
    "test_external_data_catalog.py",
    "test_external_dataset_bind_preflight.py",
    "test_external_dataset_import_apply.py",
    "test_external_dataset_import_profile.py",
    "test_frontend_chinese_copy.py",
    "test_full_run_from_run_plan.py",
    "test_manuscript_consumption.py",
    "test_method_skill_catalog.py",
    "test_method_workflow_checklist.py",
    "test_observable_execution_frontend.py",
    "test_product_workflow_contract.py",
    "test_real_variable_role_promotion.py",
    "test_results_draft_evidence_binding.py",
    "test_review_export_package.py",
    "test_reviewer_scorecard.py",
    "test_supervisor_plan.py",
    "test_variable_role_candidates.py",
    "test_variable_role_confirmation.py",
    "test_verifier_export_gates.py",
    "test_integrity_audit.py",
    "test_p3_agent_activity_panel.py",
    "test_p3_react_input_tabs.py",
    "test_p3_semantic_glow_cards.py",
    "test_p3_task_brief_demo.py",
    "test_p6_formal_package_acceptance_surface.py",
    "test_react_workbench_visual_contract.py",
    "test_section_main_results.py",
    "test_workbench_visual_contrast_contract.py",
]

if "MINIMAX_API_KEY" not in os.environ and "MINIMAX_TOKEN_PLAN_KEY" not in os.environ:
    collect_ignore.append("program/test_spec_runner.py")


_WRAPPER_MODULES = (
    "Product.backend.wrapper.brief_service",
    "Product.backend.wrapper.search_service",
    "Product.backend.wrapper.variables_service",
    "Product.backend.wrapper.design_service",
    "Product.backend.wrapper.execute_service",
)


_FAKE_BRIEF_TEXT = (
    "## 研究问题\n"
    "工业机器人是否影响城市制造业就业结构？\n\n"
    "## 边际贡献\n"
    "- 新证据\n- 新方法\n\n"
    "## 研究边界\n"
    "- 不包括服务业\n- 不包括农村\n- 限于 2010-2022\n\n"
    "## 成功标准\n"
    "- 系数显著 p<0.05\n- 平衡性检验通过\n"
)


def _fake_chat(messages, **kwargs):  # noqa: ARG001
    return _FAKE_BRIEF_TEXT, {"input_tokens": 100, "output_tokens": 200}


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    for module_name in _WRAPPER_MODULES:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        monkeypatch.setattr(f"{module_name}.chat_completion", _fake_chat, raising=False)
    yield


@pytest.fixture
def mock_llm_chat_completion():
    def _fake(messages, **kwargs):  # noqa: ARG001
        text = (
            "## 研究问题\n工业机器人对就业结构的影响。\n\n"
            "## 边际贡献\n1. 新数据 2. 新方法 3. 新结论\n\n"
            "## 研究边界\n1. 不含服务业 2. 不含农村 3. 不含小企业\n\n"
            "## 成功标准\nX 系数 p < 0.05\n"
        )
        return text, {"input_tokens": 100, "output_tokens": 200}

    with patch("Product.backend.llm_client.chat_completion", side_effect=_fake):
        yield _fake
