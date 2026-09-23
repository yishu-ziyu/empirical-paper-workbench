type AgentSpikeEnv = {
  DEV?: boolean
  VITE_ENABLE_AGENT_SPIKE?: string
}

/**
 * /spike 是独立实验面，不得因为知道 URL 就在生产环境裸露。
 * 本地开发默认可用；生产构建只有显式置 VITE_ENABLE_AGENT_SPIKE=1 才开放。
 */
export function agentSpikeEnabled(env: AgentSpikeEnv = import.meta.env): boolean {
  return env.DEV === true || env.VITE_ENABLE_AGENT_SPIKE === '1'
}
