"""L5-execution: 执行实验 (Execution) service 单元测试 (BDD + SSE)。

行为覆盖（spec §6.1 row 5）：
- 行为 1: load_inputs 读 brief/variables/design 三个文件，返回 (brief_text, variables, design_dict)
- 行为 2: write_section 落盘 Manuscripts/{topic}/sections/section_{N}.md
- 行为 3: render_paper 拼接 9 节生成 Manuscripts/{topic}/paper.pdf
- 行为 4: write_results 落盘 Results/{topic}/results.json 含 provenance
- 行为 5: run_execute_stream 生成器，按顺序 yield start / progress×N / section_done×9 / paper_ready / done
- 行为 6: run_execute_stream 在异常时 yield error 事件后停止
- 行为 7（D2 推理链）：section_done 事件携带 prompt/raw_output/parsed_output 三件套
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Callable, Iterator
from unittest.mock import patch

from Product.backend.wrapper.execute_service import (
    load_inputs,
    render_paper,
    run_execute_stream,
    write_results,
    write_section,
)
from Product.types.research import ExecuteEvent, ExecuteRequest, Variable


# ============== 测试用固定输入 ==============

SAMPLE_BRIEF_MD = """# 研究问题
工业机器人对城市制造业就业结构的影响

# 边际贡献
- 首次用 CFPS 2010-2022 检验工业机器人对就业结构的影响

# 研究边界
- 仅限 CFPS 2010-2022 年样本

# 成功标准
- 系数 β > 0 且 p < 0.05
"""

SAMPLE_VARIABLES_YAML = """
variables:
  - role: Y
    dataset_column: ln_wage
    semantic_label: 工资对数
    description: 个体年度工资取对数
    reference_papers: ["Acemoglu 2020"]
  - role: X
    dataset_column: robot_exposure
    semantic_label: 工业机器人暴露度
    description: IFR 行业级机器人装机量映射到个体职业
    reference_papers: ["Acemoglu 2020", "Graetz 2018"]
  - role: control
    dataset_column: age
    semantic_label: 年龄
    description: 个体年龄
    reference_papers: []
