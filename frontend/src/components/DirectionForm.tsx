// 研究方向输入表单
// 四问 + 发动机五类方法。方法变了，多出来的列才出现。

import { useState, type FormEvent } from 'react'
import { useT } from '../lib/i18n'
import MethodSelector, { TEMPLATES } from './MethodSelector'

export interface DirectionFormData {
  question: string
  dv: string
  iv: string
  controls: string[]
  method: string
  template: string
  instrument?: string
  time_col?: string
  id_col?: string
  first_treat_col?: string
  running_var?: string
  cutoff?: number
  unit_col?: string
  treatment_time?: string
}

function methodKind(method: string): 'ols' | 'did' | 'iv' | 'rd' | 'scm' | '' {
  const m = method.toLowerCase()
  if (!m) return ''
  if (m.includes('synth')) return 'scm'
  if (m.includes('rd') || m.includes('rkd')) return 'rd'
  if (
    m.includes('iv') ||
    m.includes('2sls') ||
    m.includes('liml') ||
    m.includes('jive') ||
    m.includes('gmm') ||
    m.includes('bartik') ||
    m.includes('shift')
  ) {
    return 'iv'
  }
  if (m.includes('did') || m.includes('diff') || m.includes('event')) return 'did'
  return 'ols'
}

export type DirectionFormInitial = {
  question?: string
  dv?: string
  iv?: string
  controls?: string
  method?: string
  template?: string
  instrument?: string
  time_col?: string
  id_col?: string
  first_treat_col?: string
  running_var?: string
  cutoff?: number
  unit_col?: string
  treatment_time?: string
}

export interface DirectionFormProps {
  onSubmit: (data: DirectionFormData) => void
  initialQuestion?: string
  initial?: DirectionFormInitial
  columns?: string[]
}

