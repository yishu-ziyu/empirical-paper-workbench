// HITL 盲评：点通过/否决之前不泄机器分；POST 后先出现「你点了…」和「看机器怎么说」，
// 点 peek 才 reveal 机器意见，点继续才调 onDecision。
//
// 契约：
// 1. 点之前不显示自动通过、综合分、五维分数
// 2. 点之前显示修改建议和通过/否决（无 hint）
// 3. 点之前不显示强制通过
// 4. 点之前不显示评审反馈
// 5. 点之前剥掉结构层失败
// 6. 点击通过：POST，出现你点了通过和看机器怎么说，还不出现分数，不调 onDecision
// 7. 点看机器怎么说才出现自动通过和综合分
// 8. 点通过后再点继续才调 onDecision
// 9. 点击否决后点继续
// 10. fetch 失败不泄底
// 11. 空建议
// 12. fail 稿：点看机器怎么说后徽章是自动不通过 0.42
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReviewPanel, { stripVerdictFromSuggestions, type ReviewPanelProps } from '../ReviewPanel'
import type { components } from '../../types/api'
import { I18nProvider } from '../../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

type ReviewInfoResponse = components['schemas']['ReviewInfoResponse']

const passReview: ReviewInfoResponse = {
  chapter_index: 0,
  feedback: '章节质量良好，内生性处理得当。',
  suggestions: '建议补充稳健性检验。',
  score: 0.87,
  rubric: {
    endogeneity: 0.9,
    identification: 0.85,
    robustness: 0.8,
    contribution: 0.9,
    readability: 0.85,
  },
  review_iteration: 1,
  max_review_iterations: 2,
  auto_decision: 'pass',
}

const failReview: ReviewInfoResponse = {
  chapter_index: 0,
  feedback: '识别策略不清晰，内生性问题未解决。',
  suggestions: '请明确工具变量或使用 DID 设计。',
  score: 0.42,
  rubric: {
    endogeneity: 0.2,
    identification: 0.3,
    robustness: 0.4,
    contribution: 0.5,
    readability: 0.6,
  },
  review_iteration: 2,
  max_review_iterations: 2,
  auto_decision: 'fail',
}

const stuffedReview: ReviewInfoResponse = {
  ...failReview,
  suggestions: '结构层失败：keyword_stuffed。不得只堆关键词。请改写引言。',
}

const baseProps: ReviewPanelProps = {
  review: passReview,
  sessionId: 'test-session-1',
  onDecision: vi.fn(),
}

const RUBRIC_DIMS = ['endogeneity', 'identification', 'robustness', 'contribution', 'readability']

function mockDecisionFetch(decision: string, nextAction: string) {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({ ok: true, decision, chapter_index: 0, next_action: nextAction }),
  })
}

function expectMachineHidden() {
  expect(screen.queryByTestId('review-auto-decision')).not.toBeInTheDocument()
  expect(screen.queryByTestId('review-score')).not.toBeInTheDocument()
  expect(screen.queryByTestId('review-rubric')).not.toBeInTheDocument()
  expect(screen.queryByTestId('review-feedback')).not.toBeInTheDocument()
  RUBRIC_DIMS.forEach((dim) => {
    expect(screen.queryByTestId(`rubric-dim-${dim}`)).not.toBeInTheDocument()
  })
  expect(screen.queryByText('自动通过')).not.toBeInTheDocument()
  expect(screen.queryByText('自动不通过')).not.toBeInTheDocument()
  expect(screen.queryByText(/综合 0\.\d+/)).not.toBeInTheDocument()
}

describe('stripVerdictFromSuggestions', () => {
  test('剥掉结构层失败、不得只堆关键词等判决短语', () => {
    expect(
      stripVerdictFromSuggestions('结构层失败：keyword_stuffed。不得只堆关键词。请改写引言。'),
    ).toBe('请改写引言。')
    expect(stripVerdictFromSuggestions('建议补充稳健性检验。')).toBe('建议补充稳健性检验。')
    expect(stripVerdictFromSuggestions('')).toBe('')
  })
})

