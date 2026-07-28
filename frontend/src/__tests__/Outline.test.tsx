import { describe, test, expect, vi } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Outline from '../components/Outline'
import type { OutlineChapter } from '../components/Outline'

const sixChapters: OutlineChapter[] = [
  { type: 'intro', title: '引言' },
  { type: 'lit_review', title: '文献综述' },
  { type: 'data_desc', title: '数据描述' },
  { type: 'methods', title: '方法' },
  { type: 'results', title: '结果' },
  { type: 'conclusion', title: '结论' },
]

describe('Outline 左栏大纲', () => {
  test('renders 6 chapters with type badges', () => {
    render(<Outline body_chapters={sixChapters} />)
    expect(screen.getAllByTestId('chapter-item')).toHaveLength(6)
    expect(screen.getAllByTestId('type-badge')).toHaveLength(6)
    expect(screen.getByText('引言')).toBeInTheDocument()
    expect(screen.getByText('文献综述')).toBeInTheDocument()
    expect(screen.getByText('结论')).toBeInTheDocument()
    // badge 文案包含 type
    expect(screen.getByText('intro')).toBeInTheDocument()
    expect(screen.getByText('conclusion')).toBeInTheDocument()
  })

  test('reorders chapters (drag via @dnd-kit + accessible move buttons)', async () => {
    // jsdom 无真实指针坐标，无法模拟 pointer drag；此处通过无障碍"下移"按钮
    // 触发与拖拽等价的 reorder 逻辑（component 同时也接了 @dnd-kit PointerSensor
    // / KeyboardSensor 供真实浏览器拖拽使用）。
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    render(<Outline body_chapters={sixChapters} onConfirm={onConfirm} />)

    const items = screen.getAllByTestId('chapter-item')
    expect(items[0]).toHaveTextContent('引言')

    // 点击第一项的"下移"按钮
    await user.click(within(items[0]).getByRole('button', { name: /下移 引言/ }))

    // 确认大纲，验证顺序已变
    await user.click(screen.getByRole('button', { name: /确认大纲/ }))
    expect(onConfirm).toHaveBeenCalledTimes(1)
    const confirmed = onConfirm.mock.calls[0][0] as OutlineChapter[]
    expect(confirmed[0].title).not.toBe('引言')
    expect(confirmed[1].title).toBe('引言')
  })

  test('delete chapter removes it', async () => {
    const user = userEvent.setup()
    render(<Outline body_chapters={sixChapters} />)
    expect(screen.getAllByTestId('chapter-item')).toHaveLength(6)
    const items = screen.getAllByTestId('chapter-item')
    await user.click(within(items[0]).getByRole('button', { name: /删除 引言/ }))
    expect(screen.getAllByTestId('chapter-item')).toHaveLength(5)
    expect(screen.queryByText('引言')).not.toBeInTheDocument()
  })

  test('add chapter adds one', async () => {
    const user = userEvent.setup()
    render(<Outline body_chapters={sixChapters} />)
    expect(screen.getAllByTestId('chapter-item')).toHaveLength(6)
    await user.click(screen.getByRole('button', { name: /添加章节/ }))
    expect(screen.getAllByTestId('chapter-item')).toHaveLength(7)
  })

  test('confirm button calls onConfirm with current outline', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    render(<Outline body_chapters={sixChapters} onConfirm={onConfirm} />)
    await user.click(screen.getByRole('button', { name: /确认大纲/ }))
    expect(onConfirm).toHaveBeenCalledTimes(1)
    const confirmed = onConfirm.mock.calls[0][0] as OutlineChapter[]
    expect(confirmed).toHaveLength(6)
    expect(confirmed.map((c) => c.type)).toEqual([
      'intro',
      'lit_review',
      'data_desc',
      'methods',
      'results',
      'conclusion',
    ])
  })
})
