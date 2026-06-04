"""L3-variables: 数据变量 (Variables) service 单元测试 (BDD)。

行为覆盖（spec §6.1 row 3）：
- 行为 1: load_schema 返回数据集 schema YAML 字符串
- 行为 2: build_mapping 调用 LLM 解析 schema + brief → list[Variable]
- 行为 3: write_variables 落盘 Tasks/{topic}/variables.yaml 含 YAML frontmatter
- 行为 4: verify_variables 在变量数 >= min_count 且每条 role ∈ 5 枚举时通过
- 行为 5: run_variables 端到端入口

BDD 命名约定: test_bdd_<feature>_<scenario>
中文 docstring 描述业务含义（项目现有风格）。
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Product.backend.wrapper.variables_service import (
    build_mapping,
    load_schema,
    run_variables,
    verify_variables,
    write_variables,
)
from Program.prompts.variables.v1 import load_prompt_v1
from Product.types.research import Variable, VariablesRequest


# ── 测试样本 ────────────────────────────────────────────────────────────────

SAMPLE_LLM_YAML = """\
variables:
  - role: X
    dataset_column: robot_density
    semantic_label: "工业机器人渗透率"
    description: "Bartik IV 的核心来源（Acemoglu & Restrepo 2020 沿用）"
    reference_papers: ["Acemoglu and Restrepo (2020) AER"]
  - role: Y
    dataset_column: ln_wage
    semantic_label: "对数小时工资"
    description: "被解释变量：制造业工人工资（CFPS 2010-2022 加权）"
    reference_papers: ["Acemoglu and Restrepo (2020) AER"]
  - role: control
    dataset_column: edu_last
    semantic_label: "受教育年限"
    description: "控制变量：人力资本"
    reference_papers: ["Bartik (1991) ILR Review"]
  - role: control
    dataset_column: age
    semantic_label: "年龄"
    description: "控制变量：经验代理"
    reference_papers: []
  - role: mediator
    dataset_column: part_time
    semantic_label: "是否兼职"
    description: "中介变量：就业劣质化通道"
    reference_papers: ["Graetz and Michaels (2018) RES"]
  - role: moderator
    dataset_column: urban
    semantic_label: "城乡虚拟变量"
    description: "调节变量：城乡异质性"
    reference_papers: ["Acemoglu and Restrepo (2020) AER"]
