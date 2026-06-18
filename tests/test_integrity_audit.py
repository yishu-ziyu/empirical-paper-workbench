"""BDD: integrity_audit.py 满足 6 条反捏造行为。

对应 6 条行为 (PaperSpine 4 大机制的反幻觉护栏):
1. evidence/ 4 个核心文件全部存在
2. 当前 (修复后) main-results.md 跑 integrity_audit 退出码 0 (CLEAN)
3. 注入 E-value=1.18 触发 BLOCKER (回归 2026-06-02 捏造事件)
4. 注入 Acemoglu 0.5% 触发 BLOCKER
5. 注入"OLS 被高估"方向错误触发 BLOCKER
6. claim_register.md 含至少 50 条声明确认
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = PROJECT_ROOT / "evidence"
SECTION_PATH = PROJECT_ROOT / "Manuscripts" / "sections" / "main-results.md"
AUDIT_SCRIPT = EVIDENCE_DIR / "integrity_audit.py"
EVIDENCE_BANK = EVIDENCE_DIR / "evidence_bank.md"
CLAIM_REGISTER = EVIDENCE_DIR / "claim_register.md"
PIPELINE = EVIDENCE_DIR / "pipeline.md"


def run_audit_on_section(section_name: str = "main-results", project_root: Path | None = None) -> int:
    """运行 integrity_audit.py 并返回退出码。"""
    project_root = project_root or PROJECT_ROOT
    result = subprocess.run(
        [sys.executable, str(AUDIT_SCRIPT), "--section", section_name, "--project-root", str(project_root)],
        capture_output=True,
        text=True,
    )
    return result.returncode


def run_audit_on_custom_section(
    section_name: str,
    section_content: str,
    project_root: Path,
) -> int:
    """写一个临时 section，跑 audit，返回退出码。"""
    section_path = project_root / "Manuscripts" / "sections" / f"{section_name}.md"
    section_path.parent.mkdir(parents=True, exist_ok=True)
    section_path.write_text(section_content, encoding="utf-8")
    try:
        return run_audit_on_section(section_name, project_root)
    finally:
        section_path.unlink(missing_ok=True)


class TestIntegrityAudit(unittest.TestCase):
    """6 条 BDD 行为。"""

    def test_1_evidence_files_exist(self):
        """行为 1: evidence/ 下 4 个核心文件全部存在。"""
        for path in [EVIDENCE_BANK, CLAIM_REGISTER, PIPELINE, AUDIT_SCRIPT]:
            self.assertTrue(path.exists(), f"Missing: {path}")

    def test_2_current_main_results_passes_audit(self):
        """行为 2: 当前 (修复后) main-results.md 跑 audit 应为 CLEAN (退出码 0)。

        业务规则：修复了 18 条捏造后，论文主结果章节应当通过 5 维 audit。
        """
        self.assertTrue(SECTION_PATH.exists(), f"Missing: {SECTION_PATH}")
        rc = run_audit_on_section("main-results")
        self.assertEqual(rc, 0, f"audit should be CLEAN on the fixed main-results.md, got rc={rc}")

    def test_3_evalue_1_18_triggers_blocker(self):
        """行为 3: 注入 'E-value=1.18' 触发 BLOCKER。

        业务规则：2026-06-02 论文捏造事件中，模型编造了 E-value=1.18 这个数字。
        audit 必须把这种历史捏造指纹列为 BLOCKER。
        """
        # 复制真实项目到临时目录（避免污染源文件）
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "evidence").mkdir()
            (tmp_root / "Manuscripts" / "sections").mkdir(parents=True)
            (tmp_root / "Results" / "json").mkdir(parents=True)
            for src in [EVIDENCE_BANK, CLAIM_REGISTER, PIPELINE]:
                (tmp_root / src.relative_to(PROJECT_ROOT)).write_bytes(src.read_bytes())
            # 伪造 section：包含 E-value=1.18
            fake_section = (
                "# §5 主结果\n\n"
                "工业机器人渗透显著正向影响个体工资水平。E-value=1.18 表明结果对未观测混杂稳健。\n"
                "Baron-Kenny 1986 中介分解显示 Sobel 30/70% 比例。\n"
            )
            rc = run_audit_on_custom_section("fabricated", fake_section, tmp_root)
            self.assertEqual(rc, 1, f"audit should BLOCK on E-value=1.18 fabrication, got rc={rc}")

    def test_4_acemoglu_0_5pct_triggers_blocker(self):
        """行为 4: 注入 'Acemoglu 0.5%' 触发 BLOCKER。

        业务规则：模型不能凭印象写 Acemoglu & Restrepo (2020) 的具体弹性数字；
        论文里一旦出现，必须先在 evidence_bank 登记 + 走 BibTeX 核验。
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "evidence").mkdir()
            (tmp_root / "Manuscripts" / "sections").mkdir(parents=True)
            (tmp_root / "Results" / "json").mkdir(parents=True)
            for src in [EVIDENCE_BANK, CLAIM_REGISTER, PIPELINE]:
                (tmp_root / src.relative_to(PROJECT_ROOT)).write_bytes(src.read_bytes())
            fake_section = (
                "# §5 主结果\n\n"
                "Acemoglu 0.5% 与 Dauth 0.4% 的弹性数字来自美国通勤区数据。\n"
            )
            rc = run_audit_on_custom_section("fabricated", fake_section, tmp_root)
            self.assertEqual(rc, 1, f"audit should BLOCK on Acemoglu 0.5% fabrication, got rc={rc}")

    def test_5_direction_error_triggers_blocker(self):
        """行为 5: 注入 'OLS 系数被高估' 方向错误触发 BLOCKER。

        业务规则：2026-06-02 论文中模型写过"OLS 系数被高估"，但实际 IV > OLS
        提示 OLS 被向下偏 (attenuation bias)，不是被高估。方向错是 LLM 经典错。
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "evidence").mkdir()
            (tmp_root / "Manuscripts" / "sections").mkdir(parents=True)
            (tmp_root / "Results" / "json").mkdir(parents=True)
            for src in [EVIDENCE_BANK, CLAIM_REGISTER, PIPELINE]:
                (tmp_root / src.relative_to(PROJECT_ROOT)).write_bytes(src.read_bytes())
            fake_section = (
                "# §5 主结果\n\n"
                "OLS 系数被高估，IV 估计的 0.1994 更接近真实因果效应。\n"
            )
            rc = run_audit_on_custom_section("fabricated", fake_section, tmp_root)
            self.assertEqual(rc, 1, f"audit should BLOCK on direction-error, got rc={rc}")

    def test_6_claim_register_has_50_entries(self):
        """行为 6: claim_register.md 含至少 50 条声明确认。

        业务规则：每条数字声明必须登记；当前 main-results.md 的全部 4 张表
        22 个 coefficient_rows + 派生数字 + 引用等应该至少有 50 行。
        """
        text = CLAIM_REGISTER.read_text(encoding="utf-8")
        # 统计表格行（以 | C- 开头）
        claim_rows = re.findall(r"^\|\s*C-\d+", text, flags=re.MULTILINE)
        self.assertGreaterEqual(
            len(claim_rows), 50,
            f"claim_register.md should have >= 50 claim rows, got {len(claim_rows)}"
        )

    def test_7_stub_section_triggers_blocker(self):
        """行为 7: 30 行 stub 触发 BLOCKER（Section Completeness 维度生效）。

        业务规则：2026-06-02 之前 audit 对 30 行 stub 误报 READY；现在必须 BLOCKED。
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "evidence").mkdir()
            (tmp_root / "Manuscripts" / "sections").mkdir(parents=True)
            (tmp_root / "Results" / "json").mkdir(parents=True)
            for src in [EVIDENCE_BANK, CLAIM_REGISTER, PIPELINE]:
                (tmp_root / src.relative_to(PROJECT_ROOT)).write_bytes(src.read_bytes())
            # 模拟一个 30 行 stub
            stub_text = "# §1 引言\n\n这是 stub placeholder。\n" * 30
            rc = run_audit_on_custom_section("introduction", stub_text, tmp_root)
            self.assertEqual(rc, 1, f"audit should BLOCK on a 30-line stub, got rc={rc}")

    def test_8_gap_only_checked_in_scope_sections(self):
        """行为 8: GAP-001~007 只在 main-results / robustness 查，其它 section 不应触发。

        业务规则：GAP-001（分样本）只属于 robustness / main-results 的责任范围。
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "evidence").mkdir()
            (tmp_root / "Manuscripts" / "sections").mkdir(parents=True)
            (tmp_root / "Results" / "json").mkdir(parents=True)
            for src in [EVIDENCE_BANK, CLAIM_REGISTER, PIPELINE]:
                (tmp_root / src.relative_to(PROJECT_ROOT)).write_bytes(src.read_bytes())
            # 在 abstract.md 写 2500 字符（足够长）但不含 GAP-001 关键词
            long_text = "# §1 Abstract\n\n" + ("这是 abstract 内容。" * 200)  # ~1200 chars
            # 但 abstract 缺 evidence binding（abstract bindings 3 个 eid），会因 COMP-002 BLOCK
            # 我们关心的是 GAP-001 不应该出现在 abstract 的报告里
            rc = run_audit_on_custom_section("abstract", long_text, tmp_root)
            result = subprocess.run(
                [sys.executable, str(AUDIT_SCRIPT), "--section", "abstract", "--project-root", str(tmp_root), "--markdown"],
                capture_output=True, text=True,
            )
            # 报告里不应该有 "GAP-001" 出现（在 abstract 里不 in-scope）
            self.assertNotIn("GAP-001", result.stdout, "GAP-001 should not appear in abstract audit (out of scope)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
