import { useT } from '../lib/i18n'

export interface CsvDropZoneProps {
  uploading?: boolean
  uploadError?: string | null
  onBrowse: () => void
  onFile?: (file: File) => void
}

export function CsvDropZone({ uploading = false, uploadError = null, onBrowse, onFile }: CsvDropZoneProps) {
  const { t } = useT()

  return (
    <div
      className="rounded-xl border border-dashed border-border bg-panel px-4 py-6 text-center"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault()
        const file = e.dataTransfer.files?.[0]
        if (file && onFile) onFile(file)
      }}
    >
      <svg className="mx-auto h-8 w-8 text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
      </svg>
      <p className="mt-3 text-[13px] text-ink">{t('workbench.dropBody')}</p>
      <p className="mt-1 text-[11px] text-muted">{t('workbench.dropFormats')}</p>
      <button
        type="button"
        data-testid="data-browse-btn"
        onClick={onBrowse}
        disabled={uploading}
        className="mt-4 w-full rounded bg-accent px-4 py-2 text-[13px] text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50"
      >
        {uploading ? t('app.uploading') : t('workbench.browse')}
      </button>
      <p className="mt-3 text-[11px] leading-5 text-danger">{t('workbench.dropWarn')}</p>
      {uploadError && (
        <p data-testid="upload-error" className="mt-2 text-[12px] text-danger">
          {uploadError}
        </p>
      )}
    </div>
  )
}
