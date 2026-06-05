"""Tests for Product.backend.identification_audit_service.

Task 44 (ui-gap-fill) — 6th tab real statspai diagnostics.

测试业务契约:
  B1 (真实数据)  当 results.json 有 event_study / first_stage 字段, service 提取出结构化数据
  B2 (数据来源)  source 字段反映数据是 statspai / results_json / unavailable
  B3 (失败兜底)  缺文件 / 空文件 / 字段缺失 → 返回 dict with error/reason, 不抛

跑法:
  PYTHONPATH=. python -m pytest tests/test_identification_audit_service.py -v
  或: PYTHONPATH=. python tests/test_identification_audit_service.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# 让 Product.* 可 import
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Product.backend.identification_audit_service import (  # noqa: E402
    IdentificationAuditError,
    run_identification_audit,
)


class IdentificationAuditServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ident-audit-"))
        self.results_path = self.tmp / "results.json"
        self.design_path = self.tmp / "design.json"

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ── B1: 真实数据 — 提取 event_study + first_stage ───────────────────
    def test_extracts_event_study_and_first_stage_from_results_json(self) -> None:
        """B1 真实数据: results.json 含 event_study + first_stage → 各 card 拿到结构化数据."""
        results = {
            "method": "IV",
            "topic": "test",
            "event_study": {
                "joint_pvalue": 0.42,
                "joint_statistic": 3.21,
                "coefficients": [
                    {"period": -3, "estimate": 0.05, "se": 0.04, "pvalue": 0.21},
                    {"period": -2, "estimate": 0.03, "se": 0.04, "pvalue": 0.45},
                    {"period": -1, "estimate": 0.0, "se": 0.0, "pvalue": None},
                    {"period": 0, "estimate": 0.18, "se": 0.05, "pvalue": 0.0003},
                    {"period": 1, "estimate": 0.22, "se": 0.06, "pvalue": 0.0002},
                ],
            },
            "first_stage": {
                "partial_r2": 0.47,
                "f_statistic": 124.5,
                "n_obs": 3210,
                "ar_pvalue": 0.000003,
                "ar_ci_lower": 0.15,
                "ar_ci_upper": 0.28,
            },
        }
        design = {
            "method": "IV",
            "identification_strategy": {
                "causal_graph": "Z -> X -> Y; U -> X; U -> Y",
            },
        }
        self.results_path.write_text(json.dumps(results), encoding="utf-8")
        self.design_path.write_text(json.dumps(design), encoding="utf-8")

        audit = run_identification_audit(
            str(self.results_path),
            str(self.design_path),
        )

        # 业务断言: 三块都有 source + 关键数字
        self.assertEqual(audit["method"], "IV")
        self.assertEqual(audit["pretrend"]["source"], "results_json")
        self.assertEqual(audit["pretrend"]["joint_pvalue"], 0.42)
        # 3 个负 period: -3, -2, -1 (后者是 reference period, 系数=0)
        self.assertEqual(audit["pretrend"]["n_pre_periods"], 3)
        self.assertEqual(len(audit["pretrend"]["coefficients"]), 5)

        self.assertEqual(audit["weak_iv"]["source"], "results_json")
        self.assertEqual(audit["weak_iv"]["partial_r2"], 0.47)
        self.assertEqual(audit["weak_iv"]["f_statistic"], 124.5)
        self.assertEqual(audit["weak_iv"]["n_obs"], 3210)
        self.assertEqual(audit["weak_iv"]["ar_pvalue"], 0.000003)

        # DAG 有 spec (source 可能是 statspai 也可能是 design_json, 都算通过)
        self.assertIn(audit["dag"]["source"], ("statspai", "design_json"))
        self.assertIn("Z -> X -> Y", audit["dag"]["spec"])

    # ── B3: 失败兜底 — 缺文件 / 字段缺失 ───────────────────────────────
    def test_missing_files_returns_structured_error(self) -> None:
        """B3 失败兜底: 两份文件都不存在 → 不抛, 返回 error + 各卡 unavailable."""
        audit = run_identification_audit(
            str(self.tmp / "nope1.json"),
            str(self.tmp / "nope2.json"),
        )
        self.assertEqual(audit["error"], "no_artifacts")
        self.assertIn("reason", audit)
        self.assertEqual(audit["pretrend"]["source"], "unavailable")
        self.assertEqual(audit["weak_iv"]["source"], "unavailable")
        self.assertEqual(audit["dag"]["source"], "unavailable")

    def test_empty_results_returns_n_a_cards(self) -> None:
        """B3 失败兜底: 文件存在但 statspai 字段缺失 → pretrend/weak_iv unavailable, dag 有默认."""
        self.results_path.write_text(json.dumps({"method": "OLS"}), encoding="utf-8")
        self.design_path.write_text(json.dumps({"method": "OLS"}), encoding="utf-8")

        audit = run_identification_audit(
            str(self.results_path),
            str(self.design_path),
        )
        # method 提取到了
        self.assertEqual(audit["method"], "OLS")
        # pretrend + weak_iv 都没数据
        self.assertEqual(audit["pretrend"]["source"], "unavailable")
        self.assertEqual(audit["pretrend"]["joint_pvalue"], None)
        self.assertEqual(audit["weak_iv"]["source"], "unavailable")
        self.assertEqual(audit["weak_iv"]["partial_r2"], None)
        # dag 有默认 spec
        self.assertEqual(audit["dag"]["source"], "default")
        self.assertIn("Z -> X -> Y", audit["dag"]["spec"])

    def test_invalid_results_path_returns_error(self) -> None:
        """B3 失败兜底: 空路径 → 端点不会崩."""
        audit = run_identification_audit("", str(self.design_path))
        self.assertEqual(audit["error"], "invalid_results_path")

    def test_corrupted_json_does_not_raise(self) -> None:
        """B3 失败兜底: JSON 解析失败 → 不会抛, pretrend/weak_iv unavailable."""
        self.results_path.write_text("{ this is not json", encoding="utf-8")
        self.design_path.write_text(json.dumps({"method": "OLS"}), encoding="utf-8")

        # 不应抛
        audit = run_identification_audit(
            str(self.results_path),
            str(self.design_path),
        )
        # results.json 损坏 → 视为 None → pretrend/weak_iv unavailable
        # (design.json 仍可读, 所以没触发 no_artifacts)
        self.assertEqual(audit["pretrend"]["source"], "unavailable")
        self.assertEqual(audit["weak_iv"]["source"], "unavailable")
        # dag 来源: design_json 或 default (没 causal_graph)
        self.assertIn(audit["dag"]["source"], ("default", "design_json"))

    def test_weak_iv_partial_r2_extraction_via_alternate_key(self) -> None:
        """B1 + 健壮性: first_stage 用 partial_r_squared / f_eff 别名也能识别."""
        results = {
            "method": "IV",
            "first_stage": {
                "partial_r_squared": 0.5,
                "f_eff": 88.0,
                "n_obs": 1000,
            },
        }
        self.results_path.write_text(json.dumps(results), encoding="utf-8")
        self.design_path.write_text(json.dumps({"method": "IV"}), encoding="utf-8")

        audit = run_identification_audit(
            str(self.results_path),
            str(self.design_path),
        )
        self.assertEqual(audit["weak_iv"]["source"], "results_json")
        self.assertEqual(audit["weak_iv"]["partial_r2"], 0.5)
        self.assertEqual(audit["weak_iv"]["f_statistic"], 88.0)
        self.assertEqual(audit["weak_iv"]["n_obs"], 1000)


if __name__ == "__main__":
    unittest.main()
