// EDA 侧边栏组件 (T-03)
// 6 个按钮 → 调 POST /sessions/{id}/eda → 渲染描述统计表 / 相关性矩阵 / 缺失值表
// 数据流：按钮点击 → fetch POST → {columns, rows} 表格 或 {variables, matrix} 热力矩阵

import { useState } from 'react'
import { API_BASE, apiFetch } from '../lib/apiBase'
import { useT } from '../lib/i18n'

export interface EdaSidebarProps {
  sessionId: string
  onClose?: () => void
  charlsDetected?: boolean
  onOpenCharlsWizard?: () => void
}

// ADR-0003 例外：EdaResponse.result 后端声明为 Any（EDA action 返回异构 shape），
// codegen 无法生成子类型。以下 3 个 interface 是 result 字段的局部解析 discriminated union，
// 属于"消费 Any 字段"的合理局部类型别名，不视为手写 API 响应 interface。
interface TableResult {
  columns: string[]
  rows: Record<string, unknown>[]
}

interface MatrixResult {
  variables: string[]
  matrix: number[][]
}

interface PlaceholderResult {
  action: string
  message: string
  placeholder?: boolean
}

type EdaResult = TableResult | MatrixResult | PlaceholderResult | null

function isTableResult(r: EdaResult): r is TableResult {
  return !!r && Array.isArray((r as TableResult).columns) && Array.isArray((r as TableResult).rows)
}

function isMatrixResult(r: EdaResult): r is MatrixResult {
  return !!r && Array.isArray((r as MatrixResult).variables) && Array.isArray((r as MatrixResult).matrix)
}

function isPlaceholderResult(r: EdaResult): r is PlaceholderResult {
  return !!r && typeof (r as PlaceholderResult).message === 'string' && !isTableResult(r) && !isMatrixResult(r)
}

const ACTIONS: { id: string; label: string }[] = [
  { id: 'describe', label: '描述统计' },
  { id: 'corr', label: '相关性' },
  { id: 'plot', label: '分布图' },
  { id: 'scatter', label: '散点图' },
  { id: 'regression', label: '回归诊断' },
  { id: 'missing', label: '缺失值' },
]

function renderCell(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (typeof value === 'number') return String(value)
  return String(value)
}

export function EdaSidebar({ sessionId, onClose, charlsDetected, onOpenCharlsWizard }: EdaSidebarProps) {
  const { t } = useT()
  const [result, setResult] = useState<EdaResult>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function runAction(action: string) {
    setLoading(true)
    setError(null)
    try {
      const resp = await apiFetch(`${API_BASE}/sessions/${sessionId}/eda`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data: EdaResult = await resp.json()
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div data-testid="eda-sidebar" className="flex h-full flex-col bg-panel">
      <div className="flex items-center justify-between border-b border-border p-3">
        <h2 className="text-xs uppercase tracking-wider text-muted">{t('eda.title')}</h2>
        {onClose && (
          <button onClick={onClose} className="text-muted hover:text-ink" aria-label="close">
            ✕
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 p-3">
        {ACTIONS.map((a) => (
          <button
            key={a.id}
            onClick={() => runAction(a.id)}
            disabled={loading}
            className="rounded border border-border px-3 py-2 text-sm hover:bg-bg disabled:opacity-50"
            data-testid={`eda-btn-${a.id}`}
          >
            {a.label}
          </button>
        ))}
      </div>

      {charlsDetected && (
        <div className="mx-3 mb-2 flex items-center justify-between rounded border border-amber-200 bg-amber-50 px-3 py-2">
          <span className="text-xs font-medium text-amber-800">{t('eda.charlsDetected')}</span>
          <button
            onClick={onOpenCharlsWizard}
            className="text-xs text-amber-700 underline hover:text-amber-900"
          >
            {t('eda.variableWizard')}
          </button>
        </div>
      )}

      <div className="flex-1 overflow-auto p-3">
        {loading && <div className="text-sm text-muted">{t('eda.loading')}</div>}
        {error && <div className="text-sm text-red-500">{error}</div>}

        {isTableResult(result) && (
          <table className="w-full text-xs">
            <thead>
              <tr>
                {result.columns.map((c) => (
                  <th key={c} className="border-b border-border p-1 text-left">
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.rows.map((row, i) => (
                <tr key={i}>
                  {result.columns.map((c) => (
                    <td key={c} className="border-b border-border p-1">
                      {renderCell(row[c])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {isMatrixResult(result) && (
          <div className="text-xs">
            <div className="mb-2 text-muted">{t('eda.corrMatrix')}</div>
            <table>
              <thead>
                <tr>
                  <th className="p-1"></th>
                  {result.variables.map((v) => (
                    <th key={v} className="p-1">
                      {v}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.matrix.map((row, i) => (
                  <tr key={i}>
                    <td className="p-1 font-bold">{result.variables[i]}</td>
                    {row.map((v, j) => (
                      <td
                        key={j}
                        className="p-1"
                        style={{ backgroundColor: `rgba(59, 130, 246, ${Math.abs(v)})` }}
                      >
                        {v.toFixed(2)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {isPlaceholderResult(result) && (
          <div className="text-sm text-muted">{result.message}</div>
        )}
      </div>
    </div>
  )
}

export default EdaSidebar
