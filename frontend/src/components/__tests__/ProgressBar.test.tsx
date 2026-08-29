// T-08c RED tests for ProgressBar component.
//
// 契约（任务规格 §T-08c）：
// 1. 显示 6 个章节标签（intro/lit_review/data_desc/methods/results/conclusion）
// 2. 已通过 = 绿色，当前 = 高亮，未开始 = 灰色
// 3. 点击章节标签可跳转（onChapterClick 回调）
// 4. 显示进度（completed/total）
import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ProgressBar, { type ProgressBarProps } from '../ProgressBar'

const bodyChapters: ProgressBarProps['body_chapters'] = [
  { type: 'intro', status: 'done', title: '引言' },
  { type: 'lit_review', status: 'done', title: '文献综述' },
  { type: 'data_desc', status: 'generated', title: '数据描述' },
  { type: 'methods', status: 'pending', title: '方法' },
  { type: 'results', status: 'pending', title: '结果' },
  { type: 'conclusion', status: 'pending', title: '结论' },
]

const baseProps: ProgressBarProps = {
  total: 6,
  completed: 2,
  current: 2,
  body_chapters: bodyChapters,
}

describe('ProgressBar 章节进度条', () => {
  test('渲染 6 个章节标签', () => {
    render(<ProgressBar {...baseProps} />)
    expect(screen.getByTestId('progress-bar')).toBeInTheDocument()
    const labels = screen.getAllByTestId('chapter-label')
    expect(labels).toHaveLength(6)
  })

  test('显示已完成数量 / 总数', () => {
    render(<ProgressBar {...baseProps} />)
    expect(screen.getByTestId('progress-bar').textContent).toContain('2')
    expect(screen.getByTestId('progress-bar').textContent).toContain('6')
  })

  test('已通过章节标记为绿色（done 状态）', () => {
    render(<ProgressBar {...baseProps} />)
    const labels = screen.getAllByTestId('chapter-label')
    // intro (index 0) 和 lit_review (index 1) 已通过
    expect(labels[0].className.toLowerCase()).toContain('green')
    expect(labels[1].className.toLowerCase()).toContain('green')
  })

  test('当前章节高亮（current 索引）', () => {
    render(<ProgressBar {...baseProps} />)
    const labels = screen.getAllByTestId('chapter-label')
    // current=2 是 data_desc
    expect(labels[2].className.toLowerCase()).toContain('accent')
  })

  test('未开始章节标记为灰色（pending 状态）', () => {
    render(<ProgressBar {...baseProps} />)
    const labels = screen.getAllByTestId('chapter-label')
    // methods (3), results (4), conclusion (5) 未开始
    expect(labels[3].className.toLowerCase()).toContain('gray')
    expect(labels[4].className.toLowerCase()).toContain('gray')
    expect(labels[5].className.toLowerCase()).toContain('gray')
  })

  test('点击章节标签触发 onChapterClick 回调', async () => {
    const user = userEvent.setup()
    const onChapterClick = vi.fn()
    render(<ProgressBar {...baseProps} onChapterClick={onChapterClick} />)
    const labels = screen.getAllByTestId('chapter-label')
    await user.click(labels[3])
    expect(onChapterClick).toHaveBeenCalledWith(3)
  })

  test('章节标签显示标题文本', () => {
    render(<ProgressBar {...baseProps} />)
    expect(screen.getByText('引言')).toBeInTheDocument()
    expect(screen.getByText('文献综述')).toBeInTheDocument()
    expect(screen.getByText('结论')).toBeInTheDocument()
  })
})
