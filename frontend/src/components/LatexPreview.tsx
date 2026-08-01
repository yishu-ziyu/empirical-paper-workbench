import { useT } from '../lib/i18n'

// LaTeX 源码编辑 + PDF 预览 (T-10)
// - 显示 LaTeX 源码（可编辑 textarea）
// - 编辑触发 onLatexChange
// - pdfUrl 提供时渲染 PDF 预览 iframe
// - degraded=true 显示降级提示（latexmk 未安装）
// - 刷新按钮触发 onRefresh
// 设计：Editorial Academic Refined — 衬线字体 + 暖色调

export interface LatexPreviewProps {
  latexSource: string
  onLatexChange?: (value: string) => void
  pdfUrl?: string
  degraded?: boolean
  onRefresh?: () => void
}

export default function LatexPreview({
  latexSource,
  onLatexChange,
  pdfUrl,
  degraded,
  onRefresh,
}: LatexPreviewProps) {
  const { t } = useT()
  return (
    <div
      data-testid="latex-preview"
      className="flex flex-col gap-3 border border-border rounded bg-paper shadow-sm p-3"
    >
      <div className="flex items-center justify-between">
        <span className="font-serif text-sm font-semibold text-ink">
          {t('latex.title')}
        </span>
        {onRefresh && (
          <button
            type="button"
            data-testid="refresh-button"
            onClick={onRefresh}
            className="rounded border border-border px-2 py-1 font-serif text-xs text-ink transition-colors hover:bg-panel"
          >
            {t('latex.refresh')}
          </button>
        )}
      </div>

      <textarea
        data-testid="latex-source-input"
        value={latexSource}
        onChange={(e) => onLatexChange?.(e.target.value)}
        spellCheck={false}
        className="h-64 w-full resize-y rounded border border-border bg-white p-2 font-mono text-xs text-ink focus:outline-none focus:ring-1 focus:ring-accent"
      />

      {degraded && (
        <div
          data-testid="degraded-hint"
          className="rounded border border-amber-400 bg-amber-50 px-3 py-2 font-serif text-xs text-amber-700"
        >
          {t('latex.degraded')}
        </div>
      )}

      {pdfUrl && (
        <iframe
          data-testid="pdf-preview"
          src={pdfUrl}
          title="PDF 预览"
          className="h-[480px] w-full rounded border border-border bg-white"
        />
      )}
    </div>
  )
}
