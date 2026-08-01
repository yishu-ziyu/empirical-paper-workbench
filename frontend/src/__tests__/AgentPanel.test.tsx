import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import AgentPanel from '../components/AgentPanel'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('AgentPanel 右栏状态', () => {
  test('显示当前 node 名称与 status', () => {
    // 模拟 WS 推 status: {node: "generate_title", status: "running"}
    renderWithI18n(
      <AgentPanel
        currentNode="generate_title"
        currentStatus="running"
        connectionState="connected"
      />,
    )

    // 期望显示 node + status
    // 占位 AgentPanel 返回 null → 红
    expect(screen.getByText(/generate_title/i)).toBeInTheDocument()
    expect(screen.getByText(/running/i)).toBeInTheDocument()
  })

  test('显示 WS 连接状态 (connecting / connected / disconnected)', () => {
    renderWithI18n(
      <AgentPanel
        currentNode=""
        currentStatus="idle"
        connectionState="connecting"
      />,
    )

    // 期望有连接状态指示
    // 占位 AgentPanel 返回 null → 红
    expect(screen.getByText(/connecting/i)).toBeInTheDocument()
  })
})
