import { useEffect, useMemo, useState } from 'react'
import { CsvDropZone } from './CsvDropZone'
import { useT } from '../lib/i18n'
import {
  candidateKey,
  fileCandidate,
  isIngestBlocking,
  type AttachCandidate,
} from '../lib/attachCandidate'

export type AttachPanelStep = 'find' | 'select' | 'upload' | 'confirm'

export interface AttachPanelProps {
  topic?: string
  prefill?: AttachCandidate | null
  uploading?: boolean
  uploadReadiness?: 'READY' | 'PROCESSING' | 'FAILED' | 'CANCELLED'
  /**
   * 已挂接事实：只来自后端 snapshot（dataAttached）/ confirm-attach 响应。
   * 本组件不再做任何本地成功判定（FORMAL-CONFIRMATION-CHAIN-1 C3）。
   */
  attached?: boolean
  /** confirm-attach 请求进行中：只显示等待，不显示成功。 */
  confirming?: boolean
  /** 上一次 confirm-attach 失败的稳定文案；保留候选、允许重试。 */
  confirmError?: string | null
  onBrowse: () => void
  onFile?: (file: File) => void
  onConfirmAttach?: (candidate: AttachCandidate) => void
}

const STEPS: Array<{ id: AttachPanelStep; labelKey: 'attach.stepFind' | 'attach.stepSelect' | 'attach.stepUpload' | 'attach.stepConfirm' }> = [
  { id: 'find', labelKey: 'attach.stepFind' },
  { id: 'select', labelKey: 'attach.stepSelect' },
  { id: 'upload', labelKey: 'attach.stepUpload' },
  { id: 'confirm', labelKey: 'attach.stepConfirm' },
]

function confirmBlockReason(
  candidate: AttachCandidate | null,
  uploading: boolean,
  uploadReadiness: AttachPanelProps['uploadReadiness'],
): 'candidate' | 'ready' | null {
  if (!candidate) return 'candidate'
  if (uploading || isIngestBlocking(uploadReadiness)) return 'ready'
  return null
}

/**
 * Formal TITLE/TOPIC attach chrome: 找 / 选 / 传 / 确认挂接.
 * Prefill and pick/upload stay candidates. dataAttached is only rendered
 * from the backend truth passed in via `attached`.
 */
