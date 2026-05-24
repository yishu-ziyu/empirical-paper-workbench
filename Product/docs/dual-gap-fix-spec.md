# Dual-Gap Fix SPEC — 体验缺口 + 能力缺口并行修复

## 概述

本 SPEC 覆盖两个并行缺口的修复，交给 Codex 按文件逐个实现。

| 缺口 | 编号 | 问题描述 | 影响 |
|------|------|----------|------|
| 体验缺口 | A1 | Journey 页面没有启动执行入口，SSE 只在 empirical-execution 视图连接 | 用户确认选题后看不到 Agent 执行，8 阶段流水线无法实时更新 |
| 体验缺口 | A2 | `_resolve_project_id()` 用中文 title 生成 project_id，与 registry 中实际 ID 不一致 | KeyError，orchestrator 无法找到项目 |
| 能力缺口 | B1 | `chat_completion()` 只返回文本，不返回 token 使用量 | cost_service 的 LLM 成本记录永远是 0 |
| 能力缺口 | B2 | `_call_llm_for_modeling()` 没有把 token 数据传给 `finish_cost_event()` | LLM 调用在成本看板中没有真实成本 |
| 能力缺口 | B3 | 成本面板前端只显示 wall_seconds，不显示 input_tokens/output_tokens/estimated_usd | 用户无法感知 LLM 消耗 |

---

## 缺口 A1：Journey 视图 SSE 连接打通

### 当前行为

- `confirmResearchTopic()`（app.js:2960）只保存选题到后端，不启动任何 run
- `connectRunStream()` 只在 `createObservableRun()`（2549）和 `createFullRunFromPlan()`（2564）中调用
- Journey 页面 actions 区域有一个 "查看 Agent 实时输出" 按钮（3097），但只在 `isStreaming` 为 true 时显示
- 事件委托（6316）只处理了 `view-output`/`refresh`/`checkpoint`，没有 `primary` 动作

### 目标行为

用户在 Journey 页面确认选题后，可以直接点击"启动完整执行"按钮，系统自动：
1. 调用 `createFullRunFromPlan()` 启动 run
2. `createFullRunFromPlan()` 内部调用 `connectRunStream()` 建立 SSE
3. Journey 页面检测到 `isStreaming=true`，显示"查看 Agent 实时输出"按钮
4. SSE 事件到来时，`updateJourneyStageStatus()` 实时更新 Journey 节点状态

### 修改清单

#### A1-1: `Product/web/assets/app.js` — Journey actions 添加启动执行按钮

**位置**: `renderJourney()` 函数内 actions 渲染逻辑（约 3095-3101 行）

**当前代码**:
```javascript
const isStreaming = state.sseConnection.connected && state.sseConnection.runId;
actions.innerHTML = `
  ${isStreaming ? `<button class="primary-button" data-journey-action="view-output">查看 Agent 实时输出</button>` : ""}
  ${primaryAction ? `<button class="primary-button" data-journey-action="primary">${escapeHtml(productTermLabel(primaryAction.action || "继续"))}</button>` : ""}
  <button class="ghost-button" data-journey-action="refresh">刷新状态</button>
  ${currentStageData?.status === "pending" ? `<button class="ghost-button" data-journey-action="checkpoint" style="color: #e67e22; border-color: #e67e22;">确认检查点</button>` : ""}
`;
```

**修改为**:
```javascript
const isStreaming = state.sseConnection.connected && state.sseConnection.runId;
const canStartRun = !isStreaming && state.researchTopicConfirmed;
actions.innerHTML = `
  ${isStreaming ? `<button class="primary-button" data-journey-action="view-output">查看 Agent 实时输出</button>` : ""}
  ${canStartRun ? `<button class="primary-button" data-journey-action="start-run">启动完整执行</button>` : ""}
  ${primaryAction && !canStartRun && !isStreaming ? `<button class="primary-button" data-journey-action="primary">${escapeHtml(productTermLabel(primaryAction.action || "继续"))}</button>` : ""}
  <button class="ghost-button" data-journey-action="refresh">刷新状态</button>
  ${currentStageData?.status === "pending" ? `<button class="ghost-button" data-journey-action="checkpoint" style="color: #e67e22; border-color: #e67e22;">确认检查点</button>` : ""}
