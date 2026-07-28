import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { WSClient } from '../lib/ws'

// Mock WebSocket - 捕获 WSClient 创建的实例并允许测试触发 onmessage
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

beforeEach(() => {
  MockWebSocket.instances = []
  vi.stubGlobal('WebSocket', MockWebSocket)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('WSClient 消息分发', () => {
  test('收到 streaming_chunk 时调用 onChunk 回调', () => {
    const onChunk = vi.fn()
    const client = new WSClient('ws://localhost/ws', { onChunk })
    client.connect()

    // 占位 WSClient.connect() 是 no-op，不会创建 WebSocket → instances 为空 → 红
    const ws = MockWebSocket.instances[0]
    expect(ws).toBeDefined()

    ws!.onmessage!({
      data: JSON.stringify({
        type: 'streaming_chunk',
        chapter_id: '1',
        chunk: 'abc',
      }),
    })

    expect(onChunk).toHaveBeenCalledWith('1', 'abc')
  })

  test('收到 status 时调用 onStatus 回调', () => {
    const onStatus = vi.fn()
    const client = new WSClient('ws://localhost/ws', { onStatus })
    client.connect()

    const ws = MockWebSocket.instances[0]
    expect(ws).toBeDefined()

    ws!.onmessage!({
      data: JSON.stringify({
        type: 'status',
        node: 'generate_title',
        status: 'done',
      }),
    })

    expect(onStatus).toHaveBeenCalledWith('generate_title', 'done')
  })
})
