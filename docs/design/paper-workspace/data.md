# 数据层

> 上级：[创作台方案](README.md)

## 现有对象（保留，不重做）

| 对象 | 位置 | 在创作台里的角色 |
|---|---|---|
| Session | `backend/facade/session_store.py`，`GET /sessions/{id}` | 一项研究 |
| Run / RunEvent | `backend/run_repository.py`（持久化、带 `seq`） | 每次计算；工具卡的“运行中 / 完成” |
| 证据与设定运行 | `/sessions/{id}/evidence`、research lab 的 `specification_runs` | 数字引用最终指向的地方 |
| 主张（claims） | `/research/claims/draft`、`/claims/{id}/approve` | 用户采用的研究结论；稿子措辞的上限 |
| 章节 | `state.body_chapters`（整块文本） | **要被下面的 Document 取代** |

## 新增对象

### Document 与 Block

稿子不再是整块章节文本，而是有序的块。

```text
Document { document_id, session_id, version, blocks: [block_id…] }
Block    { block_id, kind: heading|paragraph|table|figure|equation,
           version, content: Inline[], section }
Inline   = Text(string) | Ref(ref_id) | Cite(citation_id)
```

块是改动、批注和光标的最小单位。`version` 用于乐观并发：改动必须声明 `base_version`，与当前版本不符就拒绝，由前端重取快照。

### Ref：正文里的数字

```text
Ref { ref_id, block_id, source: {spec_run_id | evidence_id, field: coef|se|n|F…},
      format: {digits, unit}, bound_revision }
```

- 渲染时按 `source` 去证据里取值，而不是存一个写死的数字。
- `bound_revision` 记录写这句话时证据的版本。证据版本变了，这个 Ref 就是“过时”，由系统算出来，不靠人记。
- 这复用了现有的 evidence revision / claim stale 机制，只是把粒度下沉到正文里的单个数字。

### ChangeSet：一次改动

```text
ChangeSet { change_id, session_id, author: user|assistant, turn_id?,
            ops: [{block_id, base_version, before, after}],
            reason, status: applied|reverted, created_at }
```

- 助手的一次改稿就是一个 ChangeSet，可以包含多个块（原型里“换主设定”是 4 个操作）。用户直接编辑也是 ChangeSet，`author = user`。
- ChangeSet 只能改 Text；Ref 只能整体删除或移动，不能改值。
- 撤销时生成一个反向的 ChangeSet，不删除历史。
- 只有 `applied` 状态的改动会进入 Document 的新版本。

### ReviewNote：审稿批注

```text
ReviewNote { note_id, block_id, range?, category: consistency|identification|inference|…,
             text, status: open|resolved, resolved_by_change_id? }
```

批注锚定到块（可选字符范围）。批注被处理时，记下是哪个 ChangeSet 处理的；撤销那个 ChangeSet，批注就回到 open。

### Thread 与 AgentTurn：对话

```text
Thread    { thread_id, session_id, title, created_at }        一项研究可以有多条
AgentTurn { turn_id, thread_id, run_ids[], change_ids[], ask_ids[] }
```

- 多条线程共用同一份 Document、证据和计算记录；线程之间不共享对话上下文。
- 对话内容复用 LangGraph 检查点（`backend/routers/agent_spike.py` 已按 `thread_id` 持久化）。需要额外落库的只有“这一轮产生了哪些 Run、ChangeSet 和询问”，用来在对话里显示工具卡、改动卡和询问卡。
- 两条线程同时改同一块时，靠块的 `base_version` 拒绝后到的那次，由助手重读后重试。

### ComputationRecord：计算记录（Notebook）

```text
ComputationRecord { record_id, session_id, seq, run_id, code, language: python,
                    outputs, data_sha256, environment, used_by: [ref_id…], status: adopted|not_adopted|failed }
```

- `code` 是实际执行的调用（与 `backend/services/spec_run.py` 中的调用一致），不是事后重写的版本。
- `used_by` 反查稿子里的哪些 Ref 用了它，Notebook 据此显示“用于：…”。
- 复现包由记录按 `seq` 拼出：`analysis.py` 加数据说明和环境；Stata / R 版走现有 `GET /sessions/{id}/code-export` 翻译，数值核对通过前必须标“未核对”。

## 不持久化的

- 光标位置和动画：只在事件流里出现（`cursor.intent`），重连后不重放。
- 输入框草稿、面板宽度等界面偏好：只存在前端本地。

## 真相归属

研究状态只在后端（沿用 ADR-0013）。前端显示的每个“已改”“已处理”，都来自后端接受了命令之后的事件，不做只在前端生效的乐观更新。
