import { describe, expect, test } from 'vitest'
import { agentSpikeEnabled } from '../featureFlags'

describe('agentSpikeEnabled', () => {
  test('本地开发默认开放实验页', () => {
    expect(agentSpikeEnabled({ DEV: true })).toBe(true)
  })

  test('生产环境默认关闭，不因知道 /spike URL 就可访问', () => {
    expect(agentSpikeEnabled({ DEV: false })).toBe(false)
  })

  test('生产环境只有显式开关为 1 才开放', () => {
    expect(agentSpikeEnabled({ DEV: false, VITE_ENABLE_AGENT_SPIKE: '1' })).toBe(true)
    expect(agentSpikeEnabled({ DEV: false, VITE_ENABLE_AGENT_SPIKE: 'true' })).toBe(false)
  })
})
