import { useT } from '../lib/i18n'

// 版本历史下拉 (T-08c)
// - 显示所有版本列表（版本索引 + 前 50 字预览）
// - 当前版本高亮（accent）
// - 点击选择 → 触发 onSelectVersion(index)
// 设计：Editorial Academic Refined — 衬线字体 + 暖色调

export interface VersionHistoryProps {
  versions: string[]
  onSelectVersion: (index: number) => void
  currentVersionIndex?: number
}

// 取前 50 字作为预览
function preview(text: string): string {
  const clean = text.replace(/\n/g, ' ').trim()
  if (clean.length <= 50) return clean
  return clean.slice(0, 50) + '…'
}

export default function VersionHistory({
  versions,
  onSelectVersion,
  currentVersionIndex,
}: VersionHistoryProps) {
  const { t } = useT()
  return (
    <div
      data-testid="version-history"
      className="border border-border rounded bg-paper shadow-sm"
    >
      {versions.length === 0 ? (
        <div className="p-3 text-center font-serif text-xs text-muted">
          {t('version.empty')}
        </div>
      ) : (
        <ul className="divide-y divide-border">
          {versions.map((ver, idx) => {
            const isCurrent = idx === currentVersionIndex
            return (
              <li key={idx}>
                <button
                  type="button"
                  data-testid="version-item"
                  onClick={() => onSelectVersion(idx)}
                  className={`flex w-full flex-col gap-1 px-3 py-2 text-left font-serif text-xs transition-colors hover:bg-panel ${
                    isCurrent
                      ? 'border-l-2 border-accent bg-accent/5'
                      : 'border-l-2 border-transparent'
                  }`}
                >
                  <span
                    className={`font-semibold ${
                      isCurrent ? 'text-accent' : 'text-ink'
                    }`}
                  >
                    {t('version.label')} {idx}
                    {isCurrent && t('version.current')}
                  </span>
                  <span className="text-muted line-clamp-2">{preview(ver)}</span>
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
