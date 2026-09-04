import { afterEach, describe, expect, it, vi } from 'vitest'

import { RunTerminalError, waitForRun } from '../runEvents'

class FakeEventSource {
  static latest: FakeEventSource | null = null
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: (() => void) | null = null
  closed = false
  url: string

  constructor(url: string) {
    this.url = url
    FakeEventSource.latest = this
  }

  close() {
    this.closed = true
  }
}

describe('waitForRun', () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
    FakeEventSource.latest = null
  })

  it('resolves the authoritative run result after an SSE terminal event', async () => {
    vi.stubGlobal('EventSource', FakeEventSource)
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ status: 'SUCCEEDED', result: { claim: 'association' } }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    const waiting = waitForRun('run-123')
    expect(FakeEventSource.latest?.url).toBe('/api/runs/run-123/events')
    FakeEventSource.latest?.onmessage?.(
      new MessageEvent('message', {
        data: JSON.stringify({ type: 'run.succeeded', status: 'SUCCEEDED' }),
      }),
    )

    await expect(waiting).resolves.toEqual({ claim: 'association' })
    expect(FakeEventSource.latest?.closed).toBe(true)
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/runs/run-123',
      expect.objectContaining({ credentials: 'include' }),
    )
  })

  it('rejects with the durable failure returned by the run endpoint', async () => {
    vi.stubGlobal('EventSource', FakeEventSource)
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ status: 'FAILED', error: 'provider timeout' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    )

    const waiting = waitForRun('run-failed')
    FakeEventSource.latest?.onmessage?.(
      new MessageEvent('message', {
        data: JSON.stringify({ type: 'run.failed', status: 'FAILED' }),
      }),
    )

    await expect(waiting).rejects.toThrow('provider timeout')
    expect(FakeEventSource.latest?.closed).toBe(true)
  })

  it('preserves CANCELLED as a distinct terminal state for kind-aware recovery', async () => {
    vi.stubGlobal('EventSource', FakeEventSource)
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ status: 'CANCELLED' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    )

    const waiting = waitForRun('run-cancelled')
    FakeEventSource.latest?.onmessage?.(
      new MessageEvent('message', { data: JSON.stringify({ status: 'CANCELLED' }) }),
    )

    await expect(waiting).rejects.toMatchObject({
      status: 'CANCELLED',
    } satisfies Partial<RunTerminalError>)
  })

  it('uses the same durable status endpoint when EventSource is unavailable', async () => {
    vi.stubGlobal('EventSource', undefined)
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ status: 'SUCCEEDED', result: { cleaning_report: {} } }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    )

    await expect(waitForRun('run-polled')).resolves.toEqual({ cleaning_report: {} })
  })

  it('coalesces reconnect status checks and reuses the terminal response', async () => {
    vi.stubGlobal('EventSource', FakeEventSource)
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: 'SUCCEEDED', result: { outline: [] } }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const waiting = waitForRun('run-reconnected')
    FakeEventSource.latest?.onerror?.()
    FakeEventSource.latest?.onerror?.()

    await expect(waiting).resolves.toEqual({ outline: [] })
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('falls back to durable polling when the API is still down at the SSE error', async () => {
    vi.useFakeTimers()
    vi.stubGlobal('EventSource', FakeEventSource)
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('api restarting'))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ status: 'SUCCEEDED', result: { cleaning_report: { steps: [] } } }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
      )
    vi.stubGlobal('fetch', fetchMock)

    const waiting = waitForRun('run-api-restart')
    FakeEventSource.latest?.onerror?.()
    await vi.advanceTimersByTimeAsync(2000)

    expect(fetchMock).toHaveBeenCalledTimes(2)
    await expect(waiting).resolves.toEqual({ cleaning_report: { steps: [] } })
    expect(FakeEventSource.latest?.closed).toBe(true)
  })

  it('uses a durable watchdog when a dead SSE connection emits no error', async () => {
    vi.useFakeTimers()
    vi.stubGlobal('EventSource', FakeEventSource)
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ status: 'RUNNING' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ status: 'SUCCEEDED', result: { cleaning_report: { steps: [] } } }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
      )
    vi.stubGlobal('fetch', fetchMock)

    const waiting = waitForRun('run-silent-disconnect')
    await vi.advanceTimersByTimeAsync(2000)

    expect(fetchMock).toHaveBeenCalledTimes(2)
    await expect(waiting).resolves.toEqual({ cleaning_report: { steps: [] } })
    expect(FakeEventSource.latest?.closed).toBe(true)
  })

  it('retries a transient terminal status read before resolving', async () => {
    vi.stubGlobal('EventSource', FakeEventSource)
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('temporary disconnect'))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ status: 'SUCCEEDED', result: { claim: 'durable' } }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      )
    vi.stubGlobal('fetch', fetchMock)

    const waiting = waitForRun('run-retry')
    FakeEventSource.latest?.onmessage?.(
      new MessageEvent('message', {
        data: JSON.stringify({ type: 'run.succeeded', status: 'SUCCEEDED' }),
      }),
    )

    await expect(waiting).resolves.toEqual({ claim: 'durable' })
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('stops reconnecting when the durable run no longer exists', async () => {
    vi.stubGlobal('EventSource', FakeEventSource)
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{}', { status: 404 })))

    const waiting = waitForRun('run-missing')
    FakeEventSource.latest?.onerror?.()

    await expect(waiting).rejects.toThrow('HTTP 404')
    expect(FakeEventSource.latest?.closed).toBe(true)
  })
})
