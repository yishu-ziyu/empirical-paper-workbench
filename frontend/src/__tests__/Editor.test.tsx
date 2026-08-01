import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Editor from '../components/Editor'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('Editor 中栏流式 append', () => {
  test('按顺序 append streaming chunks 并拼接显示', () => {
    // 模拟 WS 推 3 个 chunk: "Hello " + "World" + "!"
    renderWithI18n(<Editor chapterId="1" chunks={['Hello ', 'World', '!']} />)

    // 期望拼接后显示 "Hello World!"
    // 占位 Editor 返回 null → 红
    expect(screen.getByText('Hello World!')).toBeInTheDocument()
  })

  test('收到 interrupt 时显示暂停提示', () => {
    renderWithI18n(<Editor chapterId="1" chunks={[]} interrupt="用户暂停，等待指令" />)

    // 期望显示 "暂停" 或 "paused" 文案（span 和 p 各匹配一次，至少一个）
    // 占位 Editor 返回 null → 红
    expect(screen.getAllByText(/暂停|paused/i).length).toBeGreaterThan(0)
  })
})
