import { useState } from 'react'
import { useT } from '../lib/i18n'

export type DecideMode = 'ai' | 'me'

export type WriteDirection = {
  question?: string
  dv?: string
  iv?: string
  controls?: string[] | string
  method?: string
  template?: string
}

export interface WriteLoopProps {
  fileName?: string | null
  rows?: number | null
  cols?: number | null
  direction?: WriteDirection | null
  hasDirection?: boolean
  hasOutline?: boolean
  hasChapter?: boolean
  isResultsPart?: boolean
  partIndex?: number
  agentPct?: number | null
  onAddMore?: () => void
  onGoPart1?: () => void
  onApplyGenerate?: () => void
  onReviseOutline?: () => void
  onApproveOutline?: () => void
}

function Decide({
  name,
  value,
  onChange,
}: {
  name: string
  value: DecideMode
  onChange: (next: DecideMode) => void
}) {
  const { t } = useT()
  return (
    <div className="mt-1 flex gap-3 text-[12px]">
      <label className="inline-flex items-center gap-1.5">
        <input
          type="radio"
          name={name}
          checked={value === 'ai'}
          onChange={() => onChange('ai')}
        />
        {t('write.aiDecides')}
      </label>
      <label className="inline-flex items-center gap-1.5">
        <input
          type="radio"
          name={name}
          checked={value === 'me'}
          onChange={() => onChange('me')}
        />
        {t('write.iDecide')}
      </label>
    </div>
  )
}

export default function WriteLoop({
  fileName,
  rows,
  cols,
  direction,
  hasDirection = false,
  hasOutline = false,
  hasChapter = false,
  isResultsPart = false,
  partIndex = 1,
  agentPct = null,
  onAddMore,
  onGoPart1,
  onApplyGenerate,
  onReviseOutline,
  onApproveOutline,
}: WriteLoopProps) {
  const { t } = useT()
  const [chapters, setChapters] = useState<DecideMode>('ai')
  const [paragraphs, setParagraphs] = useState<DecideMode>('ai')
  const [tables, setTables] = useState<DecideMode>('ai')
  const [figures, setFigures] = useState<DecideMode>('ai')
  const [refine, setRefine] = useState('')
  const controls = Array.isArray(direction?.controls)
    ? direction?.controls.join(', ')
    : direction?.controls || '—'

  return (
    <div className="mb-6 space-y-3">
      {fileName ? (
        <section data-testid="session-file" className="thread-card px-4 py-3">
          <p className="font-mono text-[12px] text-ink">{fileName}</p>
          {rows != null && cols != null ? (
            <p className="mt-1 text-[12px] text-muted">
              {t('write.fileRows').replace('{rows}', String(rows)).replace('{cols}', String(cols))}
            </p>
          ) : null}
        </section>
      ) : null}

      {agentPct != null ? (
        <p data-testid="paper-agent" className="rounded-xl bg-ink px-4 py-3 text-[13px] text-white">
          {t('write.agent').replace('{pct}', String(agentPct))}
        </p>
      ) : null}

      {hasDirection ? (
        <section data-testid="info-confirm" className="thread-card px-4 py-4">
          <h3 className="font-serif text-[1.05rem] text-ink">{t('write.infoTitle')}</h3>
          <dl className="mt-3 space-y-2 text-[12px] leading-5">
            <div>
              <dt className="text-muted">{t('write.infoBasic')}</dt>
              <dd className="text-ink">{direction?.question || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted">{t('write.infoVars')}</dt>
              <dd className="text-ink">
                {t('write.y')} {direction?.dv || '—'} · {t('write.x')} {direction?.iv || '—'}
              </dd>
            </div>
            <div>
              <dt className="text-muted">{t('write.infoControls')}</dt>
              <dd className="text-ink">{controls}</dd>
            </div>
            <div>
              <dt className="text-muted">{t('write.infoMethod')}</dt>
              <dd className="text-ink">{direction?.method || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted">{t('write.infoDataset')}</dt>
              <dd className="text-ink">{fileName || 'CSV'}</dd>
            </div>
            <div>
              <dt className="text-muted">{t('write.infoOutput')}</dt>
              <dd className="text-ink">
                {t('guide.statExport')} · {t('guide.statCode')}
              </dd>
            </div>
          </dl>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              data-testid="info-add-more"
              onClick={onAddMore}
              className="rounded-full border border-black/[0.08] px-3 py-1.5 text-[12px]"
            >
              {t('write.addMore')}
            </button>
            <button
              type="button"
              data-testid="info-go-part1"
              onClick={onGoPart1}
              className="rounded-full bg-ink px-3 py-1.5 text-[12px] text-white"
            >
              {t('write.goPart1')}
            </button>
          </div>
        </section>
      ) : null}

      {hasOutline ? (
        <section data-testid="chapter-pause" className="thread-card px-4 py-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-warning">{t('write.pause')}</p>
          <p className="mt-2 text-[12px] leading-5 text-ink">
            {t('write.y')} {direction?.dv || '—'} · {t('write.x')} {direction?.iv || '—'} · {direction?.method || 'OLS'}
          </p>
          <h3 className="mt-3 font-serif text-[1.05rem] text-ink">
            {t('write.configPart').replace('{n}', String(partIndex))}
          </h3>
          <div className="mt-3">
            <p className="text-[12px] text-muted">{t('write.chapters')}</p>
            <Decide name="chapters" value={chapters} onChange={setChapters} />
          </div>
          <div className="mt-2">
            <p className="text-[12px] text-muted">{t('write.paragraphs')}</p>
            <Decide name="paragraphs" value={paragraphs} onChange={setParagraphs} />
          </div>
          {isResultsPart ? (
            <>
              <div className="mt-2">
                <p className="text-[12px] text-muted">{t('write.tables')}</p>
                <Decide name="tables" value={tables} onChange={setTables} />
              </div>
              <div className="mt-2">
                <p className="text-[12px] text-muted">{t('write.figures')}</p>
                <Decide name="figures" value={figures} onChange={setFigures} />
              </div>
            </>
          ) : null}
          <button
            type="button"
            data-testid="pause-apply"
            onClick={onApplyGenerate}
            className="mt-4 rounded-full bg-accent px-3.5 py-1.5 text-[12px] text-white"
          >
            {t('write.apply')}
          </button>
        </section>
      ) : null}

      {hasOutline ? (
        <div data-testid="outline-approve" className="flex flex-wrap gap-2">
          <button
            type="button"
            data-testid="outline-revise-btn"
            onClick={onReviseOutline}
            className="rounded-full border border-black/[0.08] px-3 py-1.5 text-[12px]"
          >
            {t('write.reviseOutline')}
          </button>
          <button
            type="button"
            data-testid="outline-approve-btn"
            onClick={onApproveOutline}
            className="rounded-full bg-accent px-3 py-1.5 text-[12px] text-white"
          >
            {t('write.approveOutline')}
          </button>
        </div>
      ) : null}

      {hasChapter ? (
        <section data-testid="refine-chat" className="composer-shell p-3">
          <p className="px-1 pb-2 text-[12px] text-muted">{t('write.refineHint')}</p>
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-black/[0.08] text-[18px] leading-none">
              +
            </span>
            <input
              aria-label={t('write.refine')}
              value={refine}
              onChange={(e) => setRefine(e.target.value)}
              className="min-w-0 flex-1 bg-transparent text-[13px] outline-none"
              placeholder={t('write.refine')}
            />
            <span className="text-[11px] text-muted">{t('write.refineSend')}</span>
          </div>
        </section>
      ) : null}
    </div>
  )
}
