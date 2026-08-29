// 右栏 Agent 状态面板 - 显示当前 node / status / WS 连接状态
// 卡片分组 + 颜色编码状态指示器 + 脉冲动画 + 降级状态

import type { WSStatus } from '../lib/ws'
import { useT } from '../lib/i18n'

export interface AgentPanelProps {
  currentNode?: string
  currentStatus?: 'running' | 'paused' | 'done' | 'idle'
  connectionState?: WSStatus
  /** F7: Whether any degradation has occurred */
  degraded?: boolean
  /** F7: List of degradation records */
  degradations?: Array<{
    node: string
    reason: string
    fallback: string
    timestamp: string
  }>
}

const STATUS_COLORS: Record<string, string> = {
  running: 'bg-accent',
  paused: 'bg-[var(--warning)]',
  done: 'bg-[var(--success)]',
  idle: 'bg-gray-300',
}

const CONNECTION_COLORS: Record<string, string> = {
  connected: 'bg-[var(--success)]',
  connecting: 'bg-[var(--warning)]',
  disconnected: 'bg-gray-300',
}

function StatusDot({ color, pulse = false }: { color: string; pulse?: boolean }) {
  return (
    <span
      className={`inline-block h-2 w-2 rounded-full ${color} ${pulse ? 'animate-pulse-soft' : ''}`}
    />
  )
}

export default function AgentPanel({
  currentNode = '',
  currentStatus,
  connectionState = 'disconnected',
  degraded = false,
  degradations = [],
}: AgentPanelProps) {
  const { t } = useT()
  return (
    <div data-testid="agent-panel-content" className="space-y-4 text-sm">
      <h2 className="text-xs uppercase tracking-wider text-muted font-mono">{t('agent.title')}</h2>

      {/* 连接状态卡片 */}
      <div className="rounded border border-border bg-bg p-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted">{t('agent.connection')}</span>
          <div className="flex items-center gap-1.5">
            <StatusDot
              color={CONNECTION_COLORS[connectionState] ?? 'bg-gray-300'}
              pulse={connectionState === 'connecting'}
            />
            <span className="font-mono text-xs">
              {connectionState === 'connecting' ? (
                <span className="animate-pulse-soft">connecting</span>
              ) : (
                connectionState
              )}
            </span>
          </div>
        </div>
      </div>

      {/* 当前节点卡片 */}
      <div className="rounded border border-border bg-bg p-3">
        <span className="block text-xs text-muted mb-1.5">{t('agent.currentNode')}</span>
        <span className="block font-mono text-sm text-ink">
          {currentNode || (
            <span className="text-muted italic">—</span>
          )}
        </span>
      </div>

      {/* 状态卡片 */}
      <div className="rounded border border-border bg-bg p-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted">{t('agent.status')}</span>
          <div className="flex items-center gap-1.5">
            <StatusDot
              color={STATUS_COLORS[currentStatus ?? 'idle'] ?? 'bg-gray-300'}
              pulse={currentStatus === 'running'}
            />
            <span className="font-mono text-xs capitalize">
              {currentStatus ?? '—'}
            </span>
          </div>
        </div>
      </div>

      {/* F7: 降级状态卡片 */}
      {degraded && (
        <div
          data-testid="degradation-card"
          className="rounded border border-yellow-200 bg-yellow-50 p-3"
        >
          <div className="mb-1.5 flex items-center gap-1.5">
            <span className="text-xs text-yellow-700">{t('agent.degraded')}</span>
          </div>
          {degradations.length > 0 && (
            <ul className="space-y-1">
              {degradations.map((d, i) => (
                <li
                  key={i}
                  className="rounded bg-white/50 px-2 py-1 text-xs text-yellow-800"
                >
                  <span className="font-mono">{d.node}</span> → {d.fallback}
                  <br />
                  <span className="text-yellow-600">{d.reason}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}