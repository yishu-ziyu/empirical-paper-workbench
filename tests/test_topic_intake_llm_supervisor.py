from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend import llm_client
from Product.backend.registry import ensure_registry
from Product.backend.topic_intake_service import ensure_topic_supervisor_plan


LLM_ENV_KEYS = (
    "EMPIRICAL_LLM_PROVIDER",
    "EMPIRICAL_LLM_MODEL",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "STEPFUN_API_KEY",
    "STEPFUN_BASE_URL",
    "STEPFUN_MODEL",
    "MIMO_API_KEY",
    "MIMO_BASE_URL",
    "MIMO_MODEL",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MODEL",
    "MINIMAX_API_KEY",
    "MINIMAX_BASE_URL",
    "MINIMAX_MODEL",
    "KIMI_CODE_API_KEY",
    "KIMI_CODE_ANTHROPIC_TOKEN",
    "MOONSHOT_API_KEY",
    "OPENROUTER_API_KEY",
    "OPENROUTER_MODEL",
)


def _topic_specific_llm_plan() -> str:
    return json.dumps(
        {
            "stage_plan": [
                {
                    "id": "task-brief",
                    "title": "确认社会资本与主观幸福感的研究边界",
                    "owner": "Supervisor",
                    "status": "ready",
                    "reason": "先锁定 CGSS 题目中的社会资本、主观幸福感、样本口径和成功标准。",
                    "inputs": ["用户题目", "CGSS 数据线索"],
                    "outputs": ["ResearchQuestion", "TaskBrief"],
                },
                {
                    "id": "literature-map",
                    "title": "检索社会资本与幸福感文献",
                    "owner": "LiteratureAgent",
                    "status": "draft",
                    "reason": "需要用中文核心与英文文献界定社会资本维度和幸福感量表。",
                    "inputs": ["ResearchQuestion", "CNKI/Scholar/Zotero"],
                    "outputs": ["LiteratureSeedPackage"],
                },
                {
                    "id": "cgss-variable-profile",
                    "title": "建立 CGSS 变量画像",
                    "owner": "DataAgent",
                    "status": "draft",
                    "reason": "主观幸福感和社会资本变量必须绑定到真实 CGSS 题项。",
                    "inputs": ["CGSS 字段字典"],
                    "outputs": ["VariableRoleSet 草案"],
                },
            ],
            "subagent_dispatch": [
                {
                    "agent_id": "LiteratureAgent",
                    "role": "LiteratureAgent",
                    "task": "检索社会资本、主观幸福感和 CGSS 相关研究",
                    "summary": "形成候选文献和引用核验队列。",
                },
                {
                    "agent_id": "DataAgent",
                    "role": "DataAgent",
                    "task": "读取 CGSS 字段并提出变量角色草案",
                    "summary": "只生成草案，不写入正式变量角色。",
                },
                {
                    "agent_id": "MethodAgent",
                    "role": "MethodAgent",
                    "task": "判断 OLS/有序模型/固定效应等方法前置条件",
                    "summary": "方法选择进入人工审阅。",
                },
            ],
            "evidence_requirements": [
                "CGSS 主观幸福感题项、社会资本题项和控制变量必须有字段证据。",
                "文献综述需要覆盖社会资本影响幸福感的机制和内生性讨论。",
            ],
            "risks": [
                "社会资本与主观幸福感可能存在反向因果。",
                "不同年份 CGSS 题项口径可能不一致。",
            ],
            "human_gates": [
                "确认 CGSS 数据年份和样本范围。",
                "确认社会资本变量构造方式。",
            ],
            "internal_skill_judgments": [
                {
                    "skill_id": "recursive_research_search",
                    "reason": "该题需要从题目递归展开到文献、CGSS 变量和方法门。",
                    "evidence_fit": "先生成候选文献和字段证据，再进入变量角色。",
                    "agent_fit": "LiteratureAgent 与 DataAgent 可以并行工作。",
                    "risk_note": "候选引用和变量只能进入草案层。",
                    "human_review_note": "正式写回前必须人工确认。",
                    "confidence": "high",
                }
            ],
            "reference_chain_policy": {
                "source_priority": ["CNKI", "Google Scholar", "Zotero", "Local Notes"],
                "sources": [
                    {"id": "CNKI", "label": "中国知网", "trigger": "中文实证文献", "mode": "manual_assisted"},
                    {"id": "Google Scholar", "label": "Google Scholar", "trigger": "英文文献", "mode": "browser_assisted"},
                ],
                "max_depth": 2,
                "max_iterations": 5,
                "writes_formal_layer": False,
            },
            "next_action": {
                "id": "review_supervisor_plan",
                "label": "审阅路线后创建 Agent Task Queue",
            },
        },
        ensure_ascii=False,
    )


