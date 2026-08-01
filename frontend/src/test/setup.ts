import '@testing-library/jest-dom'

// Mock WebSocket for jsdom (jsdom does not provide WebSocket by default).
// ws.test.ts installs its own MockWebSocket via vi.stubGlobal per-test; this
// global mock only serves as a fallback so <App /> (which creates a WSClient
// in a useEffect) does not crash when rendered in non-WS-specific tests.
class MockWebSocket {
  url: string
  onopen: ((ev: unknown) => void) | null = null
  onmessage: ((ev: { data: string }) => void) | null = null
  onclose: ((ev: unknown) => void) | null = null
  onerror: ((ev: unknown) => void) | null = null
  readyState = 0
  constructor(url: string) {
    this.url = url
  }
  send(): void {}
  close(): void {
    this.readyState = 3
  }
}

if (typeof globalThis.WebSocket === 'undefined') {
  globalThis.WebSocket = MockWebSocket as unknown as typeof WebSocket
}
