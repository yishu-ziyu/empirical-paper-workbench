import { API_BASE, apiFetch } from './apiBase'
import type { components } from '../types/api'

type RunStatus = components['schemas']['RunStatusResponse']

const TERMINAL = new Set<RunStatus['status']>(['SUCCEEDED', 'FAILED', 'CANCELLED'])

export class RunRequestError extends Error {
  readonly status: number

  constructor(status: number) {
    super(`HTTP ${status}`)
    this.status = status
  }
}

export class RunTerminalError extends Error {
  readonly status: 'FAILED' | 'CANCELLED'

  constructor(status: 'FAILED' | 'CANCELLED', message?: string | null) {
    super(message || `Run ended with ${status}`)
    this.status = status
  }
}

export function shouldForgetRunHandle(error: unknown): boolean {
  return (
    error instanceof RunTerminalError ||
    (error instanceof RunRequestError && [401, 403, 404].includes(error.status))
  )
}

function abortError(): DOMException {
  return new DOMException('Run wait aborted', 'AbortError')
}

function delay(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(abortError())
    const onAbort = () => {
      window.clearTimeout(timer)
      reject(abortError())
    }
    const timer = window.setTimeout(() => {
      signal?.removeEventListener('abort', onAbort)
      resolve()
    }, ms)
    signal?.addEventListener('abort', onAbort, { once: true })
  })
}

async function readRun(runId: string): Promise<RunStatus> {
  const response = await apiFetch(`${API_BASE}/runs/${runId}`)
  if (!response.ok) throw new RunRequestError(response.status)
  return response.json()
}

function resultOrThrow(run: RunStatus): Record<string, any> {
  if (run.status === 'SUCCEEDED' && run.result) return run.result
  if (run.status === 'FAILED' || run.status === 'CANCELLED') {
    throw new RunTerminalError(run.status, run.error)
  }
  throw new Error(`Run ended with ${run.status}`)
}

async function readTerminalWithRetry(
  runId: string,
  signal?: AbortSignal,
): Promise<RunStatus> {
  let lastError: unknown
  for (let attempt = 0; attempt < 5; attempt += 1) {
    if (signal?.aborted) throw abortError()
    try {
      return await readRun(runId)
    } catch (error) {
      if (error instanceof RunRequestError && error.status < 500) throw error
      lastError = error
      if (attempt < 4) await delay(100 * 2 ** attempt, signal)
    }
  }
  throw lastError
}

async function pollRun(
  runId: string,
  signal?: AbortSignal,
  initialDelayMs = 0,
): Promise<Record<string, any>> {
  if (initialDelayMs > 0) await delay(initialDelayMs, signal)
  for (;;) {
    if (signal?.aborted) throw abortError()
    try {
      const run = await readRun(runId)
      if (TERMINAL.has(run.status)) return resultOrThrow(run)
    } catch (error) {
      if (error instanceof RunRequestError && error.status < 500) throw error
    }
    await delay(1000, signal)
  }
}

/** 投影给调用者的 run 事件（只含稳定标签字段，不含任何私有载荷）。 */
export type RunProgressEvent = {
  seq?: number
  type: string
  kind?: string
  status?: string
  node?: string
  specId?: string
}

function projectEvent(raw: Record<string, unknown>): RunProgressEvent {
  return {
    seq: typeof raw.seq === 'number' ? raw.seq : undefined,
    type: typeof raw.type === 'string' ? raw.type : 'run.progress',
    kind: typeof raw.kind === 'string' ? raw.kind : undefined,
    status: typeof raw.status === 'string' ? raw.status : undefined,
    node: typeof raw.node === 'string' ? raw.node : undefined,
    specId: typeof raw.spec_id === 'string' ? raw.spec_id : undefined,
  }
}

export function waitForRun(
  runId: string,
  eventsUrl = `${API_BASE}/runs/${runId}/events`,
  signal?: AbortSignal,
  onEvent?: (event: RunProgressEvent) => void,
): Promise<Record<string, any>> {
  if (typeof EventSource === 'undefined') return pollRun(runId, signal)

  return new Promise((resolve, reject) => {
    const source = new EventSource(eventsUrl)
    const pollingController = new AbortController()
    let finishing = false
    let checking = false
    let settled = false

    const succeed = (result: Record<string, any>) => {
      if (settled) return
      settled = true
      source.close()
      pollingController.abort()
      resolve(result)
    }

    const fail = (error: unknown) => {
      if (settled) return
      settled = true
      source.close()
      pollingController.abort()
      reject(error)
    }

    const finish = async (run?: RunStatus) => {
      if (finishing || settled) return
      finishing = true
      source.close()
      try {
        const terminal = run ?? (await readTerminalWithRetry(runId, signal))
        const result = resultOrThrow(terminal)
        succeed(result)
      } catch (error) {
        fail(error)
      }
    }

    const abort = () => fail(abortError())
    if (signal?.aborted) return abort()
    signal?.addEventListener('abort', abort, { once: true })

    // Keep a low-frequency durable status watchdog alongside SSE. A dead API
    // or proxy can leave an existing event stream half-open without firing a
    // useful error; the watchdog still observes the terminal database state.
    void pollRun(runId, pollingController.signal, 1000)
      .then(succeed)
      .catch((error) => {
        if (
          error instanceof DOMException &&
          error.name === 'AbortError' &&
          settled
        ) return
        fail(error)
      })

    source.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as Record<string, unknown>
        if (onEvent) {
          try {
            onEvent(projectEvent(payload))
          } catch {
            // A progress callback must never break the run wait.
          }
        }
        const status = payload.status as RunStatus['status'] | undefined
        if (status && TERMINAL.has(status)) void finish()
      } catch {
        // A malformed progress event is non-authoritative; keep the stream open.
      }
    }
    source.onerror = () => {
      // Check immediately on an explicit transport failure while the delayed
      // watchdog remains authoritative for a half-open stream with no error.
      if (finishing || checking || settled) return
      checking = true
      void readRun(runId)
        .then((run) => {
          if (TERMINAL.has(run.status)) void finish(run)
        })
        .catch((error) => {
          if (error instanceof RunRequestError && error.status < 500) fail(error)
        })
        .finally(() => {
          checking = false
        })
    }
  })
}
