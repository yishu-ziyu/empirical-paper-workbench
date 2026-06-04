"""L4-design: 方法设计 (Design) service 单元测试 (BDD)。

行为覆盖（spec §6.1 row 4）：
- 行为 1: load_variables 解析 variables.yaml 返回 list[Variable]
- 行为 2: build_candidates 调用 LLM + StatsPAI 评估，返回 3 个 DesignCandidate
- 行为 3: generate_code_stub 根据方法名返回 Python 代码模板
- 行为 4: verify_design 在 candidates >= 3 且 recommended ∈ candidates 时通过
- 行为 5: write_design 落盘 design.json 含 provenance
- 行为 6: run_design 端到端入口
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Product.backend.wrapper.design_service import (
    build_candidates,
    generate_code_stub,
    load_variables,
    run_design,
    verify_design,
    write_design,
)
from Program.prompts.design.v1 import load_prompt_v1
from Product.types.research import (
    DesignCandidate,
    DesignRequest,
    Variable,
)


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

SAMPLE_LLM_JSON = json.dumps(
    {
        "candidates": [
            {
                "method": "DID",
                "rationale": "双重差分能控制城市层面不可观测的固定效应",
                "fits_data": True,
                "sp_output": {"estimator": "did", "version": "2x2"},
            },
            {
                "method": "IV",
                "rationale": "Bartik 工具变量可以处理内生性问题",
                "fits_data": True,
                "sp_output": {"estimator": "iv", "weak_iv_test": "ar"},
            },
            {
                "method": "PSM",
                "rationale": "高暴露度组与低暴露度组存在系统性差异，可用 PSM 平衡",
                "fits_data": True,
                "sp_output": {"estimator": "psm", "caliper": 0.05},
            },
        ],
        "recommended": "IV",
    },
    ensure_ascii=False,
)


def _fake_sp_fn(method: str, variables: list) -> dict:
    """测试用 sp_fn：根据 method 返回固定 sp_output。"""
    return {
        "estimator": method.lower(),
        "tested_at": "2026-06-04T00:00:00Z",
        "n_variables": len(variables),
    }


def _fake_prompt_loader() -> str:
    return load_prompt_v1()


class DesignServiceTests(unittest.TestCase):
    """L4-design: 方法设计 service 单元测试套件。"""

    # ============== 行为 1: load_variables ==============

    def test_bdd_design_load_variables(self) -> None:
        """行为 1: load_variables 解析 YAML 返回 list[Variable]，至少 1 X + 1 Y。"""
        with tempfile.TemporaryDirectory() as tmp:
            var_path = Path(tmp) / "variables.yaml"
            var_path.write_text(SAMPLE_VARIABLES_YAML, encoding="utf-8")
            variables = load_variables(var_path)
        self.assertEqual(len(variables), 3)
        roles = {v.role for v in variables}
        self.assertIn("X", roles)
        self.assertIn("Y", roles)
        self.assertTrue(all(isinstance(v, Variable) for v in variables))

    # ============== 行为 2: build_candidates ==============

    def test_bdd_design_build_candidates_uses_llm_and_statspai(self) -> None:
        """行为 2: build_candidates 调用 LLM + sp_fn，生成 3 个 DesignCandidate + recommended。"""
        with patch(
            "Product.backend.wrapper.design_service.chat_completion",
            return_value=(SAMPLE_LLM_JSON, {"input_tokens": 100, "output_tokens": 200}),
        ):
            variables = [
                Variable(
                    role="Y",
                    dataset_column="ln_wage",
                    semantic_label="工资",
                    description="",
                    reference_papers=[],
                ),
                Variable(
                    role="X",
                    dataset_column="robot",
                    semantic_label="机器人",
                    description="",
                    reference_papers=[],
                ),
            ]
            candidates, recommended = build_candidates(
                brief_text="研究问题：工业机器人对就业的影响",
                variables=variables,
                sp_fn=_fake_sp_fn,
                prompt_loader=_fake_prompt_loader,
            )
        self.assertEqual(len(candidates), 3)
        methods = {c.method for c in candidates}
        self.assertEqual(methods, {"DID", "IV", "PSM"})
        self.assertTrue(all(c.fits_data for c in candidates))
        # sp_output 应被 sp_fn 注入（sp_fn 优先级高于 LLM 返回的 sp_output）
        self.assertEqual(candidates[1].sp_output.get("estimator"), "iv")
        # recommended 来自 LLM 的 JSON
        self.assertEqual(recommended, "IV")

    # ============== 行为 3: generate_code_stub ==============

    def test_bdd_design_generate_code_stub(self) -> None:
        """行为 3: generate_code_stub 根据方法名返回对应 Python 模板。"""
        for method in ["DID", "IV", "RDD", "PSM", "DML"]:
            stub = generate_code_stub(method, [])
            self.assertIn("import", stub)
            self.assertIn(method, stub.upper())
        # 不同方法应生成不同的代码（不能都是同一段）
        did_stub = generate_code_stub("DID", [])
        iv_stub = generate_code_stub("IV", [])
        self.assertNotEqual(did_stub, iv_stub)

    # ============== 行为 4: verify_design ==============

    def test_bdd_design_verify_passes_when_3_candidates_and_recommended(self) -> None:
        """行为 4: verify_design 在 3 个候选 + recommended ∈ candidates 时返回 True。"""
        candidates = [
            DesignCandidate(method="DID", rationale="r1", fits_data=True, sp_output={}),
            DesignCandidate(method="IV", rationale="r2", fits_data=True, sp_output={}),
            DesignCandidate(method="PSM", rationale="r3", fits_data=True, sp_output={}),
        ]
        self.assertTrue(verify_design(candidates, "IV"))

    def test_bdd_design_verify_fails_when_recommended_not_in_candidates(self) -> None:
        """行为 4 边界: recommended 不在 candidates 中时 verify 返回 False。"""
        candidates = [
            DesignCandidate(method="DID", rationale="r1", fits_data=True, sp_output={}),
            DesignCandidate(method="IV", rationale="r2", fits_data=True, sp_output={}),
        ]
        self.assertFalse(verify_design(candidates, "PSM"))

    def test_bdd_design_verify_fails_when_less_than_3_candidates(self) -> None:
        """行为 4 边界: candidates < 3 时 verify 返回 False。"""
        candidates = [
            DesignCandidate(method="DID", rationale="r1", fits_data=True, sp_output={}),
            DesignCandidate(method="IV", rationale="r2", fits_data=True, sp_output={}),
        ]
        self.assertFalse(verify_design(candidates, "DID"))

    # ============== 行为 5: write_design ==============

    def test_bdd_design_write_json_with_provenance(self) -> None:
        """行为 5: write_design 落盘 design.json，含 frontmatter + candidates + recommended + code_stub。"""
        with tempfile.TemporaryDirectory() as tmp:
            tasks_root = Path(tmp)
            candidates = [
                DesignCandidate(method="DID", rationale="r1", fits_data=True, sp_output={"x": 1}),
                DesignCandidate(method="IV", rationale="r2", fits_data=True, sp_output={"y": 2}),
                DesignCandidate(method="PSM", rationale="r3", fits_data=True, sp_output={"z": 3}),
            ]
            path = write_design(
                candidates=candidates,
                recommended="IV",
                code_stub="# IV template",
                topic="工业机器人对就业的影响",
                topic_slug="industrial-robots-employment",
                tasks_root=tasks_root,
            )
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "design.json")
            content = path.read_text(encoding="utf-8")
            # 顶层结构：JSON with topic/method/candidates/recommended/code_stub
            self.assertIn("\"candidates\"", content)
            self.assertIn("\"recommended\"", content)
            self.assertIn("\"code_stub\"", content)
            self.assertIn("\"topic\"", content)
            self.assertIn("IV", content)
            # 必须是有效 JSON
            payload = json.loads(content)
            self.assertEqual(len(payload["candidates"]), 3)
            self.assertEqual(payload["recommended"], "IV")

    # ============== 行为 6: run_design 端到端 ==============

    def test_bdd_design_run_end_to_end(self) -> None:
        """行为 6: run_design 端到端：读 variables + 调 LLM + 落盘 + 返回 DesignResponse。"""
        with tempfile.TemporaryDirectory() as tmp:
            tasks_root = Path(tmp)
            var_path = tasks_root / "industrial-robots-employment" / "variables.yaml"
            var_path.parent.mkdir(parents=True, exist_ok=True)
            var_path.write_text(SAMPLE_VARIABLES_YAML, encoding="utf-8")

            req = DesignRequest(
                topic_slug="industrial-robots-employment",
                variables_path=str(var_path),
                brief_path="Tasks/industrial-robots-employment/brief.md",
            )

            with patch(
                "Product.backend.wrapper.design_service.chat_completion",
                return_value=(SAMPLE_LLM_JSON, {"input_tokens": 100, "output_tokens": 200}),
            ):
                resp = run_design(req, tasks_root, sp_fn=_fake_sp_fn)

            self.assertTrue(resp.verdict_passed)
            self.assertEqual(len(resp.candidates), 3)
            self.assertEqual(resp.recommended, "IV")
            self.assertIn("import", resp.code_stub)
            self.assertTrue(Path(resp.design_path).exists())


if __name__ == "__main__":
    unittest.main()
