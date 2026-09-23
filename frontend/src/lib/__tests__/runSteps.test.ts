import { describe, expect, test } from 'vitest'
import {
  appendRunProgressEvent,
  createRunProgressState,
  projectRunSteps,
  RUN_NODE_LABEL_KEYS,
} from '../runSteps'
import type { RunProgressEvent } from '../runEvents'

const ev = (over: Partial<RunProgressEvent>): RunProgressEvent => ({
  type: 'run.progress',
  ...over,
})

describe('projectRunSteps', () => {
  test('没有事件就没有步骤（不拿空列表冒充进度）', () => {
    expect(projectRunSteps(undefined).hasSteps).toBe(false)
    expect(projectRunSteps([]).hasSteps).toBe(false)
    expect(projectRunSteps([]).steps).toEqual([])
    expect(projectRunSteps(undefined).activeNode).toBeNull()
  })

  test('非 run.progress 事件不产生步骤', () => {
    const progress = projectRunSteps([
      ev({ type: 'run.accepted', status: 'QUEUED' }),
      ev({ type: 'run.claimed', status: 'RUNNING' }),
      ev({ type: 'run.succeeded', status: 'SUCCEEDED' }),
    ])
    expect(progress.hasSteps).toBe(false)
  })

  test('没有 node 的 run.progress 不产生步骤', () => {
    expect(projectRunSteps([ev({ status: 'started' })]).hasSteps).toBe(false)
  })

  test('预写词表：started 进行中、completed 已完成、blocked 被拦住', () => {
    const progress = projectRunSteps([
      ev({ node: 'set_direction', status: 'started' }),
      ev({ node: 'set_direction', status: 'completed' }),
      ev({ node: 'identification_verify', status: 'started' }),
      ev({ node: 'identification_verify', status: 'completed' }),
      ev({ node: 'run_estimate', status: 'started' }),
    ])
    expect(progress.steps.map((s) => [s.node, s.status])).toEqual([
      ['set_direction', 'done'],
      ['identification_verify', 'done'],
      ['run_estimate', 'active'],
    ])
    expect(progress.activeNode).toBe('run_estimate')
    expect(progress.blocked).toBe(false)
  })

  test('后端第二套状态词表：running / done 也认', () => {
    const progress = projectRunSteps([
      ev({ node: 'legacy_batch', status: 'running' }),
      ev({ node: 'legacy_batch', status: 'done' }),
    ])
    expect(progress.steps).toHaveLength(1)
    expect(progress.steps[0]).toMatchObject({
      node: 'legacy_batch',
      status: 'done',
    })
  })

  test('blocked 是独立事实：后面还有步骤在跑也照样标出来', () => {
    const progress = projectRunSteps([
      ev({ node: 'identification_verify', status: 'blocked' }),
      ev({ node: 'search_literature', status: 'started' }),
    ])
    expect(progress.blocked).toBe(true)
    expect(progress.activeNode).toBe('search_literature')
    expect(progress.blockedStep?.node).toBe('identification_verify')
    expect(progress.activeSteps.map((step) => step.node)).toEqual([
      'identification_verify',
      'search_literature',
    ])
  })

  test('当前摘要候选按最后一次真实更新，而不是首次出现位置', () => {
    const progress = projectRunSteps([
      ev({ seq: 1, node: 'run_estimate', status: 'started' }),
      ev({ seq: 2, node: 'search_literature', status: 'started' }),
      ev({ seq: 3, node: 'run_estimate', status: 'blocked' }),
    ])
    expect(progress.latestUnresolvedStep?.node).toBe('run_estimate')
    expect(progress.blockedStep?.node).toBe('run_estimate')
  })

  test('同一节点出现多次只占一行，位置按首次出现', () => {
    const progress = projectRunSteps([
      ev({ node: 'run_estimate', status: 'started' }),
      ev({ node: 'search_literature', status: 'started' }),
      ev({ node: 'run_estimate', status: 'completed' }),
    ])
    expect(progress.steps.map((s) => s.node)).toEqual(['run_estimate', 'search_literature'])
    expect(progress.steps[0].status).toBe('done')
  })

  test('认不出的 status 不猜、不产生步骤', () => {
    expect(projectRunSteps([ev({ node: 'run_estimate', status: 'weird' })]).hasSteps).toBe(false)
  })

  test('未知节点原样保留（不丢弃、不改名）', () => {
    const progress = projectRunSteps([ev({ node: 'brand_new_node', status: 'started' })])
    expect(progress.steps[0].node).toBe('brand_new_node')
    expect(progress.steps[0].labelKey).toBeNull()
  })

  test('已知节点的文案 key 都在映射表里，未知节点不凭空造 key', () => {
    for (const [node, key] of Object.entries(RUN_NODE_LABEL_KEYS)) {
      expect(projectRunSteps([ev({ node, status: 'started' })]).steps[0].labelKey).toBe(key)
    }
    expect(Object.keys(RUN_NODE_LABEL_KEYS)).toContain('identification_verify')
    expect(Object.keys(RUN_NODE_LABEL_KEYS)).toContain('run_estimate')
    // spec_run 保留自己的 k/总数 UI；通用步骤披露不维护一份不可达文案。
    expect(Object.keys(RUN_NODE_LABEL_KEYS)).not.toContain('spec_run')
  })

  test('产出结构里没有百分比 / 预计时间 / 剩余步数这类字段', () => {
    const progress = projectRunSteps([
      ev({ node: 'run_estimate', status: 'started' }),
    ])
    expect(Object.keys(progress).sort()).toEqual([
      'activeLabelKey',
      'activeNode',
      'activeSteps',
      'blocked',
      'blockedStep',
      'hasSteps',
      'latestUnresolvedStep',
      'steps',
    ])
    for (const step of progress.steps) {
      expect(Object.keys(step).every((k) => ['node', 'labelKey', 'status', 'specId'].includes(k))).toBe(true)
    }
  })
})

