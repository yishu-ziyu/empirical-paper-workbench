import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import App from '../App'
import { I18nProvider, useT, type Translate } from '../lib/i18n'
import { htmlLangAttr } from '../lib/i18n'
import { ExpectationEditor } from '../components/ResearchLabPanels'
import { TaskHelp } from '../components/TaskHelp'
import { LangPills } from '../components/UnauthHeader'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

class FakeEventSource {
  static latest: FakeEventSource | null = null
  static constructed = 0
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: (() => void) | null = null
  closed = false
  url: string
  constructor(url: string) {
    this.url = url
    FakeEventSource.constructed += 1
    FakeEventSource.latest = this
  }
  close() {
    this.closed = true
  }
}

function snapshotRestoreGets(calls: unknown[][]) {
  return calls.filter((call) => {
    const href = String(call[0])
    const init = (call[1] || {}) as RequestInit
    const method = String(init.method || 'GET').toUpperCase()
    return method === 'GET' && /\/sessions\/sess-lang\/?$/.test(href)
  })
}

function researchWrites(calls: unknown[][]) {
  return calls.filter((call) => {
    const href = String(call[0])
    const init = (call[1] || {}) as RequestInit
    const method = String(init.method || 'GET').toUpperCase()
    if (method === 'GET' || method === 'HEAD') return false
    return /\/research(\/|$)/.test(href)
  })
}

const seedCriteria = [
  {
    id: 'criterion.seed.iv-below-ols',
    kind: 'ordering',
    operator: 'lt',
    left: { metric: 'estimate.coef', estimator: 'iv', spec_id: 'iv_region_dummies', label: 'IV estimate' },
    right: { metric: 'estimate.coef', estimator: 'ols', spec_id: 'ols_region_dummies', label: 'OLS estimate' },
    label: 'IV estimate < OLS estimate',
    source: 'seed',
  },
]

function cardSnapshot(overrides: Record<string, unknown> = {}) {
  return {
    exists: true,
    has_dataset: true,
    session_id: 'sess-lang',
    upload_readiness: 'READY',
    dataset: { name: 'card_1995.csv', rows: 3010, columns: ['lwage', 'educ'] },
    research: {
      teaching_case: 'card_1995',
      evidence_revision: 1,
      canonical_spec_id: 'iv_region_dummies',
      question: {
        prompt_en: 'Does education increase earnings?',
        prompt_zh: '教育是否提高工资？',
        outcome: { name: 'lwage', label: 'Log wage', gloss: '对数工资' },
        treatment: { name: 'educ', label: 'Years of education', gloss: '受教育年限' },
      },
      expectation: {
        text: 'OLS positive; IV may be smaller.',
        confidence: 'medium',
        version: 1,
        history: [],
        criteria: seedCriteria,
        locale: 'en',
      },
      specification_space: {
        status: 'proposed',
        frozen_at: null,
        revealed: false,
        definitions: [],
      },
      specification_runs: [],
      claims: [],
      ...overrides,
    },
  }
}

