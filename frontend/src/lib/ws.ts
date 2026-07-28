// WS 客户端 - T-02 阶段 B 实现
// 分发后端推送的 WSMessage 到对应回调

export type WSStatus = 'connecting' | 'connected' | 'disconnected'

export type WSMessage =
  | { type: 'status'; node: string; status: 'running' | 'paused' | 'done' }
  | { type: 'streaming_chunk'; chapter_id: string; chunk: string }
  | { type: 'interrupt'; chapter_id: string; content: string }
  | { type: 'error'; message: string }

export interface WSClientOptions {
  onChunk?: (chapterId: string, chunk: string) => void
  onStatus?: (node: string, status: 'running' | 'paused' | 'done') => void
  onInterrupt?: (chapterId: string, content: string) => void
  onError?: (message: string) => void
  onConnectionChange?: (state: WSStatus) => void
}

export class WSClient {
  private ws: WebSocket | null = null
  private url: string
  private options: WSClientOptions

  constructor(url: string, options: WSClientOptions = {}) {
    this.url = url
    this.options = options
  }

  connect(): void {
    this.options.onConnectionChange?.('connecting')
    const ws = new WebSocket(this.url)
    this.ws = ws

    ws.onopen = () => {
      this.options.onConnectionChange?.('connected')
    }

    ws.onmessage = (event: MessageEvent) => {
      try {
        const msg: WSMessage = JSON.parse(event.data)
        switch (msg.type) {
          case 'streaming_chunk':
            this.options.onChunk?.(msg.chapter_id, msg.chunk)
            break
          case 'status':
            this.options.onStatus?.(msg.node, msg.status)
            break
          case 'interrupt':
            this.options.onInterrupt?.(msg.chapter_id, msg.content)
            break
          case 'error':
            this.options.onError?.(msg.message)
            break
        }
      } catch {
        // 非 JSON 消息，忽略
      }
    }

    ws.onclose = () => {
      this.options.onConnectionChange?.('disconnected')
    }

    ws.onerror = () => {
      this.options.onConnectionChange?.('disconnected')
    }
  }

  close(): void {
    this.ws?.close()
    this.ws = null
  }
}