describe('run-scoped progress buffer', () => {
  const owner = {
    sessionId: 'session-a',
    runId: 'run-a',
    kind: 'prewrite',
  }

  test('同一个步骤在达到容量后仍能收到完成状态，不会冻结在进行中', () => {
    let state = createRunProgressState(owner)
    for (let index = 0; index < 200; index += 1) {
      state = appendRunProgressEvent(
        state,
        owner,
        ev({ seq: index + 1, node: `node_${index}`, status: 'started' }),
      )
    }
    state = appendRunProgressEvent(
      state,
      owner,
      ev({ seq: 201, node: 'node_199', status: 'completed' }),
    )

    expect(state.events).toHaveLength(200)
    expect(state.events.find((event) => event.node === 'node_199')?.status).toBe('completed')
    expect(state.truncated).toBe(false)
  })

  test('超过容量时保留最新事实并明确记录省略数量', () => {
    let state = createRunProgressState(owner)
    for (let index = 0; index < 201; index += 1) {
      state = appendRunProgressEvent(
        state,
        owner,
        ev({ seq: index + 1, node: `node_${index}`, status: index < 150 ? 'completed' : 'started' }),
      )
    }

    expect(state.events).toHaveLength(200)
    expect(state.events.some((event) => event.node === 'node_200')).toBe(true)
    expect(state.truncated).toBe(true)
    expect(state.omittedCount).toBe(1)
  })

  test('旧 run 的晚到事件不能写入新 run', () => {
    const newOwner = { sessionId: 'session-a', runId: 'run-b', kind: 'upload_pipeline' }
    const current = createRunProgressState(newOwner)
    const next = appendRunProgressEvent(
      current,
      owner,
      ev({ seq: 1, node: 'clean_data', status: 'started' }),
    )

    expect(next).toBe(current)
    expect(next.events).toEqual([])
  })

  test('重复或倒序 seq 不会把较新的事实覆盖回旧状态', () => {
    let state = createRunProgressState(owner)
    state = appendRunProgressEvent(
      state,
      owner,
      ev({ seq: 2, node: 'clean_data', status: 'completed' }),
    )
    state = appendRunProgressEvent(
      state,
      owner,
      ev({ seq: 1, node: 'clean_data', status: 'started' }),
    )

    expect(state.events[0].status).toBe('completed')
    expect(state.lastSeq).toBe(2)
  })
})
