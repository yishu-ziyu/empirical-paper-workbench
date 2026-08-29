// 变量构造表单 (T-05 sub-step 5)
// 类型下拉 + 列名输入 → POST /sessions/{id}/transform → 显示已构造变量列表

import { useState } from 'react'
import { API_BASE, apiFetch } from '../lib/apiBase'
import { useT } from '../lib/i18n'
import type { components } from '../types/api'

type TransformResult = components['schemas']['TransformResponse']

export interface VariableConstructorProps {
  sessionId: string
}

const TYPES: { id: string; label: string }[] = [
  { id: 'log_transform', label: '对数变换 (log)' },
  { id: 'onehot', label: 'One-Hot 编码' },
  { id: 'label', label: 'Label 编码' },
  { id: 'bin', label: '分箱 (bin)' },
  { id: 'interaction', label: '交互项' },
  { id: 'policy_dummy', label: '政策虚拟变量' },
]

export function VariableConstructor({ sessionId }: VariableConstructorProps) {
  const { t } = useT()
  const [vtype, setVtype] = useState('log_transform')
  const [column, setColumn] = useState('')
  const [constructed, setConstructed] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submit() {
    setLoading(true)
    setError(null)
    try {
      const resp = await apiFetch(`${API_BASE}/sessions/${sessionId}/transform`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: vtype, column }),
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(`${resp.status} ${err.detail ?? ''}`.trim())
      }
      const data: TransformResult = await resp.json()
      setConstructed(data.constructed_vars ?? [])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div data-testid="variable-constructor" className="space-y-4 rounded-lg border border-gray-200 p-4">
      <h2 className="text-lg font-semibold">{t('vc.title')}</h2>

      <div className="flex flex-col gap-2">
        <label className="text-sm text-gray-600">{t('vc.type')}</label>
        <select
          data-testid="vc-type-select"
          value={vtype}
          onChange={(e) => setVtype(e.target.value)}
          className="rounded border border-gray-300 px-2 py-1 text-sm"
        >
          {TYPES.map((t) => (
            <option key={t.id} value={t.id}>
              {t.label}
            </option>
          ))}
        </select>

        <label className="text-sm text-gray-600">{t('vc.col')}</label>
        <input
          data-testid="vc-column-input"
          type="text"
          value={column}
          onChange={(e) => setColumn(e.target.value)}
          placeholder={t('vc.colPlaceholder')}
          className="rounded border border-gray-300 px-2 py-1 text-sm"
        />

        <button
          data-testid="vc-submit"
          onClick={submit}
          disabled={loading}
          className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? t('vc.constructing') : t('vc.construct')}
        </button>
      </div>

      {error && <div className="text-sm text-red-500">{error}</div>}

      {constructed.length > 0 && (
        <div>
          <h3 className="mb-2 text-sm font-medium text-gray-700">{t('vc.constructed')}</h3>
          <ul className="space-y-1">
            {constructed.map((v) => (
              <li
                key={v}
                data-testid={`vc-constructed-${v}`}
                className="rounded bg-gray-50 px-2 py-1 font-mono text-sm"
              >
                {v}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default VariableConstructor