export default function AttachPanel({
  topic = '',
  prefill = null,
  uploading = false,
  uploadReadiness,
  attached = false,
  confirming = false,
  confirmError = null,
  onBrowse,
  onFile,
  onConfirmAttach,
}: AttachPanelProps) {
  const { t } = useT()
  const [step, setStep] = useState<AttachPanelStep>(prefill ? 'select' : 'find')
  const [candidate, setCandidate] = useState<AttachCandidate | null>(prefill)
  const prefillKey = prefill ? candidateKey(prefill) : ''

  useEffect(() => {
    if (!prefillKey || !prefill) return
    setCandidate(prefill)
    setStep('select')
    // Identity is prefillKey; a new object with the same key must not reset confirm.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [prefillKey])

  const block = attached ? null : confirmBlockReason(candidate, uploading, uploadReadiness)
  const confirmDisabled = attached || confirming || block !== null
  const confirmTitle = attached
    ? t('attach.hung')
    : confirming
      ? t('attach.confirmSending')
      : block === 'ready'
        ? t('attach.confirmNeedReady')
        : block === 'candidate'
          ? t('attach.confirmNeedCandidate')
          : undefined

  const statusLabel = useMemo(() => {
    if (attached) return t('attach.hung')
    if (confirming) return t('attach.confirmSending')
    if (!candidate) return t('attach.noCandidate')
    return t('attach.candidateOnly')
  }, [attached, candidate, confirming, t])

  function chooseFile(file: File) {
    setCandidate(fileCandidate(file.name))
    setStep('select')
    onFile?.(file)
  }

  function confirmAttach() {
    if (confirmDisabled || !candidate) return
    onConfirmAttach?.(candidate)
  }

  return (
    <section
      data-testid="attach-panel"
      className="mb-8 rounded-lg border border-border bg-panel p-6"
    >
      <header className="mb-4">
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
          {t('attach.title')}
        </p>
        <h2 className="mt-1 font-serif text-[1.15rem] text-ink">{t('attach.title')}</h2>
        <p className="mt-2 text-[13px] leading-6 text-muted">{t('attach.lead')}</p>
      </header>

      {topic.trim() ? (
        <p data-testid="attach-topic" className="mb-4 text-[13px] leading-6 text-ink">
          <span className="text-muted">{t('attach.topic')}：</span>
          {topic}
        </p>
      ) : null}

      {prefill && !attached ? (
        <p data-testid="attach-prefill-note" className="mb-4 text-[12px] leading-5 text-muted">
          {t('attach.prefillNote')}
        </p>
      ) : null}

      <ol
        data-testid="attach-steps"
        className="mb-5 flex flex-wrap gap-2"
      >
        {STEPS.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              data-testid={`attach-step-${item.id}`}
              aria-current={step === item.id ? 'step' : undefined}
              onClick={() => setStep(item.id)}
              className={`rounded-full px-3 py-1.5 text-[12px] transition-colors ${
                step === item.id
                  ? 'bg-ink text-white'
                  : 'border border-border bg-paper text-muted hover:text-ink'
              }`}
            >
              {t(item.labelKey)}
            </button>
          </li>
        ))}
      </ol>

      {step === 'find' && (
        <div data-testid="attach-find">
          <p className="text-[13px] leading-6 text-ink">{t('attach.findHint')}</p>
          <div
            data-testid="attach-catalog"
            className="mt-3 rounded-md border border-dashed border-border px-3 py-3"
          >
            <p className="text-[12px] font-medium text-ink">{t('attach.catalogLabel')}</p>
            <p className="mt-1 text-[12px] leading-5 text-muted">{t('attach.catalogEmpty')}</p>
            <p className="mt-1 text-[12px] leading-5 text-muted">{t('attach.catalogNote')}</p>
          </div>
          <button
            type="button"
            data-testid="attach-own-file"
            onClick={() => setStep('upload')}
            className="mt-3 rounded-full border border-border px-3.5 py-1.5 text-[13px] text-ink hover:bg-cream"
          >
            {t('attach.ownFile')}
          </button>
        </div>
      )}

      {step === 'select' && (
        <div data-testid="attach-select">
          <p className="text-[13px] leading-6 text-ink">{t('attach.selectHint')}</p>
          {candidate ? (
            <button
              type="button"
              data-testid="attach-select-candidate"
              onClick={() => {
                setCandidate(candidate)
              }}
              className="mt-3 w-full rounded-md border border-ink/15 bg-cream px-3 py-2 text-left text-[13px] text-ink"
            >
              <span className="block text-[11px] text-muted">{t('attach.candidate')}</span>
              {candidate.label}
            </button>
          ) : (
            <p className="mt-3 text-[13px] text-muted">{t('attach.noCandidate')}</p>
          )}
        </div>
      )}

      {step === 'upload' && (
        <div data-testid="attach-upload">
          <p className="mb-3 text-[13px] leading-6 text-ink">{t('attach.uploadHint')}</p>
          <CsvDropZone uploading={uploading} onBrowse={onBrowse} onFile={chooseFile} />
        </div>
      )}

      {step === 'confirm' && (
        <div data-testid="attach-confirm">
          <p className="text-[13px] leading-6 text-ink">
            {candidate ? t('attach.selectHint') : t('attach.confirmNeedCandidate')}
          </p>
        </div>
      )}

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
        <p data-testid="attach-candidate-status" className="text-[12px] text-muted">
          {candidate ? (
            <>
              <span data-testid="attach-candidate">{candidate.label}</span>
              {' · '}
              {statusLabel}
            </>
          ) : (
            statusLabel
          )}
        </p>
        <button
          type="button"
          data-testid="attach-confirm-btn"
          onClick={confirmAttach}
          disabled={confirmDisabled}
          title={confirmTitle}
          className="rounded-lg bg-accent px-4 py-2 text-[13px] font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {attached ? t('attach.hung') : t('attach.confirm')}
        </button>
      </div>

      {confirming ? (
        <p data-testid="attach-confirming" role="status" aria-live="polite" className="mt-2 text-[12px] text-muted">
          {t('attach.confirmSending')}
        </p>
      ) : null}
      {confirmError ? (
        <p data-testid="attach-confirm-error" role="alert" className="mt-2 text-[12px] text-danger">
          {confirmError}
        </p>
      ) : null}
    </section>
  )
}
