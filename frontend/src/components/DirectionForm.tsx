// 研究方向输入表单 (T-06)
// 用户输入：研究问题 / 因变量 / 自变量 / 控制变量 / 方法 (38 种) / 模板
// 提交 → onSubmit({question, dv, iv, controls[], method, template})

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
}

export interface DirectionFormProps {
  onSubmit: (data: DirectionFormData) => void
}

export default function DirectionForm({ onSubmit }: DirectionFormProps) {
  const { t } = useT()
  const [question, setQuestion] = useState('')
  const [dv, setDv] = useState('')
  const [iv, setIv] = useState('')
  const [controls, setControls] = useState('')
  const [method, setMethod] = useState('')
  const [template, setTemplate] = useState('cn_journal')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const controlsArr = controls
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    onSubmit({
      question,
      dv,
      iv,
      controls: controlsArr,
      method,
      template,
    })
  }

  return (
    <form
      data-testid="direction-form"
      onSubmit={handleSubmit}
      className="space-y-3"
    >
      <label className="block">
        <span className="block text-xs text-muted">{t('direction.question')}</span>
        <textarea
          aria-label={t('direction.question')}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="mt-1 w-full rounded border border-border p-2"
        />
      </label>
      <label className="block">
        <span className="block text-xs text-muted">{t('direction.dv')}</span>
        <input
          aria-label={t('direction.dv')}
          value={dv}
          onChange={(e) => setDv(e.target.value)}
          className="mt-1 w-full rounded border border-border p-2"
        />
      </label>
      <label className="block">
        <span className="block text-xs text-muted">{t('direction.iv')}</span>
        <input
          aria-label={t('direction.iv')}
          value={iv}
          onChange={(e) => setIv(e.target.value)}
          className="mt-1 w-full rounded border border-border p-2"
        />
      </label>
      <label className="block">
        <span className="block text-xs text-muted">{t('direction.controls')}</span>
        <input
          aria-label={t('direction.controls')}
          value={controls}
          onChange={(e) => setControls(e.target.value)}
          className="mt-1 w-full rounded border border-border p-2"
        />
      </label>
      <div className="block">
        <span className="block text-xs text-muted">{t('direction.method')}</span>
        <MethodSelector value={method} onChange={setMethod} />
      </div>
      <label className="block">
        <span className="block text-xs text-muted">{t('direction.template')}</span>
        <select
          aria-label={t('direction.template')}
          value={template}
          onChange={(e) => setTemplate(e.target.value)}
          className="mt-1 w-full rounded border border-border p-2"
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
        className="rounded bg-accent px-3 py-1 text-sm text-white"
      >
        {t('direction.submit')}
      </button>
    </form>
  )
}
