// R4: an async confirmation must carry its session identity, the session
// epoch and the version of the object it approves. A response that arrives
// after the user moved on (another session, or another candidate in the same
// session) is dropped instead of being applied to whatever is on screen now.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, renderHook, waitFor } from '@testing-library/react'

import { useWorkspace, type SessionDesign } from '../workspace'

function design(title: string, overrides: Partial<SessionDesign> = {}): SessionDesign {
  return {
    status: 'draft',
    confirmed: false,
    revision: `revision-${title}`,
    proposed_at: `2026-09-17T10:00:00Z#${title}`,
    confirmed_at: null,
    source: { title, question: '' },
    method: 'ols',
    outcome: 'income',
    treatment: 'age',
    controls: [],
    group: '',
    treated: '',
    period: '',
    time_col: '',
    id_col: '',
    first_treat_col: '',
    interactions: [],
    qType: 'average',
    heterogeneity_groups: [],
    catalog_entry_id: null,
    ...overrides,
  } as SessionDesign
}

const CONFIRMED_A = design('研究A', {
  status: 'confirmed',
  confirmed: true,
  confirmed_at: '2026-09-17T10:05:00Z',
})

function snapshotOf(sessionId: string, overrides: Record<string, unknown> = {}) {
  return {
    session_id: sessionId,
    exists: true,
    has_dataset: true,
    dataset: { name: `${sessionId}.csv`, rows: 5, columns: ['income', 'age'] },
    upload_readiness: 'READY',
    dataAttached: false,
    active_run: null,
    outline: [],
    body_chapters: [],
    design: design(`研究${sessionId}`),
    confirmation_targets: { design: `revision-研究${sessionId}`, dataset: `data-${sessionId}`, preview: null, diagnosis: null },
    ...overrides,
  }
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason?: unknown) => void
  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

type Harness = {
  result: { current: ReturnType<typeof useWorkspace> }
  rerender: (props: { sid: string | null }) => void
}

async function mountWorkspace(): Promise<Harness> {
  const options = { setSessionId: vi.fn(), setAuthed: vi.fn(), t: (key: string) => key }
  const { result, rerender } = renderHook(
    ({ sid }: { sid: string | null }) => useWorkspace({ ...options, sessionId: sid }),
    { initialProps: { sid: 'A' as string | null } },
  )
  await waitFor(() => expect(result.current.design?.source?.title).toBe('研究A'))
  return { result, rerender }
}

