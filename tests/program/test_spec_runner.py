"""Program/spec_runner.py BDD tests。

行为契约 (Phase 8 Task 8.1):
- 接受 --topic 必填 + --topic-slug 可选 (CLI 参数校验)
- 顺序 POST /api/brief → /api/search → /api/variables → /api/design → SSE /api/execute
- 每步捕获产物路径 + verdict
- 输出结构化 JSON: {topic, topic_slug, tabs: {brief, search, variables, design, execution}}
- SSE 解析: data: {...}\\n\\n 多事件流

测试约定: 用 unittest.mock.patch 替换 requests.post / iter_lines，**不**真实发 HTTP。
"""
from __future__ import annotations

import json
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from Program import spec_runner


# ── 行为 1: CLI 参数校验 ──────────────────────────────────────────────────────


class CliArgumentTests(unittest.TestCase):
    """行为 1: --topic 必填 + --topic-slug 可选."""

    def test_bdd_parse_args_requires_topic(self) -> None:
        """行为 1a: 缺 --topic 时 parser 报错 (SystemExit on parse_args)."""
        with self.assertRaises(SystemExit):
            spec_runner.parse_args([])

    def test_bdd_parse_args_accepts_topic_only(self) -> None:
        """行为 1b: 只有 --topic 时 args.topic 存在, args.topic_slug 为 None."""
        ns = spec_runner.parse_args(["--topic", "工业机器人对就业的影响"])
        self.assertEqual(ns.topic, "工业机器人对就业的影响")
        self.assertIsNone(ns.topic_slug)

    def test_bdd_parse_args_accepts_topic_slug(self) -> None:
        """行为 1c: --topic-slug 透传."""
        ns = spec_runner.parse_args(
            ["--topic", "工业机器人", "--topic-slug", "industrial-robots"]
        )
        self.assertEqual(ns.topic_slug, "industrial-robots")

    def test_bdd_slugify_topic_generates_kebab_case(self) -> None:
        """行为 1d: slugify 中英混合 → ASCII kebab-case."""
        slug = spec_runner.slugify_topic("工业机器人 Industrial Robots 2024!")
        # ASCII-only kebab-case (中文字段被丢掉)
        self.assertIn("industrial", slug)
        self.assertIn("robots", slug)
        self.assertIn("2024", slug)
        self.assertNotIn(" ", slug)
        self.assertNotIn("!", slug)


# ── 行为 2: SSE 解析器 ────────────────────────────────────────────────────────


class SseParserTests(unittest.TestCase):
    """行为 2: SSE 事件解析 (data: {...}\\n\\n)."""

    def test_bdd_sse_parse_single_event(self) -> None:
        """行为 2a: 单事件 data: {...}\\n\\n 解析为一个 dict."""
        stream = 'data: {"event": "start", "stage": "loading"}\n\n'
        events = list(spec_runner.parse_sse_stream(StringIO(stream)))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "start")
        self.assertEqual(events[0]["stage"], "loading")

    def test_bdd_sse_parse_multiple_events(self) -> None:
        """行为 2b: 多事件 + 双换行分隔，全部解析."""
        stream = (
            'data: {"event": "start"}\n\n'
            'data: {"event": "progress", "section_index": 1}\n\n'
            'data: {"event": "paper_ready", "paper_pdf_path": "/tmp/p.pdf"}\n\n'
        )
        events = list(spec_runner.parse_sse_stream(StringIO(stream)))
        self.assertEqual(len(events), 3)
        self.assertEqual(events[2]["event"], "paper_ready")
        self.assertEqual(events[2]["paper_pdf_path"], "/tmp/p.pdf")

    def test_bdd_sse_skips_non_data_lines(self) -> None:
        """行为 2c: SSE 注释行 (以 : 开头) + 空行 跳过."""
        stream = (
            ": this is a comment\n"
            "\n"
            'data: {"event": "start"}\n'
            "\n"
            ": another comment\n"
            "\n"
            'data: {"event": "done"}\n\n'
        )
        events = list(spec_runner.parse_sse_stream(StringIO(stream)))
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "start")
        self.assertEqual(events[1]["event"], "done")

    def test_bdd_sse_skips_malformed_json(self) -> None:
        """行为 2d: JSON 解析失败的 data 行跳过 (不崩)."""
        stream = (
            'data: not-json\n\n'
            'data: {"event": "ok"}\n\n'
        )
        events = list(spec_runner.parse_sse_stream(StringIO(stream)))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "ok")

    def test_bdd_sse_handles_empty_stream(self) -> None:
        """行为 2e: 空流返回空列表."""
        events = list(spec_runner.parse_sse_stream(StringIO("")))
        self.assertEqual(events, [])


