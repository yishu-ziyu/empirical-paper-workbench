import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CleanWizard from '../components/CleanWizard'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

const sampleProfile = {
  n_rows: 5,
  n_cols: 3,
  variables: {
    income: {
      dtype: 'float64',
      missing_rate: 0.2,
      n_unique: 4,
      is_numeric: true,
    },
    age: {
      dtype: 'int64',
      missing_rate: 0,
      n_unique: 5,
      is_numeric: true,
    },
    city: {
      dtype: 'object',
      missing_rate: 0,
      n_unique: 4,
      is_numeric: false,
    },
  },
}

const sampleOutliers = {
  before: {
    income: { min: 100, max: 1000, mean: 300 },
    age: { min: 25, max: 40, mean: 31 },
  },
  after: {
    income: { min: 100, max: 90, mean: 200 },
    age: { min: 25, max: 40, mean: 31 },
  },
}

describe('CleanWizard 清洗向导', () => {
  test('渲染 profiling 报告（变量列表 + 类型/缺失率/唯一值）', () => {
    renderWithI18n(
      <CleanWizard
        profile={sampleProfile}
        outliers={sampleOutliers}
        onSelectStrategy={() => {}}
      />,
    )

    // profiling 概要存在
    expect(screen.getByTestId('profile-report')).toBeInTheDocument()

    // 每个变量行渲染：变量名 + dtype + 缺失率
    const incomeRow = screen.getByTestId('var-income')
    expect(incomeRow).toHaveTextContent('income')
    expect(incomeRow).toHaveTextContent('float64')
    // missing_rate 0.2 -> 20%
    expect(incomeRow).toHaveTextContent('20%')

    const cityRow = screen.getByTestId('var-city')
    expect(cityRow).toHaveTextContent('city')
    expect(cityRow).toHaveTextContent('object')

    // 行数 / 列数概要
    expect(screen.getByTestId('profile-n-rows')).toHaveTextContent('5')
    expect(screen.getByTestId('profile-n-cols')).toHaveTextContent('3')
  })

  test('显示缺失值策略选择器（3 按钮）并触发 onSelect 回调', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()

    renderWithI18n(
      <CleanWizard
        profile={sampleProfile}
        outliers={sampleOutliers}
        onSelectStrategy={onSelect}
      />,
    )

    const dropBtn = screen.getByTestId('strategy-drop')
    const imputeBtn = screen.getByTestId('strategy-impute')
    const miceBtn = screen.getByTestId('strategy-mice')
    expect(dropBtn).toBeInTheDocument()
    expect(imputeBtn).toBeInTheDocument()
    expect(miceBtn).toBeInTheDocument()

    // 点击 drop -> 回调收到 'drop'
    await user.click(dropBtn)
    expect(onSelect).toHaveBeenLastCalledWith('drop')

    // 点击 impute -> 回调收到 'impute'
    await user.click(imputeBtn)
    expect(onSelect).toHaveBeenLastCalledWith('impute')

    // 点击 mice -> 回调收到 'mice'
    await user.click(miceBtn)
    expect(onSelect).toHaveBeenLastCalledWith('mice')
    expect(onSelect).toHaveBeenCalledTimes(3)
  })

  test('显示异常值缩尾前后分布对比', () => {
    renderWithI18n(
      <CleanWizard
        profile={sampleProfile}
        outliers={sampleOutliers}
        onSelectStrategy={() => {}}
      />,
    )

    // 异常值对比区块存在
    expect(screen.getByTestId('outlier-comparison')).toBeInTheDocument()

    // 缩尾前 income max = 1000（显示在 before 区）
    const before = screen.getByTestId('outlier-before-income')
    expect(before).toHaveTextContent('1000')

    // 缩尾后 income max = 90（显示在 after 区，已缩尾）
    const after = screen.getByTestId('outlier-after-income')
    expect(after).toHaveTextContent('90')

    // before / after 标签可见
    expect(screen.getByText(/前|before/i)).toBeInTheDocument()
    expect(screen.getByText(/后|after/i)).toBeInTheDocument()
  })
})
