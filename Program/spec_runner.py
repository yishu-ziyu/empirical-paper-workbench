"""Spec runner: 重新跑同一 topic，从任务书开始，收集 5 tab 产物路径 + verdict.

行为契约 (Phase 8 Task 8.1):
- CLI: --topic 必填 + --topic-slug 可选 (kebab-case 自动)
- 顺序调用 5 个 API:
  1. POST /api/brief       → brief_path / verdict
  2. POST /api/search      → literature_path / n_papers / verdict
  3. POST /api/variables   → variables_path / n_vars / verdict
  4. POST /api/design      → design_path / recommended / verdict
  5. POST /api/execute     → paper_pdf_path / results_json_path (SSE)
- 输出结构化 JSON: {topic, topic_slug, tabs: {...}}

设计要点:
- HTTP 用 `requests` (项目已安装) — 与 wrapper service / OpenAPI 契约对齐
- SSE 解析手写 — 项目无 sseclient，避免新增依赖
- _call_api / _call_sse 是注入点: 测试用 unittest.mock.patch 替换
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Iterator, Optional

import requests


# spec §3.2 + 任务约束: 跑 spec_runner 必须配 MiniMax Token Plan key.
# 主键 = MINIMAX_API_KEY (2026-06-04 L7 迁移); 兼容旧名 MINIMAX_TOKEN_PLAN_KEY.
# 测试在 conftest.py 里 setdefault 一个 dummy key 满足此 assert。
assert (
    "MINIMAX_API_KEY" in os.environ or "MINIMAX_TOKEN_PLAN_KEY" in os.environ
), (
    "Set MINIMAX_API_KEY (preferred) or MINIMAX_TOKEN_PLAN_KEY (legacy) "
    "before running spec_runner.py (see docs/SETUP_MINIMAX.md)."
)


API_BASE = "http://127.0.0.1:8765"


# ── helpers ───────────────────────────────────────────────────────────────────


def slugify_topic(topic: str) -> str:
    """简化版 slugify: 中英混合 → ASCII-only kebab-case.

    与 Product.backend.wrapper.brief_service._slugify 策略一致 (ASCII-only 防御)。
    """
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", topic).strip("-").lower()
    return ascii_part[:50] or "untitled"


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """解析 CLI 参数 — --topic 必填, --topic-slug 可选."""
    parser = argparse.ArgumentParser(
        prog="spec_runner",
        description="Re-run a 5-tab topic end-to-end and collect artifact paths.",
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="研究课题全文 (必填)",
    )
    parser.add_argument(
        "--topic-slug",
        default=None,
        help="URL-safe slug (可选; 缺省自动生成)",
    )
    parser.add_argument(
        "--api-base",
        default=API_BASE,
        help=f"API 服务地址 (默认 {API_BASE})",
    )
    return parser.parse_args(argv)


# ── low-level HTTP (注入点) ──────────────────────────────────────────────────


def _call_api(method: str, path: str, json_body: dict) -> Any:
    """调一次普通 (非流式) API — 实际生产用 requests.post; 测试时 mock.

    Args:
        method: HTTP 方法 (当前只支持 POST)
        path: API 路径 (e.g. "/api/brief")
        json_body: 请求体 (dict)

    Returns:
        requests.Response-like 对象 — 调用方用 .json() / .raise_for_status()
    """
    url = f"{API_BASE}{path}"
    # method 参数保留供未来扩展 (GET / DELETE), 当前仅 POST 走此路径
    if method.upper() == "POST":
        resp = requests.post(url, json=json_body, timeout=120)
    else:
        resp = requests.request(method, url, json=json_body, timeout=120)
    resp.raise_for_status()
    return resp


def _call_sse(method: str, path: str, json_body: dict) -> Iterator[dict]:
    """调一次 SSE 流式 API — 解析 data: {...}\\n\\n 事件.

    Yields:
        dict — 每个 SSE 事件的 data 字段 (已 JSON parse)
    """
    url = f"{API_BASE}{path}"
    if method.upper() == "POST":
        resp = requests.post(url, json=json_body, stream=True, timeout=None)
    else:
        resp = requests.request(method, url, json=json_body, stream=True, timeout=None)
    resp.raise_for_status()
    return parse_sse_stream(resp.iter_lines(decode_unicode=True))


def parse_sse_stream(lines: Iterator[str]) -> Iterator[dict]:
    """极简 SSE 解析器: 读 `data: {...}` 行为 JSON, 其他行 (注释/空行) 跳过.

    行为契约 (test_spec_runner.py 行为 2):
    - 单事件 data: {...}\\n\\n → 1 dict
    - 多事件: 按出现顺序 yield
    - 注释行 (以 : 开头) + 空行 跳过
    - JSON 解析失败 跳过 (不崩)
    - 空流 → 空迭代
    """
    for line in lines:
        if line is None:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(":"):
            # SSE 注释
            continue
        if not stripped.startswith("data:"):
            # 非 data 字段 (event: / id: / retry: 等) 跳过
            continue
        payload = stripped[len("data:"):].strip()
        if not payload:
            continue
        try:
            yield json.loads(payload)
        except json.JSONDecodeError:
            # 损坏的事件跳过
            continue


# ── core: rerun_topic ────────────────────────────────────────────────────────


def rerun_topic(
    topic: str,
    topic_slug: str,
    api_base: str = API_BASE,
) -> dict:
    """重跑 5 tab，收集每 tab 产物路径 + verdict.

    Args:
        topic: 研究课题全文
        topic_slug: URL-safe slug (用于 Tasks/{slug}/ 等子目录)
        api_base: API 服务地址 (默认 http://127.0.0.1:8765)

    Returns:
        {
            "topic": str,
            "topic_slug": str,
            "tabs": {
                "brief":     {"path": str, "verdict": bool},
                "search":    {"path": str, "verdict": bool, "n_papers": int},
                "variables": {"path": str, "verdict": bool, "n_vars": int},
                "design":    {"path": str, "verdict": bool, "recommended": str},
                "execution": {"paper_pdf": str, "results_json": str},
            }
        }
    """
    # 覆盖 API_BASE 临时值 (供测试注入)
    global API_BASE
    original_base = API_BASE
    API_BASE = api_base
    try:
        slug = topic_slug or slugify_topic(topic)
        result: dict[str, Any] = {
            "topic": topic,
            "topic_slug": slug,
            "tabs": {},
        }

        # 1. brief
        brief_resp = _call_api(
            "POST",
            "/api/brief",
            {"topic": topic, "topic_slug": slug},
        ).json()
        brief_path = brief_resp["brief_path"]
        result["tabs"]["brief"] = {
            "path": brief_path,
            "verdict": brief_resp["verdict_passed"],
        }

        # 2. search
        search_resp = _call_api(
            "POST",
            "/api/search",
            {"topic_slug": slug, "brief_path": brief_path},
        ).json()
        result["tabs"]["search"] = {
            "path": search_resp["literature_path"],
            "verdict": search_resp["verdict_passed"],
            "n_papers": len(search_resp.get("papers", [])),
        }

        # 3. variables
        variables_resp = _call_api(
            "POST",
            "/api/variables",
            {
                "topic_slug": slug,
                "brief_path": brief_path,
                "dataset_name": "CFPS",
            },
        ).json()
        result["tabs"]["variables"] = {
            "path": variables_resp["variables_path"],
            "verdict": variables_resp["verdict_passed"],
            "n_vars": len(variables_resp.get("variables", [])),
        }

        # 4. design
        design_resp = _call_api(
            "POST",
            "/api/design",
            {
                "topic_slug": slug,
                "variables_path": variables_resp["variables_path"],
                "brief_path": brief_path,
            },
        ).json()
        result["tabs"]["design"] = {
            "path": design_resp["design_path"],
            "verdict": design_resp["verdict_passed"],
            "recommended": design_resp["recommended"],
        }

        # 5. execution (SSE)
        execution_result: dict[str, Optional[str]] = {
            "paper_pdf": None,
            "results_json": None,
        }
        sse_events = _call_sse(
            "POST",
            "/api/execute",
            {
                "topic_slug": slug,
                "design_path": design_resp["design_path"],
                "variables_path": variables_resp["variables_path"],
                "brief_path": brief_path,
            },
        )
        for event in sse_events:
            if event.get("event") == "error":
                raise RuntimeError(
                    f"execute SSE reported error: {event.get('message', '<no message>')}"
                )
            if event.get("event") == "paper_ready":
                execution_result["paper_pdf"] = event.get("paper_pdf_path")
            if event.get("event") == "done":
                execution_result["results_json"] = event.get("results_json_path")
            # paper_ready + done 都到就 break (省流)
            if execution_result["paper_pdf"] and execution_result["results_json"]:
                break
        result["tabs"]["execution"] = execution_result

        return result
    finally:
        API_BASE = original_base


# ── main ─────────────────────────────────────────────────────────────────────


def main(argv: Optional[list[str]] = None) -> None:
    """CLI 入口: 解析 argv → rerun → 打印 JSON."""
    args = parse_args(argv)
    out = rerun_topic(args.topic, args.topic_slug, api_base=args.api_base)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
