import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CharlsWizard, { type CharlsConfig } from '../CharlsWizard'

const sampleConfig: CharlsConfig = {
  name: 'CHARLS',
  identifier: {
    required_columns: ['community_id'],
    pattern_columns: ['qe\\d+_hi'],
    min_pattern_matches: 5,
  },
  variable_mapping: {
    qe303_hi: 'oopc_exp',
    qe304_hi: 'inpatient_exp',
    qe305_hi: 'outpatient_exp',
    rage: 'age',
    ragender: 'gender',
    rmarital: 'marital_status',
    redu: 'education_level',
  },
  waves: [2011, 2013, 2015, 2018, 2020, 2024],
  default_waves: [2018, 2020],
  filter_presets: [
    { name: '60岁以上', conditions: [{ col: 'rage', op: '>=', val: 60 }] },
    { name: '城乡居民医保', conditions: [{ col: 'urban_insurance', op: '==', val: 1 }] },
    { name: '无缺失值样本', conditions: [{ type: 'no_missing' }] },
  ],
}

describe('CharlsWizard CHARLS 向导', () => {
  test('isOpen=false 时不渲染', () => {
    render(
      <CharlsWizard
        isOpen={false}
        config={sampleConfig}
        onConfirm={() => {}}
        onClose={() => {}}
      />,
    )
    expect(screen.queryByTestId('charls-wizard')).not.toBeInTheDocument()
  })

  test('isOpen=true 时渲染向导 + 变量映射表', () => {
    render(
      <CharlsWizard
        isOpen={true}
        config={sampleConfig}
        onConfirm={() => {}}
        onClose={() => {}}
      />,
    )
    expect(screen.getByTestId('charls-wizard')).toBeInTheDocument()
    expect(screen.getByTestId('variable-mapping-table')).toBeInTheDocument()
    // 每个映射行：原始 code → 可读 name
    expect(screen.getByTestId('mapping-row-qe303_hi')).toBeInTheDocument()
    expect(screen.getByTestId('mapping-row-rage')).toBeInTheDocument()
    // 可读名以 input 显示，默认值为 oopc_exp
    expect(screen.getByTestId('mapping-input-qe303_hi')).toHaveValue('oopc_exp')
  })

  test('渲染 6 个年份 checkbox，默认勾选 2018 和 2020', () => {
    render(
      <CharlsWizard
        isOpen={true}
        config={sampleConfig}
        onConfirm={() => {}}
        onClose={() => {}}
      />,
    )
    expect(screen.getByTestId('waves-section')).toBeInTheDocument()
    // 6 个 checkbox
    expect(screen.getByTestId('wave-checkbox-2011')).toBeInTheDocument()
    expect(screen.getByTestId('wave-checkbox-2013')).toBeInTheDocument()
    expect(screen.getByTestId('wave-checkbox-2015')).toBeInTheDocument()
    expect(screen.getByTestId('wave-checkbox-2018')).toBeInTheDocument()
    expect(screen.getByTestId('wave-checkbox-2020')).toBeInTheDocument()
    expect(screen.getByTestId('wave-checkbox-2024')).toBeInTheDocument()
    // 默认勾选 2018 + 2020
    expect(screen.getByTestId('wave-checkbox-2018')).toBeChecked()
    expect(screen.getByTestId('wave-checkbox-2020')).toBeChecked()
    expect(screen.getByTestId('wave-checkbox-2011')).not.toBeChecked()
  })

  test('渲染 3 个筛选预设按钮', () => {
    render(
      <CharlsWizard
        isOpen={true}
        config={sampleConfig}
        onConfirm={() => {}}
        onClose={() => {}}
      />,
    )
    expect(screen.getByTestId('filter-presets-section')).toBeInTheDocument()
    expect(screen.getByTestId('filter-preset-60岁以上')).toBeInTheDocument()
    expect(screen.getByTestId('filter-preset-城乡居民医保')).toBeInTheDocument()
    expect(screen.getByTestId('filter-preset-无缺失值样本')).toBeInTheDocument()
  })

  test('点击筛选预设按钮应用筛选', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    render(
      <CharlsWizard
        isOpen={true}
        config={sampleConfig}
        onConfirm={onConfirm}
        onClose={() => {}}
      />,
    )
    // 点击 "60岁以上" 预设
    await user.click(screen.getByTestId('filter-preset-60岁以上'))
    // 该预设应被标记为已选中
    expect(screen.getByTestId('filter-preset-60岁以上')).toHaveClass('bg-blue-600')
  })

  test('点击确认按钮触发 onConfirm，参数包含映射 + 年份 + 筛选', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    render(
      <CharlsWizard
        isOpen={true}
        config={sampleConfig}
        onConfirm={onConfirm}
        onClose={() => {}}
      />,
    )
    // 默认勾选 2018+2020，点确认
    await user.click(screen.getByTestId('charls-confirm-btn'))
    expect(onConfirm).toHaveBeenCalledTimes(1)
    const payload = onConfirm.mock.calls[0][0]
    expect(payload).toHaveProperty('variable_mapping')
    expect(payload).toHaveProperty('waves')
    expect(payload).toHaveProperty('filter_presets')
    expect(payload.waves).toEqual([2018, 2020])
    // 默认未选筛选预设
    expect(payload.filter_presets).toEqual([])
  })

  test('编辑变量映射名后确认提交新名称', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    render(
      <CharlsWizard
        isOpen={true}
        config={sampleConfig}
        onConfirm={onConfirm}
        onClose={() => {}}
      />,
    )
    // 把 qe303_hi 的可读名从 oopc_exp 改成 my_oopc
    const input = screen.getByTestId('mapping-input-qe303_hi') as HTMLInputElement
    await user.clear(input)
    await user.type(input, 'my_oopc')
    await user.click(screen.getByTestId('charls-confirm-btn'))
    const payload = onConfirm.mock.calls[0][0]
    expect(payload.variable_mapping.qe303_hi).toBe('my_oopc')
  })

  test('点击取消按钮触发 onClose', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(
      <CharlsWizard
        isOpen={true}
        config={sampleConfig}
        onConfirm={() => {}}
        onClose={onClose}
      />,
    )
    await user.click(screen.getByTestId('charls-cancel-btn'))
    expect(onClose).toHaveBeenCalledTimes(1)
  })
})