export default function DirectionForm({
  onSubmit,
  initialQuestion = '',
  initial,
  columns = [],
}: DirectionFormProps) {
  const { t } = useT()
  const [question, setQuestion] = useState(initial?.question ?? initialQuestion)
  const [dv, setDv] = useState(initial?.dv ?? '')
  const [iv, setIv] = useState(initial?.iv ?? '')
  const [controls, setControls] = useState(initial?.controls ?? '')
  const [method, setMethod] = useState(initial?.method ?? '')
  const [template, setTemplate] = useState(initial?.template ?? 'undergrad')
  const [instrument, setInstrument] = useState(initial?.instrument ?? '')
  const [timeCol, setTimeCol] = useState(initial?.time_col ?? '')
  const [idCol, setIdCol] = useState(initial?.id_col ?? '')
  const [firstTreatCol, setFirstTreatCol] = useState(initial?.first_treat_col ?? '')
  const [runningVar, setRunningVar] = useState(initial?.running_var ?? '')
  const [cutoff, setCutoff] = useState(initial?.cutoff != null ? String(initial.cutoff) : '')
  const [unitCol, setUnitCol] = useState(initial?.unit_col ?? '')
  const [treatmentTime, setTreatmentTime] = useState(initial?.treatment_time ?? '')
  const kind = methodKind(method)
  const canSubmit = Boolean(question.trim() && dv.trim() && iv.trim() && method)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!canSubmit) return
    const controlsArr = controls
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    const payload: DirectionFormData = {
      question,
      dv,
      iv,
      controls: controlsArr,
      method,
      template,
    }
    if (kind === 'iv' && instrument.trim()) payload.instrument = instrument.trim()
    if (kind === 'did') {
      if (timeCol.trim()) payload.time_col = timeCol.trim()
      if (idCol.trim()) payload.id_col = idCol.trim()
      if (firstTreatCol.trim()) payload.first_treat_col = firstTreatCol.trim()
    }
    if (kind === 'rd') {
      if (runningVar.trim()) payload.running_var = runningVar.trim()
      if (cutoff.trim()) payload.cutoff = Number(cutoff)
    }
    if (kind === 'scm') {
      if (unitCol.trim()) payload.unit_col = unitCol.trim()
      if (treatmentTime.trim()) payload.treatment_time = treatmentTime.trim()
    }
    onSubmit(payload)
  }

  return (
    <form
      data-testid="direction-form"
      onSubmit={handleSubmit}
      className="space-y-4"
    >
      {columns.length > 0 ? (
        <p data-testid="data-columns" className="text-xs leading-5 text-muted">
          {t('direction.columns')}
          {columns.join('、')}
        </p>
      ) : null}
      <label className="block">
        <span className="block text-xs text-muted">{t('direction.question')}</span>
        <textarea
          aria-label={t('direction.question')}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
        />
      </label>
      <label className="block">
        <span className="block text-xs text-muted" title={t('direction.dvHint')}>{t('direction.dv')}</span>
        <input
          aria-label={t('direction.dv')}
          value={dv}
          onChange={(e) => setDv(e.target.value)}
          className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
        />
      </label>
      <label className="block">
        <span className="block text-xs text-muted" title={t('direction.ivHint')}>{t('direction.iv')}</span>
        <input
          aria-label={t('direction.iv')}
          value={iv}
          onChange={(e) => setIv(e.target.value)}
          className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
        />
      </label>
      <label className="block">
        <span className="block text-xs text-muted" title={t('direction.controlsHint')}>{t('direction.controls')}</span>
        <input
          aria-label={t('direction.controls')}
          value={controls}
          onChange={(e) => setControls(e.target.value)}
          className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
        />
      </label>
      <div className="block">
        <span className="block text-xs text-muted">{t('direction.method')}</span>
        <MethodSelector value={method} onChange={setMethod} />
      </div>
      {kind === 'iv' && (
        <label className="block">
          <span className="block text-xs text-muted">{t('direction.instrument')}</span>
          <input
            aria-label={t('direction.instrument')}
            value={instrument}
            onChange={(e) => setInstrument(e.target.value)}
            className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
          />
        </label>
      )}
      {kind === 'did' && (
        <>
          <label className="block">
            <span className="block text-xs text-muted">{t('direction.timeCol')}</span>
            <input
              aria-label={t('direction.timeCol')}
              value={timeCol}
              onChange={(e) => setTimeCol(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
            />
          </label>
          <label className="block">
            <span className="block text-xs text-muted">{t('direction.idCol')}</span>
            <input
              aria-label={t('direction.idCol')}
              value={idCol}
              onChange={(e) => setIdCol(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
            />
          </label>
          <label className="block">
            <span className="block text-xs text-muted">{t('direction.firstTreatCol')}</span>
            <input
              aria-label={t('direction.firstTreatCol')}
              value={firstTreatCol}
              onChange={(e) => setFirstTreatCol(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
            />
          </label>
        </>
      )}
      {kind === 'rd' && (
        <>
          <label className="block">
            <span className="block text-xs text-muted">{t('direction.runningVar')}</span>
            <input
              aria-label={t('direction.runningVar')}
              value={runningVar}
              onChange={(e) => setRunningVar(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
            />
          </label>
          <label className="block">
            <span className="block text-xs text-muted">{t('direction.cutoff')}</span>
            <input
              aria-label={t('direction.cutoff')}
              value={cutoff}
              onChange={(e) => setCutoff(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
            />
          </label>
        </>
      )}
      {kind === 'scm' && (
        <>
          <label className="block">
            <span className="block text-xs text-muted">{t('direction.unitCol')}</span>
            <input
              aria-label={t('direction.unitCol')}
              value={unitCol}
              onChange={(e) => setUnitCol(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
            />
          </label>
          <label className="block">
            <span className="block text-xs text-muted">{t('direction.treatmentTime')}</span>
            <input
              aria-label={t('direction.treatmentTime')}
              value={treatmentTime}
              onChange={(e) => setTreatmentTime(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
            />
          </label>
        </>
      )}
      <label className="block">
        <span className="block text-xs text-muted">{t('direction.template')}</span>
        <select
          aria-label={t('direction.template')}
          value={template}
          onChange={(e) => setTemplate(e.target.value)}
          className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
        >
          {TEMPLATES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </label>
      <button
        type="submit"
        disabled={!canSubmit}
        className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
      >
        {t('direction.submit')}
      </button>
    </form>
  )
}
