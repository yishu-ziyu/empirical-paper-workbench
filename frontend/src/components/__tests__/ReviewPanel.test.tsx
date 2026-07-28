// ADR-0007 Stage 2: ReviewPanel 组件测试
//
// 契约：
// 1. 渲染 5 维 rubric 条形图（内生性/识别策略/稳健性/贡献度/可读性）
// 2. 渲染评审反馈 + 修改建议
// 3. 渲染自动决策标签（pass/fail）
// 4. auto_decision="pass" 时"强制通过"按钮禁用
// 5. 点击按钮调 POST /review/decision 并触发 onDecision 回调
// 6. fetch 失败时显示错误提示
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReviewPanel, { type ReviewPanelProps } from '../ReviewPanel'
import type { components } from '../../types/api'

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

describe('ReviewPanel 人工评审面板', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.restoreAllMocks()
  })

  test('渲染 5 维 rubric 条形图', () => {
    render(<ReviewPanel {...baseProps} />)
    const dims = ['endogeneity', 'identification', 'robustness', 'contribution', 'readability']
    dims.forEach((dim) => {
      expect(screen.getByTestId(`rubric-dim-${dim}`)).toBeInTheDocument()
    })
  })

  test('渲染 rubric 中文标签', () => {
    render(<ReviewPanel {...baseProps} />)
    expect(screen.getByText('内生性')).toBeInTheDocument()
    expect(screen.getByText('识别策略')).toBeInTheDocument()
    expect(screen.getByText('稳健性')).toBeInTheDocument()
    expect(screen.getByText('贡献度')).toBeInTheDocument()
    expect(screen.getByText('可读性')).toBeInTheDocument()
  })

  test('渲染评审反馈和修改建议', () => {
    render(<ReviewPanel {...baseProps} />)
    expect(screen.getByText('章节质量良好，内生性处理得当。')).toBeInTheDocument()
    expect(screen.getByText('建议补充稳健性检验。')).toBeInTheDocument()
  })

  test('渲染自动决策标签 pass', () => {
    render(<ReviewPanel {...baseProps} />)
    const badge = screen.getByTestId('review-auto-decision')
    expect(badge.textContent).toContain('自动通过')
  })

  test('渲染自动决策标签 fail', () => {
    render(<ReviewPanel {...baseProps} review={failReview} />)
    const badge = screen.getByTestId('review-auto-decision')
    expect(badge.textContent).toContain('自动不通过')
  })

  test('auto_decision=pass 时强制通过按钮禁用', () => {
    render(<ReviewPanel {...baseProps} />)
    const forcePassBtn = screen.getByTestId('review-btn-force-pass')
    expect(forcePassBtn).toBeDisabled()
  })

  test('auto_decision=fail 时强制通过按钮可用', () => {
    render(<ReviewPanel {...baseProps} review={failReview} />)
    const forcePassBtn = screen.getByTestId('review-btn-force-pass')
    expect(forcePassBtn).not.toBeDisabled()
  })

  test('点击接受按钮调 POST 并触发 onDecision 回调', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ ok: true, decision: 'accept', chapter_index: 0, next_action: 'proceed' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    render(<ReviewPanel {...baseProps} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-accept'))

    await waitFor(() => {
      expect(onDecision).toHaveBeenCalledWith('accept', 'proceed')
    })
    expect(mockFetch).toHaveBeenCalledWith(
      '/sessions/test-session-1/review/decision',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  test('点击拒绝按钮调 POST 并收到 next_action=regenerate', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ ok: true, decision: 'reject', chapter_index: 0, next_action: 'regenerate' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    render(<ReviewPanel {...baseProps} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-reject'))

    await waitFor(() => {
      expect(onDecision).toHaveBeenCalledWith('reject', 'regenerate')
    })
  })

  test('点击强制通过按钮调 POST', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ ok: true, decision: 'force_pass', chapter_index: 0, next_action: 'proceed' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    render(<ReviewPanel {...baseProps} review={failReview} onDecision={onDecision} />)
    await user.click(screen.getByTestId('review-btn-force-pass'))

    await waitFor(() => {
      expect(onDecision).toHaveBeenCalledWith('force_pass', 'proceed')
    })
  })

  test('fetch 失败时显示错误提示', async () => {
    const user = userEvent.setup()
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ detail: '服务器错误' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    render(<ReviewPanel {...baseProps} />)
    await user.click(screen.getByTestId('review-btn-accept'))

    await waitFor(() => {
      expect(screen.getByTestId('review-error')).toBeInTheDocument()
      expect(screen.getByTestId('review-error').textContent).toContain('服务器错误')
    })
  })

  test('空评审数据渲染空态提示', () => {
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
    render(<ReviewPanel {...baseProps} review={emptyReview} />)
    expect(screen.getByText('暂无评审反馈')).toBeInTheDocument()
    expect(screen.getByText('暂无修改建议')).toBeInTheDocument()
  })
})
