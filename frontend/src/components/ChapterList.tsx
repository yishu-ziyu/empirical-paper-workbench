// 章节大纲列表 (T-08c)
// - 左栏大纲列表：6 章标题 + 类型 badge + 状态图标
// - 当前章高亮（accent）
// - 点击切换章节（onSelectChapter 回调）
// 设计：Editorial Academic Refined — 衬线字体 + 暖色调
//
// Stage D: 删除手写 ChapterListItem interface，改 import types/api.ts 的
// ChapterResponse（与 ChapterWriter 共享同一 API 类型）。

import type { components } from '../types/api'

/** 章节列表项，由 OpenAPI codegen 生成（components.schemas.ChapterResponse）。 */
export type ChapterListItem = components['schemas']['ChapterResponse']

export interface ChapterListProps {
  body_chapters: ChapterListItem[]
  currentIndex: number
  onSelectChapter: (index: number) => void
}

function statusIcon(status: string): string {
  switch (status) {
    case 'done':
      return '✓'
    case 'generated':
      return '✎'
    case 'streaming':
      return '⋯'
    default:
      return '○'
  }
}

export default function ChapterList({
  body_chapters,
  currentIndex,
  onSelectChapter,
}: ChapterListProps) {
  return (
    <nav className="flex flex-col gap-1">
      {body_chapters.map((ch, idx) => {
        const isCurrent = idx === currentIndex
        return (
          <button
            key={`${ch.type}-${idx}`}
            type="button"
            data-testid="chapter-list-item"
            onClick={() => onSelectChapter(idx)}
            className={`flex items-center gap-2 rounded border-l-2 px-3 py-2 text-left font-serif transition-colors ${
              isCurrent
                ? 'border-accent bg-accent/5 text-accent'
                : 'border-transparent text-ink hover:bg-panel'
            }`}
          >
            <span
              data-testid="chapter-status-icon"
              className="w-4 text-center text-xs"
            >
              {statusIcon(ch.status ?? '')}
            </span>
            <span className="flex-1 truncate text-sm">{ch.title}</span>
          </button>
        )
      })}
    </nav>
  )
}
