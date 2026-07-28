// 研究方向输入表单 (T-06)
// 用户输入：研究问题 / 因变量 / 自变量 / 控制变量 / 方法 (38 种) / 模板
// 提交 → onSubmit({question, dv, iv, controls[], method, template})

import { useState, type FormEvent } from 'react'
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
        <span className="block text-xs text-muted">研究问题</span>
        <textarea
          aria-label="研究问题"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="mt-1 w-full rounded border border-border p-2"
        />
      </label>
      <label className="block">
        <span className="block text-xs text-muted">因变量</span>
        <input
          aria-label="因变量"
          value={dv}
          onChange={(e) => setDv(e.target.value)}
          className="mt-1 w-full rounded border border-border p-2"
        />
      </label>
      <label className="block">
        <span className="block text-xs text-muted">自变量</span>
        <input
          aria-label="自变量"
          value={iv}
          onChange={(e) => setIv(e.target.value)}
          className="mt-1 w-full rounded border border-border p-2"
        />
      </label>
      <label className="block">
        <span className="block text-xs text-muted">控制变量 (逗号分隔)</span>
        <input
          aria-label="控制变量"
          value={controls}
          onChange={(e) => setControls(e.target.value)}
          className="mt-1 w-full rounded border border-border p-2"
        />
      </label>
      <div className="block">
        <span className="block text-xs text-muted">方法</span>
        <MethodSelector value={method} onChange={setMethod} />
      </div>
      <label className="block">
        <span className="block text-xs text-muted">模板</span>
        <select
          aria-label="模板"
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
        提交
      </button>
    </form>
  )
}