"""


def _fake_prompt_loader() -> str:
    return load_prompt_v1()


class VariablesServiceTests(unittest.TestCase):
    """L3-variables: 数据变量 service 单元测试套件。"""

    # ============== 行为 1: load_schema ==============

    def test_bdd_variables_load_schema_returns_yaml_string(self) -> None:
        """行为 1: load_schema 返回数据集 schema YAML 字符串。

        已知数据集 (CFPS/CHIP/CHARLS) 返回固定 stub；custom 走 data_root 读取。
        """
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp)
            schema = load_schema("CFPS", data_root)
        self.assertIsInstance(schema, str)
        # 至少要有 5 个列名 + dataset 标识
        self.assertIn("dataset: CFPS", schema)
        self.assertIn("columns:", schema)
        # CFPS stub 必含 urban, ln_wage, robot_density 等关键列
        for col in ["urban", "ln_wage", "robot_density", "edu_last", "age"]:
            self.assertIn(col, schema)

    def test_bdd_variables_load_schema_custom_falls_back_to_stub(self) -> None:
        """行为 1b: custom 数据集无 schema.yaml 时返回通用 stub。"""
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp)
            schema = load_schema("custom", data_root, custom_dataset_path=None)
        self.assertIn("dataset: custom", schema)

    # ============== 行为 2: build_mapping ==============

    def test_bdd_variables_build_mapping_uses_llm(self) -> None:
        """行为 2: build_mapping 调用 LLM 解析 schema + brief → list[Variable]。

        至少 1 个 X + 1 个 Y + 1 个 control。
        """
        with patch(
            "Product.backend.wrapper.variables_service.chat_completion",
            return_value=(SAMPLE_LLM_YAML, {"input_tokens": 100, "output_tokens": 200}),
        ):
            variables = build_mapping(
                brief_text="## 研究问题\n工业机器人对就业结构的影响",
                schema_yaml="dataset: CFPS\ncolumns: [urban, ln_wage]",
                prompt_loader=_fake_prompt_loader,
            )
        self.assertIsInstance(variables, list)
        self.assertGreaterEqual(len(variables), 3)
        roles = {v.role for v in variables}
        self.assertIn("X", roles)
        self.assertIn("Y", roles)
        self.assertIn("control", roles)
        # 每条都是 Variable 实例
        for v in variables:
            self.assertIsInstance(v, Variable)
            self.assertTrue(v.dataset_column)
            self.assertTrue(v.semantic_label)

    # ============== 行为 3: write_variables ==============

    def test_bdd_variables_write_yaml_with_provenance(self) -> None:
        """行为 3: write_variables 落盘 Tasks/{topic_slug}/variables.yaml，附 frontmatter。"""
        with tempfile.TemporaryDirectory() as tmp:
            tasks_root = Path(tmp)
            variables = [
                Variable(
                    role="X",
                    dataset_column="robot_density",
                    semantic_label="工业机器人渗透率",
                    description="核心解释变量",
                    reference_papers=["Acemoglu 2020"],
                ),
                Variable(
                    role="Y",
                    dataset_column="ln_wage",
                    semantic_label="对数工资",
                    description="被解释变量",
                    reference_papers=["Acemoglu 2020"],
                ),
                Variable(
                    role="control",
                    dataset_column="age",
                    semantic_label="年龄",
                    description="控制变量",
                    reference_papers=[],
                ),
            ]
            path = write_variables(
                variables=variables,
                topic="工业机器人对就业的影响",
                topic_slug="industrial-robots-employment",
                tasks_root=tasks_root,
            )
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "variables.yaml")
            self.assertEqual(path.parent.name, "industrial-robots-employment")
            content = path.read_text(encoding="utf-8")
            # YAML frontmatter 验证
            self.assertIn("---", content)
            self.assertIn("topic: 工业机器人对就业的影响", content)
            self.assertIn("topic_slug: industrial-robots-employment", content)
            self.assertIn("model: MiniMax-M3", content)
            # 至少 1 个 X + 1 个 Y
            self.assertIn("role: X", content)
            self.assertIn("role: Y", content)
            self.assertIn("robot_density", content)
            self.assertIn("ln_wage", content)

    # ============== 行为 4: verify_variables ==============

    def test_bdd_variables_verify_passes_when_min_vars(self) -> None:
        """行为 4: verify_variables 在变量数 >= min_count 且 role 都在 5 枚举内时返回 True。"""
        variables = [
            Variable(role="X", dataset_column="x", semantic_label="X", description="", reference_papers=[]),
            Variable(role="Y", dataset_column="y", semantic_label="Y", description="", reference_papers=[]),
            Variable(role="control", dataset_column="c", semantic_label="C", description="", reference_papers=[]),
        ]
        self.assertTrue(verify_variables(variables, min_count=3))

    def test_bdd_variables_verify_fails_when_below_min_count(self) -> None:
        """行为 4b: verify_variables 在变量数 < min_count 时返回 False。"""
        variables = [
            Variable(role="X", dataset_column="x", semantic_label="X", description="", reference_papers=[]),
            Variable(role="Y", dataset_column="y", semantic_label="Y", description="", reference_papers=[]),
        ]
        self.assertFalse(verify_variables(variables, min_count=3))

    def test_bdd_variables_verify_fails_when_invalid_role(self) -> None:
        """行为 4c: verify_variables 在 role 不在 5 枚举内时返回 False（Pydantic 已拦截，但再防御一层）。"""
        # Pydantic 不允许非法 role；这里手工构造一个绕过验证的对象
        from dataclasses import dataclass
        @dataclass
        class _BadVar:
            role: str = "outcome"
            dataset_column: str = "x"
            semantic_label: str = "X"
            description: str = ""
            reference_papers: list = None  # type: ignore[assignment]
        variables = [_BadVar()]
        self.assertFalse(verify_variables(variables, min_count=1))

    # ============== 行为 5: run_variables ==============

    def test_bdd_variables_run_end_to_end(self) -> None:
        """行为 5: run_variables 端到端：build + write + verify。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tasks_root = tmp_path / "Tasks"
            tasks_root.mkdir()
            req = VariablesRequest(
                topic_slug="industrial-robots-employment",
                brief_path=str(tmp_path / "brief.md"),
                dataset_name="CFPS",
                custom_dataset_path=None,
            )
            with patch(
                "Product.backend.wrapper.variables_service.chat_completion",
                return_value=(SAMPLE_LLM_YAML, {"input_tokens": 100, "output_tokens": 200}),
            ):
                resp = run_variables(req, data_root=tmp_path, tasks_root=tasks_root)
            self.assertGreaterEqual(len(resp.variables), 3)
            self.assertTrue(resp.verdict_passed)
            # 文件落盘
            self.assertTrue(Path(resp.variables_path).exists())
            self.assertEqual(Path(resp.variables_path).name, "variables.yaml")
            # YAML 字段
            self.assertIn("variables_yaml", resp.model_dump())
            self.assertIn("variables:", resp.variables_yaml)


if __name__ == "__main__":
    unittest.main()
