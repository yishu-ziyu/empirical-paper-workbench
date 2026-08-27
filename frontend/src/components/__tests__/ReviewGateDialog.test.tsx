// ReviewGateDialog：审批硬证据门的显式交互契约
// 1. 显示分数与阈值
// 2. 默认步：打回重写触发 onRegenerate；关闭触发 onClose
// 3. 破坏性动作两步确认：先 arm 再 confirm 才触发一次 onForce
import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReviewGateDialog from '../ReviewGateDialog'
import { I18nProvider } from '../../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

const baseProps = {
  score: 0.4,
  threshold: 0.7,
  feedback: '主结果表缺少 treatment_row。',
  onRegenerate: vi.fn(),
  onForce: vi.fn(),
  onClose: vi.fn(),
}

describe('ReviewGateDialog 审批硬证据门', () => {
  test('alertdialog 角色与分数阈值可见', () => {
    renderWithI18n(<ReviewGateDialog {...baseProps} />)
    expect(screen.getByRole('alertdialog')).toBeInTheDocument()
    expect(screen.getByTestId('review-gate-score').textContent).toContain('0.40')
    expect(screen.getByTestId('review-gate-score').textContent).toContain('0.70')
  })

  test('无评分时显示"尚无评分"占位', () => {
    renderWithI18n(<ReviewGateDialog {...baseProps} score={null} />)
    const line = screen.getByTestId('review-gate-score').textContent ?? ''
    expect(line).toContain('尚无评分')
  })

  test('打回重写 → onRegenerate；返回修改 → onClose', async () => {
    const user = userEvent.setup()
    renderWithI18n(<ReviewGateDialog {...baseProps} />)
    await user.click(screen.getByTestId('review-gate-regen'))
    await user.click(screen.getByTestId('review-gate-close'))
    expect(baseProps.onRegenerate).toHaveBeenCalledTimes(1)
    expect(baseProps.onClose).toHaveBeenCalledTimes(1)
  })

  test('强行放行需两步确认，confirm 只发一次 onForce', async () => {
    const user = userEvent.setup()
    const onForce = vi.fn()
    renderWithI18n(<ReviewGateDialog {...baseProps} onForce={onForce} />)
    // 第一步只 arm，不触发
    await user.click(screen.getByTestId('review-gate-force-arm'))
    expect(onForce).not.toHaveBeenCalled()
    // 第二步确认
    await user.click(screen.getByTestId('review-gate-force-confirm'))
    expect(onForce).toHaveBeenCalledTimes(1)
  })

  test('评审意见有则显示，无则隐藏该块', () => {
    const { rerender } = renderWithI18n(
      <ReviewGateDialog {...baseProps} feedback="" />,
    )
    expect(screen.queryByTestId('review-gate-feedback')).toBeNull()
    rerender(<I18nProvider><ReviewGateDialog {...baseProps} /></I18nProvider>)
    expect(screen.getByTestId('review-gate-feedback')).toBeInTheDocument()
  })
})
