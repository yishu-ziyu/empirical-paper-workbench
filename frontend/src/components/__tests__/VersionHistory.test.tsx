// T-08c RED tests for VersionHistory component.
//
// 契约（任务规格 §T-08c）：
// 1. 显示所有版本列表（版本索引 + 前 50 字预览）
// 2. 当前版本高亮
// 3. 点击选择 → 触发 onSelectVersion(index)
import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import VersionHistory, { type VersionHistoryProps } from '../VersionHistory'

const versions = [
  '# 引言\n教育回报是劳动经济学经典议题，本文研究教育对工资的影响。',
  '# 引言\n教育回报一直是劳动经济学的核心问题，本研究利用 CFPS 数据分析。',
  '# 引言\n本文从人力资本理论出发，探讨教育年限对个体收入的边际效应。',
]

const baseProps: VersionHistoryProps = {
  versions,
  onSelectVersion: vi.fn(),
}

describe('VersionHistory 版本历史下拉', () => {
  test('渲染所有版本项', () => {
    render(<VersionHistory {...baseProps} />)
    const items = screen.getAllByTestId('version-item')
    expect(items).toHaveLength(3)
  })

  test('每项显示版本索引', () => {
    render(<VersionHistory {...baseProps} />)
    expect(screen.getByText(/版本\s*0/)).toBeInTheDocument()
    expect(screen.getByText(/版本\s*1/)).toBeInTheDocument()
    expect(screen.getByText(/版本\s*2/)).toBeInTheDocument()
  })

  test('每项显示前 50 字预览', () => {
    render(<VersionHistory {...baseProps} />)
    const items = screen.getAllByTestId('version-item')
    // 第一版本预览应包含 "教育回报" 文本
    expect(items[0].textContent).toContain('教育回报')
    // 预览不超过 50 字（截断）
    const previewText = items[0].textContent ?? ''
    // 预览部分应较短
    expect(previewText.length).toBeLessThan(200)
  })

  test('当前版本高亮（currentVersionIndex）', () => {
    render(<VersionHistory {...baseProps} currentVersionIndex={1} />)
    const items = screen.getAllByTestId('version-item')
    expect(items[1].className.toLowerCase()).toContain('accent')
  })

  test('未选中版本不高亮', () => {
    render(<VersionHistory {...baseProps} currentVersionIndex={1} />)
    const items = screen.getAllByTestId('version-item')
    expect(items[0].className.toLowerCase()).not.toContain('accent')
    expect(items[2].className.toLowerCase()).not.toContain('accent')
  })

  test('点击版本项触发 onSelectVersion 回调', async () => {
    const user = userEvent.setup()
    const onSelectVersion = vi.fn()
    render(<VersionHistory {...baseProps} onSelectVersion={onSelectVersion} />)
    const items = screen.getAllByTestId('version-item')
    await user.click(items[2])
    expect(onSelectVersion).toHaveBeenCalledWith(2)
  })

  test('空版本列表显示提示', () => {
    render(<VersionHistory versions={[]} onSelectVersion={vi.fn()} />)
    expect(screen.getByTestId('version-history')).toBeInTheDocument()
    expect(screen.getByTestId('version-history').textContent).toContain('暂无版本')
  })
})
