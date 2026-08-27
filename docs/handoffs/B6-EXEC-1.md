# 执行1：批次 6 - 识别后文献与估计并行（只改图）

你是 cmux 同窗口执行会话。批次 1–5 已收下。本批只动预写图的边。
不要问确认。读完就改、跑测试、写 STATUS。

产品根：`/Users/mahaoxuan/Desktop/经济学论文/econpaper`
设计：`docs/specs/paper-engine.md` 批次 6 与「后批可选并行」那张图。

## Goal

识别不是 0 星之后，图上同时走两条：估计→稳健性，文献→引用图。两边都结束后 `generate_title` 只跑一次，再出大纲后 END。

## Hard bar

1. 新测试（你写）：给 `generate_title` 打 monkeypatch 计数，带方向的 state 走 `build_graph()` 的预写路径（或与 `build_graph` 相同边的最小图），`generate_title` **恰好 1 次**。不得 0 次，不得 2 次。
2. 0 星仍进 `hitl_pause`，不进估计、不进文献。
3. 已有测试必须绿：
   - `agent/tests/test_graph_six_chapters.py`
   - `backend/tests/test_graph.py`（无方向 invoke 仍不得写出 `title_chapter`）
4. **不要**改 `run_prewrite`。Facade 继续串行：识别 → 估计 → 稳健性 → 文献 → 标题 → 大纲。

## 边（设计原文）

```
identification_verify --可继续--> run_estimate
identification_verify --可继续--> search_literature
run_estimate --> robustness_check
search_literature --> build_citation_graph
robustness_check --> generate_title
build_citation_graph --> generate_title
generate_title --> generate_outline --> END
```

LangGraph 0.2.50。节点 id 不能叫 `estimate`（与 state 键撞）。不要发明 `wait_*` 节点。

`route_after_identification` 今天返回 `"run_estimate"`。若你改成返回列表或中间节点名，必须同步改两处现有断言：

- `agent/tests/test_graph_six_chapters.py` 里 `test_route_after_identification_goes_to_estimate`
- `backend/tests/test_graph.py` 里同名测试

0 星断言必须仍是 `"hitl_pause"`。

## 失败就停

若扇入后 `generate_title` 会跑两次，且你找不到 0.2.50 上不靠全局锁、不改 `run_prewrite` 的接法：

- 把 `graph.py` **恢复线性**（现在的边：估计→稳健性→文献→引用图→标题）
- `status: blocked`
- `ran` 里写清：调用次数、你试过的接法、为何退回

未绿则保持线性。不要为了绿而让标题跑两次再丢一次结果。

## 只许改

- `agent/graph.py`
- 新建 `agent/tests/test_graph_fanin.py`
- 仅当路由返回值变了：上面两处 `test_route_after_identification_goes_to_estimate`

## 禁止改

`agent/engine/prewrite.py`，`backend/facade.py`，`estimate.py`，`robustness_check.py`，`search_literature.py`，`generate_title.py`，章节/评审文件。

## 测试

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest \
  agent/tests/test_graph_fanin.py \
  agent/tests/test_graph_six_chapters.py \
  backend/tests/test_graph.py -q --tb=short
```

`backend/tests/test_graph.py` 若必须用 backend venv 才收得到 `psycopg`，改用：

```bash
./backend/.venv/bin/python -m pytest backend/tests/test_graph.py -q --tb=short
```

两套都要绿，或 STATUS 写明哪套因环境没跑。

## 做完写

`docs/handoffs/B6-EXEC-1.STATUS.md`

```text
status: done
ran:
changed:
risk:
```

现在开工。
