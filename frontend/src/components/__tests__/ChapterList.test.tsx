// T-08c RED tests for ChapterList component.
//
// 契约（任务规格 §T-08c）：
// 1. 左栏大纲列表：6 章标题 + 类型 badge + 状态图标
// 2. 当前章高亮
// 3. 点击切换章节（onSelectChapter 回调）
import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChapterList, { type ChapterListProps } from '../ChapterList'

const bodyChapters: ChapterListProps['body_chapters'] = [
  { type: 'intro', title: '引言', status: 'done', content: '引言内容' },
  { type: 'lit_review', title: '文献综述', status: 'done', content: '文献内容' },
  { type: 'data_desc', title: '数据描述', status: 'generated', content: '数据内容' },
  { type: 'methods', title: '方法', status: 'pending' },
  { type: 'results', title: '结果', status: 'pending' },
  { type: 'conclusion', title: '结论', status: 'pending' },
]

const baseProps: ChapterListProps = {
  body_chapters: bodyChapters,
  currentIndex: 2,
  onSelectChapter: vi.fn(),
}

describe('ChapterList 章节大纲列表', () => {
  test('渲染 6 个章节项', () => {
    render(<ChapterList {...baseProps} />)
    const items = screen.getAllByTestId('chapter-list-item')
    expect(items).toHaveLength(6)
  })

  test('每项显示章节标题', () => {
    render(<ChapterList {...baseProps} />)
    expect(screen.getByText('引言')).toBeInTheDocument()
    expect(screen.getByText('文献综述')).toBeInTheDocument()
    expect(screen.getByText('数据描述')).toBeInTheDocument()
    expect(screen.getByText('方法')).toBeInTheDocument()
    expect(screen.getByText('结果')).toBeInTheDocument()
    expect(screen.getByText('结论')).toBeInTheDocument()
  })

  test('每项显示类型 badge', () => {
    render(<ChapterList {...baseProps} />)
    const badges = screen.getAllByTestId('chapter-type-badge')
    expect(badges).toHaveLength(6)
    expect(badges[0].textContent).toContain('intro')
    expect(badges[3].textContent).toContain('methods')
  })

  test('每项显示状态图标', () => {
    render(<ChapterList {...baseProps} />)
    const icons = screen.getAllByTestId('chapter-status-icon')
    expect(icons).toHaveLength(6)
  })

  test('done 状态显示完成图标', () => {
    render(<ChapterList {...baseProps} />)
    const icons = screen.getAllByTestId('chapter-status-icon')
    // intro (0) 和 lit_review (1) 是 done
    expect(icons[0].textContent).toContain('✓')
    expect(icons[1].textContent).toContain('✓')
  })

  test('当前章节高亮（currentIndex）', () => {
    render(<ChapterList {...baseProps} />)
    const items = screen.getAllByTestId('chapter-list-item')
    expect(items[2].className.toLowerCase()).toContain('accent')
  })

  test('非当前章节不高亮', () => {
    render(<ChapterList {...baseProps} />)
    const items = screen.getAllByTestId('chapter-list-item')
    expect(items[0].className.toLowerCase()).not.toContain('accent')
    expect(items[3].className.toLowerCase()).not.toContain('accent')
  })

  test('点击章节项触发 onSelectChapter 回调', async () => {
    const user = userEvent.setup()
    const onSelectChapter = vi.fn()
    render(<ChapterList {...baseProps} onSelectChapter={onSelectChapter} />)
    const items = screen.getAllByTestId('chapter-list-item')
    await user.click(items[4])
    expect(onSelectChapter).toHaveBeenCalledWith(4)
  })
})
