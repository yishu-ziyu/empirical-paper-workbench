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
 * - 设定跑批：`spec_run`，带 `spec_id`（`backend/services/spec_run.py`）
 *
 * 状态词表有**两套**，都按原样接受，不替后端做归一：
 * - 上传/预写：`started` → 进行中；`completed` → 已完成；`blocked` → 被拦住
 * - 设定跑批：`running` → 进行中；`done` → 已完成
 *
 * 这里不产出百分比、不产出预计时间、不产出「还剩几步」—— 后端没有这些事实。
 */
import type { RunProgressEvent } from './runEvents'

export type RunStepStatus = 'active' | 'done' | 'blocked'

export type RunStep = {
  /** 后端事件里的原始 node 值（未知节点也原样保留，不丢弃） */
  node: string
  /** 已知节点的 i18n key；未知节点为 null，由调用方回落到 node 原文 */
  labelKey: string | null
  status: RunStepStatus
  /** `spec_run` 会带真实 spec_id，用于区分同批里的不同设定 */
  specId?: string
}

export type RunProgress = {
  /** 最近一个「进行中/被拦住」的真实节点，没有则为 null */
  activeNode: string | null
  activeLabelKey: string | null
  blocked: boolean
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
  spec_run: 'runStep.node.specRun',
}

function statusOf(raw: string | undefined): RunStepStatus | null {
  if (raw === 'started' || raw === 'running') return 'active'
  if (raw === 'completed' || raw === 'done') return 'done'
  if (raw === 'blocked') return 'blocked'
  // 认不出的状态不猜：不产生步骤，也不伪造进度。
  return null
}

export function projectRunSteps(events: RunProgressEvent[] | undefined | null): RunProgress {
  const steps: RunStep[] = []
  const byKey = new Map<string, RunStep>()

  for (const event of events || []) {
    if (!event || event.type !== 'run.progress') continue
    const node = typeof event.node === 'string' && event.node.trim() ? event.node.trim() : null
    if (!node) continue
    const status = statusOf(event.status)
    if (!status) continue

    // 同一节点在一次 run 里可能出现多次（staged 多轮）；保留首次出现的位置，
    // 用最新状态覆盖，不重复堆一列同名步骤。
    const key = `${node}::${event.specId || ''}`
    const existing = byKey.get(key)
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

  // 「当前动作」= 最后一个还没做完的步骤。并行扇出时事件顺序就是真实发生顺序，
  // 不能假设这是一条线性流水线，所以只取最后出现的那一个未完成项。
  let activeNode: string | null = null
  let activeLabelKey: string | null = null
  for (const step of steps) {
    if (step.status === 'done') continue
    activeNode = step.node
    activeLabelKey = step.labelKey
  }
  // 被拦住是独立的事实：即使后面还有步骤在跑，也要如实标出来。
  const blocked = steps.some((step) => step.status === 'blocked')

  return {
    activeNode,
    activeLabelKey,
    blocked,
    steps,
    hasSteps: steps.length > 0,
  }
}
