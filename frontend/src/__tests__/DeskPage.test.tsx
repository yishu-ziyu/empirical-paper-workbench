import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ComponentProps } from 'react'
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

  test('打开时只有纸，没有问题卡和三栏', () => {
    renderDesk()
    expect(screen.getByTestId('desk-page')).toBeInTheDocument()
    expect(screen.getByTestId('desk-paper')).toBeInTheDocument()
    expect(screen.getByTestId('desk-listen-btn')).toBeInTheDocument()
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
    expect(screen.queryByTestId('desk-reflection')).not.toBeInTheDocument()
    expect(screen.queryByText('听到')).not.toBeInTheDocument()
    expect(screen.queryByTestId('desk-confirm-btn')).not.toBeInTheDocument()
    expect(screen.getByTestId('desk-ask-btn')).toBeInTheDocument()
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
})
