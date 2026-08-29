// 审批绕过徽标（北极星"可查"的 UI 面）
// 契约参照 shadcn/ui Badge 的变体体系（destructive pill），配色走项目
// 既有设计令牌（--danger），不引新依赖。
// 只在一件事上出现：章节评审未过审、被人显式 force 放行
// （后端留下 approved_forced: true 的永久痕迹）。

import { useT } from '../lib/i18n'
import type { components } from '../types/api'

type Chapter = components['schemas']['ChapterResponse']

export default function ApprovalBadge({ chapter }: { chapter: Chapter }) {
  const { t } = useT()
  if (!chapter.approved_forced) return null
  return (
    <span
      data-testid="approval-bypassed-badge"
      title={t('reviewGate.title')}
      className="inline-flex shrink-0 items-center gap-1 rounded-full border border-danger/40 bg-danger/10 px-2 py-0.5 text-[11px] font-medium text-danger"
    >
      {/* 实心圆点：异常态的第一眼信号 */}
      <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-danger" />
      {t('chapter.bypassedBadge')}
    </span>
  )
}