"""

SAMPLE_DESIGN_JSON = json.dumps(
    {
        "topic": "工业机器人对就业的影响",
        "method": "IV",
        "candidates": [
            {"method": "DID", "rationale": "r1", "fits_data": True, "sp_output": {}},
            {"method": "IV", "rationale": "r2", "fits_data": True, "sp_output": {}},
            {"method": "PSM", "rationale": "r3", "fits_data": True, "sp_output": {}},
        ],
        "recommended": "IV",
        "code_stub": "# IV template\nimport statsmodels.api as sm",
    },
    ensure_ascii=False,
)


def _fake_prompt_loader(section_name: str) -> Callable[[], str]:
    """测试用 prompt loader 工厂：根据 section_name 返回 mock loader。"""

    def _loader() -> str:
        return f"[MOCK PROMPT] section={section_name}"

    return _loader


def _fake_chat_completion(messages, **kwargs) -> tuple[str, dict]:
    """测试用 LLM 替代品：返回固定 markdown 段。"""

    prompt = messages[0]["content"] if messages else ""
    # 简单 echo 风格，确保不会触发真实 LLM 调用
    text = f"# Section Content\n\nGenerated for prompt: {prompt[:30]}...\n"
    return text, {"input_tokens": 1, "output_tokens": 1}


def _collect_events(gen: Iterator[ExecuteEvent]) -> list[ExecuteEvent]:
    """把 generator 消费成 list，便于断言。"""
    return list(gen)


class ExecuteServiceTests(unittest.TestCase):
    """L5-execution: 执行实验 service 单元测试套件。"""

    # ============== 行为 1: load_inputs ==============

    def test_bdd_execute_load_inputs(self) -> None:
        """行为 1: load_inputs 读 brief/variables/design 三个文件，返回 (brief_text, variables, design_dict)。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            brief_path = tmp_path / "brief.md"
            variables_path = tmp_path / "variables.yaml"
            design_path = tmp_path / "design.json"
            brief_path.write_text(SAMPLE_BRIEF_MD, encoding="utf-8")
            variables_path.write_text(SAMPLE_VARIABLES_YAML, encoding="utf-8")
            design_path.write_text(SAMPLE_DESIGN_JSON, encoding="utf-8")

            brief_text, variables, design_dict = load_inputs(
                brief_path, variables_path, design_path
            )

        self.assertIn("研究问题", brief_text)
        self.assertIn("工业机器人", brief_text)
        self.assertEqual(len(variables), 3)
        self.assertTrue(all(isinstance(v, Variable) for v in variables))
        roles = {v.role for v in variables}
        self.assertIn("X", roles)
        self.assertIn("Y", roles)
        self.assertEqual(design_dict["recommended"], "IV")
        self.assertEqual(design_dict["method"], "IV")
        self.assertIn("code_stub", design_dict)

    # ============== 行为 2: write_section ==============

    def test_bdd_execute_write_section_returns_path(self) -> None:
        """行为 2: write_section 落盘 Manuscripts/{topic}/sections/section_{N}.md。"""
        with tempfile.TemporaryDirectory() as tmp:
            manuscripts_root = Path(tmp)
            path = write_section(
                section_index=3,
                content="# Section 3 content\n",
                topic_slug="industrial-robots-employment",
                manuscripts_root=manuscripts_root,
            )
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "section_3.md")
            self.assertIn("sections", str(path))
            self.assertIn("industrial-robots-employment", str(path))
            content = path.read_text(encoding="utf-8")
            self.assertIn("Section 3 content", content)

    # ============== 行为 3: render_paper ==============

    def test_bdd_execute_render_pdf_concatenates_sections(self) -> None:
        """行为 3: render_paper 拼接 9 节生成 Manuscripts/{topic}/paper.pdf。"""
        with tempfile.TemporaryDirectory() as tmp:
            manuscripts_root = Path(tmp)
            topic_slug = "industrial-robots-employment"
            sections_root = manuscripts_root / topic_slug / "sections"
            sections_root.mkdir(parents=True, exist_ok=True)

            # 写入 9 个 section mock 内容
            for i in range(1, 10):
                (sections_root / f"section_{i}.md").write_text(
                    f"# Section {i}\n\nContent for section {i}.\n", encoding="utf-8"
                )

            paper_path = render_paper(
                topic_slug=topic_slug,
                sections_root=sections_root,
                manuscripts_root=manuscripts_root,
            )
            self.assertTrue(paper_path.exists())
            self.assertEqual(paper_path.name, "paper.pdf")
            self.assertIn(topic_slug, str(paper_path))
            # PDF 至少要 4 字节（%PDF magic）
            self.assertGreaterEqual(paper_path.stat().st_size, 4)

    # ============== 行为 4: write_results ==============

    def test_bdd_execute_write_results_json(self) -> None:
        """行为 4: write_results 落盘 Results/{topic}/results.json 含 provenance。"""
        with tempfile.TemporaryDirectory() as tmp:
            results_root = Path(tmp)
            stats = {
                "beta": 0.1995,
                "std_error": 0.0412,
                "p_value": 0.000003,
                "n_obs": 12345,
                "r_squared": 0.32,
            }
            path = write_results(
                stats=stats,
                topic="工业机器人对就业的影响",
                topic_slug="industrial-robots-employment",
                results_root=results_root,
                model="MiniMax-M3",
                prompt_version="v1",
            )
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "results.json")
            payload = json.loads(path.read_text(encoding="utf-8"))
            # 必有字段
            self.assertEqual(payload["topic"], "工业机器人对就业的影响")
            self.assertEqual(payload["topic_slug"], "industrial-robots-employment")
            self.assertIn("provenance", payload)
            prov = payload["provenance"]
            self.assertEqual(prov["model"], "MiniMax-M3")
            self.assertEqual(prov["prompt_version"], "v1")
            # stats 应平铺在 payload 中
            self.assertEqual(payload["beta"], 0.1995)
            self.assertEqual(payload["p_value"], 0.000003)
            self.assertIn("generated_at", payload)

    # ============== 行为 5: run_execute_stream 端到端 ==============

    def test_bdd_execute_run_stream_yields_all_event_types(self) -> None:
        """行为 5: run_execute_stream 按顺序 yield start → progress×9 → section_done×9 → paper_ready → done。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manuscripts_root = tmp_path / "Manuscripts"
            results_root = tmp_path / "Results"
            tasks_root = tmp_path / "Tasks"
            manuscripts_root.mkdir()
            results_root.mkdir()
            tasks_root.mkdir()

            # 准备 3 个输入文件
            brief_path = tasks_root / "industrial-robots-employment" / "brief.md"
            variables_path = tasks_root / "industrial-robots-employment" / "variables.yaml"
            design_path = tasks_root / "industrial-robots-employment" / "design.json"
            brief_path.parent.mkdir(parents=True, exist_ok=True)
            brief_path.write_text(SAMPLE_BRIEF_MD, encoding="utf-8")
            variables_path.write_text(SAMPLE_VARIABLES_YAML, encoding="utf-8")
            design_path.write_text(SAMPLE_DESIGN_JSON, encoding="utf-8")

            req = ExecuteRequest(
                topic_slug="industrial-robots-employment",
                design_path=str(design_path),
                variables_path=str(variables_path),
                brief_path=str(brief_path),
            )

            with patch(
                "Product.backend.wrapper.execute_service.chat_completion",
                side_effect=_fake_chat_completion,
            ):
                events = _collect_events(
                    run_execute_stream(
                        req,
                        manuscripts_root=manuscripts_root,
                        results_root=results_root,
                        tasks_root=tasks_root,
                        prompt_loader=_fake_prompt_loader,
                    )
                )

            # 验证事件序列（在 with 块内做磁盘检查，避免 tempdir 被清理）
            event_types = [e.event for e in events]
            self.assertEqual(event_types[0], "start")
            self.assertEqual(event_types[-1], "done")

            # 验证 start/progress/section_done/paper_ready 都出现过
            type_counts: dict[str, int] = {}
            for t in event_types:
                type_counts[t] = type_counts.get(t, 0) + 1

            self.assertEqual(type_counts.get("start"), 1)
            self.assertGreaterEqual(type_counts.get("progress"), 9)
            self.assertEqual(type_counts.get("section_done"), 9)
            self.assertEqual(type_counts.get("paper_ready"), 1)
            self.assertEqual(type_counts.get("done"), 1)
            # 9 个 section_done 各带 section_index
            section_done_events = [e for e in events if e.event == "section_done"]
            section_indices = [e.section_index for e in section_done_events]
            self.assertEqual(sorted(section_indices), list(range(1, 10)))

            # paper_ready 事件应含 paper_pdf_path
            paper_ready = next(e for e in events if e.event == "paper_ready")
            self.assertIsNotNone(paper_ready.paper_pdf_path)
            self.assertTrue(Path(paper_ready.paper_pdf_path).exists())

            # done 事件应含 results_json_path
            done = next(e for e in events if e.event == "done")
            self.assertIsNotNone(done.results_json_path)
            self.assertTrue(Path(done.results_json_path).exists())

            # 验证落盘内容
            for i in range(1, 10):
                sec_path = manuscripts_root / "industrial-robots-employment" / "sections" / f"section_{i}.md"
                self.assertTrue(sec_path.exists(), f"section_{i}.md should exist")

            paper_pdf = manuscripts_root / "industrial-robots-employment" / "paper.pdf"
            self.assertTrue(paper_pdf.exists())
            self.assertGreaterEqual(paper_pdf.stat().st_size, 4)

            results_json = results_root / "industrial-robots-employment" / "results.json"
            self.assertTrue(results_json.exists())

    # ============== 行为 6: 异常处理 ==============

    def test_bdd_execute_run_stream_yields_error_on_exception(self) -> None:
        """行为 6: 异常时 yield error 事件并停止。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manuscripts_root = tmp_path / "Manuscripts"
            results_root = tmp_path / "Results"
            tasks_root = tmp_path / "Tasks"
            manuscripts_root.mkdir()
            results_root.mkdir()
            tasks_root.mkdir()

            # 不写任何 input 文件，load_inputs 一定会抛异常
            req = ExecuteRequest(
                topic_slug="missing-topic",
                design_path=str(tmp_path / "design.json"),
                variables_path=str(tmp_path / "variables.yaml"),
                brief_path=str(tmp_path / "brief.md"),
            )

            events = _collect_events(
                run_execute_stream(
                    req,
                    manuscripts_root=manuscripts_root,
                    results_root=results_root,
                    tasks_root=tasks_root,
                    prompt_loader=_fake_prompt_loader,
                )
            )

        # 必须有 start 事件 + error 事件
        event_types = [e.event for e in events]
        self.assertEqual(event_types[0], "start")
        self.assertIn("error", event_types)
        # error 之后不应该继续 yield 其他事件（除最后一个）
        error_idx = event_types.index("error")
        self.assertEqual(error_idx, len(event_types) - 1, "error should be the last event")
        error_event = next(e for e in events if e.event == "error")
        self.assertIn("message", error_event.model_dump())

    # ============== 行为 7: D2 推理链字段 (Kimi 蜂群IDE 启发) ==============

    def test_bdd_execute_section_done_carries_reasoning_chain(self) -> None:
        """行为 7 (D2): section_done 事件携带 prompt / raw_output / parsed_output 三件套。

        这是 Kimi 蜂群IDE 推理链可视化的数据基础：
        - prompt:        喂给 LLM 的完整 prompt（含 brief[:500] 上下文）
        - raw_output:    LLM 返回的原始文本
        - parsed_output: 落盘后 / schema 解析后的最终 markdown 段
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manuscripts_root = tmp_path / "Manuscripts"
            results_root = tmp_path / "Results"
            tasks_root = tmp_path / "Tasks"
            for d in (manuscripts_root, results_root, tasks_root):
                d.mkdir()

            brief_path = tasks_root / "industrial-robots-employment" / "brief.md"
            variables_path = tasks_root / "industrial-robots-employment" / "variables.yaml"
            design_path = tasks_root / "industrial-robots-employment" / "design.json"
            brief_path.parent.mkdir(parents=True, exist_ok=True)
            brief_path.write_text(SAMPLE_BRIEF_MD, encoding="utf-8")
            variables_path.write_text(SAMPLE_VARIABLES_YAML, encoding="utf-8")
            design_path.write_text(SAMPLE_DESIGN_JSON, encoding="utf-8")

            req = ExecuteRequest(
                topic_slug="industrial-robots-employment",
                design_path=str(design_path),
                variables_path=str(variables_path),
                brief_path=str(brief_path),
            )

            with patch(
                "Product.backend.wrapper.execute_service.chat_completion",
                side_effect=_fake_chat_completion,
            ):
                events = _collect_events(
                    run_execute_stream(
                        req,
                        manuscripts_root=manuscripts_root,
                        results_root=results_root,
                        tasks_root=tasks_root,
                        prompt_loader=_fake_prompt_loader,
                    )
                )

            section_done_events = [e for e in events if e.event == "section_done"]
            self.assertEqual(len(section_done_events), 9, "应有 9 个 section_done 事件")

            # 验证每个 section_done 事件都带三件套
            for evt in section_done_events:
                self.assertIsNotNone(evt.prompt, f"section {evt.section_index} 缺 prompt")
                self.assertIsNotNone(evt.raw_output, f"section {evt.section_index} 缺 raw_output")
                self.assertIsNotNone(evt.parsed_output, f"section {evt.section_index} 缺 parsed_output")
                # prompt 应含 section 名（来自 mock loader）
                self.assertIn(
                    f"section={SECTION_NAMES_LOOKUP[evt.section_index]}",
                    evt.prompt or "",
                    f"section {evt.section_index} prompt 不含 section 标识",
                )
                # parsed_output 与 raw_output 在简单 mock 下应一致
                self.assertEqual(evt.parsed_output, evt.raw_output)

            # 验证非 section_done 事件不带三件套（避免 UI 误渲染）
            non_section_done = [e for e in events if e.event != "section_done"]
            for evt in non_section_done:
                # 允许为 None（Pydantic default），但不应回填 prompt
                self.assertIsNone(
                    evt.prompt,
                    f"{evt.event} 事件不应携带 prompt 字段",
                )


# 测试用 SECTION_NAMES 顺序（与 execute_service.SECTION_NAMES 保持一致）
SECTION_NAMES_LOOKUP = {
    1: "section_intro",
    2: "section_lit",
    3: "section_institution",
    4: "section_data",
    5: "section_strategy",
    6: "section_results",
    7: "section_robust",
    8: "section_conclusion",
    9: "section_refs",
}


if __name__ == "__main__":
    unittest.main()
