# Brief Tab Step-Cards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the brief tab's batch-mode UX with an SSE stream that shows the LLM "thinking out loud" through 4 research-journal steps, with a user checkpoint at the contribution-planning step (3 buttons: 继续 / 修改 / 重选).

**Architecture:** Convert `POST /api/brief` to streaming SSE. Backend uses one LLM call with structured markers (`### STEP_N_DONE ###`) and yields `step_start` / `step_delta` / `step_done` / `await_user` / `final_brief` / `heartbeat` / `done` / `error` events. At step 3 the backend holds. A second `POST /api/brief/resume` endpoint takes the user's action (continue/modify/reselect) plus the prior step texts, and emits the remaining events. `BriefPanel` consumes SSE via `fetch` + `ReadableStream` and renders 4 `StepCard` components.

**Tech Stack:** Python 3.12 + FastAPI + `urllib` (existing LLM client) + `iter_lines` SSE consumption; React 19 + TypeScript + Vite + Playwright. State is client-driven — no server-side resume state.

---

## File Structure

**New files:**
- `Program/prompts/brief/v4.md` — 4-step structured prompt
- `Program/prompts/brief/v4.py` — loader
- `Product/backend/wrapper/brief_stream_service.py` — generator + resume logic
- `Product/web-react/src/components/StepCard.tsx` — card component
- `tests/wrapper/test_brief_stream_service.py` — 3 BDD tests
- `tests/wrapper/test_brief_prompt_v4.py` — 1 unit test (loader)
- `tests/wrapper/test_llm_client_stream.py` — 1 unit test (streaming)
- `Product/web-react/e2e/brief-step-cards.spec.ts` — 1 e2e test

**Modified files:**
- `Product/backend/llm_client.py` — add `chat_completion_stream()` (Anthropic + OpenAI protocols)
- `Product/types/research.py` — add `BriefEvent` + `BriefResumeRequest` Pydantic models
- `Product/api/brief.py` — rewrite as SSE; add `/api/brief/resume`
- `Product/backend/wrapper/brief_service.py` — extract `_build_final_brief_markdown()` helper (shared with stream service)
- `Product/web-react/src/components/BriefPanel.tsx` — full rewrite with SSE
- `Program/prompts/CHANGELOG.md` — log v4

---

## Task 1: Add `chat_completion_stream()` to LLM client

**Files:**
- Modify: `Product/backend/llm_client.py:227-330` (both protocol functions gain streaming variants)
- Test: `tests/wrapper/test_llm_client_stream.py`

- [ ] **Step 1: Write the failing test**

Create `tests/wrapper/test_llm_client_stream.py`:

```python
"""LLM client streaming: chat_completion_stream() yields text chunks.

行为: 用 mock 替代 urllib.urlopen, 验证 chat_completion_stream() 真的按 SSE
protocol 解析 streaming 响应并逐 chunk yield 文本.
"""
from __future__ import annotations

import json
import unittest
from io import BytesIO
from unittest.mock import patch, MagicMock


def _fake_urlopen_sse_anthropic(chunks: list[dict]):
    """模拟 Anthropic-compatible SSE 响应: 每个 event 是 'data: {...}\\n\\n'."""
    body = "".join(
        f"event: {c.get('event', 'message')}\ndata: {json.dumps(c)}\n\n"
        for c in chunks
    )
    resp = MagicMock()
    resp.__enter__ = lambda self: self
    resp.__exit__ = lambda self, *args: False
    resp.readline.side_effect = BytesIO(body.encode("utf-8")).readline
    return resp


class ChatCompletionStreamTests(unittest.TestCase):

    def test_bdd_chat_completion_stream_anthropic_yields_text_chunks(self) -> None:
        """行为 1: Anthropic 协议 streaming, chat_completion_stream() 按 message_delta 顺序 yield text."""
        from Product.backend import llm_client

        chunks = [
            {"type": "message_start", "message": {"id": "m1"}},
            {"type": "content_block_start", "index": 0},
            {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "你好"}},
            {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "，世界"}},
            {"type": "content_block_stop", "index": 0},
            {"type": "message_stop"},
        ]
        fake_resp = _fake_urlopen_sse_anthropic(chunks)
        with patch("urllib.request.urlopen", return_value=fake_resp):
            with patch.dict("os.environ", {"MINIMAX_API_KEY": "sk-cp-test"}):
                pieces = list(
                    llm_client.chat_completion_stream(
                        messages=[{"role": "user", "content": "hi"}],
                        provider_id="minimax",
                    )
                )
        self.assertEqual("".join(pieces), "你好，世界")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_llm_client_stream.py -v`
Expected: `ImportError: cannot import name 'chat_completion_stream'`

- [ ] **Step 3: Implement `chat_completion_stream()` and Anthropic SSE parser**

Modify `Product/backend/llm_client.py`. Add right after `chat_completion()` (line ~407):

```python
def chat_completion_stream(
    messages: list[dict[str, str]],
    *,
    provider_id: str | None = None,
    model: str | None = None,
    temperature: float = 0.3,
    api_key: str | None = None,
    base_url: str | None = None,
) -> Iterator[str]:
    """流式调用 LLM, 逐 chunk yield 文本片段.

    与 chat_completion() 共享 provider / key / base_url 解析逻辑, 但
    通过 SSE 协议读取响应并按事件顺序提取 text_delta.

    Yields:
        文本片段 (str). 拼接后 = 完整 LLM 输出.

    Raises:
        LLMError: 同 chat_completion().
    """
    preset = resolve_provider(provider_id)

    # 与 chat_completion 共享 key / base_url 解析
    resolved_key = (api_key or "").strip()
    if not resolved_key and preset.api_key_env:
        resolved_key = os.getenv(preset.api_key_env, "").strip()
    if not resolved_key and preset.id == "minimax":
        resolved_key = os.getenv("MINIMAX_TOKEN_PLAN_KEY", "").strip()
    if preset.requires_api_key and not resolved_key:
        raise LLMError("missing_api_key", f"{preset.name} requires API key.")

    selected_model = (model or preset.default_model).strip()
    if not selected_model:
        raise LLMError("missing_model", f"{preset.name} model is required.")

    effective_base_url = base_url
    if not effective_base_url and preset.id == "minimax":
        effective_base_url = os.getenv("MINIMAX_BASE_URL", "").strip() or None

    if preset.api_type == "openai-compatible":
        yield from _stream_openai_compatible(
            api_key=resolved_key,
            base_url=normalize_base_url(effective_base_url, api_type=preset.api_type, fallback=preset.base_url),
            model=selected_model,
            messages=messages,
            temperature=temperature,
        )
        return

    if preset.api_type == "anthropic-compatible":
        yield from _stream_anthropic_compatible(
            api_key=resolved_key,
            base_url=normalize_base_url(effective_base_url, api_type=preset.api_type, fallback=preset.base_url),
            model=selected_model,
            messages=messages,
            temperature=temperature,
        )
        return

    raise LLMError("unsupported_api_type", f"Unsupported protocol: {preset.api_type}")


def _stream_anthropic_compatible(
    *,
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
) -> Iterator[str]:
    """Anthropic-compatible SSE: 解析 content_block_delta.text_delta."""
    import urllib.request
    url = f"{base_url.rstrip('/')}/messages"
    payload = {
        "model": model,
        "max_tokens": 4096,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Accept": "text/event-stream",
        },
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LLMError("provider_error", f"Anthropic stream HTTP {exc.code}: {body[:300]}")
    except urllib.error.URLError as exc:
        raise LLMError("network_error", f"Cannot reach provider: {exc}")

    # SSE 解析: 行累积, 遇到空行时 flush 一个 event
    event_type = "message"
    data_lines: list[str] = []
    try:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").rstrip("\n").rstrip("\r")
            if line == "":
                if data_lines:
                    try:
                        evt = json.loads("\n".join(data_lines))
                    except json.JSONDecodeError:
                        data_lines = []
                        continue
                    data_lines = []
                    delta = evt.get("delta") or {}
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        if text:
                            yield text
                    if evt.get("type") == "message_stop":
                        return
                continue
            if line.startswith("event: "):
                event_type = line[len("event: "):].strip()
            elif line.startswith("data: "):
                data_lines.append(line[len("data: "):])
    finally:
        resp.close()


def _stream_openai_compatible(
    *,
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
) -> Iterator[str]:
    """OpenAI-compatible SSE: 解析 choices[0].delta.content."""
    import urllib.request
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "text/event-stream",
        },
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LLMError("provider_error", f"OpenAI stream HTTP {exc.code}: {body[:300]}")
    except urllib.error.URLError as exc:
        raise LLMError("network_error", f"Cannot reach provider: {exc}")

    try:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").rstrip("\n").rstrip("\r")
            if not line.startswith("data: "):
                continue
            payload_str = line[len("data: "):]
            if payload_str.strip() == "[DONE]":
                return
            try:
                evt = json.loads(payload_str)
            except json.JSONDecodeError:
                continue
            choices = evt.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            text = delta.get("content")
            if text:
                yield text
    finally:
        resp.close()
```

