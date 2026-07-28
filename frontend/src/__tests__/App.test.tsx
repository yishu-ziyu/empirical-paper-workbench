import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

describe('App 三栏布局', () => {
  test('渲染 Outline / Editor / Agent 三栏面板', () => {
    render(<App />)

    // 三栏标签（scaffold 已有 → 通过）
    expect(screen.getByText(/outline/i)).toBeInTheDocument()
    expect(screen.getByText(/editor/i)).toBeInTheDocument()
    expect(screen.getByText(/agent/i)).toBeInTheDocument()

    // 契约要求三栏有 data-testid 标识（scaffold 未实现 → 红）
    expect(screen.getByTestId('outline-panel')).toBeInTheDocument()
    expect(screen.getByTestId('editor-panel')).toBeInTheDocument()
    expect(screen.getByTestId('agent-panel')).toBeInTheDocument()
  })

  test('左栏从 state 渲染章节列表（T-02 仅 1 章 title）', () => {
    render(<App />)

    // scaffold 硬编码 6 章 Introduction/Literature Review/...
    // 契约要求 T-02 只有 1 章 title → 红
    expect(screen.getByText(/title/i)).toBeInTheDocument()
  })
})