`;
```

#### A1-2: `Product/web/assets/app.js` — 事件委托添加 start-run 和 primary 处理

**位置**: Journey 按钮点击事件委托（约 6316-6329 行）

**当前代码**:
```javascript
const journeyButton = target.closest("[data-journey-action]");
if (!journeyButton) return;
switch (journeyButton.dataset.journeyAction) {
  case "view-output":
    state.agentOutput.visible = true;
    renderAgentOutputPanel();
    break;
  case "refresh":
    void loadV2Data("journey");
    break;
  case "checkpoint":
    void pollCheckpoint();
    break;
}
```

**在 `case "checkpoint":` 后面追加**:
```javascript
  case "start-run":
    void createFullRunFromPlan();
    break;
  case "primary":
    // Primary action from backend next_steps; if it looks like a run action, start execution
    if (primaryAction?.action?.includes("run") || primaryAction?.action?.includes("执行")) {
      void createFullRunFromPlan();
    } else {
      void loadV2Data("journey");
    }
    break;
```

注意：需要在 `renderJourney()` 的作用域内让 `primaryAction` 变量在事件委托中可访问。当前 `primaryAction` 是在 `renderJourney()` 内部定义的局部变量。有两种处理方式：

**方式一（推荐）**: 将 `primaryAction` 存入 `state`:
在 `renderJourney()` 中（约 3093 行）:
```javascript
const primaryAction = nextSteps[0];
state.journeyPrimaryAction = primaryAction; // 新增
```

然后在事件委托中:
```javascript
  case "primary":
    const pa = state.journeyPrimaryAction;
    if (pa?.action?.includes("run") || pa?.action?.includes("执行")) {
      void createFullRunFromPlan();
    } else {
      void loadV2Data("journey");
    }
    break;
```

---

## 缺口 A2：`_resolve_project_id()` KeyError 修复

### 根因分析

`registry.py:normalize_project_record()` 在 project 没有 id 时生成：`f"proj_{slug.replace('-', '_')}"`。

`orchestrator.py:_resolve_project_id()` 生成：`f"proj_{title.replace(' ', '_').replace('-', '_').lower()[:30]}"`。

当 title 是中文（如"培训是否影响工资"）时，两个生成逻辑产生不同的 id，导致 `get_project_by_id()` KeyError。

### 修复方案

`_resolve_project_id()` 应该优先使用 profile 中已有的 id 字段（因为 profile 就是来自 registry 的 project 记录），而不是重新从 title 生成。

#### A2-1: `Product/backend/orchestrator.py` — 修复 `_resolve_project_id`

**位置**: 第 136-144 行

**当前代码**:
```python
def _resolve_project_id(profile: dict[str, Any]) -> str:
    """Derive project_id from profile or fall back to registry default."""
    title = profile.get("title", "")
    slug = profile.get("slug", "")
    if slug:
        return f"proj_{slug.replace('-', '_')}"
    if title:
        return f"proj_{title.replace(' ', '_').replace('-', '_').lower()[:30]}"
    return "proj_undergraduate_thesis"
```

**修改为**:
```python
def _resolve_project_id(profile: dict[str, Any]) -> str:
    """Derive project_id from profile or fall back to registry default."""
    # Prefer existing id from registry (avoids mismatch with normalize_project_record)
    existing_id = profile.get("id")
    if existing_id:
        return existing_id
    slug = profile.get("slug", "")
    if slug:
        return f"proj_{slug.replace('-', '_')}"
    title = profile.get("title", "")
    if title:
        # Slugify to handle CJK characters safely
        safe_title = re.sub(r"[^\w\s-]", "", title).strip().lower()[:30]
        safe_title = re.sub(r"[-\s]+", "_", safe_title)
        if safe_title:
            return f"proj_{safe_title}"
    return "proj_undergraduate_thesis"
```

