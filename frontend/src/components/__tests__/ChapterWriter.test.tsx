// T-07 RED tests for ChapterWriter component.
//
// 契约（任务规格 §T-07）：
// 1. 用 CodeMirror 6 渲染 markdown 内容（流式 append 不重渲）
// 2. 章节类型 badge（6 色：intro=蓝 / lit_review=紫 / data_desc=绿 /
//    methods=橙 / results=红 / conclusion=灰）
// 3. status === 'generated' 后显示三个按钮：重新生成 / 编辑 / 通过
// 4. onRegenerate / onApprove 回调正确触发
//
// jsdom 限制：CodeMirror 6 在 jsdom 下不完全渲染（缺 ResizeObserver /
// layout），测试只断言 markdown 文本出现在 DOM 中（用 container.textContent）
// 以及 badge / 按钮交互。streaming chunks 拼接通过 props.chunks 数组传入。
import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChapterWriter, { type ChapterWriterProps } from '../ChapterWriter'
import { I18nProvider } from '../../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

const introChapter = {
  type: 'intro',
  title: '引言',
  status: 'generated',
  content: '# 引言\n\n## 研究背景\n教育回报是劳动经济学经典议题。',
}

const baseProps: ChapterWriterProps = {
  chapter: introChapter,
  chunks: [],
  onApprove: vi.fn(),
  onRegenerate: vi.fn(),
}

describe('ChapterWriter 章节写作器', () => {
  test('渲染章节内容（markdown 文本出现在 DOM）', () => {
    const { container } = renderWithI18n(
      <ChapterWriter
        {...baseProps}
        chapter={introChapter}
        chunks={['# 引言\n\n## 研究背景\n教育回报是劳动经济学经典议题。']}
      />,
    )
    // CodeMirror 在 jsdom 下可能不完全渲染，但内容文本应在 DOM 中
    expect(container.textContent).toContain('研究背景')
    expect(container.textContent).toContain('教育回报')
  })

  test('渲染章节类型 badge', () => {
    renderWithI18n(<ChapterWriter {...baseProps} chapter={introChapter} />)
    const badge = screen.getByTestId('chapter-type-badge')
    expect(badge).toBeInTheDocument()
    expect(badge.textContent).toContain('intro')
  })

  test('6 种 chapter_type 各有对应颜色 class', () => {
    const cases: Array<{ type: string; colorHint: string }> = [
      { type: 'intro', colorHint: 'blue' },
      { type: 'lit_review', colorHint: 'purple' },
      { type: 'data_desc', colorHint: 'green' },
      { type: 'methods', colorHint: 'orange' },
      { type: 'results', colorHint: 'red' },
      { type: 'conclusion', colorHint: 'gray' },
    ]
    for (const { type, colorHint } of cases) {
      const { unmount } = renderWithI18n(
        <ChapterWriter
          {...baseProps}
          chapter={{ type, title: type, status: 'generated', content: 'x' }}
        />,
      )
      const badge = screen.getByTestId('chapter-type-badge')
      // class 必须含对应颜色关键词（bg-blue-100 / text-purple-800 等）
      expect(badge.className.toLowerCase()).toContain(colorHint)
      unmount()
    }
  })

  test('status=generated 时显示 重新生成 / 编辑 / 通过 三按钮', () => {
    renderWithI18n(<ChapterWriter {...baseProps} chapter={introChapter} />)
    expect(screen.getByRole('button', { name: /重新生成/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /编辑/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /通过/ })).toBeInTheDocument()
  })

  test('status=streaming 时不显示审批按钮（仅显示加载提示）', () => {
    renderWithI18n(
      <ChapterWriter
        {...baseProps}
        chapter={{ ...introChapter, status: 'streaming' }}
      />,
    )
    expect(screen.queryByRole('button', { name: /重新生成/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /通过/ })).not.toBeInTheDocument()
    // 应有 streaming / 加载提示
    expect(screen.getByTestId('chapter-streaming-hint')).toBeInTheDocument()
  })

  test('点击"通过"按钮触发 onApprove', async () => {
    const user = userEvent.setup()
    const onApprove = vi.fn()
    renderWithI18n(<ChapterWriter {...baseProps} onApprove={onApprove} />)
    await user.click(screen.getByRole('button', { name: /通过/ }))
    expect(onApprove).toHaveBeenCalledTimes(1)
  })

  test('点击"重新生成"按钮触发 onRegenerate', async () => {
    const user = userEvent.setup()
    const onRegenerate = vi.fn()
    renderWithI18n(<ChapterWriter {...baseProps} onRegenerate={onRegenerate} />)
    await user.click(screen.getByRole('button', { name: /重新生成/ }))
    expect(onRegenerate).toHaveBeenCalledTimes(1)
  })

  test('流式 chunks 数组拼接显示（chunks prop 变化时拼接）', () => {
    const { rerender } = renderWithI18n(
      <ChapterWriter
        {...baseProps}
        chapter={{ ...introChapter, status: 'streaming' }}
        chunks={['# 引言\n\n']}
      />,
    )
    // 第一个 chunk
    expect(screen.getByTestId('chapter-writer').textContent).toContain('引言')

    // 模拟 WS 推第二个 chunk
    rerender(
      <ChapterWriter
        {...baseProps}
        chapter={{ ...introChapter, status: 'streaming' }}
        chunks={['# 引言\n\n', '## 研究背景\n教育回报。']}
      />,
    )
    expect(screen.getByTestId('chapter-writer').textContent).toContain('研究背景')
    expect(screen.getByTestId('chapter-writer').textContent).toContain('教育回报')
  })
})

