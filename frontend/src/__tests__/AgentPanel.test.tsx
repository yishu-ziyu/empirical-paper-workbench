import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import AgentPanel from '../components/AgentPanel'

describe('AgentPanel 右栏状态', () => {
  test('显示当前 node 名称与 status', () => {
    // 模拟 WS 推 status: {node: "generate_title", status: "running"}
    render(
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
    render(
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
