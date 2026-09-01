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

function StatusIcon({ status }: { status: string }) {
  // 统一 SVG 图标（不用 Unicode 字形代替图标：跨平台渲染不稳定、无法配色）
  switch (status) {
    case 'done':
      return (
        <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth={2} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 8.5 6.5 12 13 4.5" />
        </svg>
      )
    case 'generated':
      return (
        <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth={1.6} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M11 2.5l2.5 2.5L5.5 13l-3 .5.5-3L11 2.5Z" />
        </svg>
      )
    case 'streaming':
      return (
        <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" fill="currentColor" aria-hidden="true">
          <circle cx="3.5" cy="8" r="1.4" />
          <circle cx="8" cy="8" r="1.4" />
          <circle cx="12.5" cy="8" r="1.4" />
        </svg>
      )
    default:
      return (
        <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth={1.6} aria-hidden="true">
          <circle cx="8" cy="8" r="5.5" />
        </svg>
      )
  }
}

const STATUS_LABEL: Record<string, string> = {
  done: '已完成',
  generated: '已生成',
  streaming: '生成中',
  pending: '未开始',
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
            aria-current={isCurrent || undefined}
            className={`flex items-center gap-2 rounded-md border-l-2 px-3 py-2.5 text-left font-serif transition-colors ${
              isCurrent
                ? 'border-accent bg-accent/5 text-accent'
                : 'border-transparent text-ink hover:bg-panel'
            }`}
          >
            <span
              data-testid="chapter-status-icon"
              data-status={ch.status ?? 'pending'}
              role="img"
              aria-label={STATUS_LABEL[ch.status ?? ''] ?? '未开始'}
              className="flex w-4 justify-center text-xs"
            >
              <StatusIcon status={ch.status ?? ''} />
            </span>
            <span className="flex-1 truncate text-sm">{ch.title}</span>
          </button>
        )
      })}
    </nav>
  )
}