同时需要检查第 1371 行的 `project_id=profile.get("title") or project_root.name` 是否也需要修正。该处是写入 manifest，不是查找，但为了 consistency 建议改为：
```python
project_id=_resolve_project_id(profile),
```

---

## 缺口 B1：LLM Token 使用量返回

### 当前行为

- `_call_openai_compatible()` 返回 `str`
- `_call_anthropic_compatible()` 返回 `str`
- `chat_completion()` 返回 `str`
- `chat_completion_with_fallback()` 返回 `(text, metadata)`，但 metadata 不含 usage

### 目标行为

所有 LLM 调用链返回 token 使用量，格式统一为 `{"input_tokens": int, "output_tokens": int}`。

### 修改清单

#### B1-1: `Product/backend/llm_client.py` — `_call_openai_compatible` 返回 usage

**位置**: 约第 200-242 行

**修改 `_call_openai_compatible` 的返回逻辑**:

当前最后两行:
```python
    return _extract_openai_text(parsed)
```

修改为返回 tuple:
```python
    text = _extract_openai_text(parsed)
    usage = parsed.get("usage", {})
    return text, {
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
    }
```

#### B1-2: `Product/backend/llm_client.py` — `_call_anthropic_compatible` 返回 usage

**位置**: 约第 245-294 行

当前最后:
```python
    return _extract_anthropic_text(parsed)
```

修改为:
```python
    text = _extract_anthropic_text(parsed)
    usage = parsed.get("usage", {})
    return text, {
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
    }
```

#### B1-3: `Product/backend/llm_client.py` — `chat_completion` 返回 usage

**位置**: 约第 300-367 行

**修改函数签名和返回**:

当前签名:
```python
def chat_completion(...) -> str:
```

改为:
```python
def chat_completion(...) -> tuple[str, dict[str, int]]:
```

在函数 docstring 中更新 Returns:
```
    Returns:
        (generated_text, usage) where usage contains input_tokens and output_tokens.
```

修改两个 return 分支:

openai-compatible 分支（约 345-352 行）:
```python
        text, usage = _call_openai_compatible(...)
        return text, usage
```

anthropic-compatible 分支（约 354-365 行）:
```python
        text, usage = _call_anthropic_compatible(...)
        return text, usage
```

#### B1-4: `Product/backend/llm_client.py` — `chat_completion_with_fallback` 传递 usage

**位置**: 约第 370-430 行

修改 try 块内（约 402-416 行）:

当前:
```python
        try:
            text = chat_completion(...)
            preset = resolve_provider(provider_id)
            metadata = {
                "provider_id": provider_id,
                "provider_name": preset.name,
                "model": model or preset.default_model,
                "api_type": preset.api_type,
            }
            return text, metadata
```

改为:
```python
        try:
            text, usage = chat_completion(...)
            preset = resolve_provider(provider_id)
            metadata = {
                "provider_id": provider_id,
                "provider_name": preset.name,
                "model": model or preset.default_model,
                "api_type": preset.api_type,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
            }
            return text, metadata
```

---

## 缺口 B2：Orchestrator 传递 Token 到 Cost Service

### 当前行为

`_call_llm_for_modeling()`（orchestrator.py:439-473）调用 LLM 后:
```python
llm_report, llm_metadata = _call_llm_for_modeling(llm_prompt)
```

然后在 finally 块中（约 1089-1097 行）:
```python
cost_service.finish_cost_event(
    ...,
    provider=llm_metadata.get("provider_id", "unknown") if "llm_metadata" in dir() else "unknown",
    model=llm_metadata.get("model", "unknown") if "llm_metadata" in dir() else "unknown",
)
```

注意：这里没有传 `input_tokens`、`output_tokens`、`estimated_usd`。

### 目标行为

从 `llm_metadata` 中提取 `input_tokens` 和 `output_tokens`，传给 `finish_cost_event`。同时按简单规则估算 USD 成本（不同 provider 不同）。

### 修改清单

#### B2-1: `Product/backend/orchestrator.py` — `_call_llm_for_modeling` 后传递 token

**位置**: `_stage_04_modeling()` 内 finally 块（约 1089-1097 行）

