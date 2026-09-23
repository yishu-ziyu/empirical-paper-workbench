# Overview

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


econpaper 是工作区里唯一的实证论文网页产品（ADR-0010）。用户上传 CSV，回答四问方向，机器按方法跑识别诊断、主估计、稳健性、检索文献，再按固定六章写正文并评审、导出。方法是已知的（DiD / IV / RD / SCM / OLS 相关），六章骨架也是已知的。发动机不该再“发现该怎么写一篇论文”。

今天图和操作台不是同一条顺序。`agent/graph.py` 在清洗后立刻 `generate_title`，稳健性挂在六章循环之后。操作台真路径是 `POST /sessions/{id}/direction` → `AgentFacade.set_direction_and_outline`：识别非 0 星后跑 `estimate` 再出大纲，但**不跑文献、不跑稳健性**。`DirectionRequest` 是封闭模型，方法列进不来。`generate_chapter` 只要有 `outline` 就写，且只读 `outline[current_chapter_index]`，HTTP 的 `chapter.type` 被丢掉。`render_kwargs` 可把假 `results` 写进 state。评审 JSON 失败静默回 `mock_review_llm`。`check_structure` / `mock_review_llm` 仍按识别词打分，会把 OLS 方法章打回“因果”话术。

本设计保持**一张 LangGraph + 同一组节点函数**。改的是：类型化 `MainSpecification` 与按方法的估计/稳健性分派；门加宽到能送进那些列；按章就绪检查写在 `generate_chapter` 里；文献走预写路径（第一批 mock）；评审失败可见；关联主张下结构检查与 mock 评审不再奖励因果黑话。

第一批编译的是**线性图**：清洗后无方向则 `END`；有方向则预写到大纲后 `END`。章节与导出只走 Facade。后批才考虑文献∥估计。不发明 `wait_*` 节点。

---
