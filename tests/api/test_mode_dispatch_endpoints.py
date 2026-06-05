"""Mode-dispatch endpoint tests (Task 42, ui-gap-fill).

Verifies:
- POST /api/supervisor/plan returns the static 8-stage plan
- POST /api/auto-research/start returns SSE events for all 4 steps + final_brief
- get_default_plan_draft() returns a copy (not the module constant)
"""
import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from Product.app import app
from Product.backend.supervisor_plan_service import (
    DEFAULT_PLAN_DRAFT_STAGES,
    get_default_plan_draft,
)


class SupervisorPlanEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_post_supervisor_plan_returns_8_stages(self) -> None:
        resp = self.client.post(
            "/api/supervisor/plan",
            json={"topic": "工业机器人对工资的影响", "note": "test"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["topic"], "工业机器人对工资的影响")
        stages = body["stages"]
        self.assertEqual(len(stages), 8, "expected 8 stages mirroring DEFAULT_STAGES")
        # 每个 stage 必有 7 个字段
        for stage in stages:
            for key in ("id", "title", "owner", "status", "reason", "inputs", "outputs"):
                self.assertIn(key, stage, f"stage {stage.get('id')} missing {key}")
        # stage id 顺序与 DEFAULT_STAGES 一致
        self.assertEqual(
            [s["id"] for s in stages],
            [s["id"] for s in DEFAULT_PLAN_DRAFT_STAGES],
        )
        # 推荐首选分支 (data-variables) status=running
        recommended = next(s for s in stages if s["id"] == "data-variables")
        self.assertEqual(recommended["status"], "running")

    def test_post_supervisor_plan_rejects_empty_topic(self) -> None:
        resp = self.client.post("/api/supervisor/plan", json={"topic": ""})
        self.assertEqual(resp.status_code, 422)  # pydantic validation

    def test_get_default_plan_draft_returns_independent_copy(self) -> None:
        draft = get_default_plan_draft()
        self.assertEqual(len(draft), 8)
        # 修改 copy 不应影响 module constant
        draft[0]["title"] = "MUTATED"
        self.assertNotEqual(draft[0]["title"], DEFAULT_PLAN_DRAFT_STAGES[0]["title"])


class AutoResearchEndpointTests(unittest.TestCase):
    """Stream /api/auto-research/start and parse SSE events."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        # AutoResearch writes to TASKS_ROOT (Tasks/{slug}/brief.md). 隔离到 tmp。
        self._original_tasks_root = None
        from Product.api import auto_research as mod

        self._original_tasks_root = mod.TASKS_ROOT
        self.tmp = tempfile.TemporaryDirectory()
        mod.TASKS_ROOT = Path(self.tmp.name)

    def tearDown(self) -> None:
        from Product.api import auto_research as mod

        if self._original_tasks_root is not None:
            mod.TASKS_ROOT = self._original_tasks_root
        self.tmp.cleanup()

    def _collect_sse_events(self, response) -> list[dict]:
        events: list[dict] = []
        for raw in response.iter_lines():
            if not raw:
                continue
            if raw.startswith("data: "):
                payload = raw[6:]
                try:
                    events.append(json.loads(payload))
                except json.JSONDecodeError:
                    pass
        return events

    def test_auto_research_emits_4_step_starts_and_final_brief(self) -> None:
        with self.client.stream(
            "POST",
            "/api/auto-research/start",
            json={"topic": "工业机器人对工资的影响", "topic_slug": "test-robot-wage"},
        ) as resp:
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(
                resp.headers["content-type"].startswith("text/event-stream"),
                f"unexpected content-type: {resp.headers['content-type']}",
            )
            events = self._collect_sse_events(resp)

        events_by_name: dict[str, list[dict]] = {}
        for evt in events:
            events_by_name.setdefault(evt["event"], []).append(evt)

        # 4 step_start events (steps 1, 2, 3, 4)
        step_starts = events_by_name.get("step_start", [])
        self.assertEqual(len(step_starts), 4, f"expected 4 step_start, got {len(step_starts)}")
        for i, evt in enumerate(step_starts, 1):
            self.assertEqual(evt["step_index"], i)
            self.assertIn("title", evt)

        # 4 step_done events
        step_dones = events_by_name.get("step_done", [])
        self.assertEqual(len(step_dones), 4, f"expected 4 step_done, got {len(step_dones)}")

        # final_brief event with brief_path and verdict
        final_briefs = events_by_name.get("final_brief", [])
        self.assertEqual(len(final_briefs), 1)
        self.assertTrue(final_briefs[0]["brief_path"])
        self.assertTrue(final_briefs[0]["markdown"])
        self.assertTrue(final_briefs[0]["verdict_passed"])

        # 收尾 done event
        self.assertEqual(len(events_by_name.get("done", [])), 1)

        # brief.md 落盘 (Tasks/test-robot-wage/brief.md)
        written = Path(self.tmp.name) / "test-robot-wage" / "brief.md"
        self.assertTrue(written.exists())
        self.assertIn("研究问题", written.read_text(encoding="utf-8"))

    def test_auto_research_emits_step_delta_chunks(self) -> None:
        """Streaming path must exercise step_delta events."""
        with self.client.stream(
            "POST",
            "/api/auto-research/start",
            json={"topic": "test topic", "topic_slug": "test-deltas"},
        ) as resp:
            events = self._collect_sse_events(resp)
        deltas = [e for e in events if e["event"] == "step_delta"]
        self.assertGreater(len(deltas), 0, "expected at least 1 step_delta")


if __name__ == "__main__":
    unittest.main()
