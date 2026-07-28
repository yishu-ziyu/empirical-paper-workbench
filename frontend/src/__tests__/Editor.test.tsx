import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Editor from '../components/Editor'

describe('Editor 中栏流式 append', () => {
  test('按顺序 append streaming chunks 并拼接显示', () => {
    // 模拟 WS 推 3 个 chunk: "Hello " + "World" + "!"
    render(<Editor chapterId="1" chunks={['Hello ', 'World', '!']} />)

    // 期望拼接后显示 "Hello World!"
    // 占位 Editor 返回 null → 红
    expect(screen.getByText('Hello World!')).toBeInTheDocument()
  })

  test('收到 interrupt 时显示暂停提示', () => {
    render(<Editor chapterId="1" chunks={[]} interrupt="用户暂停，等待指令" />)

    // 期望显示 "暂停" 或 "paused" 文案
    // 占位 Editor 返回 null → 红
    expect(screen.getByText(/暂停|paused/i)).toBeInTheDocument()
  })
})
