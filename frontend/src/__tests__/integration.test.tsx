import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import App from '../App'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

// Mock WebSocket — 捕获 WSClient 创建的实例并允许测试触发 onmessage/onopen
class MockWebSocket {
  static instances: MockWebSocket[] = []
  url: string
  onmessage: ((ev: { data: string }) => void) | null = null
  onopen: ((ev: unknown) => void) | null = null
  onclose: ((ev: unknown) => void) | null = null
  onerror: ((ev: unknown) => void) | null = null
  readyState = 0

  constructor(url: string) {
    this.url = url
    MockWebSocket.instances.push(this)
  }

  send(_data: string): void {
    // no-op
  }

  close(): void {
    this.readyState = 3
  }
}

const API_BASE = 'http://localhost:8000'

beforeEach(() => {
  MockWebSocket.instances = []
  vi.stubGlobal('WebSocket', MockWebSocket)
  vi.stubGlobal('fetch', vi.fn())
  localStorage.clear()
  localStorage.setItem("econpaper_access_token", "test-token-for-auth")
})

afterEach(() => {
  vi.unstubAllGlobals()
  localStorage.clear()
})

describe('前端集成测试', () => {
  // ── 场景 A：upload → sessionId 传递 ──────────────────────
  test('场景 A：上传文件创建 session 并传递 sessionId 到子组件', async () => {
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (String(url).includes('/upload')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ session_id: 'test-123' }),
        })
      }
      return Promise.reject(new Error('unexpected URL'))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    expect(screen.getByTestId('desk-page')).toBeInTheDocument()

    // 触发文件上传
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement
    fireEvent.change(fileInput, {
      target: { files: [new File(['a,b\n1,2'], 'test.csv', { type: 'text/csv' })] },
    })

    // sessionId 出现在 header 中
    await waitFor(() => {
      expect(screen.getByTestId('session-id-indicator')).toBeInTheDocument()
    })
    expect(screen.getByText(/test-123/i)).toBeInTheDocument()

    // sessionId 保存到 localStorage
    expect(localStorage.getItem('econpaper_session_id')).toBe('test-123')

    // EdaSidebar 已渲染（sessionId 传递到子组件）
    expect(screen.getByTestId('eda-sidebar')).toBeInTheDocument()
  })

  // ── 场景 B：WebSocket 连接和消息分发 ──────────────────────
  test('场景 B：WebSocket 连接和消息分发更新 Editor 和 AgentPanel', async () => {
    // 预设 localStorage 有 sessionId，后端验证通过
    localStorage.setItem('econpaper_session_id', 'test-456')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (String(url).includes('/sessions/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ exists: true }),
        })
      }
      return Promise.reject(new Error('unexpected URL'))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    // 等待 sessionId 恢复并显示
    await waitFor(() => {
      expect(screen.getByTestId('session-id-indicator')).toBeInTheDocument()
    })
    expect(screen.getByText(/test-456/i)).toBeInTheDocument()

    // WSClient 被创建 → MockWebSocket 实例存在
    const ws = MockWebSocket.instances[0]
    expect(ws).toBeDefined()

    // 模拟 WebSocket 连接成功
    act(() => {
      ws.onopen!({})
    })

    // 连接状态更新为 connected
    await waitFor(() => {
      expect(screen.getByText(/connected/i)).toBeInTheDocument()
    })

    // 发送 streaming_chunk 消息
    act(() => {
      ws.onmessage!({
        data: JSON.stringify({ type: 'streaming_chunk', chapter_id: '1', chunk: 'Hello ' }),
      })
    })
    act(() => {
      ws.onmessage!({
        data: JSON.stringify({ type: 'streaming_chunk', chapter_id: '1', chunk: 'World!' }),
      })
    })

    // Editor 拼接显示内容
    await waitFor(() => {
      expect(screen.getByText('Hello World!')).toBeInTheDocument()
    })

    // 发送 status 消息
    act(() => {
      ws.onmessage!({
        data: JSON.stringify({ type: 'status', node: 'generate_title', status: 'running' }),
      })
    })

    // AgentPanel 显示当前 node
    await waitFor(() => {
      expect(screen.getByText('generate_title')).toBeInTheDocument()
    })

    // 发送 interrupt 消息
    act(() => {
      ws.onmessage!({
        data: JSON.stringify({
          type: 'interrupt',
          chapter_id: '1',
          content: '等待用户确认',
        }),
      })
    })

    // 显示暂停提示（span 和 p 各匹配一次，至少一个）
    await waitFor(() => {
      expect(screen.getAllByText(/暂停|paused/i).length).toBeGreaterThan(0)
    })
  })

  // ── 场景 C：页面刷新后 localStorage 恢复 ──────────────────────
  test('场景 C：页面刷新后从 localStorage 恢复 sessionId 并自动重连 WebSocket', async () => {
    localStorage.setItem('econpaper_session_id', 'test-789')

    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (String(url).includes('/sessions/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ exists: true }),
        })
      }
      return Promise.reject(new Error('unexpected URL'))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    // 从 localStorage 恢复 sessionId
    await waitFor(() => {
      expect(screen.getByTestId('session-id-indicator')).toBeInTheDocument()
    })
    expect(screen.getByText(/test-789/i)).toBeInTheDocument()

    // 后端验证请求被发出（含 auth headers）
    expect(mockFetch).toHaveBeenCalledWith(
      `${API_BASE}/sessions/test-789`,
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer test-token-for-auth' }),
      }),
    )

    // WebSocket 自动重连 — MockWebSocket 实例被创建
    expect(MockWebSocket.instances.length).toBeGreaterThan(0)
    expect(MockWebSocket.instances[0].url).toContain('test-789')
  })

  // ── 场景 B 补充：WebSocket 错误消息显示 ──────────────────────
  test('场景 B 补充：收到 WebSocket error 消息时显示错误提示', async () => {
    localStorage.setItem('econpaper_session_id', 'test-err')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (String(url).includes('/sessions/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ exists: true }),
        })
      }
      return Promise.reject(new Error('unexpected URL'))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    await waitFor(() => {
      expect(screen.getByTestId('session-id-indicator')).toBeInTheDocument()
    })

    const ws = MockWebSocket.instances[0]
    expect(ws).toBeDefined()

    // 发送 error 消息
    act(() => {
      ws.onmessage!({
        data: JSON.stringify({ type: 'error', message: 'StatsPAI 不可用' }),
      })
    })

    // 错误提示显示
    await waitFor(() => {
      expect(screen.getByText(/StatsPAI 不可用/i)).toBeInTheDocument()
    })
  })
})