Add the missing imports at the top of `llm_client.py` (line ~7):

```python
from typing import Any, Iterator
```

(merge with existing `from typing import Any`)

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_llm_client_stream.py -v`
Expected: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add Product/backend/llm_client.py tests/wrapper/test_llm_client_stream.py
git commit -m "feat(llm): chat_completion_stream() for Anthropic + OpenAI SSE"
```

---

## Task 2: Add brief v4 prompt with 4 STEP_N_DONE markers

**Files:**
- Create: `Program/prompts/brief/v4.md`
- Create: `Program/prompts/brief/v4.py`
- Modify: `Program/prompts/CHANGELOG.md` (append v4 entry)
- Test: `tests/wrapper/test_brief_prompt_v4.py`

- [ ] **Step 1: Write the failing test**

Create `tests/wrapper/test_brief_prompt_v4.py`:

```python
"""brief v4 prompt loader + 4-step structure.

行为:
- load_prompt_v4() 返回的 prompt 包含 4 个 STEP_N_DONE 标记 (1, 2, 3, 4)
- prompt 含 {topic} 占位符
- prompt 含 4 个 ## 段标题
"""
from __future__ import annotations

import unittest


class BriefPromptV4Tests(unittest.TestCase):

    def test_bdd_prompt_v4_contains_4_step_markers(self) -> None:
        from Program.prompts.brief.v4 import load_prompt_v4
        prompt = load_prompt_v4()
        for n in (1, 2, 3, 4):
            self.assertIn(f"### STEP_{n}_DONE ###", prompt)

    def test_bdd_prompt_v4_has_topic_placeholder(self) -> None:
        from Program.prompts.brief.v4 import load_prompt_v4
        prompt = load_prompt_v4()
        self.assertIn("{topic}", prompt)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_prompt_v4.py -v`
Expected: `ModuleNotFoundError: No module named 'Program.prompts.brief.v4'`

- [ ] **Step 3: Create v4 loader and markdown**

Create `Program/prompts/brief/v4.py`:

```python
"""brief prompt v4 loader — 4 步分步思考, 适合 SSE streaming.

每步用 ### STEP_N_DONE ### 标记切分, 后端 parser 据此 emit step_done 事件.
"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v4.md"


def load_prompt_v4() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")
```

Create `Program/prompts/brief/v4.md`:

```markdown
你是实证经济学论文简报作者。把题目拆成 4 步来想，每步走完用 ### STEP_N_DONE ### 标记切分。

题目：{topic}

请按顺序思考：

### 步骤 1: 分析研究问题 ###
1-2 句话点出这是什么类型的研究问题（因果推断/描述性/政策评估），预期用什么方法（DiD/IV/RDD/PSM/DML）。
### STEP_1_DONE ###

### 步骤 2: 映射文献缺口 ###
列出 2-3 个最相关的已有研究方向 + 1 个具体的文献缺口（哪个子问题还没人做过）。
### STEP_2_DONE ###

### 步骤 3: 拟定贡献点 (关键节点) ###
列出 3 个贡献点 bullet，每个 bullet 一句话：用什么数据 + 什么方法 + 看到什么结果。
### STEP_3_DONE ###

### 步骤 4: 写出 4 段研究简报 ###
(若用户提供了修改约束，请融合进以下内容)

## 研究简报
**研究问题**: 1 句话，含 4 要素（人群/处理/因变量/因果动词）。
**边际贡献**:
- 数据: ...
- 方法: ...
- 发现: ...
**研究边界**: 排除范围（行业/时期/人群/地区）。
**成功标准**: 可量化阈值（β/p-value/弱 IV 诊断）。
### STEP_4_DONE ###
```

- [ ] **Step 4: Update CHANGELOG**

Append to `Program/prompts/CHANGELOG.md`:

```markdown
## brief v4 (2026-06-04)
- 4 步分步思考 prompt, 含 `### STEP_N_DONE ###` 标记
- 配套 SSE pipeline: 后端按标记切分 token 流 → emit step_done
- 关键节点 = 步骤 3 (拟定贡献点), 用户可继续/修改/重选
- 替代 v3 的「单次 4 段输出」模式
```

- [ ] **Step 5: Run test to verify it passes**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_prompt_v4.py -v`
Expected: `2 passed`

- [ ] **Step 6: Commit**

```bash
git add Program/prompts/brief/v4.md Program/prompts/brief/v4.py Program/prompts/brief/v4.py Program/prompts/CHANGELOG.md tests/wrapper/test_brief_prompt_v4.py
git commit -m "feat(prompts): brief v4 — 4-step SSE-friendly structured prompt"
```

---

## Task 3: Add `BriefEvent` and `BriefResumeRequest` Pydantic types

**Files:**
- Modify: `Product/types/research.py:120-134` (after `ExecuteEvent`)

- [ ] **Step 1: Write the failing test**

Append to `tests/wrapper/test_brief_prompt_v4.py` (renaming to `tests/wrapper/test_brief_types.py`):

Actually, create a new test file `tests/wrapper/test_brief_types.py`:

