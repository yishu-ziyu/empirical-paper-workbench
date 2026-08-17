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

  test('method selector shows the five engine methods', () => {
    renderWithI18n(<DirectionForm onSubmit={() => {}} />)
    const sel = screen.getByTestId('method-selector')
    const opts = within(sel).getAllByRole('option')
    expect(opts).toHaveLength(6)
    expect(opts.map((el) => el.textContent)).toEqual([
      '选择方法…',
      'OLS',
      'DiD',
      'IV',
      'RD',
      'SCM',
    ])
    expect(screen.getByText(/只跑这五类/)).toBeInTheDocument()
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

  test('empty form cannot submit', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    renderWithI18n(<DirectionForm onSubmit={onSubmit} />)
    expect(screen.getByRole('button', { name: /提交/ })).toBeDisabled()
    await user.click(screen.getByRole('button', { name: /提交/ }))
    expect(onSubmit).not.toHaveBeenCalled()
  })

  test('sample initials and columns fill the form', () => {
    renderWithI18n(
      <DirectionForm
        onSubmit={() => {}}
        initial={{
          question: '这份课设样例里，年龄和收入是否相关？',
          dv: 'income',
          iv: 'age',
          controls: 'treat',
          method: 'OLS',
          template: 'undergrad',
        }}
        columns={['id', 'year', 'income', 'treat', 'age']}
      />,
    )
    expect(screen.getByLabelText(/研究问题/i)).toHaveValue('这份课设样例里，年龄和收入是否相关？')
    expect(screen.getByLabelText(/因变量/i)).toHaveValue('income')
    expect(screen.getByLabelText(/自变量/i)).toHaveValue('age')
    expect(screen.getByLabelText(/控制变量/i)).toHaveValue('treat')
    expect(screen.getByTestId('method-selector')).toHaveValue('OLS')
    expect(screen.getByLabelText(/模板/i)).toHaveValue('undergrad')
    expect(screen.getByTestId('data-columns')).toHaveTextContent('income')
  })
})
