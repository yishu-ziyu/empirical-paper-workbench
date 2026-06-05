"""Task 41 — /api/system/status service 单元测试.

行为覆盖 (BDD §Task 41 行为 3):
- 行为 A: aggregate() 4 项主字段 (cap_count, cost_total, artifact_count, obs_status) 正确
- 行为 B: sub-service 失败时, 字段降级为 None, 不抛异常
- 行为 C: 项目不存在时, 走 transient 兜底 (id 保留)
- 行为 D: 详情列表 (capabilities, artifacts, cost_breakdown) 透传 sub-service 输出
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Product.backend.system_status_service import aggregate


def _write_state(root: Path, project_id: str, *, cap_count: int = 2, usd: float = 1.25) -> None:
    """Build a minimal fake state tree so aggregate() can walk it."""
    caps = {
        "id": "capability_registry",
        "version": 1,
        "evidence_level": "local_file",
        "capabilities": [
            {
                "id": f"cap_x{i}",
                "name": f"cap_x{i}",
                "category": "test",
                "risk_level": "low",
            }
            for i in range(cap_count)
        ],
    }
    (root / "state" / "product").mkdir(parents=True, exist_ok=True)
    (root / "state" / "product" / "capabilities.json").write_text(
        json.dumps(caps, ensure_ascii=False), encoding="utf-8"
    )
    events = [
        {
            "event_id": f"cost_evt_{i}",
            "project_id": project_id,
            "capability_id": f"cap_x{i % cap_count or 0}",
            "actor_id": "test_actor",
            "estimated_usd": usd if i == 0 else 0.0,
            "status": "succeeded",
            "wall_seconds": 0.0,
        }
        for i in range(2)
    ]
    (root / "state" / "product" / "cost_events.jsonl").write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n",
        encoding="utf-8",
    )
    runs_dir = root / "state" / "runs" / "run_test123"
    runs_dir.mkdir(parents=True, exist_ok=True)
    (runs_dir / "run_manifest.json").write_text(
        json.dumps(
            {"project_id": project_id, "status": "completed", "run_id": "run_test123"},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


class AggregateHappyPathTests(unittest.TestCase):
    """行为 A + D: 主路径上 4 字段和详情列表都有意义数值。"""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        _write_state(self.tmp, "proj_demo", cap_count=3, usd=4.5)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_aggregate_returns_four_main_fields(self):
        out = aggregate(self.tmp, self.tmp, "proj_demo", "demo-slug")
        self.assertEqual(out["cap_count"], 3)
        self.assertEqual(out["artifact_count"], 0)
        self.assertEqual(out["obs_status"], "completed")
        # cost_total reflects the cost events in jsonl (4.5 + 0.0 = 4.5)
        self.assertAlmostEqual(out["cost_total"], 4.5, places=2)

    def test_aggregate_returns_capability_list(self):
        out = aggregate(self.tmp, self.tmp, "proj_demo", "demo-slug")
        self.assertEqual(len(out["capabilities"]), 3)
        self.assertEqual(out["capabilities"][0]["category"], "test")
        self.assertEqual(out["capabilities"][0]["risk_level"], "low")

    def test_aggregate_returns_cost_breakdown(self):
        out = aggregate(self.tmp, self.tmp, "proj_demo", "demo-slug")
        self.assertGreater(len(out["cost_breakdown"]), 0)
        self.assertEqual(out["cost_breakdown"][0]["service"], "cap_x0")
        self.assertAlmostEqual(out["cost_breakdown"][0]["amount"], 4.5, places=2)

    def test_aggregate_keeps_project_id_and_topic_slug(self):
        out = aggregate(self.tmp, self.tmp, "proj_demo", "demo-slug")
        self.assertEqual(out["project_id"], "proj_demo")
        self.assertEqual(out["topic_slug"], "demo-slug")

    def test_aggregate_observability_picks_latest_run_for_project(self):
        """Two runs in state/runs/, only the one for proj_demo should be reported."""
        other = self.tmp / "state" / "runs" / "run_other"
        other.mkdir(parents=True, exist_ok=True)
        (other / "run_manifest.json").write_text(
            json.dumps({"project_id": "proj_other", "status": "failed"}),
            encoding="utf-8",
        )
        out = aggregate(self.tmp, self.tmp, "proj_demo", "demo-slug")
        self.assertEqual(out["obs_status"], "completed")


class AggregateGracefulDegradationTests(unittest.TestCase):
    """行为 B: sub-service 任何子调用异常 → 主字段变 None, 不抛."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_capability_service_failure_yields_null_cap_count(self):
        with patch(
            "Product.backend.capability_registry.get_project_capabilities",
            side_effect=RuntimeError("boom"),
        ):
            out = aggregate(self.tmp, self.tmp, "proj_x")
        self.assertIsNone(out["cap_count"])
        self.assertEqual(out["capabilities"], [])
        # diagnostics should record the failure
        self.assertIsNotNone(out["diagnostics"]["capability_registry"])

    def test_cost_service_failure_yields_null_cost_total(self):
        with patch(
            "Product.backend.cost_service.get_project_costs",
            side_effect=RuntimeError("boom"),
        ):
            out = aggregate(self.tmp, self.tmp, "proj_x")
        self.assertIsNone(out["cost_total"])
        self.assertEqual(out["cost_breakdown"], [])

    def test_artifact_service_failure_yields_null_artifact_count(self):
        with patch(
            "Product.backend.workflow_service.list_workflows",
            side_effect=RuntimeError("boom"),
        ):
            out = aggregate(self.tmp, self.tmp, "proj_x")
        self.assertIsNone(out["artifact_count"])
        self.assertEqual(out["artifacts"], [])

    def test_observability_failure_yields_unknown(self):
        """If _aggregate_observability raises, _safe_call should swallow and the
        service-level value should fall back to the default ('unknown')."""
        with patch(
            "Product.backend.system_status_service._aggregate_observability",
            side_effect=RuntimeError("boom"),
        ):
            out = aggregate(self.tmp, self.tmp, "proj_x")
        # obs_status should be a non-null string (graceful degradation), not raise
        self.assertIsNotNone(out["obs_status"])
        self.assertIsInstance(out["obs_status"], str)

    def test_no_state_directory_returns_clean_defaults(self):
        """Empty product root — should not raise; obs_status = no_runs."""
        out = aggregate(self.tmp, self.tmp, "proj_anything")
        self.assertEqual(out["cap_count"], 0)
        self.assertEqual(out["cost_total"], 0.0)
        self.assertEqual(out["artifact_count"], 0)
        self.assertEqual(out["obs_status"], "no_runs")


class AggregateTransientFallbackTests(unittest.TestCase):
    """行为 C: project_id 不存在时, registry 兜底返回 transient 项目 (id 保留)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        _write_state(self.tmp, "proj_phantom")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_unknown_project_id_keeps_requested_id(self):
        out = aggregate(self.tmp, self.tmp, "proj_does_not_exist", "slug-x")
        self.assertEqual(out["project_id"], "proj_does_not_exist")
        self.assertEqual(out["topic_slug"], "slug-x")
        # 4 主字段都不抛 — caps/cost 取 transient 项目的 0
        self.assertIsNotNone(out["cap_count"])
        self.assertIsNotNone(out["cost_total"])


if __name__ == "__main__":
    unittest.main()
