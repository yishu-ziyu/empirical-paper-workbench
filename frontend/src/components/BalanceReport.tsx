// 面板平衡性报告 (T-05 sub-step 7)
// panel_id / time_col 输入 → POST /sessions/{id}/balance → 渲染平衡性指标表格
//
// Stage D: 删除手写 BalanceResult interface，改 import types/api.ts 的
// BalanceResponse（balanced / unbalanced / n_periods / attrition_rate）。
// 修复漂移 1：字段名 balanced_n/unbalanced_n → balanced/unbalanced，新增 n_periods。

import { useState } from 'react'
import type { components } from '../types/api'

type BalanceResponse = components['schemas']['BalanceResponse']

export interface BalanceReportProps {
  sessionId: string
}

const API_BASE = 'http://localhost:8000'

function pct(rate: number): string {
  return `${(rate * 100).toFixed(0)}%`
}

export function BalanceReport({ sessionId }: BalanceReportProps) {
  const [panelId, setPanelId] = useState('')
  const [timeCol, setTimeCol] = useState('')
  const [result, setResult] = useState<BalanceResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function check() {
    setLoading(true)
    setError(null)
    try {
      const resp = await fetch(`${API_BASE}/sessions/${sessionId}/balance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ panel_id: panelId, time_col: timeCol }),
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(`${resp.status} ${err.detail ?? ''}`.trim())
      }
      const data: BalanceResponse = await resp.json()
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div data-testid="balance-report" className="space-y-4 rounded-lg border border-gray-200 p-4">
      <h2 className="text-lg font-semibold">面板平衡性检查</h2>

      <div className="flex flex-wrap items-end gap-2">
        <div className="flex flex-col">
          <label className="text-xs text-gray-600">个体 ID 列</label>
          <input
            data-testid="br-panel-id-input"
            type="text"
            value={panelId}
            onChange={(e) => setPanelId(e.target.value)}
            placeholder="如 id"
            className="rounded border border-gray-300 px-2 py-1 text-sm"
          />
        </div>

        <div className="flex flex-col">
          <label className="text-xs text-gray-600">时间列</label>
          <input
            data-testid="br-time-col-input"
            type="text"
            value={timeCol}
            onChange={(e) => setTimeCol(e.target.value)}
            placeholder="如 year"
            className="rounded border border-gray-300 px-2 py-1 text-sm"
          />
        </div>

        <button
          data-testid="br-check"
          onClick={check}
          disabled={loading}
          className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '检查中...' : '检查平衡性'}
        </button>
      </div>

      {error && <div className="text-sm text-red-500">{error}</div>}

      {result && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-1">指标</th>
              <th className="py-1">值</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="py-1">平衡个体数</td>
              <td data-testid="br-balanced" className="py-1 font-mono font-semibold">
                {result.balanced}
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-1">不平衡个体数</td>
              <td data-testid="br-unbalanced" className="py-1 font-mono font-semibold">
                {result.unbalanced}
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-1">期数</td>
              <td data-testid="br-n-periods" className="py-1 font-mono font-semibold">
                {result.n_periods}
              </td>
            </tr>
            <tr className="border-b">
              <td className="py-1">流失率 (attrition)</td>
              <td data-testid="br-attrition-rate" className="py-1 font-mono font-semibold">
                {pct(result.attrition_rate)}
              </td>
            </tr>
          </tbody>
        </table>
      )}
    </div>
  )
}

export default BalanceReport
