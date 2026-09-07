import { describe, expect, test, vi, beforeEach } from 'vitest'
import { AgentControlPlaneError, parseSemanticId, rejectCoordinateControl } from '../agentCursor/control'
import { SemanticTargetRegistry } from '../agentCursor/registry'
import { AgentCursorPlayer, travelDurationMs, type AgentCursorDriver, type AgentCursorPresentation } from '../agentCursor/player'
import {
  CARD_CHALLENGE_EXPERIENCE_SCRIPT,
  CARD_SHOW_ME_SCRIPT,
  TARGET,
} from '../agentCursor/scripts'

const sources = import.meta.glob('../agentCursor/**/*.ts', {
  eager: true,
  query: '?raw',
  import: 'default',
}) as Record<string, string>

function mockDriver(registry: SemanticTargetRegistry, extras: Partial<AgentCursorDriver> = {}): AgentCursorDriver {
  return {
    registry,
    reducedMotion: () => false,
    moveTo: vi.fn(async () => undefined),
    openEvidence: vi.fn(),
    runPreview: vi.fn(async () => undefined),
    promote: vi.fn(async () => undefined),
    onPresentation: vi.fn(),
    clock: { sleep: vi.fn(async () => undefined) },
    waitForTarget: async (id) => registry.has(id),
    ...extras,
  }
}

describe('Agent control plane', () => {
  test('script helpers only accept semantic ids', () => {
    expect(parseSemanticId('evidence.spec.ols')).toBe('evidence.spec.ols')
    expect(() => parseSemanticId({ x: 10, y: 20 })).toThrow(AgentControlPlaneError)
    expect(() => rejectCoordinateControl({ x: 1, y: 2 })).toThrow(/coordinate/)
    expect(() => parseSemanticId('.results-space')).toThrow(/selector/)
    expect(() => parseSemanticId('#evidence-spec-ols')).toThrow(/selector/)
    expect(() => parseSemanticId('querySelector(".foo")')).toThrow(/selector/)
    expect(() => parseSemanticId('//div[@id="x"]')).toThrow(/selector/)
  })

  test('agent scripts contain no querySelector or x= control', () => {
    const scriptSrc = sources['../agentCursor/scripts.ts']
    expect(scriptSrc).toBeTruthy()
    expect(scriptSrc).not.toMatch(/querySelector/)
    expect(scriptSrc).not.toMatch(/\bx\s*=/)
    expect(scriptSrc).not.toMatch(/xpath/i)
    expect(scriptSrc).toContain(TARGET.ols)
    expect(scriptSrc).toContain(TARGET.iv)
    expect(scriptSrc).toContain(TARGET.estimator)
    expect(scriptSrc).toContain(TARGET.experience)
  })
})

describe('SemanticTargetRegistry', () => {
  test('lookup is by semantic id only', () => {
    const registry = new SemanticTargetRegistry()
    const el = document.createElement('div')
    registry.register('evidence.spec.ols', el)
    expect(registry.lookup('evidence.spec.ols')).toBe(el)
    expect(() => registry.lookup({ x: 0, y: 0 })).toThrow(AgentControlPlaneError)
    expect(() => registry.register('#ols', el)).toThrow(AgentControlPlaneError)
  })
})

