from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Product.backend.reproducibility_skill_contract import (
    build_reproducibility_product_capability,
    build_reproducibility_agent_tasks,
    build_reproducible_research_skill_contract,
    write_reproducibility_skill_contract,
)


class ReproducibilitySkillContractTests(unittest.TestCase):
    """BDD: 复现研究材料必须进入产品主线，而不是只停留在说明文档。"""

    def test_bdd_1_contract_contains_reproducible_research_principles(self) -> None:
        """行为 1：契约必须覆盖版本控制、环境锁定、原始数据不可变、代码即文档、一键复现。"""
        contract = build_reproducible_research_skill_contract()

        principles = {item["id"] for item in contract["quality_principles"]}

        self.assertEqual(contract["schema_version"], "p0.reproducible_research_skill_contract.v1")
        self.assertIn("version_control", principles)
        self.assertIn("environment_lock", principles)
        self.assertIn("immutable_raw_data", principles)
        self.assertIn("code_as_documentation", principles)
        self.assertIn("one_command_reproduction", principles)
        self.assertEqual(contract["placement"]["insert_after"], "method_execution_result")
        self.assertEqual(contract["placement"]["insert_before"], "formal_export_preflight")

    def test_bdd_2_contract_maps_generic_reproduction_structure_to_this_repo(self) -> None:
        """行为 2：通用复现结构必须映射到当前仓库的 Data/Program/Results/Manuscripts 路径。"""
        contract = build_reproducible_research_skill_contract()
        mapped_paths = contract["project_structure_mapping"]

        self.assertEqual(mapped_paths["raw_data"], "Data/Raw")
        self.assertEqual(mapped_paths["processed_data"], "Data/Final")
        self.assertEqual(mapped_paths["analysis_code"], "Program")
        self.assertEqual(mapped_paths["tables"], "Results/tab")
        self.assertEqual(mapped_paths["figures"], "Results/fig")
        self.assertEqual(mapped_paths["json_results"], "Results/json")
        self.assertEqual(mapped_paths["manuscript"], "Manuscripts")
        self.assertEqual(mapped_paths["formal_package"], "Submissions/formal_package")

    def test_bdd_3_agent_tasks_are_bounded_and_assign_real_roles(self) -> None:
        """行为 3：复现研究要拆成可派工的 Agent 任务，每个节点不超过 20 分钟。"""
        tasks = build_reproducibility_agent_tasks()
        owner_agents = {task["owner_agent"] for task in tasks}

        self.assertGreaterEqual(len(tasks), 5)
        self.assertIn("ReproAgent", owner_agents)
        self.assertIn("VerifierAgent", owner_agents)
        self.assertIn("ExecutionAgent", owner_agents)
        self.assertIn("ReviewerAgent", owner_agents)
        for task in tasks:
            self.assertLessEqual(task["max_minutes"], 20)
            self.assertIn("output_requirements", task)
            self.assertIn("blocking_gate", task)

    def test_bdd_4_write_contract_persists_state_and_handoff_doc(self) -> None:
        """行为 4：写入函数必须生成机器可读状态和人可读交接文档。"""
        with tempfile.TemporaryDirectory(prefix="repro-contract-") as tmp:
            project_root = Path(tmp)

            result = write_reproducibility_skill_contract(project_root)

            state_path = project_root / "state" / "product" / "reproducibility_skill_contract.json"
            doc_path = project_root / "docs" / "workflows" / "reproducibility-skill-contract.md"
            self.assertTrue(state_path.exists())
            self.assertTrue(doc_path.exists())
            saved = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["schema_version"], "p0.reproducible_research_skill_contract.v1")
            self.assertEqual(result["state_path"], "state/product/reproducibility_skill_contract.json")
            self.assertEqual(result["doc_path"], "docs/workflows/reproducibility-skill-contract.md")

    def test_bdd_5_product_capability_can_be_indexed_by_supervisor(self) -> None:
        """行为 5：复现研究必须作为 product capability 暴露给 Supervisor 和队列。"""
        capability = build_reproducibility_product_capability()

        self.assertEqual(capability["id"], "cap_reproducibility_contract")
        self.assertEqual(capability["namespace"], "product")
        self.assertEqual(capability["status"], "executable")
        self.assertIn("repro_agent", capability["allowed_roles"])
        self.assertIn("verifier_agent", capability["allowed_roles"])
        self.assertEqual(
            capability["adapter_path"],
            "Product.backend.reproducibility_skill_contract.write_reproducibility_skill_contract",
        )