# ── 行为 3-7: 端到端 rerun_topic（mocked HTTP） ────────────────────────────────


def _build_mock_response(json_body: dict) -> MagicMock:
    """构造一个模拟的 requests.Response-like 对象."""
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json = MagicMock(return_value=json_body)
    return mock


def _build_sse_response(events: list[dict]) -> MagicMock:
    """构造 SSE streaming response (iter_lines)."""
    mock = MagicMock()
    mock.raise_for_status = MagicMock()

    def _iter_lines(chunk_size=1, decode_unicode=False):
        for ev in events:
            yield f"data: {json.dumps(ev, ensure_ascii=False)}"

    mock.iter_lines = _iter_lines
    return mock


def _patch_requests_post(responses: list[MagicMock]):
    """Helper: 把 _call_api / _call_sse 都 patch 成给定的 mock responses."""
    return [
        patch("Program.spec_runner._call_api", side_effect=responses[:-1]),
        patch(
            "Program.spec_runner._call_sse",
            return_value=iter(responses[-1] if responses else []),
        ),
    ]


class RerunTopicTests(unittest.TestCase):
    """行为 3-7: rerun_topic 端到端串联 5 tab."""

    def _sample_responses(self) -> list[MagicMock]:
        """5 个 API + 1 个 SSE 流 (包含 paper_ready + done 事件)."""
        brief = _build_mock_response({
            "brief_markdown": "## 研究问题\nx\n",
            "brief_path": "/abs/Tasks/foo/brief.md",
            "verdict_passed": True,
        })
        search = _build_mock_response({
            "literature_markdown": "# Lit",
            "literature_path": "/abs/Tasks/foo/literature.md",
            "papers": [{"title": "p1"}, {"title": "p2"}],
            "verdict_passed": True,
        })
        variables = _build_mock_response({
            "variables_yaml": "variables: []",
            "variables_path": "/abs/Tasks/foo/variables.yaml",
            "variables": [{"role": "X"}, {"role": "Y"}],
            "verdict_passed": True,
        })
        design = _build_mock_response({
            "design_json": "{}",
            "design_path": "/abs/Tasks/foo/design.json",
            "candidates": [],
            "recommended": "IV",
            "code_stub": "# iv",
            "verdict_passed": True,
        })
        sse = _build_sse_response([
            {"event": "start", "stage": "loading"},
            {"event": "section_done", "section_index": 1},
            {"event": "paper_ready", "paper_pdf_path": "/abs/Manuscripts/foo/paper.pdf"},
            {"event": "done", "results_json_path": "/abs/Results/foo/results.json"},
        ])
        return [brief, search, variables, design, sse]

    def test_bdd_rerun_topic_calls_all_5_endpoints_in_order(self) -> None:
        """行为 3: 5 个 endpoint 按顺序调用 (brief → search → variables → design → execute)."""
        responses = self._sample_responses()
        call_log: list[str] = []

        def fake_api(method, path, json_body):
            call_log.append(f"{method} {path}")
            idx = sum(1 for c in call_log if not c.startswith("SSE")) - 1
            return responses[idx]

        def fake_sse(method, path, json_body):
            call_log.append(f"SSE {method} {path}")
            return iter(_build_sse_iter())

        with patch("Program.spec_runner._call_api", side_effect=fake_api), \
             patch("Program.spec_runner._call_sse", side_effect=fake_sse):
            spec_runner.rerun_topic("foo topic", "foo-slug")

        # 5 个调用都发生: 4 个 API + 1 个 SSE
        self.assertEqual(len(call_log), 5, f"got calls: {call_log}")
        # 顺序
        api_calls = [c for c in call_log if not c.startswith("SSE")]
        sse_calls = [c for c in call_log if c.startswith("SSE")]
        self.assertEqual(len(api_calls), 4)
        self.assertEqual(len(sse_calls), 1)
        # 路径顺序
        self.assertTrue(api_calls[0].endswith("/api/brief"))
        self.assertTrue(api_calls[1].endswith("/api/search"))
        self.assertTrue(api_calls[2].endswith("/api/variables"))
        self.assertTrue(api_calls[3].endswith("/api/design"))
        self.assertTrue(sse_calls[0].endswith("/api/execute"))

    def test_bdd_rerun_topic_returns_structured_json(self) -> None:
        """行为 4: 输出 JSON 含 topic / topic_slug / 5 tabs."""
        brief = _build_mock_response({
            "brief_markdown": "## 研究问题\nx",
            "brief_path": "/p/brief.md",
            "verdict_passed": True,
        })
        search = _build_mock_response({
            "literature_markdown": "",
            "literature_path": "/p/lit.md",
            "papers": [{}] * 10,
            "verdict_passed": True,
        })
        variables = _build_mock_response({
            "variables_yaml": "",
            "variables_path": "/p/v.yaml",
            "variables": [{}] * 5,
            "verdict_passed": True,
        })
        design = _build_mock_response({
            "design_json": "",
            "design_path": "/p/d.json",
            "candidates": [],
            "recommended": "DID",
            "code_stub": "",
            "verdict_passed": True,
        })
        sse_iter = iter(_build_sse_iter())

        with patch("Program.spec_runner._call_api", side_effect=[brief, search, variables, design]), \
             patch("Program.spec_runner._call_sse", return_value=sse_iter):
            result = spec_runner.rerun_topic("topic", "slug")

        # 顶层结构
        self.assertEqual(result["topic"], "topic")
        self.assertEqual(result["topic_slug"], "slug")
        self.assertIn("tabs", result)
        tabs = result["tabs"]
        # 5 个 tab 都有
        for tab in ("brief", "search", "variables", "design", "execution"):
            self.assertIn(tab, tabs, f"missing tab: {tab}")
        # 关键字段
        self.assertEqual(tabs["brief"]["path"], "/p/brief.md")
        self.assertTrue(tabs["brief"]["verdict"])
        self.assertEqual(tabs["search"]["n_papers"], 10)
        self.assertEqual(tabs["variables"]["n_vars"], 5)
        self.assertEqual(tabs["design"]["recommended"], "DID")
        self.assertEqual(tabs["execution"]["paper_pdf"], "/abs/Manuscripts/foo/paper.pdf")
        self.assertEqual(tabs["execution"]["results_json"], "/abs/Results/foo/results.json")

    def test_bdd_rerun_topic_uses_topic_slug_for_paths(self) -> None:
        """行为 5: 后端响应里的 path 透传到结果."""
        brief = _build_mock_response({
            "brief_markdown": "x", "brief_path": "/p/brief.md", "verdict_passed": True,
        })
        search = _build_mock_response({
            "literature_markdown": "", "literature_path": "/p/lit.md",
            "papers": [], "verdict_passed": True,
        })
        variables = _build_mock_response({
            "variables_yaml": "", "variables_path": "/p/v.yaml",
            "variables": [], "verdict_passed": True,
        })
        design = _build_mock_response({
            "design_json": "", "design_path": "/p/d.json",
            "candidates": [], "recommended": "PSM", "code_stub": "",
            "verdict_passed": True,
        })
        sse_iter = iter(_build_sse_iter())

        with patch("Program.spec_runner._call_api", side_effect=[brief, search, variables, design]), \
             patch("Program.spec_runner._call_sse", return_value=sse_iter):
            result = spec_runner.rerun_topic("x", "y")

        self.assertEqual(result["tabs"]["design"]["recommended"], "PSM")

    def test_bdd_rerun_topic_sse_error_propagates(self) -> None:
        """行为 6: SSE 收到 error 事件时抛 RuntimeError 携带 message."""
        brief = _build_mock_response({"brief_markdown": "x", "brief_path": "/p", "verdict_passed": True})
        search = _build_mock_response({"literature_markdown": "", "literature_path": "/p", "papers": [], "verdict_passed": True})
        variables = _build_mock_response({"variables_yaml": "", "variables_path": "/p", "variables": [], "verdict_passed": True})
        design = _build_mock_response({"design_json": "", "design_path": "/p", "candidates": [], "recommended": "IV", "code_stub": "", "verdict_passed": True})

        def error_sse(method, path, json_body):
            return iter([{"event": "error", "message": "boom"}])

        with patch("Program.spec_runner._call_api", side_effect=[brief, search, variables, design]), \
             patch("Program.spec_runner._call_sse", side_effect=error_sse):
            with self.assertRaises(RuntimeError) as ctx:
                spec_runner.rerun_topic("t", "s")
            self.assertIn("boom", str(ctx.exception))

    def test_bdd_rerun_topic_http_error_raises(self) -> None:
        """行为 7: HTTP 错误 (非 2xx) 让底层 _call_api 抛, 行为由 _call_api 决定."""
        brief = MagicMock()
        brief.raise_for_status.side_effect = RuntimeError("500 brief failed")

        with patch("Program.spec_runner._call_api", side_effect=RuntimeError("500 brief failed")):
            with self.assertRaises(RuntimeError):
                spec_runner.rerun_topic("t", "s")


