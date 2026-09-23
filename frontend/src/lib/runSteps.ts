/**
 * 把**真实** run 事件投影成「这一步怎样推进」的步骤列表。
 *
 * 存在的理由（见 `docs/specs/frontend-interaction-current.md` §3）：分析中默认只给
 * 一句当前动作 + 一个安静呼吸点，路径是次级信息、用户展开才看。展开后的每一步必须是
 * 后端真的发过的事件 —— 没有事件就不出现步骤，绝不用定时器凑出「看起来在忙」。
 *
 * 事实来源：`backend/runner.py` 的 `run.progress`，payload 只公开 `node` / `status`
 * / `spec_id`（`backend/routers/run_execution.py` 的 `_public_event`）。真实的 node 词表：
 * - 上传链路：`upload_data`、`clean_data`（`agent/engine/upload.py`）
 * - 预写链路：`PRWRITE_SEQUENCE` 的节点 + `prewrite_preview`（`agent/engine/prewrite.py`）
 * - 设定跑批也会发 `spec_run`，但产品保留其独立的 k/总数 UI，不把它重复接入本披露
 *
 * 状态词表有**两套**，都按原样接受，不替后端做归一：
 * - 上传/预写：`started` → 进行中；`completed` → 已完成；`blocked` → 被拦住
 * - 设定跑批：`running` → 进行中；`done` → 已完成
 *
 * 这里不产出百分比、不产出预计时间、不产出「还剩几步」—— 后端没有这些事实。
 */
import type { RunProgressEvent } from './runEvents'

export type RunStepStatus = 'active' | 'done' | 'blocked'

export type RunProgressOwner = {
  sessionId: string
  runId: string
  kind: string
}

/**
 * 底栏只拥有一个「当前 run」的短期观测状态。
 *
 * events 不是审计日志，而是每个 node::specId 的最新已收事件；完整历史由后端 RunEvent
 * 与账本负责。这样既不复制第二套运行真相，也不会在达到容量后停止接受完成/阻断事实。
 */
export type RunProgressState = RunProgressOwner & {
  events: RunProgressEvent[]
  truncated: boolean
  omittedCount: number
  lastSeq: number | null
}

export const MAX_RUN_PROGRESS_STEPS = 200

export type RunStep = {
  /** 后端事件里的原始 node 值（未知节点也原样保留，不丢弃） */
  node: string
  /** 已知节点的 i18n key；未知节点为 null，用户文案保持中性，详情保留原始 node */
  labelKey: string | null
  status: RunStepStatus
  /** 若事件带稳定 spec_id，用于区分同名节点的不同工作单元 */
  specId?: string
}

export type RunProgress = {
  /** 最近一个「进行中/被拦住」的真实节点，没有则为 null */
  activeNode: string | null
  activeLabelKey: string | null
  blocked: boolean
  /** 所有尚未完成的步骤；blocked 也属于尚未完成的事实。 */
  activeSteps: RunStep[]
  /** 最近一次被后端更新的未完成步骤，不等同于唯一“当前动作”。 */
  latestUnresolvedStep: RunStep | null
  /** 最近一次被后端更新的 blocked 步骤；摘要必须优先呈现。 */
  blockedStep: RunStep | null
  steps: RunStep[]
  /** 有没有拿到的真实步骤（没有就不该渲染展开区） */
  hasSteps: boolean
}

/**
 * 真实 node → i18n key。键必须逐字等于后端会发出的值，写错就等于编造了一个步骤名。
 * 与 `agent/engine/prewrite.py` 的 `PRWRITE_SEQUENCE` 和 `agent/engine/upload.py` 对齐。
 */
export const RUN_NODE_LABEL_KEYS: Record<string, string> = {
  upload_data: 'runStep.node.uploadData',
  clean_data: 'runStep.node.cleanData',
  set_direction: 'runStep.node.setDirection',
  identification_verify: 'runStep.node.identificationVerify',
  run_estimate: 'runStep.node.runEstimate',
  robustness_check: 'runStep.node.robustnessCheck',
  search_literature: 'runStep.node.searchLiterature',
  build_citation_graph: 'runStep.node.buildCitationGraph',
  generate_title: 'runStep.node.generateTitle',
  generate_outline: 'runStep.node.generateOutline',
  prewrite_preview: 'runStep.node.prewritePreview',
}

function statusOf(raw: string | undefined): RunStepStatus | null {
  if (raw === 'started' || raw === 'running') return 'active'
  if (raw === 'completed' || raw === 'done') return 'done'
  if (raw === 'blocked') return 'blocked'
  // 认不出的状态不猜：不产生步骤，也不伪造进度。
  return null
}

function eventKey(event: Pick<RunProgressEvent, 'node' | 'specId'>): string {
  return `${event.node || ''}::${event.specId || ''}`
}

