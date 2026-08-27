// RunTracePanel：运行档案面板契约
// - 默认拉 /trace?limit=20 并逆序展示（最新在上）
// - status 决定圆点颜色（ok 绿 / error、blocked 红 / 其他 amber）
// - 空态与刷新按钮
import { describe, test, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RunTracePanel from '../RunTracePanel'
import { I18nProvider } from '../../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

const events = [
  { ts: '2026-08-27T10:00:01+00:00', node: 'upload_pipeline', status: 'ok', duration_ms: 120.4 },
  { ts: '2026-08-27T10:00:05+00:00', node: 'approve_chapter', status: 'forced', detail: { reviewer_bypassed_review: true } },
]

function mockFetch(eventsPayload: unknown[] | null = events) {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ events: eventsPayload }),
  })
}

beforeEach(() => {
  vi.stubGlobal('fetch', mockFetch())
})

describe('RunTracePanel 运行档案', () => {
  test('展示事件列表，最新在上', async () => {
    renderWithI18n(<RunTracePanel sessionId="s1" />)
    await waitFor(() => expect(screen.getAllByTestId('trace-event')).toHaveLength(2))
    const first = screen.getAllByTestId('trace-event')[0]
    expect(first.textContent).toContain('approve_chapter')
  })

  test('空事件显示空态文案', async () => {
    vi.stubGlobal('fetch', mockFetch([]))
    renderWithI18n(<RunTracePanel sessionId="s1" />)
    await waitFor(() => expect(screen.getByText(/暂无|No runs/)).toBeInTheDocument())
  })

  test('点击刷新重新请求', async () => {
    const f = mockFetch()
    vi.stubGlobal('fetch', f)
    const user = userEvent.setup()
    renderWithI18n(<RunTracePanel sessionId="s1" />)
    await waitFor(() => expect(screen.getAllByTestId('trace-event')).toHaveLength(2))
    await user.click(screen.getByTestId('trace-refresh'))
    await waitFor(() => expect(f.mock.calls.length).toBeGreaterThanOrEqual(2))
  })
})
