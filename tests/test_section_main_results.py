"""BDD: 改写后的 main-results.md 满足 6 条行为 (改自 stub).

对应 6 条行为 (见 BDD 改写清单):
1. 主表存在 (booktabs) + 数字可追溯
2. IV 主结果完整 (系数/SE/p/N + 1% 显著)
3. OLS vs IV 对比 + Hausman 拒绝外生性
4. First-stage F 远超 Staiger-Stock 阈 10
5. 经济解释 (弹性) + 机制解释 (制造业/职业)
6. 长度 chinese_char_count ∈ [3000, 6000]
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SECTION_PATH = PROJECT_ROOT / "Manuscripts" / "sections" / "main-results.md"
TABLES_PATH = PROJECT_ROOT / "Results" / "json" / "regression_tables.json"


def read_section() -> str:
    return SECTION_PATH.read_text(encoding="utf-8")


def read_tables() -> dict:
    return json.loads(TABLES_PATH.read_text(encoding="utf-8"))


class MainResultsSectionTests(unittest.TestCase):
    """BDD: main-results.md 满足 6 条行为 (来自 BDD 改写清单)"""

    def test_bdd_behavior_1_main_table_with_booktabs_and_traceable_numbers(self) -> None:
        """行为 1: 主表存在 (booktabs), 4 列, 关键数字可 grep 回源."""
        text = read_section()
        # booktabs 三线表
        self.assertIn(r"\toprule", text, "缺 \\toprule (主表不是 booktabs 格式)")
        self.assertIn(r"\midrule", text, "缺 \\midrule")
        self.assertIn(r"\bottomrule", text, "缺 \\bottomrule")
        # 4 列名
        for col in ["OLS", "IV-ln_wage", "IV-manu", "IV-ISEI"]:
            self.assertIn(col, text, f"主表缺列: {col}")
        # 7 个关键数字 (主表) 都在源文件
        sources_text = json.dumps(read_tables(), ensure_ascii=False)
        # 0.079 子串匹配源文件 table_1 SE (0.07934) 和 table_3 coef (0.07984)
        for needle in ["0.199", "0.079", "0.103", "0.999", "34315", "15697"]:
            self.assertIn(needle, sources_text, f"源文件缺数字 {needle} (行为 1 追溯要求)")

    def test_bdd_behavior_2_iv_main_row_complete_with_significance(self) -> None:
        """行为 2: IV-ln_wage 列 ln_robot 系数/SE/p/N 齐全, 1% 显著."""
        text = read_section()
        self.assertIn("0.012", text, "缺 p = 0.012 (IV ln_robot 显著性)")
        # 3 颗星: ln_robot 同一行内出现 ***
        self.assertRegex(text, r"ln_robot[^\n]*\*\*\*", "ln_robot 缺 3 颗星 (1% 水平显著)")

    def test_bdd_behavior_3_ols_iv_comparison_with_hausman(self) -> None:
        """行为 3: OLS vs IV 对比, 显式说 N 差, 系数大小, Hausman F=284 拒绝外生性."""
        text = read_section()
        self.assertIn("15697", text, "缺 OLS N=15697")
        self.assertIn("34315", text, "缺 IV N=34315")
        self.assertIn("Hausman", text, "缺 'Hausman' 关键词")
        self.assertIn("284", text, "缺 Hausman F = 284 (拒绝外生性)")

    def test_bdd_behavior_4_first_stage_f_strong_instrument(self) -> None:
        """行为 4: First-stage F = 14685, 跟 Staiger-Stock 阈 10 比, 写'无弱工具'."""
        text = read_section()
        self.assertIn("14685", text, "缺 First-stage F = 14685")
        self.assertIn("Staiger", text, "缺 Staiger-Stock 阈值引用")
        self.assertRegex(text, r"无弱工具|不存在弱工具|not weak", "缺'无弱工具'结论")

    def test_bdd_behavior_5_economic_and_mechanism_interpretation(self) -> None:
        """行为 5: ≥1 句弹性解释 + ≥1 句机制解释."""
        text = read_section()
        # 弹性解释: 0.1-0.3% 区间 (例: "约 0.2% 工资弹性")
        self.assertRegex(text, r"0\.[123]\s*%|约?\s*0\.[12]", "缺弹性解释 (~0.2%)")
        # 机制: 制造业 + 职业声望
        self.assertIn("制造业", text, "缺机制关键词'制造业'")
        self.assertIn("职业", text, "缺机制关键词'职业'(声望)")

    def test_bdd_behavior_6_chinese_char_count_in_range(self) -> None:
        """行为 6: chinese_char_count ∈ [3000, 6000] (paper_quality_report aer_like 阈值)."""
        text = read_section()
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        self.assertGreaterEqual(
            chinese_chars, 3000, f"chinese_chars={chinese_chars} 不足 3000"
        )
        self.assertLessEqual(
            chinese_chars, 6000, f"chinese_chars={chinese_chars} 超过 6000"
        )


if __name__ == "__main__":
    unittest.main()