describe('ReviewPanel 人工评审面板', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.restoreAllMocks()
  })

  test('点之前不显示自动通过、综合分、五维分数', () => {
    renderWithI18n(<ReviewPanel {...baseProps} />)

    expectMachineHidden()
    expect(screen.queryByTestId('review-source')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-grounding')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-your-decision')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-btn-peek')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-blind-hint')).not.toBeInTheDocument()
    expect(screen.queryByText('先看正文再点')).not.toBeInTheDocument()
  })

  test('点之前显示修改建议和通过/否决（无 hint）', () => {
    renderWithI18n(<ReviewPanel {...baseProps} />)

    expect(screen.getByText('章节评审')).toBeInTheDocument()
    expect(screen.getByText('第 1/2 轮')).toBeInTheDocument()
    expect(screen.queryByTestId('review-blind-hint')).not.toBeInTheDocument()
    expect(screen.queryByText('先看正文再点')).not.toBeInTheDocument()
    expect(screen.getByTestId('review-suggestions')).toHaveTextContent('建议补充稳健性检验。')

    const acceptBtn = screen.getByTestId('review-btn-accept')
    const rejectBtn = screen.getByTestId('review-btn-reject')
    expect(acceptBtn).toHaveTextContent('通过')
    expect(acceptBtn).not.toHaveTextContent('接受重生成')
    expect(rejectBtn).toHaveTextContent('否决')
    expect(screen.queryByTestId('review-btn-continue')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-btn-peek')).not.toBeInTheDocument()
  })

  test('点之前不显示强制通过', () => {
    const { unmount } = renderWithI18n(<ReviewPanel {...baseProps} />)
    expect(screen.queryByTestId('review-btn-force-pass')).not.toBeInTheDocument()
    expect(screen.queryByText('强制通过')).not.toBeInTheDocument()
    unmount()

    renderWithI18n(<ReviewPanel {...baseProps} review={failReview} />)
    expect(screen.queryByTestId('review-btn-force-pass')).not.toBeInTheDocument()
    expect(screen.queryByText('强制通过')).not.toBeInTheDocument()
  })

  test('点之前不显示评审反馈', () => {
    renderWithI18n(<ReviewPanel {...baseProps} />)

    expect(screen.queryByTestId('review-feedback')).not.toBeInTheDocument()
    expect(screen.queryByText('章节质量良好，内生性处理得当。')).not.toBeInTheDocument()
    expect(screen.queryByText('暂无评审反馈')).not.toBeInTheDocument()
  })

  test('点之前剥掉结构层失败', () => {
    renderWithI18n(<ReviewPanel {...baseProps} review={stuffedReview} />)

    const suggestions = screen.getByTestId('review-suggestions')
    expect(suggestions).toHaveTextContent('请改写引言。')
    expect(suggestions).not.toHaveTextContent('结构层失败')
    expect(suggestions).not.toHaveTextContent('keyword_stuffed')
    expect(suggestions).not.toHaveTextContent('不得只堆关键词')
    expect(screen.queryByText('自动不通过')).not.toBeInTheDocument()
  })

  test('点击通过：POST，出现你点了通过和看机器怎么说，还不出现分数，不调 onDecision', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    const mockFetch = mockDecisionFetch('accept', 'proceed')
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<ReviewPanel {...baseProps} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-accept'))

    await waitFor(() => {
      expect(screen.getByTestId('review-your-decision')).toBeInTheDocument()
    })

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/sessions/test-session-1/review/decision'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ decision: 'accept' }),
      }),
    )
    expect(onDecision).not.toHaveBeenCalled()
    expect(screen.getByTestId('review-your-decision')).toHaveTextContent('你点了通过')
    expect(screen.getByTestId('review-btn-peek')).toHaveTextContent('看机器怎么说')
    expect(screen.getByTestId('review-btn-continue')).toHaveTextContent('继续')
    expect(screen.queryByTestId('review-btn-accept')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-btn-reject')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-blind-hint')).not.toBeInTheDocument()
    expectMachineHidden()
  })

  test('点看机器怎么说才出现自动通过和综合分', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    vi.stubGlobal('fetch', mockDecisionFetch('accept', 'proceed'))

    renderWithI18n(<ReviewPanel {...baseProps} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-accept'))

    await waitFor(() => {
      expect(screen.getByTestId('review-btn-peek')).toBeInTheDocument()
    })
    expectMachineHidden()
    expect(onDecision).not.toHaveBeenCalled()

    await user.click(screen.getByTestId('review-btn-peek'))

    expect(screen.getByTestId('review-auto-decision')).toHaveTextContent('自动通过')
    expect(screen.getByTestId('review-score')).toHaveTextContent('综合 0.87')
    expect(screen.getByTestId('review-rubric')).toBeInTheDocument()
    RUBRIC_DIMS.forEach((dim) => {
      expect(screen.getByTestId(`rubric-dim-${dim}`)).toBeInTheDocument()
    })
    expect(screen.getByTestId('review-feedback')).toHaveTextContent('章节质量良好，内生性处理得当。')
    expect(screen.getByTestId('review-btn-peek')).toHaveTextContent('收起机器意见')
    expect(onDecision).not.toHaveBeenCalled()

    await user.click(screen.getByTestId('review-btn-peek'))
    expectMachineHidden()
    expect(screen.getByTestId('review-btn-peek')).toHaveTextContent('看机器怎么说')
    expect(screen.getByTestId('review-your-decision')).toHaveTextContent('你点了通过')
  })

  test("点通过后再点继续才调 onDecision('accept', 'proceed')", async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    vi.stubGlobal('fetch', mockDecisionFetch('accept', 'proceed'))

    renderWithI18n(<ReviewPanel {...baseProps} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-accept'))

    await waitFor(() => {
      expect(screen.getByTestId('review-btn-continue')).toBeInTheDocument()
    })
    expect(onDecision).not.toHaveBeenCalled()

    await user.click(screen.getByTestId('review-btn-continue'))
    expect(onDecision).toHaveBeenCalledTimes(1)
    expect(onDecision).toHaveBeenCalledWith('accept', 'proceed')
  })

  test("点击否决后点继续：onDecision('reject', 'regenerate')", async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    const mockFetch = mockDecisionFetch('reject', 'regenerate')
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<ReviewPanel {...baseProps} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-reject'))

    await waitFor(() => {
      expect(screen.getByTestId('review-your-decision')).toBeInTheDocument()
    })

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/sessions/test-session-1/review/decision'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ decision: 'reject' }),
      }),
    )
    expect(onDecision).not.toHaveBeenCalled()
    expect(screen.getByTestId('review-your-decision')).toHaveTextContent('你点了否决')
    expect(screen.getByTestId('review-btn-peek')).toHaveTextContent('看机器怎么说')
    expectMachineHidden()

    await user.click(screen.getByTestId('review-btn-continue'))
    expect(onDecision).toHaveBeenCalledTimes(1)
    expect(onDecision).toHaveBeenCalledWith('reject', 'regenerate')
  })

  test('fetch 失败不泄底', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ detail: '服务器错误' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<ReviewPanel {...baseProps} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-accept'))

    await waitFor(() => {
      expect(screen.getByTestId('review-error')).toBeInTheDocument()
    })
    expect(screen.getByTestId('review-error').textContent).toContain('服务器错误')
    expectMachineHidden()
    expect(screen.queryByTestId('review-your-decision')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-btn-peek')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-btn-continue')).not.toBeInTheDocument()
    expect(screen.getByTestId('review-btn-accept')).toBeInTheDocument()
    expect(screen.getByTestId('review-btn-reject')).toBeInTheDocument()
    expect(onDecision).not.toHaveBeenCalled()
  })

  test('空建议', () => {
    const emptyReview: ReviewInfoResponse = {
      chapter_index: 0,
      feedback: '',
      suggestions: '',
      score: 0,
      rubric: {},
      review_iteration: 0,
      max_review_iterations: 2,
      auto_decision: 'fail',
    }
    renderWithI18n(<ReviewPanel {...baseProps} review={emptyReview} />)

    expect(screen.getByTestId('review-suggestions')).toHaveTextContent('暂无修改建议')
    expect(screen.getByText('暂无修改建议')).toBeInTheDocument()
    expect(screen.queryByTestId('review-feedback')).not.toBeInTheDocument()
    expect(screen.queryByText('暂无评审反馈')).not.toBeInTheDocument()
  })

  test('fail 稿：点看机器怎么说后徽章是自动不通过 0.42', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    vi.stubGlobal('fetch', mockDecisionFetch('accept', 'proceed'))

    renderWithI18n(<ReviewPanel {...baseProps} review={failReview} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-accept'))

    await waitFor(() => {
      expect(screen.getByTestId('review-btn-peek')).toBeInTheDocument()
    })
    expect(screen.queryByTestId('review-auto-decision')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-score')).not.toBeInTheDocument()

    await user.click(screen.getByTestId('review-btn-peek'))

    expect(screen.getByTestId('review-auto-decision')).toHaveTextContent('自动不通过')
    expect(screen.getByTestId('review-score')).toHaveTextContent('综合 0.42')
    expect(onDecision).not.toHaveBeenCalled()
  })

  test('点看机器怎么说后还原完整建议（含结构层失败）', async () => {
    const user = userEvent.setup()
    vi.stubGlobal('fetch', mockDecisionFetch('accept', 'proceed'))

    renderWithI18n(<ReviewPanel {...baseProps} review={stuffedReview} />)
    expect(screen.getByTestId('review-suggestions')).not.toHaveTextContent('结构层失败')

    await user.click(screen.getByTestId('review-btn-accept'))
    await waitFor(() => {
      expect(screen.getByTestId('review-btn-peek')).toBeInTheDocument()
    })
    expect(screen.getByTestId('review-suggestions')).toHaveTextContent('请改写引言。')
    expect(screen.getByTestId('review-suggestions')).not.toHaveTextContent('结构层失败')

    await user.click(screen.getByTestId('review-btn-peek'))
    expect(screen.getByTestId('review-suggestions')).toHaveTextContent(
      '结构层失败：keyword_stuffed。不得只堆关键词。请改写引言。',
    )
  })
})
