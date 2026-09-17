import { describe, expect, test } from 'vitest'
import { projectRunSteps, RUN_NODE_LABEL_KEYS } from '../runSteps'
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

  test('设定跑批词表：running / done 也认', () => {
    const progress = projectRunSteps([
      ev({ node: 'spec_run', status: 'running', specId: 'ols_linear_exper' }),
      ev({ node: 'spec_run', status: 'done', specId: 'ols_linear_exper' }),
    ])
    expect(progress.steps).toHaveLength(1)
    expect(progress.steps[0]).toMatchObject({
      node: 'spec_run',
      status: 'done',
      specId: 'ols_linear_exper',
    })
  })

  test('blocked 是独立事实：后面还有步骤在跑也照样标出来', () => {
    const progress = projectRunSteps([
      ev({ node: 'identification_verify', status: 'blocked' }),
      ev({ node: 'search_literature', status: 'started' }),
    ])
    expect(progress.blocked).toBe(true)
    expect(progress.activeNode).toBe('search_literature')
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
  })

  test('产出结构里没有百分比 / 预计时间 / 剩余步数这类字段', () => {
    const progress = projectRunSteps([
      ev({ node: 'run_estimate', status: 'started' }),
    ])
    expect(Object.keys(progress).sort()).toEqual([
      'activeLabelKey',
      'activeNode',
      'blocked',
      'hasSteps',
      'steps',
    ])
    for (const step of progress.steps) {
      expect(Object.keys(step).every((k) => ['node', 'labelKey', 'status', 'specId'].includes(k))).toBe(true)
    }
  })
})
