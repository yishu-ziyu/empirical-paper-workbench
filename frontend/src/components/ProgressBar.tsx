// 章节进度条 (T-08c)
// - 显示 6 个章节标签（intro/lit_review/data_desc/methods/results/conclusion）
// - 已通过 = 绿色，当前 = 高亮（accent），未开始 = 灰色
// - 点击章节标签可跳转（onChapterClick 回调）
// - 显示进度（completed/total）
// 设计：Editorial Academic Refined — 衬线字体 + 暖色调 + 克制动效
//
// Stage D: 删除手写 ChapterProgress interface，改 import types/api.ts 的
// ProgressChapterSummary（与 GET /sessions/{id}/progress 返回体一致）。

import type { components } from '../types/api'

/** 章节进度概要，由 OpenAPI codegen 生成（components.schemas.ProgressChapterSummary）。 */
export type ChapterProgress = components['schemas']['ProgressChapterSummary']

export interface ProgressBarProps {
  total: number
  completed: number
  current: number
  body_chapters: ChapterProgress[]
  onChapterClick?: (index: number) => void
}

// 根据章节状态 + 是否当前章，决定 label 的样式 class
function labelClass(
  index: number,
  current: number,
  status: string,
): string {
  // 当前章高亮（accent）— 优先级最高
  if (index === current) {
    return 'bg-accent text-white border-accent'
  }
  // 已通过 = 绿色
  if (status === 'done') {
    return 'bg-green-100 text-green-800 border-green-300'
  }
  // 未开始 = 灰色
  return 'bg-gray-100 text-gray-500 border-gray-300'
}

export default function ProgressBar({
  total,
  completed,
  current,
  body_chapters,
  onChapterClick,
}: ProgressBarProps) {
  return (
    <div
      data-testid="progress-bar"
      className="flex items-center gap-2 border border-border rounded bg-paper p-3"
    >
      {/* 进度数字 */}
      <span className="font-serif text-sm text-muted whitespace-nowrap">
        {completed} / {total}
      </span>

      {/* 分隔线 */}
      <span className="h-4 w-px bg-border" />

      {/* 章节标签 */}
      <div className="flex flex-1 items-center gap-1 overflow-x-auto">
        {body_chapters.map((ch, idx) => (
          <button
            key={`${ch.type}-${idx}`}
            type="button"
            data-testid="chapter-label"
            onClick={() => onChapterClick?.(idx)}
            className={`cursor-pointer whitespace-nowrap rounded border px-2 py-0.5 font-serif text-xs transition-colors ${labelClass(idx, current, ch.status ?? '')}`}
            title={ch.title ?? ''}
          >
            {ch.title}
          </button>
        ))}
      </div>
    </div>
  )
}