```python
"""Brief SSE event + resume request Pydantic models."""
from __future__ import annotations

import unittest


class BriefTypesTests(unittest.TestCase):

    def test_bdd_brief_event_step_done_has_summary(self) -> None:
        from Product.types.research import BriefEvent
        evt = BriefEvent(
            event="step_done", step_index=1, summary="这是因果推断问题，用 DID 方法"
        )
        d = evt.model_dump()
        self.assertEqual(d["event"], "step_done")
        self.assertEqual(d["step_index"], 1)
        self.assertIn("summary", d)

    def test_bdd_brief_resume_request_modify_requires_user_input(self) -> None:
        from Product.types.research import BriefResumeRequest
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            BriefResumeRequest(topic="x", action="modify", user_input=None)

    def test_bdd_brief_resume_request_continue_does_not_need_user_input(self) -> None:
        from Product.types.research import BriefResumeRequest
        req = BriefResumeRequest(topic="x", action="continue", user_input=None)
        self.assertEqual(req.action, "continue")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_types.py -v`
Expected: `ImportError: cannot import name 'BriefEvent'`

- [ ] **Step 3: Add types to `Product/types/research.py`**

Modify `Product/types/research.py`. Replace the `ExecuteEvent` class (lines 118-134) — actually add **after** `ExecuteEvent`:

```python
# ============== Brief SSE (Phase 1 step-cards) ==============

from typing import Union  # 加到顶部 import 区


class BriefEvent(BaseModel):
    """SSE event for /api/brief streaming.

    event types: step_start / step_delta / step_done / await_user /
                 final_brief / heartbeat / done / error
    """
    event: Literal[
        "step_start", "step_delta", "step_done", "await_user",
        "final_brief", "heartbeat", "done", "error",
    ]
    step_index: Optional[int] = None
    title: Optional[str] = None
    text: Optional[str] = None
    summary: Optional[str] = None
    markdown: Optional[str] = None
    brief_path: Optional[str] = None
    verdict_passed: Optional[bool] = None
    message: Optional[str] = None


class BriefResumeRequest(BaseModel):
    """Resume /api/brief after await_user checkpoint.

    action:
        "continue" — proceed to step 4
        "modify"   — redo step 3 with user_input as constraint
        "reselect" — restart from step 1
    prior_steps: 客户端缓存的 step 1+2+3 输出 (供 LLM 上下文)
    """
    topic: str
    topic_slug: Optional[str] = None
    action: Literal["continue", "modify", "reselect"]
    user_input: Optional[str] = None
    prior_steps: dict = Field(default_factory=dict)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_types.py -v`
Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add Product/types/research.py tests/wrapper/test_brief_types.py
git commit -m "feat(types): BriefEvent + BriefResumeRequest for SSE pipeline"
```

---

## Task 4: Add `run_brief_stream()` generator (steps 1-3, then await_user)

**Files:**
- Create: `Product/backend/wrapper/brief_stream_service.py`
- Test: `tests/wrapper/test_brief_stream_service.py`

- [ ] **Step 1: Write the failing test**

Create `tests/wrapper/test_brief_stream_service.py`:

```python
"""Brief stream service: run_brief_stream() yields BriefEvent in order.

行为: 模拟 LLM 输出含 3 个 STEP_N_DONE 标记, 验证 generator emit 序列
step_start(1) → step_delta* → step_done(1) → step_start(2) → ... → step_done(3) → await_user.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

# 模拟 LLM 输出: 步骤 1 走一段, 步骤 2 走一段, 步骤 3 走一段
FAKE_LLM_CHUNKS = [
    "### 步骤 1: 分析研究问题 ###\n这是因果推断问题，用 DID 方法。\n### STEP_1_DONE ###\n",
    "### 步骤 2: 映射文献缺口 ###\n已有 A/B/C 研究；缺口：没人用 CFPS 跑过。\n### STEP_2_DONE ###\n",
    "### 步骤 3: 拟定贡献点 (关键节点) ###\n- 数据: CFPS\n- 方法: DID\n- 发现: 显著\n### STEP_3_DONE ###\n",
]


def _fake_stream(**kwargs):
    for chunk in FAKE_LLM_CHUNKS:
        yield chunk


class BriefStreamServiceTests(unittest.TestCase):

    def test_bdd_run_brief_stream_emits_step_events_then_awaits(self) -> None:
        from Product.backend.wrapper import brief_stream_service

        events = []
        with patch.object(
            brief_stream_service, "chat_completion_stream", _fake_stream
        ):
            gen = brief_stream_service.run_brief_stream(topic="工业机器人对工资")
            for evt in gen:
                events.append(evt)
                # 遇到 await_user 就停
                if evt.event == "await_user":
                    break

        event_types = [e.event for e in events]
        # 序列: step_start(1) → step_done(1) → step_start(2) → step_done(2) →
        #       step_start(3) → step_done(3) → await_user
        self.assertEqual(event_types[0], "step_start")
        self.assertIn("step_done", event_types)
        self.assertEqual(event_types[-1], "await_user")
        # step_done 出现 3 次 (步骤 1, 2, 3)
        self.assertEqual(event_types.count("step_done"), 3)
        # step_done(1).summary 是第一句
        step1_done = next(e for e in events if e.event == "step_done" and e.step_index == 1)
        self.assertIn("因果推断", step1_done.summary)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_stream_service.py -v`
Expected: `ModuleNotFoundError: No module named 'Product.backend.wrapper.brief_stream_service'`

- [ ] **Step 3: Implement `run_brief_stream()`**

Create `Product/backend/wrapper/brief_stream_service.py`:

```python
"""L1-brief streaming service (Phase 1 step-cards).

行为契约 (ref: docs/superpowers/specs/2026-06-04-brief-step-cards-design.md):
- run_brief_stream(topic) → Iterator[BriefEvent]
  序列: step_start(1) → step_delta* → step_done(1) → step_start(2) →
        step_delta* → step_done(2) → step_start(3) → step_delta* → step_done(3) →
        await_user
  到 await_user 后停止 yield (resume 走单独函数).

- resume_brief_stream(topic, action, prior_steps, user_input) → Iterator[BriefEvent]
  action="continue": step_start(4) → step_delta* → step_done(4) → final_brief → done
  action="modify":   step_start(3) → ... → step_done(3) → step_start(4) → ... → final_brief → done
  action="reselect": 等价于 run_brief_stream (重置)

关键设计:
- 每 15s yield 一个 heartbeat (防止长 step 流被 proxy 切断)
- 解析 LLM token 流, 按 `### STEP_N_DONE ###` 标记切分
- step_done.summary = 整个 step live text 的第一句 (后端计算)
- 写盘到 Tasks/{slug}/brief.md 发生在 final_brief 时 (而非每步)
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator, Optional

import yaml

from Product.backend.llm_client import chat_completion_stream
from Product.types.research import BriefEvent

# 与 brief_service.py 保持一致
_MODEL = "MiniMax-M3"
_PROVIDER_ID = "minimax"
_STEP_MARKER_RE = re.compile(r"### STEP_(\d+)_DONE ###")
HEARTBEAT_INTERVAL_SEC = 15.0
STEP_TITLES = {
    1: "分析研究问题",
    2: "映射文献缺口",
    3: "拟定贡献点",
    4: "写出研究简报",
}
PROMPT_V4_LOADER: Callable[[], str] = None  # type: ignore[assignment]


