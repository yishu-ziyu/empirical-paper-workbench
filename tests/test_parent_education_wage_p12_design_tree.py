from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_TREE_PATH = ROOT / "docs/product-control/p12-p16-design-tree.md"
DASHBOARD_STATE_PATH = ROOT / "docs/product-control/workflow-dashboard-state.json"


class ParentEducationWageP12DesignTreeTests(unittest.TestCase):
    """BDD: P12-0 creates a design tree before any DesignSpec or model work."""

    def test_bdd_p12_0_design_tree_tracks_p9_saved_to_p12_preflight_path(self) -> None:
        """行为 1：P12-0 必须承接 P9 已保存状态，并只打开 DesignSpec 预检。"""
        content = DESIGN_TREE_PATH.read_text(encoding="utf-8")

        self.assertIn("P12-0 Design Tree / Pre-PRD", content)
        self.assertIn("P9 已正式保存", content)
        self.assertIn("state/product/variable_roles.json", content)
        self.assertIn("P12 DesignSpec Preflight", content)
        self.assertIn("不是模型执行", content)

    def test_bdd_p12_0_design_tree_covers_p12_to_p16_with_acceptance_and_fallbacks(self) -> None:
        """行为 2：设计树必须覆盖 P12-P16，并写清验收和回退。"""
        content = DESIGN_TREE_PATH.read_text(encoding="utf-8")

        for phase in [
            "P12 DesignSpec Preflight",
            "P13 RunPlan Approval",
            "P14 Model Execution And Evidence Ledger",
            "P15 Draft Generation And Export",
            "P16 User Acceptance And Satisfaction Loop",
        ]:
            self.assertIn(phase, content)
        self.assertIn("验收标准", content)
        self.assertIn("回退路径", content)
        self.assertIn("停机条件", content)

    def test_bdd_p12_dashboard_keeps_p12_branch_without_model_execution(self) -> None:
        """行为 3：仪表盘推进到 P16 后仍必须保留 P12 分支且不允许伪造模型。"""
        state = json.loads(DASHBOARD_STATE_PATH.read_text(encoding="utf-8"))

        self.assertIn(
            state["status_code"],
            {"p12_design_tree_ready", "p12_design_spec_preflight_ready", "p16_blocked_branch_ready"},
        )
        self.assertIn("P16", state["current_gate"])
        self.assertIn("P13-P16", state["executive_summary"]["next_action"])
        self.assertEqual("不运行模型", state["forbidden_output"])
        self.assertIn("不伪造回归结果", state["guardrail"])
        self.assertIn("P12 方法规格预检", [branch["title"] for branch in state["branches"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
