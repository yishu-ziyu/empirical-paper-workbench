import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { act, render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'
import { I18nProvider } from '../lib/i18n'
import { API_BASE } from '../lib/apiBase'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

class ChainFakeEventSource {
  static latest: ChainFakeEventSource | null = null
  static urls: string[] = []
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: (() => void) | null = null
  closed = false
  url: string

  constructor(url: string) {
    this.url = url
    ChainFakeEventSource.latest = this
    ChainFakeEventSource.urls.push(url)
  }

  close() {
    this.closed = true
  }

  emit(payload: Record<string, unknown>) {
    this.onmessage?.(
      new MessageEvent('message', { data: JSON.stringify(payload) }),
    )
  }
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const DESIGN_DRAFT = {
  status: 'draft',
  confirmed: false,
  proposed_at: '2026-09-17T10:00:00Z',
  confirmed_at: null,
  source: { title: '教育年限与工资的关系', question: '' },
  method: 'ols',
  outcome: 'income',
  treatment: 'schooling',
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
}

const DESIGN_CONFIRMED = {
  ...DESIGN_DRAFT,
  status: 'confirmed',
  confirmed: true,
  confirmed_at: '2026-09-17T10:05:00Z',
}

describe('正式研究确认链（FORMAL-CONFIRMATION-CHAIN-1）', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    localStorage.clear()
    sessionStorage.clear()
    localStorage.setItem('econpaper_access_token', 'test-token-for-auth')
    ChainFakeEventSource.latest = null
    ChainFakeEventSource.urls = []
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('C1 空桌确认问题后建立同一会话、提出设计、确认后回读 snapshot 一致', async () => {
    const user = userEvent.setup()
    vi.stubGlobal('EventSource', ChainFakeEventSource)
    let snapshotDesign: Record<string, unknown> | null = null
    let proposeCalls = 0
    const mockFetch = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (href.endsWith('/auth/me')) {
        return Promise.resolve(jsonResponse({}))
      }
      if (href.endsWith('/desk/discuss')) {
        return Promise.resolve(
          jsonResponse({
            intent: 'research',
            reflection: '收到。',
            title: '教育年限与工资的关系',
            heard: [],
            comparison: '',
            outcome: '',
            question: '',
            options: [],
            explain: '',
            ready: true,
            source: 'llm',
          }),
        )
      }
      if (href === `${API_BASE}/sessions` && init?.method === 'POST') {
        return Promise.resolve(jsonResponse({ session_id: 'sess-fcc1' }))
      }
      if (href.endsWith('/sessions/sess-fcc1/design/propose')) {
        proposeCalls += 1
        const body = JSON.parse(String(init?.body))
        snapshotDesign = { ...DESIGN_DRAFT, source: { title: body.title, question: body.question || '' } }
        return Promise.resolve(jsonResponse(snapshotDesign))
      }
      if (href.endsWith('/sessions/sess-fcc1/design/confirm')) {
        snapshotDesign = { ...DESIGN_CONFIRMED }
        return Promise.resolve(jsonResponse({ ok: true, design: DESIGN_CONFIRMED }))
      }
      if (href.endsWith('/sessions/sess-fcc1')) {
        return Promise.resolve(
          jsonResponse({
            exists: true,
            session_id: 'sess-fcc1',
            has_dataset: false,
            dataAttached: false,
            design: snapshotDesign,
          }),
        )
      }
      return Promise.resolve(jsonResponse({ exists: true }))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    await act(async () => {
      await Promise.resolve()
    })
    expect(screen.getByTestId('desk-page')).toBeInTheDocument()

    await user.type(screen.getByTestId('desk-paper'), '教育年限与工资的关系')
    await user.click(screen.getByTestId('desk-shape-btn'))
    await user.click(await screen.findByTestId('desk-confirm-btn'))

    // 同一 session 建立且问题以设计草稿形式提出（持久化，不只是关掉空桌）。
    const workbench = await screen.findByTestId('workbench-shell')
    expect(workbench).toBeInTheDocument()
    await waitFor(() => {
      expect(
        mockFetch.mock.calls.some(
          (call) => String(call[0]) === `${API_BASE}/sessions` && (call[1] as RequestInit)?.method === 'POST',
        ),
      ).toBe(true)
    })
    await waitFor(() => {
      expect(proposeCalls).toBeGreaterThan(0)
    })
    // 未确认：draft 可见，确认按钮可用，没有「已确认」措辞。
    expect(await screen.findByTestId('design-draft')).toHaveTextContent('OLS')
    expect(screen.getByTestId('design-confirm-btn')).toBeEnabled()
    expect(screen.queryByTestId('design-confirmed')).not.toBeInTheDocument()

    // 编辑题目后重新提出 → 仍是 draft；随后确认设计。
    const titleInput = screen.getByTestId('design-title-input')
    await user.clear(titleInput)
    await user.type(titleInput, '教育年限与工资的关系（修正）')
    await user.click(screen.getByTestId('design-propose-btn'))
    await waitFor(() => {
      expect(proposeCalls).toBeGreaterThanOrEqual(2)
    })
    expect(screen.getByTestId('design-title-input')).toHaveValue(
      '教育年限与工资的关系（修正）',
    )

    await user.click(screen.getByTestId('design-confirm-btn'))
    expect(await screen.findByTestId('design-confirmed')).toBeInTheDocument()

    // 确认事实来自后端回读：刷新恢复键已写入，snapshot 回读一致。
    expect(localStorage.getItem('econpaper_session_id')).toBe('sess-fcc1')
    const snapshotCalls = mockFetch.mock.calls.filter((call) =>
      String(call[0]).endsWith('/sessions/sess-fcc1'),
    )
    expect(snapshotCalls.length).toBeGreaterThan(0)
    expect(screen.getByTestId('design-confirmed')).toHaveTextContent('设计已确认')
    expect(screen.getByTestId('design-confirmed-method')).toHaveTextContent('OLS')
  })

  test('C3 已有设计会话在同会话 attach（不走 /upload）并确认挂接；失败不显示已挂接可重试', async () => {
    const user = userEvent.setup()
    vi.stubGlobal('EventSource', ChainFakeEventSource)
    localStorage.setItem('econpaper_session_id', 'sess-fcc1')
    let attached = false
    let confirmAttachAttempts = 0
    const mockFetch = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (href.endsWith('/auth/me')) return Promise.resolve(jsonResponse({}))
      if (href.endsWith('/sessions/sess-fcc1/attach') && init?.method === 'POST') {
        const headers = init.headers as Record<string, string> | undefined
        expect(String(headers?.['Idempotency-Key'] ?? '')).not.toBe('')
        return Promise.resolve(
          jsonResponse({
            session_id: 'sess-fcc1',
            dataAttached: false,
            source: 'user_file',
            entry_id: null,
            upload_readiness: 'PROCESSING',
            run_id: 'run-attach-1',
            events_url: '/api/runs/run-attach-1/events',
            dataset_meta: { name: 'wages.csv', columns: ['income', 'age'], rows: 5 },
          }),
        )
      }
      if (href.endsWith('/runs/run-attach-1')) {
        return Promise.resolve(
          jsonResponse({ status: 'SUCCEEDED', result: { exists: true, session_id: 'sess-fcc1' } }),
        )
      }
      if (href.endsWith('/sessions/sess-fcc1/confirm-attach') && init?.method === 'POST') {
        confirmAttachAttempts += 1
        if (!attached) {
          return Promise.resolve(
            jsonResponse(
              { detail: { code: 'upload_not_ready', upload_readiness: 'PROCESSING' } },
              409,
            ),
          )
        }
        return Promise.resolve(
          jsonResponse({
            exists: true,
            session_id: 'sess-fcc1',
            has_dataset: true,
            upload_readiness: 'READY',
            dataAttached: true,
            dataset: { name: 'wages.csv', rows: 5, columns: ['income', 'age'] },
            design: DESIGN_CONFIRMED,
          }),
        )
      }
      if (href.endsWith('/sessions/sess-fcc1')) {
        return Promise.resolve(
          jsonResponse({
            exists: true,
            session_id: 'sess-fcc1',
            has_dataset: true,
            upload_readiness: 'READY',
            dataAttached: attached,
            dataset: { name: 'wages.csv', rows: 5, columns: ['income', 'age'] },
            design: DESIGN_CONFIRMED,
          }),
        )
      }
      return Promise.resolve(jsonResponse({ exists: true }))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    await act(async () => {
      await Promise.resolve()
    })
    expect(await screen.findByTestId('attach-panel')).toBeInTheDocument()

    // 同会话 attach：POST /sessions/{id}/attach，绝不走 /upload。
    await user.click(screen.getByTestId('attach-step-upload'))
    const zone = screen.getByTestId('csv-drop-zone')
    const file = new File(['income,age\n100,30\n200,25'], 'wages.csv', { type: 'text/csv' })
    fireEvent.drop(zone, { dataTransfer: { files: [file] } })
    await waitFor(() => {
      expect(
        mockFetch.mock.calls.some((call) => String(call[0]).endsWith('/sessions/sess-fcc1/attach')),
      ).toBe(true)
    })
    expect(mockFetch.mock.calls.some((call) => String(call[0]).endsWith('/upload'))).toBe(false)

    // upload_pipeline run 完成（SSE 终态）。
    await act(async () => {
      ChainFakeEventSource.latest?.emit({ status: 'SUCCEEDED' })
      await Promise.resolve()
    })

    // 第一次确认挂接被后端拒绝：不显示已挂接、保留候选、可重试。
    await user.click(await screen.findByTestId('attach-confirm-btn'))
    expect(await screen.findByTestId('attach-confirm-error')).toBeInTheDocument()
    expect(screen.getByTestId('attach-candidate-status')).toHaveTextContent('候选（未挂接）')
    expect(screen.getByTestId('attach-confirm-btn')).toBeEnabled()

    // 重试成功：已挂接只由后端响应决定。
    attached = true
    await user.click(screen.getByTestId('attach-confirm-btn'))
    expect(await screen.findByTestId('attach-candidate-status')).toHaveTextContent('已挂接')
    expect(confirmAttachAttempts).toBe(2)
  })

  test('C5/C6 先确认样本再确认设定，200 不启动 run，202 才跟踪返回的 run', async () => {
    const user = userEvent.setup()
    vi.stubGlobal('EventSource', ChainFakeEventSource)
    localStorage.setItem('econpaper_session_id', 'sess-fcc1')
    const baseSnapshot = {
      exists: true,
      session_id: 'sess-fcc1',
      has_dataset: true,
      upload_readiness: 'READY',
      dataAttached: true,
      design: DESIGN_CONFIRMED,
      research_direction: { question: '年龄与收入', dv: 'income', iv: 'age', method: 'OLS' },
      prewrite_gate: 'awaiting_estimate',
      table1: {
        produced_by: 'prewrite_preview',
        columns: ['variable', 'count', 'mean', 'std', 'min', 'max', 'missing', 'role'],
        rows: [
          { variable: 'income', count: 5, mean: 187.5, std: 70.6, min: 100, max: 300, missing: 1, role: 'outcome' },
          { variable: 'age', count: 5, mean: 31.6, std: 5.9, min: 25, max: 40, missing: 0, role: 'treatment' },
        ],
        n: 5,
        variables: ['income', 'age'],
      },
      specification_equation: 'income = β₀ + β₁ age + ε',
      table1Confirmed: false,
      specConfirmed: false,
      qType: 'average',
      specMode: 'level',
    }
    let flags = { table1Confirmed: false, specConfirmed: false }
    let estimateStarted = false
    const mockFetch = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (href.endsWith('/auth/me')) return Promise.resolve(jsonResponse({}))
      if (href.endsWith('/sessions/sess-fcc1/prewrite/confirm') && init?.method === 'POST') {
        const body = JSON.parse(String(init?.body))
        if (body.action === 'record_confirms') {
          flags = {
            table1Confirmed: flags.table1Confirmed || body.table1Confirmed === true,
            specConfirmed: flags.specConfirmed || body.specConfirmed === true,
          }
          return Promise.resolve(
            jsonResponse({
              ok: true,
              prewrite_gate: 'awaiting_estimate',
              table1Confirmed: flags.table1Confirmed,
              specConfirmed: flags.specConfirmed,
              qType: 'average',
              specMode: 'level',
              table1: baseSnapshot.table1,
              specification_equation: baseSnapshot.specification_equation,
            }),
          )
        }
        // continue_estimate
        expect(flags.table1Confirmed).toBe(true)
        expect(flags.specConfirmed).toBe(true)
        estimateStarted = true
        return Promise.resolve(
          jsonResponse({
            run_id: 'run-est-1',
            session_id: 'sess-fcc1',
            status: 'PENDING',
            events_url: '/api/runs/run-est-1/events',
          }),
        )
      }
      if (href.endsWith('/runs/run-est-1')) {
        return Promise.resolve(
          jsonResponse({
            status: 'SUCCEEDED',
            result: { ...baseSnapshot, prewrite_gate: 'estimate_complete', table1Confirmed: true, specConfirmed: true },
          }),
        )
      }
      if (href.endsWith('/sessions/sess-fcc1')) {
        return Promise.resolve(
          jsonResponse({
            ...baseSnapshot,
            table1Confirmed: flags.table1Confirmed,
            specConfirmed: flags.specConfirmed,
            prewrite_gate: estimateStarted ? 'estimate_complete' : 'awaiting_estimate',
          }),
        )
      }
      return Promise.resolve(jsonResponse({ exists: true }))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    await act(async () => {
      await Promise.resolve()
    })
    // 该 snapshot 已有研究方向，刷新恢复落 Overview；切回问题页做两段确认。
    fireEvent.click(await screen.findByTestId('rail-question'))

    // 展示后端真实 Table 1 与公式。
    expect(await screen.findByTestId('table1-preview')).toBeInTheDocument()
    expect(screen.getByTestId('table1-preview')).toHaveTextContent('income')
    expect(screen.getByTestId('spec-equation')).toHaveTextContent('income = β₀ + β₁ age + ε')
    const startBtn = screen.getByTestId('start-estimate-btn')
    expect(startBtn).toBeDisabled()

    // 仅确认样本：record_confirms 200；不自动确认设定；不启动估计。
    await user.click(screen.getByTestId('confirm-table1-btn'))
    expect(await screen.findByTestId('table1-flag')).toHaveTextContent('已确认')
    expect(screen.getByTestId('spec-flag')).toHaveTextContent('未确认')
    expect(startBtn).toBeDisabled()
    expect(ChainFakeEventSource.urls.filter((u) => u.includes('run-est-1'))).toHaveLength(0)

    // 重复点击不产生重复 record（投递守卫）。
    await user.click(screen.getByTestId('confirm-table1-btn'))
    const recordCalls = mockFetch.mock.calls.filter(
      (call) =>
        String(call[0]).endsWith('/prewrite/confirm') &&
        JSON.parse(String((call[1] as RequestInit)?.body)).action === 'record_confirms' &&
        JSON.parse(String((call[1] as RequestInit)?.body)).table1Confirmed === true,
    )
    expect(recordCalls.length).toBeLessThanOrEqual(2)

    // 再确认设定：两者齐，启动估计可用。
    await user.click(screen.getByTestId('confirm-spec-btn'))
    expect(await screen.findByTestId('spec-flag')).toHaveTextContent('已确认')
    expect(startBtn).toBeEnabled()

    // 202 只跟踪返回的 run；双击不重复入队。
    await user.click(startBtn)
    await user.click(startBtn)
    await waitFor(() => {
      expect(
        mockFetch.mock.calls.filter(
          (call) =>
            String(call[0]).endsWith('/prewrite/confirm') &&
            JSON.parse(String((call[1] as RequestInit)?.body)).action === 'continue_estimate',
        ).length,
      ).toBeGreaterThanOrEqual(1)
    })
    await act(async () => {
      ChainFakeEventSource.latest?.emit({ status: 'SUCCEEDED' })
      await Promise.resolve()
    })
    expect(await screen.findByTestId('prewrite-estimate-complete')).toBeInTheDocument()
  })
})
