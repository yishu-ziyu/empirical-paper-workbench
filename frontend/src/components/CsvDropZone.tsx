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
      className="composer-shell px-5 py-6"
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
      <p className="text-[15px] font-medium tracking-tight text-ink">{t('guide.ingestKicker')}</p>
      <p className="mt-1 text-[15px] leading-7 text-ink/80">{t('workbench.dropBody')}</p>
      <p className="mt-1 text-[12px] text-muted">{t('workbench.dropFormats')}</p>
      <div className="mt-5 flex items-center gap-2">
        <button
          type="button"
          data-testid="data-browse-btn"
          onClick={onBrowse}
          disabled={uploading}
          aria-label={t('workbench.browse')}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-black/[0.08] text-[22px] leading-none text-ink transition-colors hover:bg-black/[0.04] disabled:opacity-50"
        >
          +
        </button>
        <button
          type="button"
          onClick={onBrowse}
          disabled={uploading}
          className="ml-auto rounded-full bg-ink px-4 py-2 text-[13px] font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {uploading ? t('app.uploading') : t('workbench.browse')}
        </button>
      </div>
      <p className="mt-4 text-[11px] leading-5 text-muted">{t('workbench.dropWarn')}</p>
      {error && (
        <p data-testid="upload-error" className="mt-2 text-[12px] text-danger">
          {error}
        </p>
      )}
    </div>
  )
}