beforeEach(() => {
  localStorage.clear()
  sessionStorage.clear()
  localStorage.setItem('econpaper_session_id', 'A')
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('R4 confirmation ownership — design', () => {
  it('drops a late design confirmation instead of entering the next session', async () => {
    const confirm = deferred<Response>()
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string, init?: RequestInit) => {
        const href = String(url)
        if (init?.method === 'POST' && href.endsWith('/sessions/A/design/confirm')) {
          return confirm.promise
        }
        if (href.endsWith('/sessions/A')) return Promise.resolve(json(snapshotOf('A')))
        if (href.endsWith('/sessions/B')) return Promise.resolve(json(snapshotOf('B')))
        return Promise.resolve(json({}))
      }),
    )

    const { result, rerender } = await mountWorkspace()
    let pending!: Promise<void>
    act(() => {
      pending = result.current.confirmDesign()
    })
    rerender({ sid: 'B' })
    await waitFor(() => expect(result.current.design).toBeNull())

    await act(async () => {
      confirm.resolve(json({ ok: true, design: CONFIRMED_A }))
      await pending
    })

    expect(result.current.design).toBeNull()
  })

  it('does not raise a rejection of a design confirmation in the next session', async () => {
    const confirm = deferred<Response>()
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string, init?: RequestInit) => {
        const href = String(url)
        if (init?.method === 'POST' && href.endsWith('/sessions/A/design/confirm')) {
          return confirm.promise
        }
        if (href.endsWith('/sessions/A')) return Promise.resolve(json(snapshotOf('A')))
        if (href.endsWith('/sessions/B')) return Promise.resolve(json(snapshotOf('B')))
        return Promise.resolve(json({}))
      }),
    )

    const { result, rerender } = await mountWorkspace()
    let pending!: Promise<void>
    act(() => {
      pending = result.current.confirmDesign()
    })
    rerender({ sid: 'B' })
    await waitFor(() => expect(result.current.design).toBeNull())

    await act(async () => {
      confirm.reject(new TypeError('response lost'))
      await pending
    })

    expect(result.current.designError).toBeNull()
  })

  it('drops a late confirmation read-back instead of overwriting the next session', async () => {
    const confirm = deferred<Response>()
    const lateSnapshot = deferred<Response>()
    let snapshotCalls = 0
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string, init?: RequestInit) => {
        const href = String(url)
        if (init?.method === 'POST' && href.endsWith('/sessions/A/design/confirm')) {
          return confirm.promise
        }
        if (href.endsWith('/sessions/A')) {
          snapshotCalls += 1
          return snapshotCalls === 1
            ? Promise.resolve(json(snapshotOf('A')))
            : lateSnapshot.promise
        }
        if (href.endsWith('/sessions/B')) return Promise.resolve(json(snapshotOf('B')))
        return Promise.resolve(json({}))
      }),
    )

    const { result, rerender } = await mountWorkspace()
    let pending!: Promise<void>
    act(() => {
      pending = result.current.confirmDesign()
    })
    // The POST resolves while session A is still current: the read-back starts.
    await act(async () => {
      confirm.resolve(json({ ok: true, design: CONFIRMED_A }))
      await Promise.resolve()
    })
    await waitFor(() => expect(snapshotCalls).toBeGreaterThan(1))

    rerender({ sid: 'B' })
    await waitFor(() => expect(result.current.design).toBeNull())

    await act(async () => {
      lateSnapshot.resolve(json(snapshotOf('A', { design: CONFIRMED_A })))
      await pending
    })

    expect(result.current.design).toBeNull()
  })

  it('invalidates an in-flight estimate when the design candidate is re-proposed', async () => {
    const estimate = deferred<Response>()
    let fetchMock: ReturnType<typeof vi.fn>
    let current = design('研究A', { status: 'confirmed', confirmed: true })
    const awaiting = (overrides: Record<string, unknown> = {}) => ({
      session_id: 'A',
      exists: true,
      has_dataset: true,
      dataset: { name: 'A.csv', rows: 5, columns: ['income', 'age'] },
      upload_readiness: 'READY',
      dataAttached: true,
      design: current,
      confirmation_targets: { design: current.revision, dataset: 'data-A', preview: `preview-${current.revision}`, diagnosis: 'diag-A' },
      active_run: null,
      outline: [],
      body_chapters: [],
      prewrite_gate: 'awaiting_estimate',
      table1: { produced_by: 'prewrite_preview', columns: ['variable'], rows: [{ variable: 'age' }], n: 5 },
      specification_equation: 'income = β₀ + β₁ age + ε',
      table1Confirmed: true,
      specConfirmed: true,
      permissions: { continue_to_estimate: 'allow' },
      ...overrides,
    })
    vi.stubGlobal(
      'fetch',
      (fetchMock = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
        const href = String(url)
        if (init?.method === 'POST' && href.endsWith('/sessions/A/prewrite/confirm')) {
          return estimate.promise
        }
        if (init?.method === 'POST' && href.endsWith('/sessions/A/design/propose')) {
          const body = JSON.parse(String(init.body))
          current = design(body.title)
          return Promise.resolve(json(current))
        }
        if (href.endsWith('/runs/run-est-stale')) {
          return Promise.resolve(json({ status: 'SUCCEEDED', result: awaiting() }))
        }
        if (href.endsWith('/sessions/A')) return Promise.resolve(json(awaiting()))
        return Promise.resolve(json({}))
      })),
    )

    const { result } = await mountWorkspace()
    await waitFor(() => expect(result.current.prewriteGate).toBe('awaiting_estimate'))
    let pending!: Promise<void>
    act(() => {
      pending = result.current.continueEstimate()
    })

    await act(async () => {
      await result.current.proposeDesign('研究B', '', { revise: true })
    })
    await waitFor(() => expect(result.current.design?.source?.title).toBe('研究B'))

    await act(async () => {
      estimate.resolve(
        json(
          {
            run_id: 'run-est-stale',
            session_id: 'A',
            status: 'PENDING',
            events_url: '/api/runs/run-est-stale/events',
          },
          202,
        ),
      )
      await pending
    })

    expect(
      fetchMock.mock.calls.filter((call) => String(call[0]).includes('/runs/run-est-stale')),
    ).toHaveLength(0)
    expect(result.current.design?.status).toBe('draft')
  })
})

