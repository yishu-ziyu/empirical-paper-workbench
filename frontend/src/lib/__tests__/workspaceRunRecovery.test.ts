import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  LS_ACTIVE_RUN_KEY,
  LS_PENDING_RUN_KEY,
  LS_PENDING_UPLOAD_KEY,
  acceptUploadRun,
  acceptDirectionRun,
  beginUploadIntent,
  createRestoreSnapshotGate,
  directionGateForReadiness,
  recoverAcceptedRun,
  resolvePendingUpload,
} from '../workspace'

describe('workspace run recovery ordering', () => {
  afterEach(() => {
    localStorage.clear()
    vi.unstubAllGlobals()
  })

  it('does not let a late session snapshot overwrite a completed run', () => {
    const applySession = vi.fn()
    const applyRun = vi.fn()
    const gate = createRestoreSnapshotGate()

    gate.applyRun(applyRun)
    gate.applySession(applySession)

    expect(applyRun).toHaveBeenCalledOnce()
    expect(applySession).not.toHaveBeenCalled()
  })

  it('allows session hydration before the run reaches a terminal state', () => {
    const order: string[] = []
    const gate = createRestoreSnapshotGate()

    gate.applySession(() => order.push('session'))
    gate.applyRun(() => order.push('run'))

    expect(order).toEqual(['session', 'run'])
  })

  it('replays a pending command with its original idempotency key', async () => {
    localStorage.setItem(
      `${LS_PENDING_RUN_KEY}:session-1`,
      JSON.stringify({
        idempotencyKey: 'stable-command-key',
        direction: {
          question: 'q',
          dv: 'income',
          iv: 'age',
          controls: [],
          method: 'OLS',
          template: 'cn_journal',
        },
      }),
    )
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          run_id: 'run-recovered',
          session_id: 'session-1',
          status: 'PENDING',
          events_url: '/api/runs/run-recovered/events',
        }),
        { status: 202, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    await expect(recoverAcceptedRun('session-1')).resolves.toEqual({
      run_id: 'run-recovered',
      session_id: 'session-1',
      status: 'PENDING',
      events_url: '/api/runs/run-recovered/events',
      kind: 'prewrite',
    })
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/sessions/session-1/direction',
      expect.objectContaining({
        headers: expect.objectContaining({ 'Idempotency-Key': 'stable-command-key' }),
      }),
    )
    expect(JSON.parse(localStorage.getItem(`${LS_ACTIVE_RUN_KEY}:session-1`) || '{}')).toEqual({
      runId: 'run-recovered',
      eventsUrl: '/api/runs/run-recovered/events',
      kind: 'prewrite',
    })
    expect(localStorage.getItem(`${LS_PENDING_RUN_KEY}:session-1`)).toBeNull()
  })

  it('does not recover an active run into a different session', async () => {
    localStorage.setItem(
      `${LS_ACTIVE_RUN_KEY}:session-1`,
      JSON.stringify({
        runId: 'run-1',
        eventsUrl: '/api/runs/run-1/events',
      }),
    )
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    await expect(recoverAcceptedRun('session-2')).resolves.toBeNull()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('keeps recovery handles isolated across sessions', async () => {
    localStorage.setItem(
      `${LS_ACTIVE_RUN_KEY}:session-1`,
      JSON.stringify({ runId: 'run-1', eventsUrl: '/api/runs/run-1/events' }),
    )
    localStorage.setItem(
      `${LS_ACTIVE_RUN_KEY}:session-2`,
      JSON.stringify({ runId: 'run-2', eventsUrl: '/api/runs/run-2/events' }),
    )

    await expect(recoverAcceptedRun('session-1')).resolves.toEqual({
      run_id: 'run-1',
      events_url: '/api/runs/run-1/events',
      kind: 'prewrite',
    })
    await expect(recoverAcceptedRun('session-2')).resolves.toEqual({
      run_id: 'run-2',
      events_url: '/api/runs/run-2/events',
      kind: 'prewrite',
    })
  })

  it('does not replay a direction rejected as session busy', async () => {
    localStorage.setItem(
      `${LS_PENDING_RUN_KEY}:session-1`,
      JSON.stringify({
        idempotencyKey: 'new-direction',
        direction: {
          question: 'new question',
          dv: 'income',
          iv: 'age',
          controls: [],
          method: 'OLS',
          template: 'undergrad',
        },
      }),
    )
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({ detail: { code: 'session_busy', run_id: 'other-run' } }),
          { status: 409, headers: { 'Content-Type': 'application/json' } },
        ),
      ),
    )

    await expect(
      acceptDirectionRun(
        'session-1',
        {
          question: 'new question',
          dv: 'income',
          iv: 'age',
          controls: [],
          method: 'OLS',
          template: 'undergrad',
        },
        'new-direction',
      ),
    ).rejects.toThrow('HTTP 409')
    expect(localStorage.getItem(`${LS_PENDING_RUN_KEY}:session-1`)).toBeNull()
  })

  it('persists a UUID upload intent before the first request and reuses it for a bounded retry', async () => {
    const randomUUID = vi
      .spyOn(crypto, 'randomUUID')
      .mockReturnValue('11111111-1111-4111-8111-111111111111')
    const intent = beginUploadIntent('panel.csv')
    expect(JSON.parse(localStorage.getItem(LS_PENDING_UPLOAD_KEY) || '{}')).toEqual(intent)

    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('response lost'))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            session_id: 'session-upload',
            dataset_meta: { columns: ['year', 'income'], rows: 2 },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
      )
    vi.stubGlobal('fetch', fetchMock)

    await expect(
      acceptUploadRun(new File(['year,income\n2020,1'], 'panel.csv'), intent.idempotencyKey),
    ).resolves.toMatchObject({ session_id: 'session-upload' })
    expect(fetchMock).toHaveBeenCalledTimes(2)
    for (const [, init] of fetchMock.mock.calls) {
      expect(init.headers).toMatchObject({ 'Idempotency-Key': intent.idempotencyKey })
      expect(init.body).toBeInstanceOf(FormData)
    }
    randomUUID.mockRestore()
  })

  it('retries a 5xx upload once with the same idempotency key', async () => {
    const key = '11111111-1111-4111-8111-111111111111'
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response('{}', { status: 500 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            session_id: 'session-upload',
            run_id: 'run-upload',
            status: 'PENDING',
            events_url: '/api/runs/run-upload/events',
            dataset_meta: { columns: ['year'], rows: 1 },
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        ),
      )
    vi.stubGlobal('fetch', fetchMock)

    await expect(
      acceptUploadRun(new File(['year\n2020'], 'panel.csv'), key),
    ).resolves.toMatchObject({ run_id: 'run-upload' })
    expect(fetchMock).toHaveBeenCalledTimes(2)
    for (const [, init] of fetchMock.mock.calls) {
      expect(init.headers).toMatchObject({ 'Idempotency-Key': key })
    }
  })

  it('creates a new key for a later file-selection intent', () => {
    const randomUUID = vi
      .spyOn(crypto, 'randomUUID')
      .mockReturnValueOnce('11111111-1111-4111-8111-111111111111')
      .mockReturnValueOnce('22222222-2222-4222-8222-222222222222')

    const first = beginUploadIntent('first.csv')
    const second = beginUploadIntent('second.csv')

    expect(second.idempotencyKey).not.toBe(first.idempotencyKey)
    expect(JSON.parse(localStorage.getItem(LS_PENDING_UPLOAD_KEY) || '{}')).toEqual(second)
    randomUUID.mockRestore()
  })

  it('resolves an accepted upload after refresh without replaying the file body', async () => {
    localStorage.setItem(
      LS_PENDING_UPLOAD_KEY,
      JSON.stringify({
        idempotencyKey: '11111111-1111-4111-8111-111111111111',
        fileName: 'panel.csv',
      }),
    )
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          run_id: 'run-upload',
          session_id: 'session-upload',
          status: 'PENDING',
          events_url: '/api/runs/run-upload/events',
          dataset_meta: { columns: ['year'], rows: 1 },
        }),
        { status: 202, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    await expect(resolvePendingUpload()).resolves.toMatchObject({ run_id: 'run-upload' })
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/upload/resolve',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Idempotency-Key': '11111111-1111-4111-8111-111111111111',
        }),
      }),
    )
    expect(fetchMock.mock.calls[0][1]).not.toHaveProperty('body')
  })

  it('restores kind-less handles as prewrite and keeps upload handles distinct', async () => {
    localStorage.setItem(
      `${LS_ACTIVE_RUN_KEY}:session-legacy`,
      JSON.stringify({ runId: 'run-legacy', eventsUrl: '/api/runs/run-legacy/events' }),
    )
    localStorage.setItem(
      `${LS_ACTIVE_RUN_KEY}:session-upload`,
      JSON.stringify({
        runId: 'run-upload',
        eventsUrl: '/api/runs/run-upload/events',
        kind: 'upload_pipeline',
      }),
    )

    await expect(recoverAcceptedRun('session-legacy')).resolves.toMatchObject({ kind: 'prewrite' })
    await expect(recoverAcceptedRun('session-upload')).resolves.toMatchObject({
      kind: 'upload_pipeline',
    })
  })

  it('blocks direction for explicit non-ready upload states but preserves legacy sessions', () => {
    expect(directionGateForReadiness(undefined)).toEqual({ disabled: false, reason: null })
    expect(directionGateForReadiness('READY')).toEqual({ disabled: false, reason: null })
    expect(directionGateForReadiness('PROCESSING').disabled).toBe(true)
    expect(directionGateForReadiness('FAILED').disabled).toBe(true)
    expect(directionGateForReadiness('CANCELLED').disabled).toBe(true)
  })
})
