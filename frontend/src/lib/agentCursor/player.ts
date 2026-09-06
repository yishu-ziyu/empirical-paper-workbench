import { parseSemanticId } from './control'
import type { SemanticTargetRegistry } from './registry'
import type { AgentScript, AgentScriptStep } from './scripts'

export type AgentCursorStatus =
  | 'idle'
  | 'running'
  | 'paused'
  | 'awaiting-confirm'
  | 'aborted'
  | 'done'

export type AgentCursorPresentation = {
  status: AgentCursorStatus
  scriptId: string | null
  intent: string | null
  intentZh: string | null
  highlighted: string[]
  comparePair: [string, string] | null
  fadeUnchanged: boolean
  previewCommand: string | null
  awaiting: 'runPreview' | 'promote' | null
  abortReason: string | null
}

export const IDLE_PRESENTATION: AgentCursorPresentation = {
  status: 'idle',
  scriptId: null,
  intent: null,
  intentZh: null,
  highlighted: [],
  comparePair: null,
  fadeUnchanged: false,
  previewCommand: null,
  awaiting: null,
  abortReason: null,
}

class AgentAbort extends Error {
  reason: string
  constructor(reason: string) {
    super(reason)
    this.reason = reason
    this.name = 'AgentAbort'
  }
}

export type AgentCursorDriver = {
  registry: SemanticTargetRegistry
  reducedMotion: () => boolean
  moveTo: (el: Element, opts: { reduced: boolean }) => Promise<void>
  openEvidence: () => void
  runPreview: (command: string) => Promise<void>
  promote: () => Promise<void>
  onPresentation: (next: AgentCursorPresentation) => void
  clock: { sleep: (ms: number) => Promise<void> }
  waitForTarget?: (id: string, timeoutMs: number) => Promise<boolean>
  readDelta?: () => { deltaAbs: number | null; deltaPct: number | null } | null
}

export function travelDurationMs(reduced: boolean): number {
  return reduced ? 0 : 420
}

export function isSmallDelta(delta: { deltaAbs: number | null; deltaPct: number | null } | null): boolean {
  if (!delta || delta.deltaAbs == null) return false
  if (Math.abs(delta.deltaAbs) < 0.02) return true
  if (delta.deltaPct != null && Math.abs(delta.deltaPct) < 15) return true
  return false
}

function defaultWaitForTarget(
  registry: SemanticTargetRegistry,
  clock: { sleep: (ms: number) => Promise<void> },
  id: string,
  timeoutMs: number,
): Promise<boolean> {
  const deadline = Date.now() + timeoutMs
  const poll = async (): Promise<boolean> => {
    if (registry.has(id)) return true
    if (Date.now() >= deadline) return false
    await clock.sleep(40)
    return poll()
  }
  return poll()
}

export class AgentCursorPlayer {
  private presentation: AgentCursorPresentation = { ...IDLE_PRESENTATION }
  private cancelled = false
  private paused = false
  private resumeWaiters: Array<() => void> = []
  private confirmWaiters: Array<() => void> = []
  private confirmed: 'runPreview' | 'promote' | null = null
  private activeScript: AgentScript | null = null
  private generation = 0

  private readonly driver: AgentCursorDriver

  constructor(driver: AgentCursorDriver) {
    this.driver = driver
  }

  get state(): AgentCursorPresentation {
    return this.presentation
  }

  async play(script: AgentScript): Promise<AgentCursorPresentation> {
    this.generation += 1
    const gen = this.generation
    this.cancelled = false
    this.paused = false
    this.confirmed = null
    this.activeScript = script
    this.patch({
      ...IDLE_PRESENTATION,
      status: 'running',
      scriptId: script.id,
    })
    this.driver.openEvidence()
    try {
      for (const step of script.steps) {
        if (gen !== this.generation) return this.presentation
        await this.guard()
        await this.execute(step)
        if (this.presentation.status === 'aborted') return this.presentation
      }
      if (this.presentation.status !== 'aborted') {
        this.patch({ status: 'done', awaiting: null })
      }
    } catch (err) {
      if (err instanceof AgentAbort) {
        this.patch({
          status: 'aborted',
          abortReason: err.reason,
          awaiting: null,
        })
        return this.presentation
      }
      throw err
    }
    return this.presentation
  }

  cancel(): void {
    this.cancelled = true
    this.paused = false
    this.flushWaits()
    this.activeScript = null
    this.patch({ ...IDLE_PRESENTATION, status: 'idle' })
  }

  pause(): void {
    if (this.presentation.status !== 'running') return
    this.paused = true
    this.patch({ status: 'paused' })
  }

  resume(): void {
    if (this.presentation.status !== 'paused') return
    this.paused = false
    this.patch({ status: 'running' })
    this.flushResume()
  }

  replay(): Promise<AgentCursorPresentation> {
    const script = this.activeScript
    this.cancelled = true
    this.flushWaits()
    if (!script) {
      this.patch({ ...IDLE_PRESENTATION })
      return Promise.resolve(this.presentation)
    }
    return this.play(script)
  }