**当前代码**:
```python
        finally:
            cost_service.finish_cost_event(
                project_root=project_root,
                event_id=llm_event_id,
                status=llm_status,
                wall_seconds=round(time.perf_counter() - llm_start_ts, 3),
                provider=llm_metadata.get("provider_id", "unknown") if "llm_metadata" in dir() else "unknown",
                model=llm_metadata.get("model", "unknown") if "llm_metadata" in dir() else "unknown",
            )
```

**修改为**:
```python
        finally:
            input_tokens = llm_metadata.get("input_tokens", 0) if "llm_metadata" in dir() else 0
            output_tokens = llm_metadata.get("output_tokens", 0) if "llm_metadata" in dir() else 0
            estimated_usd = _estimate_llm_cost(
                llm_metadata.get("provider_id", ""),
                llm_metadata.get("model", ""),
                input_tokens,
                output_tokens,
            ) if "llm_metadata" in dir() else 0.0
            cost_service.finish_cost_event(
                project_root=project_root,
                event_id=llm_event_id,
                status=llm_status,
                wall_seconds=round(time.perf_counter() - llm_start_ts, 3),
                provider=llm_metadata.get("provider_id", "unknown") if "llm_metadata" in dir() else "unknown",
                model=llm_metadata.get("model", "unknown") if "llm_metadata" in dir() else "unknown",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_usd=estimated_usd,
            )
```

#### B2-2: `Product/backend/orchestrator.py` — 添加 `_estimate_llm_cost` 辅助函数

**位置**: 在 `_resolve_agent_id()` 函数之后添加（约第 165 行之后）

```python
def _estimate_llm_cost(provider_id: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate LLM cost in USD based on provider and token counts."""
    # Pricing per 1M tokens (rough estimates, update as needed)
    pricing = {
        "openrouter": {
            "anthropic/claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
            "anthropic/claude-opus-4-6": {"input": 15.0, "output": 75.0},
            "anthropic/claude-haiku-4-5-20251001": {"input": 0.25, "output": 1.25},
            "openai/gpt-4o": {"input": 2.5, "output": 10.0},
            "openai/gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "default": {"input": 3.0, "output": 15.0},
        },
        "kimi-code": {"default": {"input": 0.5, "output": 2.0}},
        "kimi-code-anthropic-token": {"default": {"input": 0.5, "output": 2.0}},
        "moonshot-kimi": {"default": {"input": 0.5, "output": 2.0}},
    }
    provider_pricing = pricing.get(provider_id, pricing["openrouter"])
    model_pricing = provider_pricing.get(model, provider_pricing.get("default", {"input": 3.0, "output": 15.0}))
    input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
    return round(input_cost + output_cost, 6)
```

---

## 缺口 B3：成本面板显示真实 LLM 成本

### 当前行为

前端成本面板（governance 面板的 Cost tab）只显示 `wall_seconds` 和事件数量，不显示 `input_tokens`、`output_tokens`、`estimated_usd`。

### 目标行为

成本面板显示每个事件的：
- wall_seconds
- input_tokens / output_tokens
- estimated_usd
- 按 provider/model 汇总

### 修改清单

#### B3-1: `Product/web/assets/app.js` — `renderGovernanceCosts` 增强

**位置**: `renderGovernanceCosts()` 函数内（搜索该函数名定位）

当前该函数大概渲染一个成本事件列表。需要增强为显示 token 和 USD。

在事件列表渲染中，找到显示每个事件的 HTML 模板，添加 token 和 USD 信息。

假设当前事件行渲染类似:
```javascript
`<div class="cost-event">${event.actor_id} — ${event.wall_seconds}s</div>`
```

改为:
```javascript
const tokenInfo = event.input_tokens || event.output_tokens
  ? `<span class="cost-tokens">${event.input_tokens || 0} → ${event.output_tokens || 0} tokens</span>`
  : "";
const usdInfo = event.estimated_usd
  ? `<span class="cost-usd">$${event.estimated_usd.toFixed(4)}</span>`
  : "";
`<div class="cost-event">
  <span class="cost-actor">${escapeHtml(event.actor_id)}</span>
  <span class="cost-time">${event.wall_seconds}s</span>
  ${tokenInfo}
  ${usdInfo}
  <span class="cost-cap">${escapeHtml(event.capability_id)}</span>