describe('R4 confirmation ownership — attach', () => {
  it('drops a late confirm-attach instead of entering the next session', async () => {
    const confirm = deferred<Response>()
    let attached = false
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string, init?: RequestInit) => {
        const href = String(url)
        if (init?.method === 'POST' && href.endsWith('/sessions/A/confirm-attach')) {
          return confirm.promise
        }
        if (href.endsWith('/sessions/A')) {
          return Promise.resolve(json(snapshotOf('A', { dataAttached: attached })))
        }
        if (href.endsWith('/sessions/B')) return Promise.resolve(json(snapshotOf('B')))
        return Promise.resolve(json({}))
      }),
    )

    const { result, rerender } = await mountWorkspace()
    let pending!: Promise<void>
    act(() => {
      pending = result.current.confirmAttach()
    })
    rerender({ sid: 'B' })
    await waitFor(() => expect(result.current.design).toBeNull())

    await act(async () => {
      attached = true
      confirm.resolve(json(snapshotOf('A', { dataAttached: true })))
      await pending
    })

    expect(result.current.dataAttached).toBe(false)
    expect(result.current.design).toBeNull()
  })

  it('does not raise a rejected confirm-attach in the next session', async () => {
    const confirm = deferred<Response>()
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string, init?: RequestInit) => {
        const href = String(url)
        if (init?.method === 'POST' && href.endsWith('/sessions/A/confirm-attach')) {
          return confirm.promise
        }
        if (href.endsWith('/sessions/A')) return Promise.resolve(json(snapshotOf('A')))
        if (href.endsWith('/sessions/B')) return Promise.resolve(json(snapshotOf('B')))
        return Promise.resolve(json({}))
      }),
    )

    const { result, rerender } = await mountWorkspace()
    let pending!: Promise<void>
    act(() => {
      pending = result.current.confirmAttach()
    })
    rerender({ sid: 'B' })
    await waitFor(() => expect(result.current.design).toBeNull())

    await act(async () => {
      confirm.reject(new TypeError('response lost'))
      await pending
    })

    expect(result.current.attachConfirmError).toBeNull()
  })

  it('drops a late confirm-attach read-back instead of overwriting the next session', async () => {
    const confirm = deferred<Response>()
    const lateSnapshot = deferred<Response>()
    let snapshotCalls = 0
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string, init?: RequestInit) => {
        const href = String(url)
        if (init?.method === 'POST' && href.endsWith('/sessions/A/confirm-attach')) {
          return confirm.promise
        }
        if (href.endsWith('/sessions/A')) {
          snapshotCalls += 1
          return snapshotCalls === 1
            ? Promise.resolve(json(snapshotOf('A')))
            : lateSnapshot.promise
        }
        if (href.endsWith('/sessions/B')) return Promise.resolve(json(snapshotOf('B')))
        return Promise.resolve(json({}))
      }),
    )

    const { result, rerender } = await mountWorkspace()
    let pending!: Promise<void>
    act(() => {
      pending = result.current.confirmAttach()
    })
    await act(async () => {
      confirm.resolve(json(snapshotOf('A', { dataAttached: true })))
      await Promise.resolve()
    })
    await waitFor(() => expect(snapshotCalls).toBeGreaterThan(1))

    rerender({ sid: 'B' })
    await waitFor(() => expect(result.current.design).toBeNull())

    await act(async () => {
      lateSnapshot.resolve(json(snapshotOf('A', { dataAttached: true })))
      await pending
    })

    expect(result.current.design).toBeNull()
  })

  it('drops an in-flight confirm-attach when the data candidate is replaced', async () => {
    const confirm = deferred<Response>()
    let attached = false
    let datasetName = 'A.csv'
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string, init?: RequestInit) => {
        const href = String(url)
        if (init?.method === 'POST' && href.endsWith('/sessions/A/confirm-attach')) {
          return confirm.promise
        }
        if (init?.method === 'POST' && href.endsWith('/sessions/A/attach')) {
          datasetName = 'B.csv'
          return Promise.resolve(
            json({
              session_id: 'A',
              dataAttached: false,
              source: 'user_file',
              entry_id: null,
              upload_readiness: 'READY',
              dataset_meta: { name: 'B.csv', columns: ['income', 'age'], rows: 7 },
            }),
          )
        }
        if (href.endsWith('/sessions/A')) {
          return Promise.resolve(
            json(
              snapshotOf('A', {
                dataAttached: attached,
                dataset: { name: datasetName, rows: 5, columns: ['income', 'age'] },
              }),
            ),
          )
        }
        return Promise.resolve(json({}))
      }),
    )

    const { result } = await mountWorkspace()
    let pending!: Promise<void>
    act(() => {
      pending = result.current.confirmAttach()
    })
    await act(async () => {
      await result.current.takeCsv(new File(['income\n1'], 'B.csv', { type: 'text/csv' }))
    })
    expect(result.current.csvName).toBe('B.csv')

    await act(async () => {
      attached = true
      confirm.resolve(json(snapshotOf('A', { dataAttached: true })))
      await pending
    })

    expect(result.current.dataAttached).toBe(false)
  })
})
