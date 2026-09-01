import { beforeEach, describe, expect, test, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { I18nProvider } from '../../lib/i18n'
import AgentSpikePage from '../AgentSpikePage'

function sse(lines: object[]): Response {
  const body = lines.map((line) => `data: ${JSON.stringify(line)}\n\n`).join('')
  return new Response(body, { status: 200, headers: { 'content-type': 'text/event-stream' } })
}

describe('AgentSpikePage visible conversation seam', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  test('starts with an idea composer and turns a real ask into an approval panel', async () => {
    const optionOne = {
      id: 'policy_change',
      label: '最低工资上涨后，低薪岗位有没有减少？',
      consequence: '更接近因果，但需要政策变化前后的可比数据。',
    }
    const optionTwo = {
      id: 'region_difference',
      label: '最低工资较高的地区，就业是否不同？',
      consequence: '更容易完成，但只能说明同时出现。',
    }
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (String(url).endsWith('/state')) {
        return Promise.resolve(new Response('', { status: 404 }))
      }
      const call = mockFetch.mock.calls.length
      if (call === 1) {
        return Promise.resolve(
          sse([
            { kind: 'message', message_type: 'ai', node: 'model' },
            {
              kind: 'state',
              status: 'waiting_user',
              decision: {
                action: 'ask',
                message: '先确认你要回答的比较问题。',
                question: '你更想先回答哪一个问题？',
                options: [optionOne, optionTwo],
              },
            },
          ]),
        )
      }
      return Promise.resolve(
        sse([
          { kind: 'update', nodes: ['model'] },
          {
            kind: 'interrupt',
            value: {
              action_requests: [
                {
                  name: 'filter_fixture_data',
                  description:
                    '这个筛选会改变临时数据副本。预计保留 2 行（原始 4 行）。之后仍可以调整规则。',
                  args: { column: 'year', operator: '>=', value: 1992 },
                },
              ],
            },
          },
          {
            kind: 'state',
            status: 'waiting_approval',
            decision: {
              action: 'act',
              message: '需要你确认后才会改动临时副本。',
              preview: { status: 'ready', n_before: 4, n_after: 2 },
            },
          },
        ]),
      )
    })
    vi.stubGlobal('fetch', mockFetch)

    render(
      <I18nProvider>
        <AgentSpikePage />
      </I18nProvider>,
    )

    expect(screen.getByTestId('spike-page')).toBeInTheDocument()
    expect(screen.getByTestId('spike-idea-input')).toBeInTheDocument()
    expect(screen.getByTestId('spike-example-0')).toHaveTextContent('最低工资')
    expect(screen.queryByText(/DID|SCM|OLS|Agent|模型|插件/)).not.toBeInTheDocument()

    const user = userEvent.setup()
    await user.type(screen.getByTestId('spike-idea-input'), '我想研究最低工资提高后，会不会减少就业。')
    await user.click(screen.getByTestId('spike-send'))

    expect(await screen.findByTestId('spike-ask')).toBeInTheDocument()
    expect(screen.getByTestId('spike-option-policy_change')).toHaveTextContent(optionOne.label)
    expect(screen.getByTestId('spike-option-policy_change')).toHaveTextContent(optionOne.consequence)
    expect(screen.getByTestId('spike-option-region_difference')).toHaveTextContent(optionTwo.label)

    await user.click(screen.getByTestId('spike-option-policy_change'))
    expect(await screen.findByTestId('spike-approval-panel')).toBeInTheDocument()
    expect(screen.getByTestId('spike-approval-panel')).toHaveTextContent('预计保留 2 行')
    expect(screen.getByTestId('spike-progress')).toBeInTheDocument()
    expect(screen.getByTestId('spike-step-0')).toHaveTextContent('明确关心结果')
    expect(screen.getByTestId('spike-step-1')).toHaveTextContent('查看公开数据')
    expect(screen.getByTestId('spike-step-2')).toHaveTextContent('形成研究方向')
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/spike/agent/'),
      expect.objectContaining({ method: 'POST' }),
    )
  })

  test('restores a waiting approval checkpoint on reload', async () => {
    localStorage.setItem('econpaper_spike_session_id', 'persisted-thread')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            session_id: 'persisted-thread',
            status: 'waiting_approval',
            interrupt: {
              action_requests: [
                {
                  name: 'filter_fixture_data',
                  description: '预计保留 2 行（原始 4 行）。',
                },
              ],
            },
            decision: { action: 'act', preview: { status: 'ready', n_before: 4, n_after: 2 } },
          }),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      ),
    )

    render(
      <I18nProvider>
        <AgentSpikePage />
      </I18nProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('spike-approval-panel')).toBeInTheDocument())
    expect(screen.getByTestId('spike-session-id')).toHaveTextContent('persiste')
  })

  test('restores a paused checkpoint with a visible recovery entry', async () => {
    localStorage.setItem('econpaper_spike_session_id', 'paused-thread')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            session_id: 'paused-thread',
            status: 'paused_by_user',
            interrupt: {
              action_requests: [
                {
                  name: 'filter_fixture_data',
                  description: '预计保留 2 行（原始 4 行）。',
                },
              ],
            },
            decision: { action: 'act', preview: { status: 'ready', n_before: 4, n_after: 2 } },
          }),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      ),
    )

    render(
      <I18nProvider>
        <AgentSpikePage />
      </I18nProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('spike-paused')).toBeInTheDocument())
    expect(screen.getByTestId('spike-paused')).toHaveTextContent('已暂停，可稍后继续')
    expect(screen.getByTestId('spike-resume')).toBeInTheDocument()
  })

  test('persists pause, keeps the approval interrupt, and resumes into the same panel', async () => {
    localStorage.setItem('econpaper_spike_session_id', 'pause-thread')
    const interrupt = {
      action_requests: [
        {
          name: 'filter_fixture_data',
          description: '预计保留 2 行（原始 4 行）。',
          args: { column: 'year', operator: '>=', value: 1992 },
        },
      ],
    }
    const decision = { action: 'act', message: '需要你确认。', preview: { status: 'ready', n_before: 4, n_after: 2 } }
    const mockFetch = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      if (url.endsWith('/state')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({ session_id: 'pause-thread', status: 'waiting_approval', decision, interrupt }),
            { status: 200, headers: { 'content-type': 'application/json' } },
          ),
        )
      }
      if (url.endsWith('/pause')) {
        expect(init?.method).toBe('POST')
        return Promise.resolve(
          new Response(
            JSON.stringify({ session_id: 'pause-thread', status: 'paused_by_user', decision, interrupt }),
            { status: 200, headers: { 'content-type': 'application/json' } },
          ),
        )
      }
      if (url.endsWith('/resume')) {
        expect(init?.method).toBe('POST')
        return Promise.resolve(
          new Response(
            JSON.stringify({ session_id: 'pause-thread', status: 'waiting_approval', decision, interrupt }),
            { status: 200, headers: { 'content-type': 'application/json' } },
          ),
        )
      }
      throw new Error(`unexpected request: ${url}`)
    })
    vi.stubGlobal('fetch', mockFetch)

    render(
      <I18nProvider>
        <AgentSpikePage />
      </I18nProvider>,
    )

    const user = userEvent.setup()
    await waitFor(() => expect(screen.getByTestId('spike-approval-panel')).toBeInTheDocument())
    await user.click(screen.getByTestId('spike-pause'))
    expect(await screen.findByTestId('spike-paused')).toHaveTextContent('已暂停，可稍后继续')
    expect(screen.getByTestId('spike-resume')).toBeInTheDocument()
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/spike/agent/pause-thread/pause'),
      expect.objectContaining({ method: 'POST' }),
    )
    expect(mockFetch.mock.calls.some(([url]) => String(url).endsWith('/decision/stream'))).toBe(false)

    await user.click(screen.getByTestId('spike-resume'))
    expect(await screen.findByTestId('spike-approval-panel')).toBeInTheDocument()
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/spike/agent/pause-thread/resume'),
      expect.objectContaining({ method: 'POST' }),
    )
    expect(mockFetch.mock.calls.some(([url]) => String(url).endsWith('/decision/stream'))).toBe(false)
  })
})
