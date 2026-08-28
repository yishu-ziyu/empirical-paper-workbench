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

export type OutlinePart = { type: string; title: string }

export type PausePayload = {
  outline: OutlinePart[]
  render_kwargs: Record<string, number>
  decideChapters: DecideMode
}

const CATALOG: OutlinePart[] = [
  { type: 'intro', title: '引言' },
  { type: 'lit_review', title: '文献综述' },
  { type: 'data_desc', title: '数据描述' },
  { type: 'methods', title: '方法' },
  { type: 'results', title: '结果' },
  { type: 'conclusion', title: '结论' },
]

export interface WriteLoopProps {
  fileName?: string | null
  rows?: number | null
  cols?: number | null
  direction?: WriteDirection | null
  outline?: OutlinePart[]
  outlineLocked?: boolean
  hasDirection?: boolean
  hasOutline?: boolean
  hasChapter?: boolean
  isResultsPart?: boolean
  partIndex?: number
  agentPct?: number | null
  writeBusy?: boolean
  onAddMore?: () => void
  onGoPart1?: () => void
  onApplyGenerate?: (payload: PausePayload) => void
  onReviseOutline?: () => void
  onApproveOutline?: (outline: OutlinePart[]) => void
  onRefine?: (instruction: string) => void
}

function Decide({
  name,
  value,
  disabled,
  onChange,
}: {
  name: string
  value: DecideMode
  disabled?: boolean
  onChange: (next: DecideMode) => void
}) {
  const { t } = useT()
  return (
    <div className="mt-1 flex gap-3 text-[12px]">
      <label className="inline-flex items-center gap-1.5">
        <input
          type="radio"
          name={name}
          data-testid={`${name}-ai`}
          checked={value === 'ai'}
          disabled={disabled}
          onChange={() => onChange('ai')}
        />
        {t('write.aiDecides')}
      </label>
      <label className="inline-flex items-center gap-1.5">
        <input
          type="radio"
          name={name}
          data-testid={`${name}-me`}
          checked={value === 'me'}
          disabled={disabled}
          onChange={() => onChange('me')}
        />
        {t('write.iDecide')}
      </label>
    </div>
  )
}

function resizeOutline(current: OutlinePart[], n: number): OutlinePart[] {
  const count = Math.max(1, Math.min(CATALOG.length, Math.floor(n) || 1))
  if (count <= current.length) return current.slice(0, count)
  const used = new Set(current.map((ch) => ch.type))
  const next = [...current]
  for (const part of CATALOG) {
    if (next.length >= count) break
    if (!used.has(part.type)) {
      next.push({ ...part })
      used.add(part.type)
    }
  }
  return next
}

