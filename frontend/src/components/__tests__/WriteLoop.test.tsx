import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WriteLoop from '../WriteLoop'
import { I18nProvider } from '../../lib/i18n'

describe('WriteLoop Copaper writing chrome', () => {
  test('file card, confirm, pause, and outline approve stay out of the right-pane path', async () => {
    const user = userEvent.setup()
    const onApply = vi.fn()
    const onApprove = vi.fn()
    render(
      <I18nProvider>
        <WriteLoop
          fileName="panel.csv"
          rows={891}
          cols={8}
          direction={{ question: '年龄和收入是否相关？', dv: 'income', iv: 'age', method: 'OLS' }}
          hasDirection
          hasOutline
          partIndex={1}
          onApplyGenerate={onApply}
          onApproveOutline={onApprove}
        />
      </I18nProvider>,
    )
    expect(screen.getByTestId('session-file')).toHaveTextContent('891')
    expect(screen.getByTestId('info-confirm')).toHaveTextContent('已收集研究信息')
    expect(screen.getByTestId('chapter-pause')).toHaveTextContent('CHAPTER PAUSE')
    expect(screen.getAllByText('AI 决定').length).toBeGreaterThan(0)
    expect(screen.queryByTestId('refine-chat')).not.toBeInTheDocument()
    await user.click(screen.getByTestId('pause-apply'))
    await user.click(screen.getByTestId('outline-approve-btn'))
    expect(onApply).toHaveBeenCalledTimes(1)
    expect(onApprove).toHaveBeenCalledTimes(1)
  })

  test('results pause exposes tables and figures; refine chat appears after a chapter', () => {
    render(
      <I18nProvider>
        <WriteLoop hasOutline hasChapter isResultsPart agentPct={10} />
      </I18nProvider>,
    )
    expect(screen.getByText('表')).toBeInTheDocument()
    expect(screen.getByText('图')).toBeInTheDocument()
    expect(screen.getByTestId('refine-chat')).toBeInTheDocument()
    expect(screen.getByTestId('paper-agent')).toHaveTextContent('10%')
  })
})