def _get_prompt_v4() -> str:
    global PROMPT_V4_LOADER
    if PROMPT_V4_LOADER is None:
        from Program.prompts.brief.v4 import load_prompt_v4
        PROMPT_V4_LOADER = load_prompt_v4
    return PROMPT_V4_LOADER()


def _first_sentence(text: str, max_len: int = 80) -> str:
    """提取第一句作为 summary. 中文按 '。' 切."""
    if not text:
        return ""
    for sep in ("。", ". ", "！", "?"):
        idx = text.find(sep)
        if 0 < idx < max_len:
            return text[: idx + 1].strip()
    return text[:max_len].strip()


def _slugify(topic: str) -> str:
    import re as _re
    return _re.sub(r"[^a-zA-Z0-9]+", "-", topic).strip("-").lower()[:50] or "untitled"


def _write_brief_disk(
    content: str, topic: str, topic_slug: str, tasks_root: Path
) -> Path:
    topic_dir = tasks_root / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    path = topic_dir / "brief.md"
    frontmatter = yaml.safe_dump(
        {
            "topic": topic,
            "topic_slug": topic_slug,
            "generated_by": "brief-llm-sse",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": _MODEL,
            "prompt_version": "v4",
            "upstream": [],
            "downstream_consumers": ["literature.md", "variables.yaml"],
        },
        allow_unicode=True,
        sort_keys=False,
    )
    path.write_text(f"---\n{frontmatter}---\n\n{content}\n", encoding="utf-8")
    return path


def _parse_step_chunks(
    text_so_far: str,
    chunk: str,
    current_step: Optional[int],
    expected_step: int,
) -> tuple[str, bool, Optional[int]]:
    """累积 chunk 进 text_so_far, 检测 expected_step 的 DONE 标记.

    Returns:
        (new_text_so_far, marker_found, next_current_step)
    """
    text_so_far += chunk
    marker = _STEP_MARKER_RE.search(text_so_far)
    if marker and int(marker.group(1)) == expected_step:
        return text_so_far, True, expected_step
    return text_so_far, False, current_step


def run_brief_stream(topic: str) -> Iterator[BriefEvent]:
    """Generate events for steps 1-3, then await_user.

    Yields step_start → step_delta* → step_done in order, holding at
    step 3 with await_user. Resumption is handled by resume_brief_stream.
    """
    prompt = _get_prompt_v4().replace("{topic}", topic)
    messages = [{"role": "user", "content": prompt}]

    last_heartbeat = time.monotonic()
    for step_index in (1, 2, 3):
        yield BriefEvent(
            event="step_start",
            step_index=step_index,
            title=STEP_TITLES[step_index],
        )
        live_text = ""
        done = False
        for chunk in chat_completion_stream(
            messages=messages,
            provider_id=_PROVIDER_ID,
            model=_MODEL,
        ):
            now = time.monotonic()
            if now - last_heartbeat > HEARTBEAT_INTERVAL_SEC:
                yield BriefEvent(event="heartbeat")
                last_heartbeat = now
            yield BriefEvent(event="step_delta", step_index=step_index, text=chunk)
            live_text, done, _ = _parse_step_chunks(
                live_text, chunk, current_step=step_index, expected_step=step_index
            )
            if done:
                # 把这一段也加进 LLM 上下文, 给后面 step 用
                messages.append({"role": "assistant", "content": live_text})
                break
        else:
            # stream 走完都没看到 marker, 把 live_text 当成 step 内容塞回去
            if live_text:
                messages.append({"role": "assistant", "content": live_text})

        yield BriefEvent(
            event="step_done",
            step_index=step_index,
            summary=_first_sentence(live_text),
        )

    yield BriefEvent(event="await_user", step_index=3)


def resume_brief_stream(
    topic: str,
    action: str,
    prior_steps: dict,
    user_input: Optional[str] = None,
    *,
    tasks_root: Optional[Path] = None,
) -> Iterator[BriefEvent]:
    """Resume from await_user checkpoint.

    action="continue": use prior steps as context, generate step 4 → final_brief
    action="modify":   rebuild step 3 prompt with user_input constraint, then step 4
    action="reselect": delegate to run_brief_stream (no context carried)
    """
    if action == "reselect":
        yield from run_brief_stream(topic)
        return

    # 重构 messages: system + 之前 step 1/2/3 (作为 assistant turns)
    base_prompt = _get_prompt_v4()
    messages: list[dict[str, str]] = []
    if action == "modify":
        # 改写步骤 3: 把 user_input 当作高优先级约束 prepend
        modify_constraint = (
            f"用户的额外约束: {user_input}\n请用这个约束重做步骤 3。\n### STEP_3_DONE ###\n"
        )
        # 重建 messages: 只保留 step 1, step 2 (来自 prior_steps), 然后 prepend user constraint + redo step 3
        for s in (1, 2):
            text = prior_steps.get(str(s), "")
            if text:
                messages.append({"role": "assistant", "content": text})
        messages.append({"role": "user", "content": modify_constraint})
    elif action == "continue":
        for s in (1, 2, 3):
            text = prior_steps.get(str(s), "")
            if text:
                messages.append({"role": "assistant", "content": text})

    last_heartbeat = time.monotonic()

    def _heartbeat() -> Optional[BriefEvent]:
        nonlocal last_heartbeat
        if time.monotonic() - last_heartbeat > HEARTBEAT_INTERVAL_SEC:
            last_heartbeat = time.monotonic()
            return BriefEvent(event="heartbeat")
        return None

    if action == "modify":
        # 步骤 3 重做
        yield BriefEvent(event="step_start", step_index=3, title=STEP_TITLES[3])
        live_text = ""
        for chunk in chat_completion_stream(
            messages=messages,
            provider_id=_PROVIDER_ID,
            model=_MODEL,
        ):
            hb = _heartbeat()
            if hb:
                yield hb
            yield BriefEvent(event="step_delta", step_index=3, text=chunk)
            live_text += chunk
            if "### STEP_3_DONE ###" in live_text:
                messages.append({"role": "assistant", "content": live_text})
                break
        yield BriefEvent(
            event="step_done", step_index=3, summary=_first_sentence(live_text)
        )

    # 步骤 4 (写 4 段 markdown)
    yield BriefEvent(event="step_start", step_index=4, title=STEP_TITLES[4])
    live_text = ""
    for chunk in chat_completion_stream(
        messages=messages,
        provider_id=_PROVIDER_ID,
        model=_MODEL,
    ):
        hb = _heartbeat()
        if hb:
            yield hb
        yield BriefEvent(event="step_delta", step_index=4, text=chunk)
        live_text += chunk
        if "### STEP_4_DONE ###" in live_text:
            break

    # 提取 step 4 的 markdown (去掉 marker)
    final_markdown = re.sub(
        r"### STEP_4_DONE ###", "", live_text
    ).strip()

    yield BriefEvent(
        event="step_done",
        step_index=4,
        summary=_first_sentence(final_markdown),
    )

    # 4 段齐全才 verdict_passed=True
    verdict_passed = all(
        f"## {sec}" in final_markdown or f"# {sec}" in final_markdown
        for sec in ("研究问题", "边际贡献", "研究边界", "成功标准")
    )

    # 落盘
    brief_path: Optional[str] = None
    if tasks_root is not None:
        slug = _slugify(topic)
        path = _write_brief_disk(final_markdown, topic, slug, tasks_root)
        brief_path = str(path)

    yield BriefEvent(
        event="final_brief",
        markdown=final_markdown,
        brief_path=brief_path,
        verdict_passed=verdict_passed,
    )
    yield BriefEvent(event="done")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_stream_service.py -v`
Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add Product/backend/wrapper/brief_stream_service.py tests/wrapper/test_brief_stream_service.py
git commit -m "feat(brief-stream): run_brief_stream + resume_brief_stream generators"
```

