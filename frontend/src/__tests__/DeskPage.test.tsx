import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ComponentProps } from 'react'
import { StrictMode } from 'react'
import DeskPage from '../pages/DeskPage'
import { I18nProvider } from '../lib/i18n'

function renderDesk(props: Partial<ComponentProps<typeof DeskPage>> = {}) {
  return render(
    <I18nProvider>
      <DeskPage
      authed onConfirm={vi.fn()} onPickData={vi.fn()} {...props} />
    </I18nProvider>,
  )
}

function mockDiscuss(body: Record<string, unknown>) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(body),
    }),
  )
}

describe('DeskPage', () => {
  beforeEach(() => {
    mockDiscuss({
      reflection: '我听到了 CHARLS、养老。现在比较像一个方向，还不太像一个问题。',
      title: '养老金并轨之后，临近退休的人是不是更早离开劳动力市场？',
      heard: ['CHARLS', '养老'],
      comparison: '还没定',
      outcome: '还没定',
      question: '你现在更想弄清哪一件事？',
      options: [
        { id: 'policy', label: '政策有没有效果' },
        { id: 'who', label: '谁受到了影响' },
      ],
      explain: '',
      ready: false,
      source: 'llm',
    })
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('打开时是连续对话空态，并保留左右功能栏', () => {
    renderDesk()
    expect(screen.getByTestId('desk-page')).toBeInTheDocument()
    expect(screen.getByTestId('desk-paper')).toBeInTheDocument()
    expect(screen.getByTestId('desk-listen-btn')).toBeInTheDocument()
    expect(screen.getByTestId('desk-left-sidebar')).toBeInTheDocument()
    expect(screen.getByTestId('agent-window')).toBeInTheDocument()
    expect(screen.getByTestId('desk-empty-state')).toBeInTheDocument()
    expect(screen.queryByTestId('question-card')).not.toBeInTheDocument()
    expect(screen.queryByTestId('direction-section')).not.toBeInTheDocument()
  })

  test('倒出想法后出现一张可改的问题卡，一次只问一件事', async () => {
    const user = userEvent.setup()
    renderDesk()

    await user.type(screen.getByTestId('desk-paper'), '导师让我用 CHARLS 做点养老的')
    await user.click(screen.getByTestId('desk-shape-btn'))

    await waitFor(() => {
      expect(screen.getByTestId('question-card')).toBeInTheDocument()
    })
    expect((screen.getByTestId('question-title') as HTMLTextAreaElement).value).toMatch(/养老|退休/)
    expect(screen.getByTestId('desk-option-policy')).toBeInTheDocument()
    expect(screen.queryByTestId('desk-option-work')).not.toBeInTheDocument()
    expect(screen.getByTestId('desk-thread')).toHaveTextContent('导师让我用 CHARLS 做点养老的')
    expect(screen.getByTestId('desk-reflection')).toHaveTextContent('我听到了 CHARLS、养老')
    expect(screen.getByTestId('desk-ask-input')).toBeInTheDocument()
    expect(screen.queryByTestId('desk-confirm-btn')).not.toBeInTheDocument()
    expect(screen.getByTestId('desk-ask-btn')).toBeInTheDocument()
  })

  test('从首屏带入的想法在 StrictMode 下也会自动触发首次追问', async () => {
    sessionStorage.setItem('desk_idea_draft', '我想研究高铁开通是否促进县域创业')
    render(
      <StrictMode>
        <I18nProvider>
          <DeskPage authed onConfirm={vi.fn()} onPickData={vi.fn()} />
        </I18nProvider>
      </StrictMode>,
    )

    expect(screen.getByTestId('desk-paper')).toHaveValue('我想研究高铁开通是否促进县域创业')
    expect(await screen.findByTestId('question-card', {}, { timeout: 2500 })).toBeInTheDocument()
  })

  test('两侧栏可以收起，宽度设置会保留', async () => {
    const user = userEvent.setup()
    renderDesk()

    await user.click(screen.getByTestId('left-collapse-btn'))
    await user.click(screen.getByTestId('right-collapse-btn'))

    expect(screen.getByTestId('desk-left-sidebar')).toHaveClass('hidden')
    expect(screen.getByTestId('agent-window')).toHaveClass('hidden')
    expect(localStorage.getItem('econpaper.direction.layout.v2')).toContain('"leftOpen":false')
    expect(localStorage.getItem('econpaper.direction.layout.v2')).toContain('"rightOpen":false')
  })

  test('问候只得到自然引导，不出现论文标题和固定研究选项', async () => {
    const user = userEvent.setup()
    mockDiscuss({
      intent: 'conversation',
      reflection: '你好！你可以随便说一句最近想研究的现象或问题。',
      title: '',
      heard: [],
      comparison: '还没定',
      outcome: '还没定',
      question: '',
      options: [],
      explain: '',
      ready: false,
      source: 'llm',
    })
    renderDesk()

    await user.type(screen.getByTestId('desk-paper'), "ni'hao")
    await user.click(screen.getByTestId('desk-shape-btn'))

    expect(await screen.findByTestId('conversation-reply')).toHaveTextContent('你好')
    expect(screen.queryByTestId('question-title')).not.toBeInTheDocument()
    expect(screen.queryByTestId('desk-option-policy')).not.toBeInTheDocument()
    expect(screen.getByTestId('desk-conversation-input')).toBeInTheDocument()

    mockDiscuss({
      reflection: '我先保留你的原话。现在只确认要比较什么。',
      title: '我想研究绿色金融是否降低了高耗能企业的碳排放',
      heard: [],
      comparison: '还没定',
      outcome: '还没定',
      question: '你现在更想弄清哪一件事？',
      options: [{ id: 'policy', label: '政策有没有效果' }],
      explain: '',
      ready: false,
      source: 'llm',
    })
    await user.type(
      screen.getByTestId('desk-conversation-input'),
      '我想研究绿色金融是否降低了高耗能企业的碳排放',
    )
    await user.click(screen.getByTestId('desk-ask-send'))

    expect(await screen.findByTestId('question-card')).toBeInTheDocument()
    expect(screen.getByTestId('desk-thread')).toHaveTextContent("ni'hao")
    expect(screen.getByTestId('desk-thread')).toHaveTextContent('绿色金融是否降低')
  })

  test('两轮选择后才能确认问题', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    renderDesk({ onConfirm })

    await user.type(screen.getByTestId('desk-paper'), '导师让我用 CHARLS 做点养老的')
    await user.click(screen.getByTestId('desk-shape-btn'))
    await waitFor(() => {
      expect(screen.getByTestId('desk-option-policy')).toBeInTheDocument()
    })
    mockDiscuss({
      reflection: '比较这边有了。还差结果看什么。',
      title: '养老金并轨之后，临近退休的人是不是更早离开劳动力市场？',
      heard: ['CHARLS', '养老'],
      comparison: '比较政策前后',
      outcome: '还没定',
      question: '结果你更想看哪一类？',
      options: [{ id: 'work', label: '工作和退休' }],
      ready: false,
      source: 'llm',
    })
    await user.click(screen.getByTestId('desk-option-policy'))
    await waitFor(() => {
      expect(screen.getByTestId('desk-option-work')).toBeInTheDocument()
    })
    mockDiscuss({
      reflection: '可以停在这里了。',
      title: '养老金并轨之后，临近退休的人是不是更早离开劳动力市场？',
      heard: ['CHARLS', '养老'],
      comparison: '比较政策前后',
      outcome: '看就业、工时或退休',
      question: '',
      options: [],
      ready: true,
      source: 'llm',
    })
    await user.click(screen.getByTestId('desk-option-work'))

    const confirm = await screen.findByTestId('desk-confirm-btn')
    expect(confirm).toBeEnabled()
    await user.click(confirm)
    expect(onConfirm).toHaveBeenCalledTimes(1)
    expect(String(onConfirm.mock.calls[0][0])).toMatch(/养老|退休/)
  })

  test('用户直接求助时不重复旧问题，并把回复作为自由回答发送', async () => {
    const user = userEvent.setup()
    const question = '你打算用什么数据来源？'
    let resolveGuidance!: (value: unknown) => void
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          intent: 'research',
          reflection: '这个问题需要一份能连接两代人的数据。',
          title: '教育的作用会不会隔代才显著',
          heard: ['教育', '代际'],
          comparison: '还没定',
          outcome: '还没定',
          question,
          options: [{ id: 'unknown', label: '我不清楚' }],
          explain: '',
          ready: false,
          source: 'llm',
        }),
      })
      .mockImplementationOnce(() => new Promise((resolve) => {
        resolveGuidance = resolve
      }))
    vi.stubGlobal('fetch', fetchMock)
    renderDesk()

    await user.type(screen.getByTestId('desk-paper'), '教育的作用会不会隔代才显著')
    await user.click(screen.getByTestId('desk-shape-btn'))
    expect(await screen.findByText(question)).toBeInTheDocument()

    await user.type(screen.getByTestId('desk-ask-input'), '我不太清楚，你觉得用哪些数据会更合适？')
    await user.click(screen.getByTestId('desk-ask-send'))

    expect(screen.getAllByText(question)).toHaveLength(1)
    expect(screen.getByTestId('desk-thinking')).toBeInTheDocument()
    expect(screen.getByTestId('desk-ask-input')).toHaveValue('')
    expect(screen.queryByTestId('desk-paper')).not.toBeInTheDocument()
    const secondBody = JSON.parse(String(fetchMock.mock.calls[1][1]?.body))
    expect(secondBody.turns[0].id).toBe('freeform')

    resolveGuidance({
      ok: true,
      json: () => Promise.resolve({
        intent: 'research',
        reflection: '我来替你比较。',
        title: '教育的作用会不会隔代才显著',
        heard: ['教育', '代际'],
        comparison: '还没定',
        outcome: '还没定',
        question: '先按我的建议继续，可以吗？',
        options: [{ id: 'accept_recommendation', label: '按建议继续' }],
        explain: '我建议先看 CFPS，因为它更接近家庭与代际追踪场景。',
        ready: false,
        source: 'llm',
      }),
    })

    expect(await screen.findByText(/我建议先看 CFPS/)).toBeInTheDocument()
    expect(screen.getAllByText(question)).toHaveLength(1)
  })
})
