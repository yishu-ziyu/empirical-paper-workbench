# ADR-0001: Split title and body chapters in state

- **Status**: accepted
- **Date**: 2026-07-28
- **Decision**: 把 `state.chapters: List[Chapter]` 拆分为 `state.title_chapter: Chapter` + `state.body_chapters: List[Chapter]`

## Context

T-01~T-11 完成后，`state.chapters` 把两类语义异质的对象混在同一数组：

- `chapters[0]` 是 `type="title"` 的标题章节（单数，由 `generate_title` 写入）
- `chapters[1..6]` 是正文章节（复数，由 `generate_chapter` 按 `current_chapter_index` 循环写入）

为区分这两类，代码里散布了：

- `generate_chapter` 计算 `title_offset`，正文从 `chapters[idx+1]` 写入
- `chapter.py` 端点用 `last_generated_chapter` + fallback `chapters[idx-1]` / `chapters[-1]` 三重定位
- `current_chapter_index` 语义歧义：是 outline 索引还是 chapters 数组索引？

架构评审（improve-codebase-architecture）识别为最高优先级深化机会：浅接口（位置数组混入语义异质对象），无 locality（改 title 影响 body 逻辑）。

## Decision

拆分 `chapters` 为两个字段：

```python
class EconPaperState(TypedDict, total=False):
    title_chapter: Chapter       # 由 generate_title 写入，单数
    body_chapters: List[Chapter]  # 由 generate_chapter 按 idx 写入，6 项
    current_chapter_index: int    # 0-5，body_chapters 索引（与 outline 对齐）
```

## Consequences

### 正面

- **Locality**：`generate_title` 只动 `title_chapter`，`generate_chapter` 只动 `body_chapters`，互不影响
- **Depth**：`current_chapter_index` 语义单一化（body_chapters 索引），删 `title_offset` 计算
- **Testability**：端点直接 `body_chapters[-1]` 定位，删 `last_generated_chapter` fallback 链
- **语义清晰**：title 和 body 在 state schema 层面显式分离，不靠 `type=="title"` 隐式约定

### 负面

- **破坏性**：所有依赖 `state.chapters` 的节点、端点、测试需同步改（约 8-10 个测试文件，30-50 处断言）
- **无向后兼容**：项目未上线，无生产 session 需要迁移，接受破坏性重构

## Alternatives considered

1. **保留 `chapters` + 加 `title_index: int` 显式定位** — 治标不治本，仍靠位置数组 + 隐式约定
2. **引入 `ChapterList` 容器类** — 违反 YAGNI，LangGraph state 是 TypedDict，容器类增加无谓抽象
3. **`chapters_by_type: dict[str, Chapter/List]`** — 过度抽象，title 只有一个，不需要 dict

## Implementation

- 删 `state.chapters` 字段，新增 `title_chapter` + `body_chapters`
- `generate_title`：只写 `title_chapter`
- `generate_chapter`：删 `title_offset` + legacy `current_chapter` 路径，直接 `body_chapters[idx] = new_chapter`
- `approve_chapter` / `rollback`：操作 `body_chapters`
- `export_docx._extract_title`：读 `title_chapter`，不再遍历数组
- 端点 `chapter.py`：删 `last_generated_chapter` fallback，直接 `body_chapters[-1]`
- 所有相关测试同步更新

## References

- 架构评审：improve-codebase-architecture session（2026-07-28）
- 词汇表：[CONTEXT.md](../../CONTEXT.md) — Title Chapter / Body Chapter / Chapter Index
