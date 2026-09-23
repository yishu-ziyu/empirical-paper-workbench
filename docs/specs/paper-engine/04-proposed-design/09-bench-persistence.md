# 操作台持久化

> 上级：[Proposed Design](../04-proposed-design.md)


**决定：上传之后，操作台的权威状态是 Facade 内存。** `save_state` / `get_state` 的内存分支是方向、估计、章节的读写真值。PostgresSaver 只服务上传/清洗那次 `graph.invoke`。不要暗示“在 checkpointer 里点一次方向就能重生整篇”。重生 = 再 `POST /direction`（走 `run_prewrite` + `save_state`）。以后若要把预写写入 checkpointer，另开批次，本设计不假装已经统一。

---