describe('language switch is display-only', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    localStorage.setItem('econpaper_access_token', 'test-token-for-auth')
    FakeEventSource.latest = null
    FakeEventSource.constructed = 0
    vi.stubGlobal('EventSource', FakeEventSource)
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('html lang follows UI language', () => {
    expect(htmlLangAttr('zh')).toBe('zh-CN')
    expect(htmlLangAttr('en')).toBe('en')
    renderWithI18n(<App />)
    expect(document.documentElement.lang).toBe('zh-CN')
    fireEvent.click(screen.getByRole('button', { name: 'EN' }))
    expect(document.documentElement.lang).toBe('en')
    fireEvent.click(screen.getByRole('button', { name: '中' }))
    expect(document.documentElement.lang).toBe('zh-CN')
  })

  test('unsaved expectation text survives language switch with no PUT', () => {
    const onSave = vi.fn(async () => undefined)
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(
      <div>
        <LangPills />
        <ExpectationEditor
          expectation={{
            text: 'OLS positive',
            confidence: 'medium',
            version: 1,
            history: [],
            criteria: seedCriteria as never,
          }}
          onSave={onSave}
        />
      </div>,
    )
    const box = screen.getByRole('textbox')
    fireEvent.change(box, { target: { value: '未保存的中文预期，不要写回。' } })
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    expect(screen.getByRole('textbox')).toHaveValue('未保存的中文预期，不要写回。')
    expect(document.documentElement.lang).toBe('en')
    expect(onSave).not.toHaveBeenCalled()
    expect(researchWrites(mockFetch.mock.calls)).toEqual([])
  })

  test('switching language during spec_run does not add research writes', async () => {
    const snapshot = cardSnapshot({
      specification_space: {
        status: 'frozen',
        frozen_at: '2026-09-06T00:00:00+00:00',
        revealed: false,
        definitions: [],
      },
    })
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-lang')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              ...snapshot,
              active_run: {
                run_id: 'run-spec-live',
                kind: 'spec_run',
                status: 'RUNNING',
              },
            }),
        })
      }
      if (href.includes('/runs/run-spec-live')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ status: 'RUNNING', kind: 'spec_run' }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    localStorage.setItem('econpaper_session_id', 'sess-lang')
    renderWithI18n(<App />)
    expect(await screen.findByTestId('workbench-shell')).toBeInTheDocument()
    const writesBefore = researchWrites(mockFetch.mock.calls).length
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    fireEvent.click(screen.getByRole('button', { name: '中文' }))
    expect(researchWrites(mockFetch.mock.calls).length).toBe(writesBefore)
    expect(screen.getByTestId('workbench-shell')).toBeInTheDocument()
  })

  test('switching language after approved claim does not rebuild claim or bump evidence', async () => {
    const snapshot = cardSnapshot({
      evidence_revision: 4,
      canonical_spec_id: 'iv_region_dummies',
      specification_space: {
        status: 'frozen',
        frozen_at: '2026-09-06T00:00:00+00:00',
        revealed: true,
        definitions: [],
      },
      specification_runs: [
        {
          id: 'run-iv',
          spec_id: 'iv_region_dummies',
          label: 'IV',
          method: 'iv',
          coef: 0.13,
          se: 0.01,
          status: 'ok',
          relation: 'canonical',
          choices: [{ dimension: 'estimator', value: 'iv' }],
        },
      ],
      claim: {
        id: 'claim.card.education-earnings',
        claim_text: 'Education is positively associated with earnings.',
        approved_by_user: true,
        stale: false,
        version: 2,
        based_on_evidence_revision: 4,
        evidence_status: 'supported',
      },
      claims: [
        {
          id: 'claim.card.education-earnings',
          approved_by_user: true,
          stale: false,
          version: 2,
          based_on_evidence_revision: 4,
        },
      ],
    })
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-lang')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(snapshot) })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    localStorage.setItem('econpaper_session_id', 'sess-lang')
    renderWithI18n(<App />)
    fireEvent.click(await screen.findByTestId('rail-evidence'))
    const writesBefore = researchWrites(mockFetch.mock.calls).length
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    expect(researchWrites(mockFetch.mock.calls).length).toBe(writesBefore)
    const mutating = mockFetch.mock.calls.filter((call) => {
      const href = String(call[0])
      const method = String(((call[1] || {}) as RequestInit).method || 'GET').toUpperCase()
      return method !== 'GET' && /claim|promote|canonical|expectation|specification/.test(href)
    })
    expect(mutating).toEqual([])
  })

  test('after reveal, language switch does not PUT translated criterion labels', async () => {
    const onSave = vi.fn(async () => undefined)
    renderWithI18n(
      <div>
        <LangPills />
        <ExpectationEditor
          expectation={{
            text: 'OLS positive',
            confidence: 'medium',
            version: 1,
            history: [],
            criteria: seedCriteria as never,
          }}
          onSave={onSave}
          criteriaLocked
        />
      </div>,
    )
    expect(screen.getByTestId('expectation-criterion-locked')).toBeInTheDocument()
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent('IV 估计 < OLS 估计')
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    expect(onSave).not.toHaveBeenCalled()
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent('IV estimate < OLS estimate')
    expect(screen.getByTestId('expectation-criterion')).not.toHaveTextContent('IV 估计')
    expect(screen.getByTestId('expectation-criterion-select')).toBeDisabled()
  })

  test('opening and closing help does not call research writers', () => {
    const onSave = vi.fn()
    renderWithI18n(
      <>
        <TaskHelp summary="先确认方案。" details="确认之后才比较。" />
        <button type="button" onClick={onSave}>
          save
        </button>
      </>,
    )
    fireEvent.click(screen.getByTestId('task-help-toggle'))
    fireEvent.click(screen.getByTestId('task-help-toggle'))
    expect(onSave).not.toHaveBeenCalled()
  })

  test('stable translator identity still reads the new language after switch', () => {
    const seen: Translate[] = []
    function Probe() {
      const { t } = useT()
      seen.push(t)
      return <span data-testid="probe">{t('nav.overview')}</span>
    }
    renderWithI18n(
      <div>
        <LangPills />
        <Probe />
      </div>,
    )
    expect(screen.getByTestId('probe')).toHaveTextContent('总览')
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    expect(screen.getByTestId('probe')).toHaveTextContent('Overview')
    fireEvent.click(screen.getByRole('button', { name: '中文' }))
    expect(screen.getByTestId('probe')).toHaveTextContent('总览')
    expect(new Set(seen).size).toBe(1)
  })

  test('Scene A: evidence Compare stays open across zh→en→zh without restore GET', async () => {
    const snapshot = cardSnapshot({
      specification_space: {
        status: 'frozen',
        frozen_at: '2026-09-06T00:00:00+00:00',
        revealed: true,
        definitions: [],
      },
      specification_runs: [
        {
          id: 'run-ols-exact',
          spec_id: 'ols_region_dummies',
          label: 'OLS · 1966 region dummies',
          method: 'ols',
          coef: 0.08,
          se: 0.01,
          status: 'ok',
          relation: 'exploratory',
          choices: [{ dimension: 'estimator', value: 'ols' }],
        },
        {
          id: 'run-iv-exact',
          spec_id: 'iv_region_dummies',
          label: 'IV · nearc4 with 1966 region dummies',
          method: 'iv',
          coef: 0.13,
          se: 0.05,
          status: 'ok',
          relation: 'canonical',
          choices: [{ dimension: 'estimator', value: 'iv' }],
        },
      ],
    })
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-lang')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(snapshot) })
      }
      if (href.includes('/research/compare')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              coef_a: 0.08,
              coef_b: 0.13,
              delta_abs: 0.05,
              changed: [{ dimension: 'estimator', a: 'ols', b: 'iv' }],
              unchanged: [],
              why_moved: 'Identification strategy changed',
            }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    localStorage.setItem('econpaper_session_id', 'sess-lang')
    renderWithI18n(<App />)
    expect(await screen.findByTestId('workbench-shell')).toBeInTheDocument()
    fireEvent.click(await screen.findByTestId('rail-evidence'))
    expect(await screen.findByTestId('evidence-lab')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('evidence-matrix-ols_region_dummies'))
    fireEvent.click(screen.getByTestId('evidence-matrix-iv_region_dummies'))
    expect(await screen.findByTestId('evidence-compare-intent')).toBeInTheDocument()
    expect(screen.getByTestId('evidence-lab')).toHaveAttribute(
      'data-selected-ids',
      'run-ols-exact,run-iv-exact',
    )
    expect(screen.getByTestId('evidence-compare')).toHaveAttribute('data-expanded', 'true')
    const restoresBefore = snapshotRestoreGets(mockFetch.mock.calls).length
    const sourcesBefore = FakeEventSource.constructed
    const writesBefore = researchWrites(mockFetch.mock.calls).length
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    fireEvent.click(screen.getByRole('button', { name: '中文' }))
    expect(screen.getByTestId('rail-evidence')).toHaveAttribute('aria-current', 'true')
    expect(screen.getByTestId('evidence-lab')).toBeInTheDocument()
    expect(screen.queryByTestId('overview-view')).not.toBeInTheDocument()
    expect(screen.getByTestId('evidence-lab')).toHaveAttribute(
      'data-selected-ids',
      'run-ols-exact,run-iv-exact',
    )
    expect(screen.getByTestId('evidence-compare')).toHaveAttribute('data-expanded', 'true')
    expect(snapshotRestoreGets(mockFetch.mock.calls).length).toBe(restoresBefore)
    expect(FakeEventSource.constructed).toBe(sourcesBefore)
    expect(researchWrites(mockFetch.mock.calls).length).toBe(writesBefore)
    const mutating = mockFetch.mock.calls.filter((call) => {
      const href = String(call[0])
      const method = String(((call[1] || {}) as RequestInit).method || 'GET').toUpperCase()
      return method !== 'GET' && /claim|promote|canonical|expectation|specification/.test(href)
    })
    expect(mutating).toEqual([])
  })

  test('Scene B: spec_run in progress does not rebuild EventSource on language switch', async () => {
    const snapshot = cardSnapshot({
      specification_space: {
        status: 'frozen',
        frozen_at: '2026-09-06T00:00:00+00:00',
        revealed: false,
        definitions: [],
      },
    })
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-lang')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              ...snapshot,
              active_run: {
                run_id: 'run-spec-live',
                kind: 'spec_run',
                status: 'RUNNING',
              },
            }),
        })
      }
      if (href.includes('/runs/run-spec-live')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ status: 'RUNNING', kind: 'spec_run' }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    localStorage.setItem('econpaper_session_id', 'sess-lang')
    renderWithI18n(<App />)
    expect(await screen.findByTestId('workbench-shell')).toBeInTheDocument()
    await waitFor(() => expect(FakeEventSource.latest).not.toBeNull())
    const source = FakeEventSource.latest
    const restoresBefore = snapshotRestoreGets(mockFetch.mock.calls).length
    const sourcesBefore = FakeEventSource.constructed
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    fireEvent.click(screen.getByRole('button', { name: '中文' }))
    expect(FakeEventSource.constructed).toBe(sourcesBefore)
    expect(FakeEventSource.latest).toBe(source)
    expect(source?.closed).toBe(false)
    expect(snapshotRestoreGets(mockFetch.mock.calls).length).toBe(restoresBefore)
    expect(screen.getByTestId('workbench-shell')).toBeInTheDocument()
  })

  test('Scene C: unsaved expectation, tab, selected run, and help survive language switch', async () => {
    const snapshot = cardSnapshot({
      specification_space: {
        status: 'frozen',
        frozen_at: '2026-09-06T00:00:00+00:00',
        revealed: true,
        definitions: [],
      },
      specification_runs: [
        {
          id: 'run-ols-exact',
          spec_id: 'ols_region_dummies',
          method: 'ols',
          coef: 0.07,
          status: 'ok',
          choices: [{ dimension: 'estimator', value: 'ols' }],
        },
        {
          id: 'run-iv-exact',
          spec_id: 'iv_region_dummies',
          method: 'iv',
          coef: 0.13,
          status: 'ok',
          choices: [{ dimension: 'estimator', value: 'iv' }],
        },
      ],
    })
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-lang')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(snapshot) })
      }
      if (href.includes('/research/compare')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ coef_a: 0.07, coef_b: 0.13, changed: [], unchanged: [] }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    localStorage.setItem('econpaper_session_id', 'sess-lang')
    renderWithI18n(<App />)
    fireEvent.click(await screen.findByTestId('rail-evidence'))
    expect(await screen.findByTestId('evidence-lab')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('evidence-matrix-ols_region_dummies'))
    fireEvent.click(screen.getByTestId('help-promote-toggle'))
    expect(screen.getByTestId('help-promote-details')).toBeInTheDocument()
    const restoresBefore = snapshotRestoreGets(mockFetch.mock.calls).length
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    expect(screen.getByTestId('rail-evidence')).toHaveAttribute('aria-current', 'true')
    expect(screen.getByTestId('evidence-lab')).toHaveAttribute('data-selected-ids', 'run-ols-exact')
    expect(screen.getByTestId('help-promote-details')).toBeInTheDocument()
    expect(snapshotRestoreGets(mockFetch.mock.calls).length).toBe(restoresBefore)
  })

  test('Scene D: r3 surprise observed from backend outcomes re-renders per language with no writes', async () => {
    const snapshot = cardSnapshot({
      specification_space: {
        status: 'frozen',
        frozen_at: '2026-09-06T00:00:00+00:00',
        revealed: true,
        definitions: [],
      },
      specification_runs: [
        {
          id: 'run-ols-exact',
          spec_id: 'ols_region_dummies',
          method: 'ols',
          coef: 0.08,
          status: 'ok',
          choices: [{ dimension: 'estimator', value: 'ols' }],
        },
        {
          id: 'run-iv-exact',
          spec_id: 'iv_region_dummies',
          method: 'iv',
          coef: 0.13,
          status: 'ok',
          choices: [{ dimension: 'estimator', value: 'iv' }],
        },
      ],
      surprise: {
        status: 'Unexpected',
        criterion_outcomes: [
          {
            id: 'criterion.seed.iv-below-ols',
            outcome: 'violated',
            kind: 'ordering',
            operator: 'lt',
            left: {
              source: 'metric',
              metric: 'estimate.coef',
              estimator: 'iv',
              spec_id: 'iv_region_dummies',
              run_id: 'run-iv-exact',
              value: 0.13,
            },
            right: {
              source: 'metric',
              metric: 'estimate.coef',
              estimator: 'ols',
              spec_id: 'ols_region_dummies',
              run_id: 'run-ols-exact',
              value: 0.08,
            },
          },
        ],
      },
    })
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-lang')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(snapshot) })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    localStorage.setItem('econpaper_session_id', 'sess-lang')
    renderWithI18n(<App />)
    fireEvent.click(await screen.findByTestId('rail-evidence'))
    expect(await screen.findByTestId('evidence-surprise')).toBeInTheDocument()
    expect(screen.getByTestId('evidence-surprise')).toHaveTextContent(
      'IV 估计 0.1300 > OLS 估计 0.0800',
    )
    const restoresBefore = snapshotRestoreGets(mockFetch.mock.calls).length
    const sourcesBefore = FakeEventSource.constructed
    const writesBefore = researchWrites(mockFetch.mock.calls).length
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    expect(screen.getByTestId('evidence-surprise')).toHaveTextContent(
      'IV estimate 0.1300 > OLS estimate 0.0800',
    )
    fireEvent.click(screen.getByRole('button', { name: '中文' }))
    expect(screen.getByTestId('evidence-surprise')).toHaveTextContent(
      'IV 估计 0.1300 > OLS 估计 0.0800',
    )
    expect(snapshotRestoreGets(mockFetch.mock.calls).length).toBe(restoresBefore)
    expect(FakeEventSource.constructed).toBe(sourcesBefore)
    expect(researchWrites(mockFetch.mock.calls).length).toBe(writesBefore)
    const mutating = mockFetch.mock.calls.filter((call) => {
      const href = String(call[0])
      const method = String(((call[1] || {}) as RequestInit).method || 'GET').toUpperCase()
      return method !== 'GET' && /claim|promote|canonical|expectation|specification|surprise/.test(href)
    })
    expect(mutating).toEqual([])
  })
})
