import { API_BASE } from './apiBase'

export type SpikeAction = 'act' | 'ask' | 'explain' | 'summarize'

export interface SpikeOption {
  id: string
  label: string
  consequence: string
}

export interface SpikeDecision {
  action: SpikeAction
  message: string
  question?: string | null
  options?: SpikeOption[]
  research_goal?: string
  known_context?: Record<string, string>
  preview?: SpikePreview
  tool_name?: string
  tool_args?: Record<string, unknown>
}

export interface SpikePreview {
  status: string
  n_before?: number
  n_after?: number
  error?: string
}

export interface SpikeActionRequest {
  name: string
  description: string
  args?: Record<string, unknown>
}

export interface SpikeInterrupt {
  action_requests: SpikeActionRequest[]
}

export interface SpikeState {
  session_id: string
  status: string
  decision?: SpikeDecision | null
  interrupt?: SpikeInterrupt | null
  last_tool_result?: Record<string, unknown> | null
}

export interface SpikeEvent {
  kind: string
  status?: string
  session_id?: string
  decision?: SpikeDecision | null
  interrupt?: SpikeInterrupt | null
  last_tool_result?: Record<string, unknown> | null
  message_type?: string
  node?: string | null
  tool_calls?: Array<{ name?: string; args?: Record<string, unknown> }>
  nodes?: string[]
  value?: SpikeInterrupt
  content?: string
  [key: string]: unknown
}

const SESSION_KEY = 'econpaper_spike_session_id'

export function readSpikeSessionId(): string | null {
  return localStorage.getItem(SESSION_KEY)
}

export function createSpikeSessionId(): string {
  const id =
    typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
      ? crypto.randomUUID()
      : `spike-${Date.now()}-${Math.random().toString(36).slice(2)}`
  localStorage.setItem(SESSION_KEY, id)
  return id
}

export function persistSpikeSessionId(id: string): void {
  localStorage.setItem(SESSION_KEY, id)
}

function endpoint(sessionId: string, suffix: string): string {
  return `${API_BASE}/spike/agent/${encodeURIComponent(sessionId)}/${suffix}`
}

async function parseError(response: Response): Promise<Error> {
  let detail = `请求失败（HTTP ${response.status}）`
  try {
    const body = (await response.json()) as { detail?: string; error?: string }
    detail = body.detail || body.error || detail
  } catch {
    // Keep the HTTP status when the server did not return JSON.
  }
  return new Error(detail)
}

function parseSseBlock(block: string): SpikeEvent | null {
  const data = block
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trimStart())
    .join('\n')
  if (!data) return null
  try {
    return JSON.parse(data) as SpikeEvent
  } catch {
    return null
  }
}

export async function streamSpike(
  sessionId: string,
  suffix: 'turn/stream' | 'decision/stream',
  payload: Record<string, unknown>,
  onEvent: (event: SpikeEvent) => void,
  signal?: AbortSignal,
): Promise<SpikeState | null> {
  const response = await fetch(endpoint(sessionId, suffix), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload),
    signal,
  })
  if (!response.ok) throw await parseError(response)
  if (!response.body) throw new Error('服务没有返回可读取的事件流')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finalState: SpikeState | null = null
  const consume = (chunk: string) => {
    buffer += chunk
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() || ''
    for (const block of blocks) {
      const event = parseSseBlock(block)
      if (!event) continue
      onEvent(event)
      if (event.kind === 'state' && event.session_id && event.status) {
        finalState = {
          session_id: event.session_id,
          status: event.status,
          decision: event.decision,
          interrupt: event.interrupt,
          last_tool_result: event.last_tool_result,
        }
      }
    }
  }

  while (true) {
    const next = await reader.read()
    if (next.done) break
    consume(decoder.decode(next.value, { stream: true }))
  }
  consume(decoder.decode())
  if (buffer.trim()) {
    const event = parseSseBlock(buffer)
    if (event) {
      onEvent(event)
      if (event.kind === 'state' && event.session_id && event.status) {
        finalState = {
          session_id: event.session_id,
          status: event.status,
          decision: event.decision,
          interrupt: event.interrupt,
          last_tool_result: event.last_tool_result,
        }
      }
    }
  }
  return finalState
}

export async function readSpikeState(sessionId: string): Promise<SpikeState | null> {
  const response = await fetch(endpoint(sessionId, 'state'), {
    credentials: 'include',
  })
  if (response.status === 404) return null
  if (!response.ok) throw await parseError(response)
  return (await response.json()) as SpikeState
}

async function postSpikeCheckpointAction(
  sessionId: string,
  action: 'pause' | 'resume',
): Promise<SpikeState> {
  const response = await fetch(endpoint(sessionId, action), {
    method: 'POST',
    credentials: 'include',
  })
  if (!response.ok) throw await parseError(response)
  return (await response.json()) as SpikeState
}

export function pauseSpike(sessionId: string): Promise<SpikeState> {
  return postSpikeCheckpointAction(sessionId, 'pause')
}

export function resumeSpike(sessionId: string): Promise<SpikeState> {
  return postSpikeCheckpointAction(sessionId, 'resume')
}
