# 前端层与后端层

> 上级：[创作台方案](README.md)

## 前端

### 状态

一个会话一个 store，结构是“快照 + 事件归约”：

```text
state = reduce(snapshot, events[seq > snapshot.seq])
```

- `document`：块、版本、Ref
- `evidence`：Ref 要读的值和版本
- `thread`：消息、工具卡、询问卡、改动卡
- `notes`：审稿批注
- `lastSeq`：断点续传用

派生值不入库，由选择器算出：

- `staleRefs = refs.filter(r => evidence[r.source].revision !== r.bound_revision)`
- `openNotes`、`busy`（有进行中的 turn）

### 光标播放器

复用 `frontend/src/lib/agentCursor/`（语义目标注册表 + player）：

1. 收到 `cursor.intent` → 放进播放队列；
2. 播放器按顺序执行 move / click / select / type，每步等动画完成；
3. 收到对应的 `change.applied` 时，如果光标还在播放，就等它播完再落最终文字；
4. 队列积压超过 3 条，或者标签页不在前台时，跳过动画直接落结果。

光标只是表现层。任何时候丢掉光标事件，稿子的最终状态都不会变。

### 组件

| 组件 | 读什么 | 发什么命令 |
|---|---|---|
| `StudyList` | 研究列表 | — |
| `Thread` | thread | 发消息、回答询问、撤销 |
| `Manuscript` | document、evidence、notes | 用户手改、点 Ref 打开来源 |
| `Notebook` | runs、cells | 重跑某个 cell（后续） |
| `AgentCursor` | 播放队列 | — |

## 后端

### 研究助手编排

在现有 LangGraph v1 试验（`agent/spike/langgraph_v1.py`、`backend/routers/agent_spike.py`）的基础上，把工具换成有副作用边界的一组：

| 工具 | 做什么 | 副作用 |
|---|---|---|
| `read_document` / `read_evidence` | 读稿子和证据 | 无 |
| `run_spec` | 提交一次设定运行 | 创建 Run（沿用 durable runner） |
| `ask_user` | 提一个问题并暂停 | LangGraph interrupt → `ask.opened` |
| `point_at` | 表达光标意图 | 只发 `cursor.intent` |
| `propose_change` | 生成一组块改动 | 写 ChangeSet，发 `change.applied` |
| `resolve_note` | 标记批注已处理 | 更新 ReviewNote |

规则写在编排层，不写在提示词里：`propose_change` 涉及 2 个以上块，或者措辞越过已批准主张的强度（例如相关写成因果），必须先经过 `ask_user`。

### 改动落库与事件外发

1. 工具在一个数据库事务里写业务对象（ChangeSet、块的新版本、批注状态），同时往 outbox 表写事件，并分配 `seq`。
2. 事件分发器读 outbox，推给会话的 SSE 订阅者。
3. 同一个事务保证“事件发出了，数据就一定写进去了”，断线重连也不会看到半截改动。

### 数字绑定服务

- 主设定或证据变化时，找出 `bound_revision` 过时的 Ref，得到受影响的块。
- 助手据此生成 ChangeSet（改措辞），或者只标记过时，等用户决定。
- 撤销时一起恢复 `bound_revision`。

### 鉴权与隔离

所有命令和 SSE 都走现有的会话归属检查（`require_session_ownership`）。助手的工具以当前用户身份调用服务层，不绕过同一套权限。
