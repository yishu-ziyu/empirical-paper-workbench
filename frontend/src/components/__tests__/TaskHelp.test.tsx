import { describe, expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { I18nProvider } from '../../lib/i18n'
import { TaskHelp } from '../TaskHelp'

describe('TaskHelp', () => {
  test('one sentence is visible; details are pull, closable, keyboard accessible, no trap', async () => {
    const user = userEvent.setup()
    const onSave = vi.fn()
    render(
      <I18nProvider>
        <TaskHelp summary="先确认方案。" details="确认之后才比较。" />
        <button type="button" onClick={onSave}>
          保存
        </button>
      </I18nProvider>,
    )
    expect(screen.getByTestId('task-help-summary')).toHaveTextContent('先确认方案。')
    expect(screen.queryByTestId('task-help-details')).not.toBeInTheDocument()
    const toggle = screen.getByTestId('task-help-toggle')
    toggle.focus()
    expect(toggle).toHaveFocus()
    await user.keyboard('{Enter}')
    expect(screen.getByTestId('task-help-details')).toHaveTextContent('确认之后才比较。')
    expect(toggle).toHaveAttribute('aria-expanded', 'true')
    await user.keyboard('{Enter}')
    expect(screen.queryByTestId('task-help-details')).not.toBeInTheDocument()
    await user.tab()
    expect(screen.getByRole('button', { name: '保存' })).toHaveFocus()
    expect(onSave).not.toHaveBeenCalled()
    fireEvent.click(toggle)
    fireEvent.click(toggle)
    expect(onSave).not.toHaveBeenCalled()
  })
})
