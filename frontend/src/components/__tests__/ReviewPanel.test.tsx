// HITL 盲评：点通过/否决之前不泄机器分；POST 成功后才 reveal，点继续才调 onDecision。
//
// 契约：
// 1. 点之前不显示自动通过、综合分、五维分数
// 2. 点之前显示修改建议和通过/否决（按钮永远是「通过」，不是「接受重生成」）
// 3. 点之前不显示强制通过
// 4. 点之前不显示评审反馈（反馈会泄底）
// 5. 点击通过：POST，出现机器分，还不调 onDecision
// 6. 点通过后再点继续：才调 onDecision('accept', 'proceed')
// 7. 点击否决：POST，reveal，点继续后 onDecision('reject', 'regenerate')
// 8. fetch 失败显示错误，仍不出现 auto-decision
// 9. 空建议显示暂无修改建议；反馈空态只在 reveal 之后
// 10. 点 fail 稿通过后，徽章是自动不通过，综合分 0.42 出现
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReviewPanel, { type ReviewPanelProps } from '../ReviewPanel'
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

describe('ReviewPanel 人工评审面板', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.restoreAllMocks()
  })

  test('点之前不显示自动通过、综合分、五维分数', () => {
    renderWithI18n(<ReviewPanel {...baseProps} />)

    expect(screen.queryByTestId('review-auto-decision')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-score')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-rubric')).not.toBeInTheDocument()
    RUBRIC_DIMS.forEach((dim) => {
      expect(screen.queryByTestId(`rubric-dim-${dim}`)).not.toBeInTheDocument()
    })
    expect(screen.queryByText('自动通过')).not.toBeInTheDocument()
    expect(screen.queryByText('自动不通过')).not.toBeInTheDocument()
    expect(screen.queryByText(/综合 0\.87/)).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-source')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-grounding')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-machine-reveal')).not.toBeInTheDocument()
  })

  test('点之前显示修改建议和通过/否决', () => {
    renderWithI18n(<ReviewPanel {...baseProps} />)

    expect(screen.getByText('章节评审')).toBeInTheDocument()
    expect(screen.getByText('第 1/2 轮')).toBeInTheDocument()
    expect(screen.getByTestId('review-blind-hint')).toHaveTextContent('先看正文再点。点完才显示机器分。')
    expect(screen.getByTestId('review-suggestions')).toHaveTextContent('建议补充稳健性检验。')

    const acceptBtn = screen.getByTestId('review-btn-accept')
    const rejectBtn = screen.getByTestId('review-btn-reject')
    expect(acceptBtn).toHaveTextContent('通过')
    expect(acceptBtn).not.toHaveTextContent('接受重生成')
    expect(rejectBtn).toHaveTextContent('否决')
    expect(screen.queryByTestId('review-btn-continue')).not.toBeInTheDocument()
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

  test('点之前不显示评审反馈（反馈会泄底）', () => {
    renderWithI18n(<ReviewPanel {...baseProps} />)

    expect(screen.queryByTestId('review-feedback')).not.toBeInTheDocument()
    expect(screen.queryByText('章节质量良好，内生性处理得当。')).not.toBeInTheDocument()
    expect(screen.queryByText('暂无评审反馈')).not.toBeInTheDocument()
  })

  test('点击通过：POST，出现机器分，还不调 onDecision', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    const mockFetch = mockDecisionFetch('accept', 'proceed')
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<ReviewPanel {...baseProps} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-accept'))

    await waitFor(() => {
      expect(screen.getByTestId('review-auto-decision')).toBeInTheDocument()
    })

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/sessions/test-session-1/review/decision'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ decision: 'accept' }),
      }),
    )
    expect(onDecision).not.toHaveBeenCalled()
    expect(screen.getByTestId('review-auto-decision')).toHaveTextContent('自动通过')
    expect(screen.getByTestId('review-score')).toHaveTextContent('综合 0.87')
    expect(screen.getByTestId('review-rubric')).toBeInTheDocument()
    RUBRIC_DIMS.forEach((dim) => {
      expect(screen.getByTestId(`rubric-dim-${dim}`)).toBeInTheDocument()
    })
    expect(screen.getByTestId('review-feedback')).toHaveTextContent('章节质量良好，内生性处理得当。')
    expect(screen.getByTestId('review-machine-reveal')).toBeInTheDocument()
    expect(screen.getByTestId('review-btn-continue')).toHaveTextContent('继续')
    expect(screen.queryByTestId('review-btn-accept')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-btn-reject')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-blind-hint')).not.toBeInTheDocument()
  })

  test("点通过后再点继续：才调 onDecision('accept', 'proceed')", async () => {
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

  test("点击否决：POST，reveal，点继续后 onDecision('reject', 'regenerate')", async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    const mockFetch = mockDecisionFetch('reject', 'regenerate')
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<ReviewPanel {...baseProps} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-reject'))

    await waitFor(() => {
      expect(screen.getByTestId('review-machine-reveal')).toBeInTheDocument()
    })

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/sessions/test-session-1/review/decision'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ decision: 'reject' }),
      }),
    )
    expect(onDecision).not.toHaveBeenCalled()
    expect(screen.getByTestId('review-auto-decision')).toBeInTheDocument()
    expect(screen.getByTestId('review-score')).toBeInTheDocument()
    expect(screen.getByTestId('review-rubric')).toBeInTheDocument()
    expect(screen.getByTestId('review-feedback')).toBeInTheDocument()

    await user.click(screen.getByTestId('review-btn-continue'))
    expect(onDecision).toHaveBeenCalledTimes(1)
    expect(onDecision).toHaveBeenCalledWith('reject', 'regenerate')
  })

  test('fetch 失败显示错误，仍不出现 auto-decision', async () => {
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
    expect(screen.queryByTestId('review-auto-decision')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-score')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-rubric')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-feedback')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-machine-reveal')).not.toBeInTheDocument()
    expect(screen.queryByTestId('review-btn-continue')).not.toBeInTheDocument()
    expect(screen.getByTestId('review-btn-accept')).toBeInTheDocument()
    expect(screen.getByTestId('review-btn-reject')).toBeInTheDocument()
    expect(onDecision).not.toHaveBeenCalled()
  })

  test('空建议显示暂无修改建议', () => {
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

  test('点 fail 稿通过后，徽章是自动不通过，综合分 0.42 出现', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    vi.stubGlobal('fetch', mockDecisionFetch('accept', 'proceed'))

    renderWithI18n(<ReviewPanel {...baseProps} review={failReview} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-accept'))

    await waitFor(() => {
      expect(screen.getByTestId('review-auto-decision')).toBeInTheDocument()
    })

    expect(screen.getByTestId('review-auto-decision')).toHaveTextContent('自动不通过')
    expect(screen.getByTestId('review-score')).toHaveTextContent('综合 0.42')
    expect(screen.getByTestId('review-machine-reveal').textContent).toContain('自动不通过')
    expect(onDecision).not.toHaveBeenCalled()
  })
})