function sameOwner(state: RunProgressState, owner: RunProgressOwner): boolean {
  return (
    state.sessionId === owner.sessionId
    && state.runId === owner.runId
    && state.kind === owner.kind
  )
}

export function createRunProgressState(owner: RunProgressOwner): RunProgressState {
  return {
    ...owner,
    events: [],
    truncated: false,
    omittedCount: 0,
    lastSeq: null,
  }
}

/**
 * 把一个真实事件写入指定 run 的短期观测缓冲。
 *
 * - owner 不匹配：这是旧 run 的晚到事件，原样忽略；
 * - 同一 node::specId：保留首次位置，但永远接受最新状态；
 * - 达到容量：先丢最早已完成项，再丢最早 active，最后才会丢 blocked；
 * - 截断必须显式记录，UI 不得装作路径完整。
 */
export function appendRunProgressEvent(
  state: RunProgressState,
  owner: RunProgressOwner,
  event: RunProgressEvent,
  limit = MAX_RUN_PROGRESS_STEPS,
): RunProgressState {
  if (!sameOwner(state, owner)) return state
  if (event.type !== 'run.progress') return state
  const node = typeof event.node === 'string' ? event.node.trim() : ''
  const status = statusOf(event.status)
  if (!node || !status) return state
  if (
    typeof event.seq === 'number'
    && state.lastSeq !== null
    && event.seq <= state.lastSeq
  ) return state

  const normalized: RunProgressEvent = { ...event, node }
  const nextLastSeq = typeof event.seq === 'number' ? event.seq : state.lastSeq
  const key = eventKey(normalized)
  const existingIndex = state.events.findIndex((item) => eventKey(item) === key)
  if (existingIndex >= 0) {
    const events = [...state.events]
    events[existingIndex] = normalized
    return { ...state, events, lastSeq: nextLastSeq }
  }

  if (limit <= 0) {
    return {
      ...state,
      truncated: true,
      omittedCount: state.omittedCount + 1,
      lastSeq: nextLastSeq,
    }
  }

  if (state.events.length < limit) {
    return {
      ...state,
      events: [...state.events, normalized],
      lastSeq: nextLastSeq,
    }
  }

  const settledIndex = state.events.findIndex((item) => statusOf(item.status) === 'done')
  const activeIndex = state.events.findIndex((item) => statusOf(item.status) === 'active')
  const dropIndex = settledIndex >= 0 ? settledIndex : activeIndex >= 0 ? activeIndex : 0
  const events = [...state.events]
  events.splice(dropIndex, 1)
  events.push(normalized)
  return {
    ...state,
    events,
    truncated: true,
    omittedCount: state.omittedCount + 1,
    lastSeq: nextLastSeq,
  }
}

function newestStep(
  candidates: RunStep[],
  lastOrderByKey: Map<string, number>,
): RunStep | null {
  let newest: RunStep | null = null
  let newestOrder = Number.NEGATIVE_INFINITY
  for (const step of candidates) {
    const order = lastOrderByKey.get(`${step.node}::${step.specId || ''}`) ?? -1
    if (order >= newestOrder) {
      newest = step
      newestOrder = order
    }
  }
  return newest
}

export function projectRunSteps(events: RunProgressEvent[] | undefined | null): RunProgress {
  const steps: RunStep[] = []
  const byKey = new Map<string, RunStep>()
  const lastOrderByKey = new Map<string, number>()

  for (const [index, event] of (events || []).entries()) {
    if (!event || event.type !== 'run.progress') continue
    const node = typeof event.node === 'string' && event.node.trim() ? event.node.trim() : null
    if (!node) continue
    const status = statusOf(event.status)
    if (!status) continue

    // 同一节点在一次 run 里可能出现多次（staged 多轮）；保留首次出现的位置，
    // 用最新状态覆盖，不重复堆一列同名步骤。
    const key = `${node}::${event.specId || ''}`
    const existing = byKey.get(key)
    lastOrderByKey.set(key, typeof event.seq === 'number' ? event.seq : index)
    if (existing) {
      existing.status = status
      continue
    }
    const step: RunStep = {
      node,
      labelKey: RUN_NODE_LABEL_KEYS[node] ?? null,
      status,
      ...(event.specId ? { specId: event.specId } : {}),
    }
    byKey.set(key, step)
    steps.push(step)
  }

  const activeSteps = steps.filter((step) => step.status !== 'done')
  const latestUnresolvedStep = newestStep(activeSteps, lastOrderByKey)
  const blockedSteps = activeSteps.filter((step) => step.status === 'blocked')
  const blockedStep = newestStep(blockedSteps, lastOrderByKey)
  const blocked = blockedStep !== null

  return {
    activeNode: latestUnresolvedStep?.node ?? null,
    activeLabelKey: latestUnresolvedStep?.labelKey ?? null,
    blocked,
    activeSteps,
    latestUnresolvedStep,
    blockedStep,
    steps,
    hasSteps: steps.length > 0,
  }
}
