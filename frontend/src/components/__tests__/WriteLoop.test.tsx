import { describe, test, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WriteLoop from '../WriteLoop'
import { I18nProvider } from '../../lib/i18n'

const SERVER_OUTLINE = [
  { type: 'intro', title: '引言' },
  { type: 'results', title: '结果' },
]

describe('WriteLoop pause and refine', () => {
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
          outline={SERVER_OUTLINE}
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
    expect(onApprove.mock.calls[0][0]).toEqual(SERVER_OUTLINE)
    expect(onApply.mock.calls[0][0]).toEqual({ outline: SERVER_OUTLINE, render_kwargs: {} })
  })

  test('I-decide chapters changes the outline passed to Approve Outline', async () => {
    const user = userEvent.setup()
    const onApprove = vi.fn()
    render(
      <I18nProvider>
        <WriteLoop
          outline={SERVER_OUTLINE}
          hasOutline
          onApproveOutline={onApprove}
        />
      </I18nProvider>,
    )
    await user.click(screen.getByTestId('chapters-me'))
    expect(screen.getByTestId('pause-chapter-editor')).toBeInTheDocument()
    expect(screen.getByTestId('pause-chapter-count')).toHaveValue(2)
    await user.click(screen.getByTestId('pause-keep-results'))
    await user.click(screen.getByTestId('outline-approve-btn'))
    expect(onApprove).toHaveBeenCalledTimes(1)
    expect(onApprove.mock.calls[0][0]).toEqual([{ type: 'intro', title: '引言' }])
  })

  test('I-decide paragraphs/tables/figures land in the generate payload', async () => {
    const user = userEvent.setup()
    const onApply = vi.fn()
    render(
      <I18nProvider>
        <WriteLoop
          outline={SERVER_OUTLINE}
          hasOutline
          isResultsPart
          partIndex={2}
          onApplyGenerate={onApply}
        />
      </I18nProvider>,
    )
    await user.click(screen.getByTestId('paragraphs-me'))
    fireEvent.change(screen.getByTestId('pause-paragraphs'), { target: { value: '5' } })
    await user.click(screen.getByTestId('tables-me'))
    fireEvent.change(screen.getByTestId('pause-tables'), { target: { value: '2' } })
    await user.click(screen.getByTestId('figures-me'))
    fireEvent.change(screen.getByTestId('pause-figures'), { target: { value: '1' } })
    await user.click(screen.getByTestId('pause-apply'))
    expect(onApply.mock.calls[0][0].render_kwargs).toEqual({
      paragraphs: 5,
      tables: 2,
      figures: 1,
    })
    expect(onApply.mock.calls[0][0].outline).toEqual(SERVER_OUTLINE)
  })

  test('refine 发送 is a button and fires on click and Enter', async () => {
    const user = userEvent.setup()
    const onRefine = vi.fn()
    render(
      <I18nProvider>
        <WriteLoop hasOutline hasChapter onRefine={onRefine} />
      </I18nProvider>,
    )
    const send = screen.getByTestId('refine-send-btn')
    expect(send.tagName).toBe('BUTTON')
    expect(send).toHaveTextContent('发送')
    await user.type(screen.getByTestId('refine-input'), '写短一点')
    await user.click(send)
    expect(onRefine).toHaveBeenCalledWith('写短一点')
    await user.clear(screen.getByTestId('refine-input'))
    await user.type(screen.getByTestId('refine-input'), '再补稳健性{Enter}')
    expect(onRefine).toHaveBeenLastCalledWith('再补稳健性')
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
    expect(screen.getByTestId('refine-send-btn').tagName).toBe('BUTTON')
    expect(screen.getByTestId('paper-agent')).toHaveTextContent('10%')
  })
})
