/* 章节审批状态徽章：approved=已批准（绿）/ generated=待批准（告警金）/
 * edited=已编辑（墨）/ rolled_back=已回滚（弱化）。
 * DESIGN.md 徽章规范：当前/可点=绿淡底绿字；告警金=写不了/需注意。不用阴影。
 * Hallmark · design-system: DESIGN.md · designed-as-app
 */
import { useT } from '../lib/i18n'

export interface ApprovalBadgeProps {
  chapter: { status?: string; approved?: boolean }
}

const STYLES: Record<string, { cls: string; key: string }> = {
  approved: { cls: 'bg-accent/10 text-accent', key: 'badge.approved' },
  generated: { cls: 'bg-warning/10 text-warning', key: 'badge.pending' },
  edited: { cls: 'bg-ink/5 text-ink', key: 'badge.edited' },
  rolled_back: { cls: 'bg-muted/10 text-muted', key: 'badge.rolledBack' },
}

export default function ApprovalBadge({ chapter }: ApprovalBadgeProps) {
  const { t } = useT()
  const status = chapter.approved ? 'approved' : (chapter.status ?? 'generated')
  const style = STYLES[status] ?? STYLES.generated
  return (
    <span
      data-testid="approval-badge"
      className={`inline-block rounded px-1.5 py-0.5 font-mono text-[11px] leading-4 ${style.cls}`}
    >
      {t(style.key)}
    </span>
  )
}
