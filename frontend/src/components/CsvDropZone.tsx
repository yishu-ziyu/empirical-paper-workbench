import { useState } from 'react'
import { useT } from '../lib/i18n'

export interface CsvDropZoneProps {
  uploading?: boolean
  uploadError?: string | null
  onBrowse: () => void
  onFile?: (file: File) => void
}

function isCsvFile(file: File): boolean {
  return file.name.toLowerCase().endsWith('.csv')
}

export function CsvDropZone({ uploading = false, uploadError = null, onBrowse, onFile }: CsvDropZoneProps) {
  const { t } = useT()
  const [dropError, setDropError] = useState<string | null>(null)
  const error = dropError || uploadError

  return (
    <div
      data-testid="csv-drop-zone"
      className="rounded-2xl border border-dashed border-border bg-panel px-6 py-14 text-center"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault()
        const file = e.dataTransfer.files?.[0]
        if (!file) return
        if (!isCsvFile(file)) {
          setDropError(t('workbench.dropCsvOnly'))
          return
        }
        setDropError(null)
        onFile?.(file)
      }}
    >
      <svg className="mx-auto h-10 w-10 text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
      </svg>
      <p className="mt-4 text-[15px] text-ink">{t('workbench.dropBody')}</p>
      <p className="mt-1 text-[12px] text-muted">{t('workbench.dropFormats')}</p>
      <button
        type="button"
        data-testid="data-browse-btn"
        onClick={onBrowse}
        disabled={uploading}
        className="mt-6 rounded-lg bg-accent px-5 py-2.5 text-[13px] font-medium text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50"
      >
        {uploading ? t('app.uploading') : t('workbench.browse')}
      </button>
      <p className="mt-4 text-[11px] leading-5 text-muted">{t('workbench.dropWarn')}</p>
      {error && (
        <p data-testid="upload-error" className="mt-2 text-[12px] text-danger">
          {error}
        </p>
      )}
    </div>
  )
}
