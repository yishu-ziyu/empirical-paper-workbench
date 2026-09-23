// Review §3 (front-end side): one intention keeps one delivery credential, and
// a lost response is resolved by reading the server state back — never by
// treating an unknown delivery as a plain refusal, and never by inventing a
// second run.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, renderHook, waitFor } from '@testing-library/react'

import { useWorkspace, type SessionDesign } from '../workspace'

const DESIGN: SessionDesign = {
  status: 'confirmed',
  confirmed: true,
  revision: 'design-a',
  proposed_at: '2026-09-17T10:00:00Z',
  confirmed_at: '2026-09-17T10:05:00Z',
  source: { title: '教育年限与工资', question: '' },
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
} as SessionDesign

function awaitingSnapshot(overrides: Record<string, unknown> = {}) {
  return {
    session_id: 'A',
    exists: true,
    has_dataset: true,
    dataset: { name: 'wages.csv', rows: 5, columns: ['income', 'age'] },
    upload_readiness: 'READY',
    dataAttached: true,
    design: DESIGN,
    confirmation_targets: { design: 'design-a', dataset: 'bytes-a', preview: 'preview-a', diagnosis: 'diag-a' },
    active_run: null,
    outline: [],
    body_chapters: [],
    research_direction: { question: '教育年限与工资', dv: 'income', iv: 'age', method: 'OLS' },
    prewrite_gate: 'awaiting_estimate',
    table1: {
      produced_by: 'prewrite_preview',
      columns: ['variable', 'count'],
      rows: [{ variable: 'income', count: 5 }],
      n: 5,
    },
    specification_equation: 'income = β₀ + β₁ age + ε',
    table1Confirmed: true,
    specConfirmed: true,
    riskConfirmed: false,
    permissions: { continue_to_estimate: 'allow' },
    qType: 'average',
    specMode: 'level',
    ...overrides,
  }
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function idempotencyKeys(calls: unknown[][], suffix: string): string[] {
  return calls
    .filter((call) => String(call[0]).endsWith(suffix))
    .map((call) => String((call[1] as RequestInit)?.headers?.['Idempotency-Key' as never] ?? ''))
}

async function mountAwaiting() {
  const options = { setSessionId: vi.fn(), setAuthed: vi.fn(), t: (key: string) => key }
  const { result } = renderHook(() =>
    useWorkspace({ ...options, sessionId: 'A' }),
  )
  await waitFor(() => expect(result.current.prewriteGate).toBe('awaiting_estimate'))
  return result
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

describe('one intention, one delivery credential', () => {
  it('replays a lost estimate command with the same idempotency key', async () => {
    let attempts = 0
    let finished = false
    const fetchMock = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (init?.method === 'POST' && href.endsWith('/prewrite/confirm')) {
        attempts += 1
        if (attempts === 1) return Promise.reject(new TypeError('response lost'))
        return Promise.resolve(
          json(
            {
              run_id: 'run-est-1',
              session_id: 'A',
              status: 'PENDING',
              events_url: '/api/runs/run-est-1/events',
            },
            202,
          ),
        )
      }
      if (href.endsWith('/runs/run-est-1')) {
        finished = true
        return Promise.resolve(
          json({ status: 'SUCCEEDED', result: awaitingSnapshot({ prewrite_gate: 'estimate_complete' }) }),
        )
      }
      if (href.endsWith('/sessions/A')) {
        return Promise.resolve(
          json(
            awaitingSnapshot(
              finished ? { prewrite_gate: 'estimate_complete' } : {},
            ),
          ),
        )
      }
      return Promise.resolve(json({}))
    })
    vi.stubGlobal('fetch', fetchMock)
    const result = await mountAwaiting()

    await act(async () => {
      await result.current.continueEstimate()
    })
    await act(async () => {
      await result.current.continueEstimate()
    })

    const keys = idempotencyKeys(fetchMock.mock.calls, '/prewrite/confirm')
    expect(keys).toHaveLength(2)
    expect(keys[0]).not.toBe('')
    expect(keys[1]).toBe(keys[0])
  })

  it('re-attaches to the run the server already queued instead of enqueueing a second one', async () => {
    let snapshotCalls = 0
    let posts = 0
    let finished = false
    const fetchMock = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (init?.method === 'POST' && href.endsWith('/prewrite/confirm')) {
        posts += 1
        return posts === 1 ? Promise.reject(new TypeError('response lost')) : Promise.resolve(json({
          run_id: 'run-est-queued', session_id: 'A', status: 'PENDING',
          events_url: '/api/runs/run-est-queued/events',
        }, 202))
      }
      if (href.endsWith('/runs/run-est-queued')) {
        finished = true
        return Promise.resolve(
          json({ status: 'SUCCEEDED', result: awaitingSnapshot({ prewrite_gate: 'estimate_complete' }) }),
        )
      }
      if (href.endsWith('/sessions/A')) {
        snapshotCalls += 1
        const active = snapshotCalls > 1 && !finished
        return Promise.resolve(
          json(
            awaitingSnapshot({
              ...(active
                ? { active_run: { run_id: 'run-est-queued', kind: 'prewrite', status: 'RUNNING' } }
                : {}),
              ...(finished ? { prewrite_gate: 'estimate_complete' } : {}),
            }),
          ),
        )
      }
      return Promise.resolve(json({}))
    })
    vi.stubGlobal('fetch', fetchMock)
    const result = await mountAwaiting()

    await act(async () => {
      await result.current.continueEstimate()
    })

    const keys = idempotencyKeys(fetchMock.mock.calls, '/prewrite/confirm')
    expect(keys).toHaveLength(2)
    expect(keys[1]).toBe(keys[0])
    expect(
      fetchMock.mock.calls.filter((call) => String(call[0]).endsWith('/runs/run-est-queued')).length,
    ).toBeGreaterThan(0)
    expect(result.current.prewriteGate).toBe('estimate_complete')
  })

  it('keeps the attach intention across a lost response', async () => {
    let attempts = 0
    const fetchMock = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (init?.method === 'POST' && href.endsWith('/sessions/A/attach')) {
        attempts += 1
        return attempts === 1
          ? Promise.reject(new TypeError('response lost'))
          : Promise.resolve(
              json({
                session_id: 'A',
                dataAttached: false,
                source: 'user_file',
                entry_id: null,
                upload_readiness: 'READY',
                dataset_meta: { name: 'wages.csv', columns: ['income', 'age'], rows: 5 },
              }),
            )
      }
      if (href.endsWith('/sessions/A')) return Promise.resolve(json(awaitingSnapshot()))
      return Promise.resolve(json({}))
    })
    vi.stubGlobal('fetch', fetchMock)
    const result = await mountAwaiting()

    const file = new File(['income,age\n100,30'], 'wages.csv', { type: 'text/csv' })
    await act(async () => {
      await result.current.takeCsv(file)
    })
    await act(async () => {
      await result.current.takeCsv(file)
    })

    const keys = idempotencyKeys(fetchMock.mock.calls, '/sessions/A/attach')
    expect(keys).toHaveLength(2)
    expect(keys[1]).toBe(keys[0])
  })
})

