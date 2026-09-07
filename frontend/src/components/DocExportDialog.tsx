// 文档导出对话框 (T-10)
// - 4 个 LaTeX 模板选择（单选）
// - 3 种格式导出按钮（.tex / .pdf / .docx）
// - 点击导出 → onExport(format, template)
// - 关闭按钮 → onClose
// 设计：Editorial Academic Refined — 衬线字体 + 暖色调

import { useState } from 'react'
import { useT } from '../lib/i18n'

export type ExportFormat = 'tex' | 'pdf' | 'docx'

export interface DocExportDialogProps {
  sessionId: string
  onClose: () => void
  onExport: (format: ExportFormat, template: string) => void
}

const TEMPLATES = [
  { value: 'cn_journal', labelKey: 'docExport.tpl.cn_journal' },
  { value: 'undergraduate', labelKey: 'docExport.tpl.undergraduate' },
  { value: 'master_thesis', labelKey: 'docExport.tpl.master_thesis' },
  { value: 'english_submission', labelKey: 'docExport.tpl.english_submission' },
]

const FORMATS: { format: ExportFormat; labelKey: string }[] = [
  { format: 'tex', labelKey: 'docExport.fmt.tex' },
  { format: 'pdf', labelKey: 'docExport.fmt.pdf' },
  { format: 'docx', labelKey: 'docExport.fmt.docx' },
]

export default function DocExportDialog({
  sessionId,
  onClose,
  onExport,
}: DocExportDialogProps) {
  const { t } = useT()
  const [template, setTemplate] = useState('cn_journal')

  return (
    <div
      data-testid="doc-export-dialog"
      className="flex flex-col gap-4 rounded border border-border bg-paper p-5 shadow-lg"
    >
      <div className="flex items-center justify-between border-b border-border pb-2">
        <h2 className="font-serif text-base font-semibold text-ink">
          {t('docExport.title')}
        </h2>
        <button
          type="button"
          data-testid="close-button"
          onClick={onClose}
          className="font-serif text-lg text-muted transition-colors hover:text-ink"
        >
          ×
        </button>
      </div>

      <div className="flex flex-col gap-2">
        <span className="font-serif text-xs font-semibold text-muted">
            {t('docExport.selectTemplate')}
          </span>
        <div className="grid grid-cols-1 gap-1 sm:grid-cols-2">
          {TEMPLATES.map((item) => (
            <label
              key={item.value}
              className="flex cursor-pointer items-center gap-2 rounded border border-border px-2 py-1 font-serif text-xs text-ink transition-colors hover:bg-panel"
            >
              <input
                type="radio"
                name="template"
                value={item.value}
                data-testid="template-option"
                checked={template === item.value}
                onChange={() => setTemplate(item.value)}
                className="accent-accent"
              />
              <span className="font-semibold">{item.value}</span>
              <span className="text-muted">— {t(item.labelKey)}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <span className="font-serif text-xs font-semibold text-muted">
          {t('docExport.exportFormat')}
        </span>
        <div className="flex flex-wrap gap-2">
          {FORMATS.map((f) => (
            <button
              key={f.format}
              type="button"
              data-testid="export-button"
              data-format={f.format}
              onClick={() => onExport(f.format, template)}
              className="rounded border border-accent bg-accent/5 px-4 py-2 font-serif text-xs font-semibold text-accent transition-colors hover:bg-accent hover:text-paper"
            >
              {t(f.labelKey)}
            </button>
          ))}
        </div>
      </div>

      <span className="font-serif text-xs text-muted">
        {t('docExport.session')} {sessionId} · {t('docExport.selectTemplate')} {template}
      </span>
    </div>
  )
}