describe('AgentCursorPlayer', () => {
  let registry: SemanticTargetRegistry
  let ols: HTMLDivElement
  let iv: HTMLDivElement

  beforeEach(() => {
    registry = new SemanticTargetRegistry()
    ols = document.createElement('div')
    iv = document.createElement('div')
    registry.register(TARGET.ols, ols)
    registry.register(TARGET.iv, iv)
    registry.register(TARGET.estimator, document.createElement('th'))
  })

  test('point does not call promote or runPreview', async () => {
    const driver = mockDriver(registry)
    const player = new AgentCursorPlayer(driver)
    await player.point(TARGET.ols)
    expect(driver.moveTo).toHaveBeenCalledTimes(1)
    expect(driver.runPreview).not.toHaveBeenCalled()
    expect(driver.promote).not.toHaveBeenCalled()
  })

  test('missing target aborts without throw', async () => {
    const driver = mockDriver(registry)
    const player = new AgentCursorPlayer(driver)
    await expect(player.point('evidence.spec.missing')).resolves.toBeUndefined()
    expect(player.state.status).toBe('aborted')
    expect(player.state.abortReason).toBe('missing-target')
    expect(driver.runPreview).not.toHaveBeenCalled()
    expect(driver.promote).not.toHaveBeenCalled()
  })

  test('reduced-motion path skips travel duration', () => {
    expect(travelDurationMs(true)).toBe(0)
    expect(travelDurationMs(false)).toBeGreaterThan(0)
  })

  test('show-me script points then compares without running specs', async () => {
    const presentations: AgentCursorPresentation[] = []
    const driver = mockDriver(registry, {
      onPresentation: (p) => presentations.push({ ...p }),
    })
    const player = new AgentCursorPlayer(driver)
    const result = await player.play(CARD_SHOW_ME_SCRIPT)
    expect(result.status).toBe('done')
    expect(result.comparePair).toEqual([TARGET.ols, TARGET.iv])
    expect(result.fadeUnchanged).toBe(true)
    expect(presentations.some((p) => p.intent === 'Identification strategy changed' && p.intentZh === '识别策略发生变化')).toBe(true)
    expect(result.intent).toBe('This is the main change.')
    expect(result.intentZh).toBe('主要变化来自这里。')
    expect(driver.runPreview).not.toHaveBeenCalled()
    expect(driver.promote).not.toHaveBeenCalled()
    expect(driver.openEvidence).toHaveBeenCalled()
  })

  test('runPreview is a no-op until the user confirms', async () => {
    const driver = mockDriver(registry)
    const player = new AgentCursorPlayer(driver)
    await player.preview('experience.linear-quadratic')
    await player.runPreview()
    expect(driver.runPreview).not.toHaveBeenCalled()
    player.confirm('runPreview')
    await player.runPreview()
    expect(driver.runPreview).toHaveBeenCalledTimes(1)
  })

  test('challenge script waits for confirm before runPreview', async () => {
    registry.register(TARGET.experience, document.createElement('th'))
    registry.register(TARGET.experienceLinear, document.createElement('div'))
    registry.register(TARGET.experienceQuadratic, document.createElement('div'))
    const driver = mockDriver(registry)
    const player = new AgentCursorPlayer(driver)
    const playing = player.play(CARD_CHALLENGE_EXPERIENCE_SCRIPT)
    await vi.waitFor(() => {
      expect(player.state.status).toBe('awaiting-confirm')
    })
    expect(driver.runPreview).not.toHaveBeenCalled()
    player.confirm('runPreview')
    const result = await playing
    expect(result.status).toBe('done')
    expect(driver.runPreview).toHaveBeenCalledTimes(1)
    expect(driver.promote).not.toHaveBeenCalled()
  })
})

describe('Show me choreography budget (M3/C14)', () => {
  test('healthy-path wall clock from script data is ≤ 6s', () => {
    const travel = travelDurationMs(false)
    let total = 0
    for (const step of CARD_SHOW_ME_SCRIPT.steps) {
      if (step.op === 'pause') total += step.ms
      else if (step.op === 'point') total += travel
      else if (step.op === 'compare') total += travel * 2
    }
    // 6 travels ×420ms + 500+500+1600+600ms pauses = 5720ms
    expect(total).toBeLessThanOrEqual(6000)
    expect(total).toBeGreaterThan(0)
  })

  test('reduced-motion path stays within budget too', () => {
    const travel = travelDurationMs(true)
    expect(travel).toBe(0)
    let total = 0
    for (const step of CARD_SHOW_ME_SCRIPT.steps) {
      if (step.op === 'pause') total += Math.min(step.ms, 80)
      else if (step.op === 'point') total += travel
      else if (step.op === 'compare') total += travel * 2
    }
    expect(total).toBeLessThanOrEqual(600)
  })

  test('pause mid-play then resume continues from the current step (C15)', async () => {
    const localRegistry = new SemanticTargetRegistry()
    localRegistry.register(TARGET.ols, document.createElement('div'))
    localRegistry.register(TARGET.iv, document.createElement('div'))
    localRegistry.register(TARGET.estimator, document.createElement('th'))
    const driver = mockDriver(localRegistry)
    const player = new AgentCursorPlayer(driver)
    let moves = 0
    driver.moveTo = async () => {
      moves += 1
      if (moves === 3) player.pause()
    }
    const playing = player.play(CARD_SHOW_ME_SCRIPT)
    await vi.waitFor(() => {
      expect(player.state.status).toBe('paused')
    })
    expect(moves).toBe(3)
    player.resume()
    expect(player.state.status).toBe('running')
    const result = await playing
    // Resume continues from the current step: all 6 travels still run and
    // the script reaches done with the final intent.
    expect(result.status).toBe('done')
    expect(moves).toBe(6)
    expect(result.intent).toBe('This is the main change.')
  })
})
