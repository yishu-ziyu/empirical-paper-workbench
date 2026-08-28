// 样本筛选条件构建器 (T-05 sub-step 6)
// 列 / 操作符 / 值 → 添加条件 → 应用筛选 → POST /sessions/{id}/filter → 显示前后样本量

import { useState } from 'react'
import { API_BASE } from '../lib/apiBase'
import { useT } from '../lib/i18n'
import type { components } from '../types/api'

type Condition = components['schemas']['FilterConditionItem']
type FilterResult = components['schemas']['FilterResultResponse']

export interface SampleFilterProps {
  sessionId: string
}

const OPERATORS = ['>=', '<=', '>', '<', '==', '!=']

function parseVal(raw: string): string | number {
  const n = Number(raw)
  return isNaN(n) ? raw : n
}

export function SampleFilter({ sessionId }: SampleFilterProps) {
  const { t } = useT()
  const [col, setCol] = useState('')
  const [op, setOp] = useState('>=')
  const [val, setVal] = useState('')
  const [conditions, setConditions] = useState<Condition[]>([])
  const [result, setResult] = useState<FilterResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function addCondition() {
    if (!col) return
    setConditions([...conditions, { col, op, val: parseVal(val) }])
    setCol('')
    setVal('')
  }

  async function apply() {
    setLoading(true)
    setError(null)
    try {
      const resp = await fetch(`${API_BASE}/sessions/${sessionId}/filter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conditions }),
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(`${resp.status} ${err.detail ?? ''}`.trim())
      }
      const data: FilterResult = await resp.json()
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div data-testid="sample-filter" className="space-y-4 rounded-lg border border-gray-200 p-4">
      <h2 className="text-lg font-semibold">{t('filter.title')}</h2>

      <div className="flex flex-wrap items-end gap-2">
        <div className="flex flex-col">
          <label className="text-xs text-gray-600">{t('filter.col')}</label>
          <input
            data-testid="sf-column-input"
            type="text"
            value={col}
            onChange={(e) => setCol(e.target.value)}
            placeholder={t('filter.colPlaceholder')}
            className="rounded border border-gray-300 px-2 py-1 text-sm"
          />
        </div>

        <div className="flex flex-col">
          <label className="text-xs text-gray-600">{t('filter.op')}</label>
          <select
            data-testid="sf-op-select"
            value={op}
            onChange={(e) => setOp(e.target.value)}
            className="rounded border border-gray-300 px-2 py-1 text-sm"
          >
            {OPERATORS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col">
          <label className="text-xs text-gray-600">{t('filter.value')}</label>
          <input
            data-testid="sf-value-input"
            type="text"
            value={val}
            onChange={(e) => setVal(e.target.value)}
            placeholder={t('filter.valuePlaceholder')}
            className="rounded border border-gray-300 px-2 py-1 text-sm"
          />
        </div>

        <button
          data-testid="sf-add-condition"
          onClick={addCondition}
          className="rounded bg-gray-100 px-3 py-1 text-sm text-gray-700 hover:bg-gray-200"
        >
          {t('filter.addCondition')}
          </button>
      </div>

      {conditions.length > 0 && (
        <div>
          <h3 className="mb-2 text-sm font-medium text-gray-700">{t('filter.conditions')}</h3>
          <ul className="space-y-1">
            {conditions.map((c, i) => (
              <li
                key={i}
                data-testid={`sf-condition-${i}`}
                className="rounded bg-gray-50 px-2 py-1 font-mono text-sm"
              >
                {c.col} {c.op} {String(c.val)}
              </li>
            ))}
          </ul>
        </div>
      )}

      <button
        data-testid="sf-apply"
        onClick={apply}
        disabled={loading || conditions.length === 0}
        className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? t('filter.applying') : t('filter.apply')}
      </button>

      {error && <div className="text-sm text-red-500">{error}</div>}

      {result && (
        <div className="rounded bg-blue-50 p-3 text-sm">
          <p>
            {t('filter.nBefore')}：<span data-testid="sf-n-before" className="font-mono font-semibold">{result.n_before}</span>
          </p>
          <p>
            {t('filter.nAfter')}：<span data-testid="sf-n-after" className="font-mono font-semibold">{result.n_after}</span>
          </p>
        </div>
      )}
    </div>
  )
}

export default SampleFilter
