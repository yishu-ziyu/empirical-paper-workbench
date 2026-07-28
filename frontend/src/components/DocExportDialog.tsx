// 文档导出对话框 (T-10)
// - 4 个 LaTeX 模板选择（单选）
// - 3 种格式导出按钮（.tex / .pdf / .docx）
// - 点击导出 → onExport(format, template)
// - 关闭按钮 → onClose
// 设计：Editorial Academic Refined — 衬线字体 + 暖色调

import { useState } from 'react'

export type ExportFormat = 'tex' | 'pdf' | 'docx'

export interface DocExportDialogProps {
  sessionId: string
  onClose: () => void
  onExport: (format: ExportFormat, template: string) => void
}

const TEMPLATES = [
  { value: 'cn_journal', label: '中文核心期刊' },
  { value: 'undergraduate', label: '本科论文' },
  { value: 'master_thesis', label: '硕士学位论文' },
  { value: 'english_submission', label: '英文投稿' },
]

const FORMATS: { format: ExportFormat; label: string }[] = [
  { format: 'tex', label: '.tex 源码' },
  { format: 'pdf', label: '.pdf' },
  { format: 'docx', label: '.docx' },
]

export default function DocExportDialog({
  sessionId,
  onClose,
  onExport,
}: DocExportDialogProps) {
  const [template, setTemplate] = useState('cn_journal')

  return (
    <div
      data-testid="doc-export-dialog"
      className="flex flex-col gap-4 rounded border border-border bg-paper p-5 shadow-lg"
    >
      <div className="flex items-center justify-between border-b border-border pb-2">
        <h2 className="font-serif text-base font-semibold text-ink">
          导出文档
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
          选择模板
        </span>
        <div className="grid grid-cols-1 gap-1 sm:grid-cols-2">
          {TEMPLATES.map((t) => (
            <label
              key={t.value}
              className="flex cursor-pointer items-center gap-2 rounded border border-border px-2 py-1 font-serif text-xs text-ink transition-colors hover:bg-panel"
            >
              <input
                type="radio"
                name="template"
                value={t.value}
                data-testid="template-option"
                checked={template === t.value}
                onChange={() => setTemplate(t.value)}
                className="accent-accent"
              />
              <span className="font-semibold">{t.value}</span>
              <span className="text-muted">— {t.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <span className="font-serif text-xs font-semibold text-muted">
          导出格式
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
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <span className="font-serif text-xs text-muted">
        会话 {sessionId} · 模板 {template}
      </span>
    </div>
  )
}