  confirm(kind: 'runPreview' | 'promote' = 'runPreview'): void {
    this.confirmed = kind
    const waiters = this.confirmWaiters.splice(0)
    for (const waiter of waiters) waiter()
  }

  /** Point: highlight only. Never run or promote. */
  async point(target: unknown, intent?: string, intentZh?: string): Promise<void> {
    const id = parseSemanticId(target)
    const el = await this.requireTarget(id)
    if (!el) return
    this.patch({
      highlighted: [id],
      intent: intent ?? this.presentation.intent,
      intentZh: intentZh ?? this.presentation.intentZh,
    })
    await this.driver.moveTo(el, { reduced: this.driver.reducedMotion() })
  }

  async compare(a: unknown, b: unknown, intent?: string, intentZh?: string): Promise<void> {
    const idA = parseSemanticId(a)
    const idB = parseSemanticId(b)
    const elA = await this.requireTarget(idA)
    const elB = await this.requireTarget(idB)
    if (!elA || !elB) return
    this.patch({
      highlighted: [idA, idB],
      comparePair: [idA, idB],
      intent: intent ?? this.presentation.intent,
      intentZh: intentZh ?? this.presentation.intentZh,
    })
    await this.driver.moveTo(elA, { reduced: this.driver.reducedMotion() })
    await this.guard()
    await this.driver.moveTo(elB, { reduced: this.driver.reducedMotion() })
    const delta = this.driver.readDelta?.() ?? null
    if (isSmallDelta(delta)) {
      this.patch({ intent: 'Little changed', intentZh: this.presentation.intentZh })
    }
  }

  async preview(command: unknown, intent?: string, intentZh?: string): Promise<void> {
    const id = parseSemanticId(command)
    this.patch({
      previewCommand: id,
      intent: intent ?? this.presentation.intent,
      intentZh: intentZh ?? this.presentation.intentZh,
    })
  }

  async runPreview(): Promise<void> {
    if (this.confirmed !== 'runPreview') return
    const command = this.presentation.previewCommand
    if (!command) return
    await this.driver.runPreview(command)
  }

  async promote(): Promise<void> {
    if (this.confirmed !== 'promote') return
    await this.driver.promote()
  }

  private async execute(step: AgentScriptStep): Promise<void> {
    switch (step.op) {
      case 'point':
        await this.point(step.target, step.intent, step.intentZh)
        return
      case 'compare':
        await this.compare(step.a, step.b, step.intent, step.intentZh)
        return
      case 'preview':
        await this.preview(step.command, step.intent, step.intentZh)
        return
      case 'runPreview':
        await this.runPreview()
        return
      case 'promote':
        await this.promote()
        return
      case 'pause': {
        const ms = this.driver.reducedMotion() ? Math.min(step.ms, 80) : step.ms
        await this.driver.clock.sleep(ms)
        return
      }
      case 'awaitConfirm':
        this.patch({ status: 'awaiting-confirm', awaiting: step.kind })
        await this.waitForConfirm()
        if (this.cancelled) throw new AgentAbort('cancelled')
        this.patch({ status: 'running', awaiting: step.kind })
        return
      case 'fadeUnchanged':
        this.patch({ fadeUnchanged: true })
        return
      case 'stop':
        this.patch({ status: 'done', awaiting: null })
        return
      default:
        return
    }
  }

  private async requireTarget(id: string): Promise<Element | null> {
    const wait =
      this.driver.waitForTarget ??
      ((target: string, timeoutMs: number) =>
        defaultWaitForTarget(this.driver.registry, this.driver.clock, target, timeoutMs))
    const found =
      this.driver.registry.lookup(id) ??
      ((await wait(id, 2500)) ? this.driver.registry.lookup(id) : null)
    if (!found) {
      this.patch({ status: 'aborted', abortReason: 'missing-target', awaiting: null })
      return null
    }
    return found
  }

  private async guard(): Promise<void> {
    if (this.cancelled) throw new AgentAbort('cancelled')
    while (this.paused && !this.cancelled) {
      await new Promise<void>((resolve) => {
        this.resumeWaiters.push(resolve)
      })
    }
    if (this.cancelled) throw new AgentAbort('cancelled')
  }

  private waitForConfirm(): Promise<void> {
    if (this.confirmed) return Promise.resolve()
    return new Promise((resolve) => {
      this.confirmWaiters.push(resolve)
    })
  }

  private flushWaits() {
    this.flushResume()
    const confirms = this.confirmWaiters.splice(0)
    for (const waiter of confirms) waiter()
  }

  private flushResume() {
    const waiters = this.resumeWaiters.splice(0)
    for (const waiter of waiters) waiter()
  }

  private patch(partial: Partial<AgentCursorPresentation>) {
    this.presentation = { ...this.presentation, ...partial }
    this.driver.onPresentation(this.presentation)
  }
}