# ── 行为 8: main() CLI 入口 ───────────────────────────────────────────────────


class MainEntryTests(unittest.TestCase):
    """行为 8: spec_runner.main() 接受 sys.argv + 输出 JSON."""

    def test_bdd_main_prints_json_with_topic(self) -> None:
        """行为 8a: main() 解析 argv + rerun + 打印 JSON 到 stdout."""
        brief = _build_mock_response({"brief_markdown": "x", "brief_path": "/p", "verdict_passed": True})
        search = _build_mock_response({"literature_markdown": "", "literature_path": "/p", "papers": [], "verdict_passed": True})
        variables = _build_mock_response({"variables_yaml": "", "variables_path": "/p", "variables": [], "verdict_passed": True})
        design = _build_mock_response({"design_json": "", "design_path": "/p", "candidates": [], "recommended": "IV", "code_stub": "", "verdict_passed": True})

        with patch("Program.spec_runner._call_api", side_effect=[brief, search, variables, design]), \
             patch("Program.spec_runner._call_sse", return_value=iter(_build_sse_iter())), \
             patch("sys.argv", ["spec_runner", "--topic", "工业机器人", "--topic-slug", "robots"]):
            with patch("sys.stdout", new_callable=StringIO) as out:
                spec_runner.main()
                output = out.getvalue()

        # 输出是合法 JSON
        parsed = json.loads(output)
        self.assertEqual(parsed["topic"], "工业机器人")
        self.assertEqual(parsed["topic_slug"], "robots")

    def test_bdd_main_auto_generates_slug_when_missing(self) -> None:
        """行为 8b: --topic-slug 缺省时 main() 自动 slugify."""
        brief = _build_mock_response({"brief_markdown": "x", "brief_path": "/p", "verdict_passed": True})
        search = _build_mock_response({"literature_markdown": "", "literature_path": "/p", "papers": [], "verdict_passed": True})
        variables = _build_mock_response({"variables_yaml": "", "variables_path": "/p", "variables": [], "verdict_passed": True})
        design = _build_mock_response({"design_json": "", "design_path": "/p", "candidates": [], "recommended": "IV", "code_stub": "", "verdict_passed": True})

        with patch("Program.spec_runner._call_api", side_effect=[brief, search, variables, design]), \
             patch("Program.spec_runner._call_sse", return_value=iter(_build_sse_iter())), \
             patch("sys.argv", ["spec_runner", "--topic", "Industrial Robots 2024"]):
            with patch("sys.stdout", new_callable=StringIO) as out:
                spec_runner.main()
                parsed = json.loads(out.getvalue())

        # slug 自动生成 (ASCII kebab-case)
        self.assertIn("industrial", parsed["topic_slug"])
        self.assertIn("robots", parsed["topic_slug"])
        self.assertNotIn(" ", parsed["topic_slug"])