---

## Task 5: Add BDD test for resume (continue + modify)

**Files:**
- Modify: `tests/wrapper/test_brief_stream_service.py` (add 2 more test cases)

- [ ] **Step 1: Add resume BDD tests**

Append to `tests/wrapper/test_brief_stream_service.py`:

```python
# Modify branch FAKE 输出
FAKE_MODIFY_CHUNKS = [
    "### 步骤 3: 拟定贡献点 (关键节点, 用新约束) ###\n- 数据: 改进版\n- 方法: IV\n### STEP_3_DONE ###\n",
]
# Continue branch step 4 输出
FAKE_STEP4_CHUNKS = [
    "## 研究简报\n**研究问题**: 因果推断题。\n**边际贡献**: x\n**研究边界**: y\n**成功标准**: z\n### STEP_4_DONE ###\n",
]


def _fake_stream_picker(messages, **kwargs):
    """根据 messages 长度选不同 fixture: 短 = step 3 redo, 长 = step 4."""
    n = len(messages)
    if n <= 2:
        # modify 分支: 第一轮是 step 3 redo
        for c in FAKE_MODIFY_CHUNKS:
            yield c
    else:
        # continue / modify step 4
        for c in FAKE_STEP4_CHUNKS:
            yield c


class BriefStreamResumeTests(unittest.TestCase):

    def test_bdd_resume_continue_emits_step4_then_final(self) -> None:
        from Product.backend.wrapper import brief_stream_service
        events = []
        with patch.object(
            brief_stream_service, "chat_completion_stream", _fake_stream_picker
        ):
            for evt in brief_stream_service.resume_brief_stream(
                topic="x",
                action="continue",
                prior_steps={"1": "s1", "2": "s2", "3": "s3"},
            ):
                events.append(evt)
        types = [e.event for e in events]
        self.assertIn("step_start", types)
        self.assertIn("step_done", types)
        self.assertEqual(types[-2], "final_brief")
        self.assertEqual(types[-1], "done")
        # final_brief 含 markdown + verdict
        final = next(e for e in events if e.event == "final_brief")
        self.assertIn("研究问题", final.markdown)
        self.assertTrue(final.verdict_passed)

    def test_bdd_resume_modify_redoes_step3_then_step4(self) -> None:
        from Product.backend.wrapper import brief_stream_service
        events = []
        with patch.object(
            brief_stream_service, "chat_completion_stream", _fake_stream_picker
        ):
            for evt in brief_stream_service.resume_brief_stream(
                topic="x",
                action="modify",
                prior_steps={"1": "s1", "2": "s2"},
                user_input="用 Bartik IV",
            ):
                events.append(evt)
        # modify 分支: step_start(3) → step_done(3) → step_start(4) → step_done(4) → final → done
        types = [e.event for e in events]
        self.assertIn("await_user", [])  # modify 不会 await, 直接出
        self.assertEqual(types[-1], "done")
        # step_done 至少 2 次 (3 和 4)
        self.assertGreaterEqual(types.count("step_done"), 2)
```

- [ ] **Step 2: Run test to verify it passes**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_stream_service.py -v`
Expected: `3 passed` (1 from Task 4 + 2 new)

- [ ] **Step 3: Commit**

```bash
git add tests/wrapper/test_brief_stream_service.py
git commit -m "test(brief-stream): BDD for continue + modify resume actions"
```

---

## Task 6: Convert `/api/brief` to SSE endpoint

**Files:**
- Modify: `Product/api/brief.py` (replace batch endpoint with SSE)

- [ ] **Step 1: Write the failing test**

Create `tests/wrapper/test_brief_sse_wire_in.py`:

```python
"""/api/brief SSE wire-in: 端到端 FastAPI TestClient 流式消费.

行为: POST /api/brief → text/event-stream → 4 step_done events + 1 await_user.
不带 /resume 单独测 (Phase 1 续测).
"""
from __future__ import annotations

import json
import unittest
from unittest.mock import patch


FAKE_CHUNKS = [
    "### 步骤 1: 分析研究问题 ###\n因果推断。\n### STEP_1_DONE ###\n",
    "### 步骤 2: 映射文献缺口 ###\n缺口 X。\n### STEP_2_DONE ###\n",
    "### 步骤 3: 拟定贡献点 (关键节点) ###\n- 数据\n### STEP_3_DONE ###\n",
]


def _fake_stream(**kwargs):
    for c in FAKE_CHUNKS:
        yield c


