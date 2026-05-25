from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGN_CONTRACT = REPO_ROOT / "docs" / "architecture-v2" / "codex-phase-p3-react-workbench-design-contract.md"


class ReactWorkbenchDesignContractTest(unittest.TestCase):
    """P3：先规范各模块 UI，再接入具体工作流。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = DESIGN_CONTRACT.read_text(encoding="utf-8")

    def test_contract_names_all_primary_modules(self) -> None:
        expected_modules = [
            "研究入口",
            "任务队列",
            "递归搜索",
            "数据与变量",
            "方法设计",
            "执行实验",
            "结果解释",
            "论文草稿",
            "复现导出",
            "Agent 审计",
        ]
        for module in expected_modules:
            self.assertIn(module, self.source)

    def test_contract_defines_progressive_disclosure_and_right_drawer(self) -> None:
        expected_markers = [
            "默认只显示",
            "按需展开",
            "右侧 Drawer",
            "详情不占主屏",
            "主屏只承载当前决策",
            "正式层写回必须显式确认",
        ]
        for marker in expected_markers:
            self.assertIn(marker, self.source)

    def test_contract_locks_visual_language(self) -> None:
        expected_markers = [
            "黑白灰",
            "低对比",
            "DottedSurface",
            "禁止防守性文案",
            "不使用彩色状态色",
            "不做普通 SaaS landing page",
        ]
        for marker in expected_markers:
            self.assertIn(marker, self.source)

    def test_contract_defines_module_specific_interactions(self) -> None:
        expected_markers = [
            "输入题目",
            "生成任务书",
            "创建任务队列",
            "查看搜索证据",
            "确认变量角色",
            "审阅方法前提",
            "启动实验",
            "审阅 finding",
            "绑定证据",
            "导出预检",
        ]
        for marker in expected_markers:
            self.assertIn(marker, self.source)


if __name__ == "__main__":
    unittest.main()