</div>`
```

#### B3-2: `Product/web/assets/app.js` — 成本汇总卡片增强

在 summary 渲染区域，添加总 token 和总 USD:

```javascript
const totalTokens = events.reduce((sum, e) => sum + (e.input_tokens || 0) + (e.output_tokens || 0), 0);
const totalUsd = events.reduce((sum, e) => sum + (e.estimated_usd || 0), 0);
```

在汇总卡片 HTML 中插入:
```javascript
`<div class="governance-stat">
  <div class="governance-stat-value">${totalTokens.toLocaleString()}</div>
  <div class="governance-stat-label">总 Tokens</div>
</div>
<div class="governance-stat">
  <div class="governance-stat-value">$${totalUsd.toFixed(4)}</div>
  <div class="governance-stat-label">预估成本</div>
</div>`
```

#### B3-3: `Product/web/assets/styles.css` — 成本面板样式

在 governance 相关样式区域添加:

```css
.cost-event {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
}
.cost-actor {
  font-weight: 600;
  min-width: 120px;
}
.cost-time {
  color: var(--muted);
  min-width: 60px;
}
.cost-tokens {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: var(--font-mono);
}
.cost-usd {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-mono);
}
.cost-cap {
  color: var(--muted);
  font-size: 12px;
  margin-left: auto;
}
```

---

## 修改文件汇总

| # | 文件 | 修改类型 | 修改内容 |
|---|------|----------|----------|
| A1-1 | `Product/web/assets/app.js` | 修改 | renderJourney actions 添加 start-run 按钮 |
| A1-2 | `Product/web/assets/app.js` | 修改 | 事件委托添加 start-run / primary 处理 |
| A2-1 | `Product/backend/orchestrator.py` | 修改 | _resolve_project_id 优先使用 profile.id |
| B1-1 | `Product/backend/llm_client.py` | 修改 | _call_openai_compatible 返回 usage tuple |
| B1-2 | `Product/backend/llm_client.py` | 修改 | _call_anthropic_compatible 返回 usage tuple |
| B1-3 | `Product/backend/llm_client.py` | 修改 | chat_completion 返回 (text, usage) |
| B1-4 | `Product/backend/llm_client.py` | 修改 | chat_completion_with_fallback 在 metadata 中传递 usage |
| B2-1 | `Product/backend/orchestrator.py` | 修改 | _stage_04_modeling finally 块传递 token 和 estimated_usd |
| B2-2 | `Product/backend/orchestrator.py` | 新增 | _estimate_llm_cost 辅助函数 |
| B3-1 | `Product/web/assets/app.js` | 修改 | renderGovernanceCosts 显示 tokens 和 USD |
| B3-2 | `Product/web/assets/app.js` | 修改 | 成本汇总卡片添加 totalTokens / totalUsd |
| B3-3 | `Product/web/assets/styles.css` | 新增 | cost-event 相关样式 |

---

## 验证步骤

1. 启动后端 `python -m Product.app`
2. 打开前端 `http://localhost:8000`
3. **A1 验证**:
   - 进入 Journey 页面，确认选题
   - 应看到"启动完整执行"按钮
   - 点击后应看到"查看 Agent 实时输出"按钮出现
   - 点击"查看 Agent 实时输出"应弹出 agent-output-panel
   - Journey 节点应随 SSE 事件实时变色
4. **A2 验证**:
   - 使用中文标题创建项目（如"培训对工资的影响"）
   - 在 orchestrator 中执行不应再出现 KeyError
5. **B1+B2 验证**:
   - 执行到 04_modeling 阶段（触发 LLM 调用）
   - 检查 `state/product/cost_events.jsonl`
   - 应有 `input_tokens`、`output_tokens`、`estimated_usd` 字段且非零
6. **B3 验证**:
   - 打开治理面板 → Cost tab
   - 应看到每个事件的 tokens 和 USD
   - 汇总卡片应显示总 tokens 和总成本