class BriefSseWireInTests(unittest.TestCase):

    def test_sse_brief_yields_steps_then_await_user(self) -> None:
        from Product.app import app
        from fastapi.testclient import TestClient
        from Product.backend.wrapper import brief_stream_service

        client = TestClient(app)
        events: list[dict] = []
        with patch.object(
            brief_stream_service, "chat_completion_stream", _fake_stream
        ):
            with client.stream(
                "POST", "/api/brief", json={"topic": "test topic"}
            ) as response:
                self.assertEqual(response.status_code, 200)
                self.assertTrue(
                    response.headers.get("content-type", "").startswith(
                        "text/event-stream"
                    )
                )
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        events.append(json.loads(line[6:]))
        types = [e["event"] for e in events]
        # 至少 3 个 step_done + 1 await_user
        self.assertEqual(types.count("step_done"), 3)
        self.assertEqual(types[-1], "await_user")
        # step_done events 都含 step_index
        for e in events:
            if e["event"] == "step_done":
                self.assertIn("step_index", e)
                self.assertIn("summary", e)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_sse_wire_in.py -v`
Expected: SSE stream returns wrong shape (because brief.py still has batch endpoint)

- [ ] **Step 3: Rewrite `Product/api/brief.py` as SSE**

Replace `Product/api/brief.py` entirely:

```python
"""/api/brief + /api/brief/resume SSE endpoints.

L1-brief lane (Phase 1 step-cards): 流式返回 BriefEvent, 在关键节点 (step 3)
await_user 暂停, 用户决策后由 /api/brief/resume 续推 step 4 + final_brief.

事件类型 (ref: docs/superpowers/specs/2026-06-04-brief-step-cards-design.md §1):
- step_start / step_delta / step_done: 单步 LLM token 流
- await_user: 关键节点暂停 (step 3)
- heartbeat: 15s keepalive
- final_brief: step 4 完成 + 落盘 + verdict
- done: 全部结束
- error: 失败 (连接正常关)

失败模式 (DoD #3):
- request 缺字段 → 入口 HTTPException 400
- LLM 中途异常 → try/except 包成 error event
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from Product.backend.wrapper.brief_stream_service import (
    resume_brief_stream,
    run_brief_stream,
)
from Product.types.research import BriefEvent, BriefRequest, BriefResumeRequest

router = APIRouter()

log = logging.getLogger(__name__)

# 仓库根目录: Tasks/ 放在 repo 根
_REPO_ROOT = Path(__file__).resolve().parents[2]
_TASKS_ROOT = _REPO_ROOT / "Tasks"


def _sse_format(evt: BriefEvent) -> str:
    return f"data: {json.dumps(evt.model_dump(), ensure_ascii=False)}\n\n"


@router.post("/api/brief")
def post_brief(req: BriefRequest) -> StreamingResponse:
    """SSE: 跑步骤 1-3, await_user 暂停."""
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="topic is required")

    def event_stream():
        try:
            for evt in run_brief_stream(req.topic):
                yield _sse_format(evt)
        except Exception as exc:  # noqa: BLE001 — endpoint boundary
            log.exception("brief stream failed for topic=%r", req.topic)
            yield _sse_format(
                BriefEvent(
                    event="error", message=f"brief failed: {exc}"
                )
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/api/brief/resume")
def post_brief_resume(req: BriefResumeRequest) -> StreamingResponse:
    """SSE: 从 await_user 继续, 走完 step 4 + final_brief."""
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="topic is required")
    if req.action == "modify" and not (req.user_input and req.user_input.strip()):
        raise HTTPException(
            status_code=400,
            detail="user_input is required when action='modify'",
        )

    def event_stream():
        try:
            for evt in resume_brief_stream(
                topic=req.topic,
                action=req.action,
                prior_steps=req.prior_steps,
                user_input=req.user_input,
                tasks_root=_TASKS_ROOT,
            ):
                yield _sse_format(evt)
        except Exception as exc:  # noqa: BLE001 — endpoint boundary
            log.exception("brief resume failed for topic=%r", req.topic)
            yield _sse_format(
                BriefEvent(
                    event="error", message=f"brief resume failed: {exc}"
                )
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. python -m pytest tests/wrapper/test_brief_sse_wire_in.py -v`
Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add Product/api/brief.py tests/wrapper/test_brief_sse_wire_in.py
git commit -m "feat(api): /api/brief + /api/brief/resume as SSE endpoints"
```

---

## Task 7: Add StepCard component

**Files:**
- Create: `Product/web-react/src/components/StepCard.tsx`

- [ ] **Step 1: Write the component**

Create `Product/web-react/src/components/StepCard.tsx`:

```tsx
import { useState } from "react";

export type StepStatus =
  | "pending"
  | "running"
  | "done"
  | "awaiting"
  | "error";

export interface StepCardProps {
  stepIndex: 1 | 2 | 3 | 4;
  title: string;
  status: StepStatus;
  liveText?: string;
  summary?: string;
  // 仅 step 3 awaiting 时用
  onContinue?: () => void;
  onModify?: (userInput: string) => void;
  onReselect?: () => void;
}

/**
 * StepCard — 单步研究日志卡片.
 *
 * 行为: 状态机
 *   pending  → running  → done
 *   running  → error
 *   done     → (用户看 summary)
 *   awaiting → (用户点按钮) → done
 */
export function StepCard({
  stepIndex,
  title,
  status,
  liveText = "",
  summary = "",
  onContinue,
  onModify,
  onReselect,
}: StepCardProps) {
  const [showModifyInput, setShowModifyInput] = useState(false);
  const [userInput, setUserInput] = useState("");

  const isAwaiting = status === "awaiting" && stepIndex === 3;
  const showFullText = status === "running" || status === "done" || status === "error";

  return (
    <div
      className={`step-card step-card--${status}`}
      data-testid={`step-card-${stepIndex}`}
      data-status={status}
    >
      <header className="step-card__head">
        <span className="step-card__index">步骤 {stepIndex}</span>
        <h3 className="step-card__title">{title}</h3>
        <span className="step-card__status">
          {status === "pending" && "⏳ 等待"}
          {status === "running" && "✍️ 思考中…"}
          {status === "done" && "✓ 完成"}
          {status === "awaiting" && "🛑 等你决策"}
          {status === "error" && "❌ 失败"}
        </span>
      </header>

      {showFullText && (
        <div className="step-card__body" data-testid={`step-card-${stepIndex}-body`}>
          {status === "running" ? (
            <pre className="step-card__live">{liveText}<span className="caret" /></pre>
          ) : (
            <p className="step-card__summary">{summary}</p>
          )}
        </div>
      )}

      {isAwaiting && (
        <div className="step-card__actions" data-testid="step-3-actions">
          {!showModifyInput && (
            <>
              <button
                type="button"
                className="btn btn--primary"
                onClick={onContinue}
                data-testid="step-3-continue"
              >
                ✓ 继续
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => setShowModifyInput(true)}
                data-testid="step-3-modify"
              >
                ✎ 修改
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={onReselect}
                data-testid="step-3-reselect"
              >
                ✗ 重选
              </button>
            </>
          )}
          {showModifyInput && (
            <div className="step-card__modify">
              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="告诉 LLM 怎么调整这 3 个贡献点…"
                rows={3}
                data-testid="step-3-modify-input"
              />
              <div className="step-card__modify-actions">
                <button
                  type="button"
                  className="btn btn--primary"
                  disabled={!userInput.trim()}
                  onClick={() => onModify?.(userInput.trim())}
                  data-testid="step-3-modify-submit"
                >
                  提交修改
                </button>
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => {
                    setShowModifyInput(false);
                    setUserInput("");
                  }}
                >
                  取消
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default StepCard;
```

- [ ] **Step 2: Type-check**

Run: `cd Product/web-react && npx tsc --noEmit 2>&1 | head -20`
Expected: no errors from StepCard.tsx

- [ ] **Step 3: Commit**

```bash
git add Product/web-react/src/components/StepCard.tsx
git commit -m "feat(web): StepCard component for brief tab step-cards"
```

---

## Task 8: Rewrite BriefPanel to consume SSE

**Files:**
- Modify: `Product/web-react/src/components/BriefPanel.tsx` (full rewrite)

- [ ] **Step 1: Rewrite BriefPanel**

Replace `Product/web-react/src/components/BriefPanel.tsx` entirely:

```tsx
import { useCallback, useRef, useState } from "react";
import { StepCard, type StepStatus } from "./StepCard";

export interface BriefResult {
  markdown: string;
  path: string;
}

export interface BriefPanelProps {
  topic: string;
  onComplete?: (brief: BriefResult) => void;
}

interface StepState {
  status: StepStatus;
  title: string;
  liveText: string;
  summary: string;
}

type Phase = "idle" | "running" | "awaiting" | "completed" | "error";

const STEP_TITLES: Record<1 | 2 | 3 | 4, string> = {
  1: "分析研究问题",
  2: "映射文献缺口",
  3: "拟定贡献点",
  4: "写出研究简报",
};

const INITIAL_STEPS: Record<1 | 2 | 3 | 4, StepState> = {
  1: { status: "pending", title: STEP_TITLES[1], liveText: "", summary: "" },
  2: { status: "pending", title: STEP_TITLES[2], liveText: "", summary: "" },
  3: { status: "pending", title: STEP_TITLES[3], liveText: "", summary: "" },
  4: { status: "pending", title: STEP_TITLES[4], liveText: "", summary: "" },
};

interface BriefSseEvent {
  event: string;
  step_index?: number;
  title?: string;
  text?: string;
  summary?: string;
  markdown?: string;
  brief_path?: string;
  verdict_passed?: boolean;
  message?: string;
}

/**
 * BriefPanel — 任务书 LLM 扩写面板 (L1 brief tab, Phase 1 step-cards).
 *
 * 行为契约 (ref: docs/superpowers/specs/2026-06-04-brief-step-cards-design.md):
 * - 点 "开始研究" → POST /api/brief SSE → 4 步流式播放
 * - 步骤 3 抵达时显示 3 个按钮 (继续/修改/重选)
 * - 用户决策 → POST /api/brief/resume SSE → 步骤 4 → final_brief → onComplete
 * - 任何 SSE 错误显示重试按钮
 */
export function BriefPanel({ topic, onComplete }: BriefPanelProps) {
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState(INITIAL_STEPS);
  const [finalBrief, setFinalBrief] = useState<{ markdown: string; path: string; verdict: boolean } | null>(null);
  // 保存 step 1-3 输出, 供 /resume 用
  const priorStepsRef = useRef<Record<string, string>>({});
  const abortRef = useRef<AbortController | null>(null);

  const updateStep = useCallback(
    (idx: 1 | 2 | 3 | 4, patch: Partial<StepState>) => {
      setSteps((prev) => ({ ...prev, [idx]: { ...prev[idx], ...patch } }));
    },
    []
  );

  const consumeSse = useCallback(
    async (url: string, body: object): Promise<BriefSseEvent[]> => {
      const collected: BriefSseEvent[] = [];
      const ctrl = new AbortController();
      abortRef.current = ctrl;
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: ctrl.signal,
      });
      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        // 切 SSE event (空行分隔)
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";
        for (const part of parts) {
          const dataLine = part.split("\n").find((l) => l.startsWith("data: "));
          if (!dataLine) continue;
          try {
            const evt: BriefSseEvent = JSON.parse(dataLine.slice(6));
            collected.push(evt);
            applyEvent(evt);
          } catch {
            // ignore malformed
          }
        }
      }
      return collected;
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const applyEvent = useCallback(
    (evt: BriefSseEvent) => {
      switch (evt.event) {
        case "step_start": {
          const idx = evt.step_index as 1 | 2 | 3 | 4;
          updateStep(idx, { status: "running", title: evt.title || STEP_TITLES[idx], liveText: "" });
          break;
        }
        case "step_delta": {
          const idx = evt.step_index as 1 | 2 | 3 | 4;
          setSteps((prev) => ({
            ...prev,
            [idx]: { ...prev[idx], liveText: prev[idx].liveText + (evt.text || "") },
          }));
          break;
        }
        case "step_done": {
          const idx = evt.step_index as 1 | 2 | 3 | 4;
          updateStep(idx, { status: "done", summary: evt.summary || "" });
          // 缓存到 priorSteps (供 /resume)
          setSteps((prev) => {
            priorStepsRef.current[String(idx)] = prev[idx].liveText;
            return prev;
          });
          break;
        }
        case "await_user": {
          const idx = evt.step_index as 1 | 2 | 3 | 4;
          updateStep(idx, { status: "awaiting" });
          setPhase("awaiting");
          break;
        }
        case "final_brief": {
          setFinalBrief({
            markdown: evt.markdown || "",
            path: evt.brief_path || "",
            verdict: evt.verdict_passed || false,
          });
          break;
        }
        case "done": {
          setPhase("completed");
          break;
        }
        case "error": {
          setError(evt.message || "未知错误");
          setPhase("error");
          break;
        }
        default:
          // heartbeat 等忽略
          break;
      }
    },
    [updateStep]
  );

  const handleStart = useCallback(async () => {
    setPhase("running");
    setError(null);
    setSteps(INITIAL_STEPS);
    setFinalBrief(null);
    priorStepsRef.current = {};
    try {
      await consumeSse("/api/brief", { topic });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setPhase("error");
    }
  }, [topic, consumeSse]);

  const handleResume = useCallback(
    async (action: "continue" | "modify" | "reselect", userInput?: string) => {
      setPhase("running");
      try {
        const events = await consumeSse("/api/brief/resume", {
          topic,
          action,
          user_input: userInput,
          prior_steps: priorStepsRef.current,
        });
        // 检查 final_brief
        const final = events.find((e) => e.event === "final_brief");
        if (final && final.verdict_passed && onComplete) {
          onComplete({ markdown: final.markdown || "", path: final.brief_path || "" });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setPhase("error");
      }
    },
    [topic, consumeSse, onComplete]
  );

  return (
    <section aria-label="任务书扩写" className="task-brief">
      <div className="task-brief__main">
        <div className="task-brief__lead">
          <span className="eyebrow">第 1 阶段：研究简报</span>
          <h2>生成研究简报</h2>
          <p>研究题目：{topic || "（未填）"}</p>
        </div>

        <div className="task-brief__confirm-actions">
          <button
            type="button"
            className="btn btn--primary"
            onClick={handleStart}
            disabled={phase === "running" || phase === "awaiting" || !topic.trim()}
            data-testid="brief-start"
          >
            {phase === "running" ? "研究中…" : phase === "awaiting" ? "等你的决策" : "开始研究"}
          </button>
        </div>

        {phase === "error" && error && (
          <div className="task-brief__error" role="alert" data-testid="brief-error">
            <strong>错误：</strong> {error}
            <button type="button" className="btn btn--ghost" onClick={handleStart}>
              重试
            </button>
          </div>
        )}

        <div className="step-cards" data-testid="step-cards">
          {([1, 2, 3, 4] as const).map((idx) => (
            <StepCard
              key={idx}
              stepIndex={idx}
              title={steps[idx].title}
              status={steps[idx].status}
              liveText={steps[idx].liveText}
              summary={steps[idx].summary}
              onContinue={() => handleResume("continue")}
              onModify={(userInput) => handleResume("modify", userInput)}
              onReselect={() => handleResume("reselect")}
            />
          ))}
        </div>

        {finalBrief && (
          <div className="task-brief__result" data-testid="brief-result">
            <div className="task-brief__verdict">
              <span
                className={
                  finalBrief.verdict
                    ? "checklist-status-badge checklist-status-badge--ready"
                    : "checklist-status-badge checklist-status-badge--pending"
                }
                data-testid="brief-verdict"
              >
                {finalBrief.verdict ? "verdict passed" : "verdict failed"}
              </span>
              <span className="task-brief__path">文件：{finalBrief.path}</span>
            </div>
            <pre
              className="task-brief__markdown"
              data-testid="brief-markdown"
            >
              {finalBrief.markdown}
            </pre>
          </div>
        )}
      </div>
    </section>
  );
}

export default BriefPanel;
```

- [ ] **Step 2: Type-check**

Run: `cd Product/web-react && npx tsc --noEmit 2>&1 | head -30`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add Product/web-react/src/components/BriefPanel.tsx
git commit -m "feat(web): BriefPanel rewrite — SSE consumption + step-cards"
```

---

## Task 9: Add Playwright e2e test for step-cards flow

**Files:**
- Create: `Product/web-react/e2e/brief-step-cards.spec.ts`

- [ ] **Step 1: Write the e2e test**

Create `Product/web-react/e2e/brief-step-cards.spec.ts`:

```typescript
// Brief tab step-cards e2e: 点开始 → 看 4 个 card → step 3 点继续 → 看 final_brief
//
// 跑法:
//   1. 后端: PYTHONPATH=. python -m uvicorn Product.app:app --port 8765 (with mock)
//   2. 前端: cd Product/web-react && npm run dev -- --port 5173
//   3. e2e:  npx playwright test e2e/brief-step-cards.spec.ts
//
// 用例默认 mock LLM 输出 (走 FastAPI 在 test 模式注入 fixture).
// 若启用了真 LLM, 此测试需 ~30s 完成.

import { test, expect } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL ?? "http://127.0.0.1:5173";

test.describe("Brief tab step-cards (Phase 1)", () => {
  test("happy path — generate, await step 3, click 继续, see final_brief", async ({ page }) => {
    await page.goto(BASE_URL);
    // 输入 topic
    const topicInput = page.locator('input[name="topic"], textarea[name="topic"]').first();
    await topicInput.fill("工业机器人对城市制造业蓝领工资的影响——基于 CFPS 2010-2022");

    // 点开始
    await page.getByTestId("brief-start").click();

    // 等步骤 1, 2 done
    await expect(page.getByTestId("step-card-1")).toHaveAttribute("data-status", "done", { timeout: 30_000 });
    await expect(page.getByTestId("step-card-2")).toHaveAttribute("data-status", "done", { timeout: 30_000 });

    // 等步骤 3 抵达 awaiting
    await expect(page.getByTestId("step-card-3")).toHaveAttribute("data-status", "awaiting", { timeout: 30_000 });

    // 看到 3 个按钮
    await expect(page.getByTestId("step-3-continue")).toBeVisible();
    await expect(page.getByTestId("step-3-modify")).toBeVisible();
    await expect(page.getByTestId("step-3-reselect")).toBeVisible();

    // 点继续
    await page.getByTestId("step-3-continue").click();

    // 等步骤 4 done
    await expect(page.getByTestId("step-card-4")).toHaveAttribute("data-status", "done", { timeout: 30_000 });

    // final_brief 显示
    await expect(page.getByTestId("brief-result")).toBeVisible({ timeout: 30_000 });
    await expect(page.getByTestId("brief-verdict")).toContainText(/passed|failed/);
    await expect(page.getByTestId("brief-markdown")).toContainText("研究问题");
  });
});
```

- [ ] **Step 2: Verify the e2e file compiles**

Run: `cd Product/web-react && npx tsc --noEmit 2>&1 | head -10`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add Product/web-react/e2e/brief-step-cards.spec.ts
git commit -m "test(e2e): brief step-cards happy path with await step 3 + continue"
```

---

## Task 10: Final cross-task validation

**Files:** None new. Just verify.

- [ ] **Step 1: Run all tests**

Run:
```bash
PYTHONPATH=. python -m pytest tests/wrapper/ -v 2>&1 | tail -30
```
Expected: All wrapper tests pass (brief_service, brief_stream_service, brief_sse_wire_in, brief_prompt_v4, brief_types, llm_client_stream, plus existing ones).

- [ ] **Step 2: Type-check the frontend**

Run:
```bash
cd Product/web-react && npx tsc --noEmit 2>&1 | tail -10
```
Expected: no errors

- [ ] **Step 3: Manual smoke (optional but recommended)**

```bash
# 1. 启动后端 (用真 LLM key)
PYTHONPATH=. MINIMAX_API_KEY=$MINIMAX_API_KEY python -m uvicorn Product.app:app --port 8765 &

# 2. curl 看 SSE 流
curl -N -X POST http://127.0.0.1:8765/api/brief \
  -H 'Content-Type: application/json' \
  -d '{"topic": "工业机器人对工资的影响"}'

# 期望看到:
#   data: {"event":"step_start",...}
#   data: {"event":"step_delta",...}
#   ...
#   data: {"event":"await_user",...}
```

If you got 4 step_done events + 1 await_user with real M3, manual smoke passes.

- [ ] **Step 4: Final commit (if any drift)**

```bash
git status
# 若有未提交改动:
# git add <files> && git commit -m "chore: address review feedback"
```

---

## Self-Review

**Spec coverage check:**
- ✅ SSE event protocol (spec §1) → Task 1 (stream) + Task 3 (types) + Task 4 (generator) + Task 6 (endpoint)
- ✅ Backend flow (spec §2) → Task 4 (run_brief_stream) + Task 5 (resume_brief_stream) + Task 6 (endpoints)
- ✅ 4-step template (spec §3) → Task 2 (v4.md) + Task 4 (STEP_TITLES)
- ✅ Prompt design with markers (spec §4) → Task 2 (v4.md content)
- ✅ Frontend StepCard (spec §5) → Task 7
- ✅ State machine (spec §6) → Task 8 (applyEvent switch + priorStepsRef)
- ✅ Error handling (spec §7) → Task 1 (LLMError raises) + Task 6 (try/except → error event) + Task 8 (catch + retry button)
- ✅ Testing (spec §8) → Task 1 + Task 2 + Task 3 + Task 4 + Task 5 + Task 6 + Task 9
- ✅ Migration / compat (spec §9) → /api/brief same shape but SSE; old batch endpoint replaced (Phase 2 deprecation note in spec)
- ✅ Heartbeat → Task 4 (`_heartbeat` helper)
- ✅ Marker detection → Task 4 (`_STEP_MARKER_RE` + `_parse_step_chunks`)

**Placeholder scan:** No "TBD" / "TODO" / "implement later" anywhere. All step code is complete and runnable.

**Type consistency check:**
- `BriefEvent.event` literal types match between `Product/types/research.py` and Python side / TS side
- `step_index` is `int` in Pydantic and `1|2|3|4` union in TS — Python side accepts any int, TS narrows
- `prior_steps` is `dict` in Pydantic, `Record<string, string>` in TS ref (`priorStepsRef`)
- `action` literal "continue" | "modify" | "reselect" consistent across Pydantic, Python, TS, and backend dispatch

**Risk items already mitigated in plan:**
- LLM emits marker in unexpected place → strict regex match against expected step number (Task 4)
- User double-clicks button → button disabled when phase=running/awaiting (Task 8)
- Slow LLM timeout → heartbeat every 15s (Task 4)

**Known limitations (out of scope per spec §10):**
- Per-step regenerate (only reselect = full restart)
- Multi-round dialog inside a step
- Server-side resume state held 5 min — we use client-driven state (simpler, works for normal use)
