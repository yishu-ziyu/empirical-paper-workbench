from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from Program.prompts.brief.v4 import load_prompt_v4
from Product.backend.wrapper import brief_stream_service as svc


class BriefStreamSelfCritiqueTests(unittest.TestCase):
    """BDD: 任务书 step 3 必须辅助用户判断，但不能替用户判断。"""

    def test_bdd_step3_done_carries_three_llm_concerns_only(self) -> None:
        """行为 1：step 3 done 事件携带最多三条 LLM 最不放心点。"""
        chunks_by_call = iter(
            [
                ["步骤一内容。### STEP_1_DONE ###"],
                ["步骤二内容。### STEP_2_DONE ###"],
                [
                    "贡献点草稿。\n"
                    "## 我最不放心的 3 点\n"
                    "- 数据是否真的能观察到社会资本的关键维度。\n"
                    "- 题目中的因果语言可能超过横截面数据能支持的范围。\n"
                    "- 需要用户确认 CGSS 年份和变量口径。\n"
                    "### STEP_3_DONE ###"
                ],
            ]
        )

        def fake_stream(**_: object):
            yield from next(chunks_by_call)

        with patch.object(svc, "chat_completion_stream", side_effect=fake_stream):
            events = list(svc.run_brief_stream("社会资本对居民主观幸福感的影响"))

        step3_done = next(
            e for e in events if e.event == "step_done" and e.step_index == 3
        )
        self.assertEqual(
            step3_done.critique,
            [
                "数据是否真的能观察到社会资本的关键维度。",
                "题目中的因果语言可能超过横截面数据能支持的范围。",
                "需要用户确认 CGSS 年份和变量口径。",
            ],
        )

    def test_bdd_non_decision_steps_do_not_emit_self_critique(self) -> None:
        """行为 2：step 1/2 不是用户决策点，不应展示 LLM 自评。"""
        chunks_by_call = iter(
            [
                ["步骤一内容。\n## 我最不放心的 3 点\n- 不应显示。\n### STEP_1_DONE ###"],
                ["步骤二内容。\n## 我最不放心的 3 点\n- 不应显示。\n### STEP_2_DONE ###"],
                ["步骤三内容。\n### STEP_3_DONE ###"],
            ]
        )

        def fake_stream(**_: object):
            yield from next(chunks_by_call)

        with patch.object(svc, "chat_completion_stream", side_effect=fake_stream):
            events = list(svc.run_brief_stream("社会资本对居民主观幸福感的影响"))

        non_decision_done = [
            e for e in events if e.event == "step_done" and e.step_index in (1, 2)
        ]
        self.assertEqual(len(non_decision_done), 2)
        self.assertTrue(all(e.critique is None for e in non_decision_done))

    def test_bdd_parser_drops_positive_self_grade_and_limits_concerns(self) -> None:
        """行为 3：自评只保留风险/疑虑，不把“做得不错”当成用户判断依据。"""
        text = (
            "贡献点草稿。\n"
            "## 自评\n"
            "整体来说这个方案比较完整。\n"
            "- 最不放心的是 CGSS 是否能稳定测量社会资本。\n"
            "- 还需要确认幸福感变量是否为有序因变量。\n"
            "- 控制变量遗漏会影响解释力度。\n"
            "- 第四条应该被截断。\n"
            "## 下一节\n"
            "其他内容"
        )

        self.assertEqual(
            svc._extract_critique(text),
            [
                "最不放心的是 CGSS 是否能稳定测量社会资本。",
                "还需要确认幸福感变量是否为有序因变量。",
                "控制变量遗漏会影响解释力度。",
            ],
        )

    def test_bdd_prompt_requires_step3_to_output_three_concerns(self) -> None:
        """行为 4：真实 LLM 路径必须被提示生成 step 3 用户决策辅助信息。"""
        prompt = load_prompt_v4()
        self.assertIn("我最不放心的 3 点", prompt)
        self.assertIn("不是评价自己做得好不好", prompt)
        self.assertLess(prompt.index("### 步骤 3"), prompt.index("我最不放心的 3 点"))
        self.assertLess(prompt.index("我最不放心的 3 点"), prompt.index("### STEP_3_DONE ###"))


if __name__ == "__main__":
    unittest.main()
