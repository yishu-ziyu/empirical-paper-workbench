// 运行档案面板：run 目录 trace.jsonl 的只读 UI 面
// - GET /sessions/{id}/trace?limit=20，展示最近节点事件
// - status 三色点：ok=绿 accent / error|blocked=红 danger / forced、
//   accept 等人工决策=amber warning
// - 数据源头见 backend/run_store.py；每次导出/审批/评审都会留痕

import { useCallback, useEffect, useState } from 'react'
import { useT } from '../lib/i18n'

const API_BASE = 'http://localhost:8000'

interface TraceEvent {
  ts: string
  node: string
  status: string
  duration_ms?: number | null
  detail?: Record<string, unknown> | null
}

function statusDotClass(status: string): string {
  if (status === 'ok' || status === 'accept' || status === 'done') return 'bg-accent'
  if (status === 'error' || status === 'blocked') return 'bg-danger'
  return 'bg-amber-600' // forced / reject / 其他人工与降级动作
}

function shortTime(ts: string): string {
  // ISO → HH:MM:SS（本地时区），失败退回原串前 19 位
  const d = new Date(ts)
  if (Number.isNaN(d.getTime())) return ts.slice(0, 19)
  return d.toLocaleTimeString([], { hour12: false })
}

export default function RunTracePanel({ sessionId }: { sessionId: string }) {
  const { t } = useT()
  const [events, setEvents] = useState<TraceEvent[] | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    setBusy(true)
    try {
      const resp = await fetch(
        `${API_BASE}/sessions/${sessionId}/trace?limit=20`,
      )
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data = (await resp.json()) as { events?: TraceEvent[] }
      setEvents(data.events ?? [])
    } catch {
      setEvents([])
    } finally {
      setBusy(false)
    }
  }, [sessionId])

  useEffect(() => {
    load()
  }, [load])

  return (
    <section data-testid="run-trace-panel" className="mt-4 border-t border-border pt-3">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-mono text-[11px] uppercase tracking-wider text-muted">
          {t('trace.title')}
        </h3>
        <button
          type="button"
          data-testid="trace-refresh"
          onClick={load}
          disabled={busy}
          className="text-[11px] text-accent transition-colors duration-200 hover:text-accent/80 disabled:opacity-50"
        >
          {t('trace.refresh')}
        </button>
      </div>

      {events === null ? (
        <p className="text-xs leading-5 text-muted">…</p>
      ) : events.length === 0 ? (
        <p className="text-xs leading-5 text-muted">{t('trace.empty')}</p>
      ) : (
        <ul className="flex flex-col gap-1.5">
          {[...events].reverse().map((e, i) => (
            <li key={`${e.ts}-${i}`} data-testid="trace-event" className="flex items-baseline gap-2 font-mono text-[11px] leading-4">
              <span aria-hidden className={`inline-block h-1.5 w-1.5 shrink-0 translate-y-[-1px] rounded-full ${statusDotClass(e.status)}`} />
              <span className="shrink-0 text-muted">{shortTime(e.ts)}</span>
              <span className={`shrink-0 font-medium ${e.status === 'ok' ? 'text-ink' : 'text-danger'}`}>{e.node}</span>
              <span className="shrink-0 text-muted">{e.status}</span>
              {typeof e.duration_ms === 'number' && (
                <span className="ml-auto shrink-0 text-muted">{Math.round(e.duration_ms)}ms</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