describe('a lost acknowledgement is resolved by reading the server back', () => {
  it('accepts a recorded confirmation whose response was lost', async () => {
    let snapshotCalls = 0
    const fetchMock = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (init?.method === 'POST' && href.endsWith('/prewrite/confirm')) {
        return Promise.reject(new TypeError('response lost'))
      }
      if (href.endsWith('/sessions/A')) {
        snapshotCalls += 1
        return Promise.resolve(
          json(
            awaitingSnapshot({
              prewrite_gate: 'awaiting_estimate',
              table1Confirmed: false,
              specConfirmed: false,
              ...(snapshotCalls > 1 ? { table1Confirmed: true } : {}),
            }),
          ),
        )
      }
      return Promise.resolve(json({}))
    })
    vi.stubGlobal('fetch', fetchMock)
    const result = await mountAwaiting()

    await act(async () => {
      await result.current.recordPrewriteConfirms('table1')
    })

    expect(result.current.table1Confirmed).toBe(true)
    expect(result.current.confirmError).toBeNull()
  })

  it('does not claim a confirmation the read-back could not verify', async () => {
    let snapshotCalls = 0
    const fetchMock = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (init?.method === 'POST' && href.endsWith('/prewrite/confirm')) {
        return Promise.resolve(
          json({
            ok: true,
            prewrite_gate: 'awaiting_estimate',
            table1Confirmed: true,
            specConfirmed: false,
            table1: awaitingSnapshot().table1,
            specification_equation: awaitingSnapshot().specification_equation,
          }),
        )
      }
      if (href.endsWith('/sessions/A')) {
        snapshotCalls += 1
        if (snapshotCalls === 1) {
          return Promise.resolve(
            json(awaitingSnapshot({ table1Confirmed: false, specConfirmed: false })),
          )
        }
        return Promise.reject(new TypeError('offline'))
      }
      return Promise.resolve(json({}))
    })
    vi.stubGlobal('fetch', fetchMock)
    const result = await mountAwaiting()

    await act(async () => {
      await result.current.recordPrewriteConfirms('table1')
    })

    expect(result.current.table1Confirmed).toBe(false)
    expect(result.current.confirmError).not.toBeNull()
  })

  it('reports a definite design revision conflict instead of an unknown delivery', async () => {
    const fetchMock = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (init?.method === 'POST' && href.endsWith('/sessions/A/design/confirm')) {
        expect(JSON.parse(String(init.body)).expectedRevision).toBe('2026-09-17T10:00:00Z')
        return Promise.resolve(
          json(
            {
              detail: {
                code: 'design_revision_mismatch',
                expected: '2026-09-17T11:00:00Z',
                submitted: '2026-09-17T10:00:00Z',
              },
            },
            409,
          ),
        )
      }
      if (href.endsWith('/sessions/A')) return Promise.resolve(json(awaitingSnapshot()))
      return Promise.resolve(json({}))
    })
    vi.stubGlobal('fetch', fetchMock)
    const result = await mountAwaiting()

    await act(async () => {
      await result.current.confirmDesign('2026-09-17T10:00:00Z')
    })

    expect(result.current.designError).toBe('design.revisionMismatch')
  })
})
