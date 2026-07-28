// 右栏 Agent 状态面板 - 显示当前 node / status / WS 连接状态

import type { WSStatus } from '../lib/ws'

export interface AgentPanelProps {
  currentNode?: string
  currentStatus?: 'running' | 'paused' | 'done' | 'idle'
  connectionState?: WSStatus
}

export default function AgentPanel({
  currentNode = '',
  currentStatus,
  connectionState = 'disconnected',
}: AgentPanelProps) {
  return (
    <div data-testid="agent-panel-content" className="space-y-3 text-sm">
      <h2 className="mb-3 text-xs uppercase tracking-wider text-muted">Agent</h2>

      <div className="space-y-1">
        <span className="block text-xs text-muted">Node</span>
        <span className="block font-mono">{currentNode || '—'}</span>
      </div>

      <div className="space-y-1">
        <span className="block text-xs text-muted">Status</span>
        <span className="block font-mono">{currentStatus ?? '—'}</span>
      </div>

      <div className="space-y-1">
        <span className="block text-xs text-muted">Connection</span>
        <span className="block font-mono">{connectionState}</span>
      </div>
    </div>
  )
}