def _build_sse_iter():
    """生成 SSE 事件的辅助函数."""
    return [
        {"event": "start", "stage": "loading"},
        {"event": "paper_ready", "paper_pdf_path": "/abs/Manuscripts/foo/paper.pdf"},
        {"event": "done", "results_json_path": "/abs/Results/foo/results.json"},
    ]


# ── 行为 9: _call_api / _call_sse 简单调用形态 ─────────────────────────────────


class LowLevelHttpTests(unittest.TestCase):
    """行为 9: _call_api 和 _call_sse 接受 (method, path, json_body) 并返回响应/迭代器."""

    def test_bdd_call_api_uses_requests_post(self) -> None:
        """行为 9a: _call_api 内部调 requests.post."""
        with patch("Program.spec_runner.requests.post") as mock_post:
            mock_post.return_value = MagicMock()
            spec_runner._call_api("POST", "/api/brief", {"topic": "x"})
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(args[0].endswith("/api/brief"), True)
            self.assertEqual(kwargs["json"], {"topic": "x"})

    def test_bdd_call_sse_uses_requests_post_stream(self) -> None:
        """行为 9b: _call_sse 内部调 requests.post(stream=True)."""
        with patch("Program.spec_runner.requests.post") as mock_post:
            mock_post.return_value = MagicMock()
            spec_runner._call_sse("POST", "/api/execute", {"topic_slug": "x"})
            mock_post.assert_called_once()
            kwargs = mock_post.call_args.kwargs
            self.assertTrue(kwargs.get("stream", False))


if __name__ == "__main__":
    unittest.main()