export default function WriteLoop({
  fileName,
  rows,
  cols,
  direction,
  outline = [],
  outlineLocked = false,
  hasDirection = false,
  hasOutline = false,
  hasChapter = false,
  isResultsPart = false,
  partIndex = 1,
  agentPct = null,
  writeBusy = false,
  onAddMore,
  onGoPart1,
  onApplyGenerate,
  onReviseOutline,
  onApproveOutline,
  onRefine,
}: WriteLoopProps) {
  const { t } = useT()
  const [chapters, setChapters] = useState<DecideMode>('ai')
  const [paragraphs, setParagraphs] = useState<DecideMode>('ai')
  const [tables, setTables] = useState<DecideMode>('ai')
  const [figures, setFigures] = useState<DecideMode>('ai')
  const [draftOutline, setDraftOutline] = useState<OutlinePart[] | null>(null)
  const [paragraphCount, setParagraphCount] = useState(3)
  const [tableCount, setTableCount] = useState(1)
  const [figureCount, setFigureCount] = useState(1)
  const [refine, setRefine] = useState('')
  const [showInfoFull, setShowInfoFull] = useState(false)
  const controls = Array.isArray(direction?.controls)
    ? direction?.controls.join(', ')
    : direction?.controls || '—'

  const currentOutline = chapters === 'me' && draftOutline?.length ? draftOutline : outline

  function chooseChapters(next: DecideMode) {
    setChapters(next)
    setDraftOutline(next === 'me' ? outline.map((ch) => ({ type: ch.type, title: ch.title })) : null)
  }

  function pausePayload(): PausePayload {
    const render_kwargs: Record<string, number> = {}
    if (paragraphs === 'me') render_kwargs.paragraphs = paragraphCount
    if (isResultsPart && tables === 'me') render_kwargs.tables = tableCount
    if (isResultsPart && figures === 'me') render_kwargs.figures = figureCount
    return { outline: currentOutline, render_kwargs, decideChapters: chapters }
  }

  function sendRefine() {
    if (writeBusy) return
    onRefine?.(refine)
  }

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
          {hasOutline && !showInfoFull ? (
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px]">
              <span className="font-medium text-accent">✓</span>
              <span className="text-ink">{t('write.infoTitle')}</span>
              <span className="text-muted">
                {direction?.dv || '—'} ~ {direction?.iv || '—'} · {direction?.method || 'OLS'}
              </span>
              <button
                type="button"
                data-testid="info-expand"
                onClick={() => setShowInfoFull(true)}
                className="ml-auto text-muted underline-offset-2 hover:text-ink hover:underline"
              >
                {t('write.addMore')}
              </button>
            </div>
          ) : (
          <>
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
              <dd data-testid="info-controls" className="text-ink">{controls}</dd>
            </div>
            <div>
              <dt className="text-muted">{t('write.infoMethod')}</dt>
              <dd className="text-ink">{direction?.method || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted">{t('write.infoDataset')}</dt>
              <dd data-testid="info-dataset" className="text-ink">
                {fileName
                  ? rows != null
                    ? `${fileName} (${rows})`
                    : fileName
                  : 'CSV'}
              </dd>
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
          </>
          )}
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
            <Decide name="chapters" value={chapters} disabled={outlineLocked} onChange={chooseChapters} />
            {chapters === 'me' && !outlineLocked ? (
              <div className="mt-2 space-y-2" data-testid="pause-chapter-editor">
                <label className="flex items-center gap-2 text-[12px] text-ink">
                  {t('write.chapters')}
                  <input
                    type="number"
                    min={1}
                    max={CATALOG.length}
                    data-testid="pause-chapter-count"
                    value={currentOutline.length}
                    onChange={(e) => setDraftOutline(resizeOutline(currentOutline, Number(e.target.value)))}
                    className="w-16 rounded border border-border bg-bg px-2 py-1"
                  />
                </label>
                <ul className="space-y-1">
                  {currentOutline.map((ch) => (
                    <li key={ch.type}>
                      <label className="inline-flex items-center gap-1.5 text-[12px] text-ink">
                        <input
                          type="checkbox"
                          data-testid={`pause-keep-${ch.type}`}
                          checked
                          onChange={() => {
                            const next = currentOutline.filter((item) => item.type !== ch.type)
                            setDraftOutline(next.length ? next : currentOutline)
                          }}
                        />
                        {ch.title}
                      </label>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
          <div className="mt-2">
            <p className="text-[12px] text-muted">{t('write.paragraphs')}</p>
            <Decide name="paragraphs" value={paragraphs} onChange={setParagraphs} />
            {paragraphs === 'me' ? (
              <input
                type="number"
                min={1}
                max={12}
                data-testid="pause-paragraphs"
                value={paragraphCount}
                onChange={(e) => setParagraphCount(Math.max(1, Number(e.target.value) || 1))}
                className="mt-1 w-16 rounded border border-border bg-bg px-2 py-1 text-[12px]"
              />
            ) : null}
          </div>
          {isResultsPart ? (
            <>
              <div className="mt-2">
                <p className="text-[12px] text-muted">{t('write.tables')}</p>
                <Decide name="tables" value={tables} onChange={setTables} />
                {tables === 'me' ? (
                  <input
                    type="number"
                    min={0}
                    max={8}
                    data-testid="pause-tables"
                    value={tableCount}
                    onChange={(e) => setTableCount(Math.max(0, Number(e.target.value) || 0))}
                    className="mt-1 w-16 rounded border border-border bg-bg px-2 py-1 text-[12px]"
                  />
                ) : null}
              </div>
              <div className="mt-2">
                <p className="text-[12px] text-muted">{t('write.figures')}</p>
                <Decide name="figures" value={figures} onChange={setFigures} />
                {figures === 'me' ? (
                  <input
                    type="number"
                    min={0}
                    max={8}
                    data-testid="pause-figures"
                    value={figureCount}
                    onChange={(e) => setFigureCount(Math.max(0, Number(e.target.value) || 0))}
                    className="mt-1 w-16 rounded border border-border bg-bg px-2 py-1 text-[12px]"
                  />
                ) : null}
              </div>
            </>
          ) : null}
          <button
            type="button"
            data-testid="pause-apply"
            onClick={() => onApplyGenerate?.(pausePayload())}
            disabled={writeBusy}
            className="mt-4 rounded-full border border-black/[0.12] px-3.5 py-1.5 text-[12px] text-ink transition-colors duration-200 hover:bg-black/[0.03] disabled:opacity-40"
          >
            {t('write.apply')}
          </button>
          {hasOutline && !outlineLocked ? (
            <div data-testid="outline-approve" className="mt-3 flex flex-wrap gap-2 border-t border-black/[0.06] pt-3">
              <button
                type="button"
                data-testid="outline-approve-btn"
                disabled={!onApproveOutline || writeBusy}
                onClick={() => onApproveOutline?.(currentOutline)}
                className="rounded-full bg-accent px-3.5 py-1.5 text-[12px] text-white disabled:opacity-40"
              >
                {t('write.approveOutline')}
              </button>
              <button
                type="button"
                data-testid="outline-revise-btn"
                onClick={onReviseOutline}
                className="rounded-full border border-black/[0.08] px-3 py-1.5 text-[12px]"
              >
                {t('write.reviseOutline')}
              </button>
            </div>
          ) : null}
        </section>
      ) : null}

      {hasChapter ? (
        <section data-testid="refine-chat" className="composer-shell p-3">
          <p className="px-1 pb-2 text-[12px] text-muted">{t('write.refineHint')}</p>
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-black/[0.08] text-[18px] leading-none">
              +
            </span>
            <input
              data-testid="refine-input"
              aria-label={t('write.refine')}
              value={refine}
              disabled={writeBusy}
              onChange={(e) => setRefine(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  sendRefine()
                }
              }}
              className="min-w-0 flex-1 bg-transparent text-[13px] outline-none"
              placeholder={t('write.refine')}
            />
            <button
              type="button"
              data-testid="refine-send-btn"
              onClick={sendRefine}
              disabled={writeBusy}
              className="rounded-full bg-ink px-3 py-1.5 text-[11px] text-white disabled:opacity-40"
            >
              {t('write.refineSend')}
            </button>
          </div>
        </section>
      ) : null}
    </div>
  )
}