class TopicIntakeLlmSupervisorTests(unittest.TestCase):
    """BDD: 题目登记后的研究判断必须接入真实 LLM Supervisor。"""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="topic-intake-llm-"))
        self.repo_root = self.temp_dir / "repo"
        self.product_root = self.repo_root / "Product"
        self.product_root.mkdir(parents=True)
        ensure_registry(self.product_root, self.repo_root)

        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_topic_intake_uses_llm_supervisor_and_persists_model_metadata(self) -> None:
        """行为 1/2：SupervisorPlan 来自 LLM，并且不得出现与题目无关的固定案例。"""
        topic = "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析"

        with patch.object(
            llm_client,
            "chat_completion_with_fallback",
            return_value=(
                _topic_specific_llm_plan(),
                {
                    "provider_id": "openai",
                    "provider_name": "Codex GPT",
                    "model": "gpt-5.5",
                    "api_type": "openai-compatible",
                    "input_tokens": 800,
                    "output_tokens": 420,
                },
            ),
        ) as mocked_llm:
            payload = ensure_topic_supervisor_plan(
                self.product_root,
                self.repo_root,
                topic,
                slug="cgss-happiness",
                note="用户从首页输入题目。",
            )

        mocked_llm.assert_called_once()
        messages = mocked_llm.call_args.args[0]
        self.assertIn(topic, json.dumps(messages, ensure_ascii=False))

        plan = payload["supervisor_plan"]
        self.assertEqual(plan["evidence_level"], "llm_supervisor")
        self.assertEqual(plan["provider"]["provider_id"], "openai")
        self.assertEqual(plan["provider"]["model"], "gpt-5.5")
        self.assertEqual(plan["provider"]["input_tokens"], 800)
        self.assertIn("recursive_research_search", plan["selected_skill_ids"])
        rendered_plan = json.dumps(plan, ensure_ascii=False)
        self.assertIn("CGSS", rendered_plan)
        self.assertIn("主观幸福感", rendered_plan)
        self.assertNotIn("工业机器人", rendered_plan)
        self.assertNotIn("蓝领工资", rendered_plan)

        saved = json.loads(
            (
                self.product_root
                / "workspaces"
                / "cgss-happiness"
                / "state"
                / "product"
                / "supervisor_plan.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(saved["provider"]["provider_id"], "openai")
        self.assertEqual(saved["evidence_level"], "llm_supervisor")

    def test_bdd_topic_intake_persists_fallback_plan_when_llm_is_unavailable(self) -> None:
        """行为 3：模型层不可用时先登记项目，并保存明确标记的可重试 fallback 计划。"""
        with patch.object(
            llm_client,
            "chat_completion_with_fallback",
            side_effect=llm_client.LLMError("all_attempts_failed", "All providers failed."),
        ):
            response = self.client.post(
                "/api/v1/topic-intake/supervisor-plan",
                json={
                    "topic": "父母的教育水平对子女工资水平的影响",
                    "slug": "parent-education-wage",
                },
            )

        self.assertEqual(response.status_code, 201, msg=response.text)
        payload = response.json()
        self.assertEqual(payload["_meta"]["evidence_level"], "topic_intake_fallback")
        self.assertEqual(payload["_meta"]["llm_enrichment"]["status"], "failed")
        self.assertTrue(payload["_meta"]["llm_enrichment"]["retryable"])

        project = payload["project"]
        self.assertEqual(project["id"], "proj_parent_education_wage")
        workspace = self.product_root / "workspaces" / "parent-education-wage"
        self.assertTrue((workspace / "paper.yaml").exists())
        self.assertTrue((workspace / "state" / "product" / "research_question.json").exists())
        self.assertTrue((workspace / "state" / "product" / "supervisor_plan.json").exists())

        plan = payload["supervisor_plan"]
        self.assertEqual(plan["evidence_level"], "topic_intake_fallback")
        self.assertEqual(plan["provider"]["provider_id"], "unavailable")
        self.assertEqual(plan["llm_enrichment"]["status"], "failed")
        self.assertTrue(plan["llm_enrichment"]["retryable"])
        self.assertEqual(plan["status"], "needs_review")
        self.assertFalse(plan["can_dispatch"])
        self.assertGreaterEqual(len(plan["stage_plan"]), 4)
        self.assertGreaterEqual(len(plan["subagent_dispatch"]), 3)
        self.assertNotIn("工业机器人", json.dumps(plan, ensure_ascii=False))
        self.assertFalse((workspace / "state" / "product" / "variable_roles.json").exists())
        self.assertFalse((workspace / "state" / "product" / "design_spec.json").exists())
        self.assertFalse((workspace / "state" / "product" / "run_plan.json").exists())

    def test_bdd_default_llm_attempts_include_local_env_providers(self) -> None:
        """行为 4：默认 LLM fallback 必须识别本机已有 provider，而不是只尝试 OpenRouter。"""
        keys = {
            "OPENAI_API_KEY": "test-openai",
            "OPENAI_MODEL": "gpt-5.5",
            "STEPFUN_API_KEY": "test-stepfun",
            "STEPFUN_BASE_URL": "https://stepfun.example/v1",
            "STEPFUN_MODEL": "step-2",
            "DEEPSEEK_API_KEY": "test-deepseek",
            "DEEPSEEK_BASE_URL": "https://deepseek.example/v1",
            "DEEPSEEK_MODEL": "deepseek-chat",
        }
        previous = {key: os.environ.get(key) for key in LLM_ENV_KEYS}
        try:
            for key in LLM_ENV_KEYS:
                os.environ.pop(key, None)
            for key, value in keys.items():
                os.environ[key] = value

            with patch.object(llm_client, "load_local_env_if_present", return_value=None):
                attempts = llm_client.build_default_llm_attempts()

            self.assertEqual(attempts[0]["provider_id"], "openai")
            self.assertEqual(attempts[0]["model"], "gpt-5.5")
            self.assertIn({"provider_id": "stepfun", "model": "step-2", "env": "STEPFUN_API_KEY"}, attempts)
            self.assertIn(
                {"provider_id": "deepseek", "model": "deepseek-chat", "env": "DEEPSEEK_API_KEY"},
                attempts,
            )
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_bdd_default_llm_fallback_fails_without_any_config(self) -> None:
        """行为 5：没有 provider 配置时，默认 fallback 不能伪造一个 SupervisorPlan。"""
        previous = {key: os.environ.get(key) for key in LLM_ENV_KEYS}
        try:
            for key in LLM_ENV_KEYS:
                os.environ.pop(key, None)

            with patch.object(llm_client, "load_local_env_if_present", return_value=None):
                with self.assertRaises(llm_client.LLMError) as raised:
                    llm_client.chat_completion_with_fallback(
                        [{"role": "user", "content": "生成研究计划"}],
                        temperature=0,
                    )

            self.assertEqual(raised.exception.code, "all_attempts_failed")
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