// T-08c 扩展测试：4 按钮 + 回滚下拉 + 编辑模式
//
// 契约（任务规格 §T-08c）：
// 1. status=generated 显示 4 按钮：重新生成 / 回滚 / 编辑 / 通过
// 2. 回滚下拉：点"回滚"显示版本列表，选择版本触发 onRollback(index)
// 3. 编辑模式：点"编辑"切换为可编辑 + 显示"保存"按钮，点"保存"触发 onSaveEdit
describe('ChapterWriter T-08c 扩展：4 按钮 + 回滚 + 编辑模式', () => {
  const versions = [
    '# 引言\n教育回报是劳动经济学经典议题，本文研究教育对工资的影响。',
    '# 引言\n教育回报一直是核心问题，本研究利用 CFPS 数据分析。',
    '# 引言\n本文从人力资本理论出发，探讨教育年限对收入的边际效应。',
  ]

  test('status=generated 时显示 4 按钮（重新生成 / 回滚 / 编辑 / 通过）', () => {
    renderWithI18n(<ChapterWriter {...baseProps} chapter={introChapter} />)
    expect(screen.getByRole('button', { name: /重新生成/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /回滚/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /编辑/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /通过/ })).toBeInTheDocument()
  })

  test('默认不显示版本历史下拉', () => {
    renderWithI18n(<ChapterWriter {...baseProps} chapter={introChapter} versions={versions} />)
    expect(screen.queryByTestId('version-history')).not.toBeInTheDocument()
  })

  test('点击"回滚"按钮显示版本历史下拉', async () => {
    const user = userEvent.setup()
    renderWithI18n(<ChapterWriter {...baseProps} chapter={introChapter} versions={versions} />)
    await user.click(screen.getByRole('button', { name: /回滚/ }))
    expect(screen.getByTestId('version-history')).toBeInTheDocument()
  })

  test('版本历史下拉显示所有版本', async () => {
    const user = userEvent.setup()
    renderWithI18n(<ChapterWriter {...baseProps} chapter={introChapter} versions={versions} />)
    await user.click(screen.getByRole('button', { name: /回滚/ }))
    const items = screen.getAllByTestId('version-item')
    expect(items).toHaveLength(3)
  })

  test('选择版本触发 onRollback 回调', async () => {
    const user = userEvent.setup()
    const onRollback = vi.fn()
    renderWithI18n(
      <ChapterWriter
        {...baseProps}
        chapter={introChapter}
        versions={versions}
        onRollback={onRollback}
      />,
    )
    await user.click(screen.getByRole('button', { name: /回滚/ }))
    const items = screen.getAllByTestId('version-item')
    await user.click(items[1])
    expect(onRollback).toHaveBeenCalledWith(1)
  })

  test('点击"编辑"进入编辑模式（显示"保存"按钮）', async () => {
    const user = userEvent.setup()
    renderWithI18n(<ChapterWriter {...baseProps} chapter={introChapter} />)
    await user.click(screen.getByRole('button', { name: /编辑/ }))
    expect(screen.getByRole('button', { name: /保存/ })).toBeInTheDocument()
  })

  test('编辑模式下点"保存"退出编辑模式（恢复"编辑"按钮）', async () => {
    const user = userEvent.setup()
    renderWithI18n(<ChapterWriter {...baseProps} chapter={introChapter} />)
    // 进入编辑模式
    await user.click(screen.getByRole('button', { name: /编辑/ }))
    expect(screen.getByRole('button', { name: /保存/ })).toBeInTheDocument()
    // 保存
    await user.click(screen.getByRole('button', { name: /保存/ }))
    expect(screen.getByRole('button', { name: /编辑/ })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /保存/ })).not.toBeInTheDocument()
  })

  test('点"保存"触发 onSaveEdit 回调', async () => {
    const user = userEvent.setup()
    const onSaveEdit = vi.fn()
    renderWithI18n(<ChapterWriter {...baseProps} chapter={introChapter} onSaveEdit={onSaveEdit} />)
    await user.click(screen.getByRole('button', { name: /编辑/ }))
    await user.click(screen.getByRole('button', { name: /保存/ }))
    expect(onSaveEdit).toHaveBeenCalledTimes(1)
  })
})