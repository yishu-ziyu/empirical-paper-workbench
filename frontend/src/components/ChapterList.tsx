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

// 6 色 badge（与 ChapterWriter 一致）
const BADGE_COLORS: Record<string, string> = {
  intro: 'bg-blue-100 text-blue-800',
  lit_review: 'bg-purple-100 text-purple-800',
  data_desc: 'bg-green-100 text-green-800',
  methods: 'bg-orange-100 text-orange-800',
  results: 'bg-red-100 text-red-800',
  conclusion: 'bg-gray-200 text-gray-800',
}

function badgeClass(type: string): string {
  return BADGE_COLORS[type] ?? 'bg-gray-100 text-gray-700'
}

// 状态图标
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
            {/* 状态图标 */}
            <span
              data-testid="chapter-status-icon"
              className="w-4 text-center text-xs"
            >
              {statusIcon(ch.status ?? '')}
            </span>

            {/* 章节标题 */}
            <span className="flex-1 truncate text-sm">{ch.title}</span>

            {/* 类型 badge */}
            <span
              data-testid="chapter-type-badge"
              className={`rounded px-1.5 py-0.5 font-mono text-[10px] ${badgeClass(ch.type)}`}
            >
              {ch.type}
            </span>
          </button>
        )
      })}
    </nav>
  )
}
