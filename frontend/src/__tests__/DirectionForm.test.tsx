import { describe, test, expect, vi } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DirectionForm from '../components/DirectionForm'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('DirectionForm 研究方向输入', () => {
  test('renders research question / dv / iv / controls / method / template inputs', () => {
    renderWithI18n(<DirectionForm onSubmit={() => {}} />)
    expect(screen.getByLabelText(/研究问题/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/因变量/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/自变量/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/控制变量/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/方法/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/模板/i)).toBeInTheDocument()
    expect(screen.getByTestId('direction-form')).toBeInTheDocument()
    expect(screen.getByTestId('method-selector')).toBeInTheDocument()
  })

  test('method selector shows 38 options', () => {
    renderWithI18n(<DirectionForm onSubmit={() => {}} />)
    const sel = screen.getByTestId('method-selector')
    const opts = within(sel).getAllByRole('option')
    // 38 个方法 + 1 个占位 "选择方法…"
    expect(opts).toHaveLength(39)
  })

  test('submit calls onSubmit with form data', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    renderWithI18n(<DirectionForm onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText(/研究问题/i), '教育对收入的影响')
    await user.type(screen.getByLabelText(/因变量/i), 'income')
    await user.type(screen.getByLabelText(/自变量/i), 'education')
    await user.type(screen.getByLabelText(/控制变量/i), 'age, gender')
    await user.selectOptions(screen.getByLabelText(/方法/i), 'OLS')
    await user.selectOptions(screen.getByLabelText(/模板/i), 'master')
    await user.click(screen.getByRole('button', { name: /提交/ }))

    expect(onSubmit).toHaveBeenCalledTimes(1)
    const data = onSubmit.mock.calls[0][0]
    expect(data.question).toBe('教育对收入的影响')
    expect(data.dv).toBe('income')
    expect(data.iv).toBe('education')
    expect(data.controls).toEqual(['age', 'gender'])
    expect(data.method).toBe('OLS')
    expect(data.template).toBe('master')
  })

  test('DiD reveals panel columns and submits them', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    renderWithI18n(<DirectionForm onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText(/研究问题/i), '政策')
    await user.type(screen.getByLabelText(/因变量/i), 'y')
    await user.type(screen.getByLabelText(/自变量/i), 'd')
    await user.selectOptions(screen.getByLabelText(/方法/i), 'DiD')
    expect(screen.getByLabelText(/时间列/i)).toBeInTheDocument()
    await user.type(screen.getByLabelText(/时间列/i), 'year')
    await user.type(screen.getByLabelText(/个体列/i), 'id')
    await user.type(screen.getByLabelText(/队列列/i), 'g')
    await user.click(screen.getByRole('button', { name: /提交/ }))

    expect(onSubmit.mock.calls[0][0]).toMatchObject({
      method: 'DiD',
      time_col: 'year',
      id_col: 'id',
      first_treat_col: 'g',
    })
  })
})
