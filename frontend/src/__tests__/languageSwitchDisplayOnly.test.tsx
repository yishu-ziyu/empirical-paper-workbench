import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import App from '../App'
import { I18nProvider } from '../lib/i18n'
import { htmlLangAttr } from '../lib/i18n'
import { ExpectationEditor } from '../components/ResearchLabPanels'
import { TaskHelp } from '../components/TaskHelp'
import { LangPills } from '../components/UnauthHeader'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

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
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    expect(onSave).not.toHaveBeenCalled()
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent('IV estimate < OLS estimate')
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
})
