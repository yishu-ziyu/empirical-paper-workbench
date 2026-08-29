/* 章节版本历史下拉：选一个历史版本回滚（rollback）。
 * 契约由消费方 ChapterWriter 决定：versions 为版本标识字符串数组。
 * Hallmark · design-system: DESIGN.md · designed-as-app
 */
import { useT } from '../lib/i18n'

export interface VersionHistoryProps {
  versions: string[]
  onSelectVersion: (index: number) => void
}

function clip(v: string): string {
  return v.length > 24 ? `${v.slice(0, 24)}…` : v
}

export default function VersionHistory({ versions, onSelectVersion }: VersionHistoryProps) {
  const { t } = useT()
  if (!versions.length) {
    return (
      <p data-testid="version-history-empty" className="text-xs leading-5 text-muted">
        {t('versionHistory.empty')}
      </p>
    )
  }
  return (
    <div data-testid="version-history" className="rounded border border-border bg-panel p-2">
      <p className="mb-1.5 font-mono text-[11px] uppercase tracking-wider text-muted">
        {t('versionHistory.title')}
      </p>
      <ul className="flex flex-col gap-1">
        {versions.map((v, idx) => (
          <li key={`${v.slice(0, 16)}-${idx}`}>
            <button
              type="button"
              data-testid="version-item"
              onClick={() => onSelectVersion(idx)}
              className="w-full rounded px-2 py-1.5 text-left text-xs text-ink transition-colors duration-150 hover:bg-accent/10"
            >
              <span className="mr-2 font-mono text-[11px] text-muted">
                v{versions.length - idx}
              </span>
              {clip(v.split('\n')[0] ?? v)}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
