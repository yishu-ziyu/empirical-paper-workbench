import { describe, expect, it } from 'vitest'

import {
  AdmissionConflictError,
  canOpenSpecConfirm,
  canOpenTable1,
  canRunEstimate,
  canSubmitDirection,
  formalAttachApplies,
  parseAdmissionConflict,
  readDataAttached,
  shouldDivertToAttach,
  snapshotAttachFields,
} from '../dataAttachedGate'

describe('DC-FE-gate dataAttached', () => {
  it('fails closed: only explicit true is attached', () => {
    expect(readDataAttached({})).toBe(false)
    expect(readDataAttached({ dataAttached: false })).toBe(false)
    expect(readDataAttached({ dataAttached: null })).toBe(false)
    expect(readDataAttached({ dataAttached: true })).toBe(true)
  })

  it('does not treat has_dataset / READY as confirm-attach', () => {
    const candidate = snapshotAttachFields({
      has_dataset: true,
      upload_readiness: 'READY',
      dataset: { name: 'panel.csv', rows: 10, columns: ['y'] },
    })
    expect(readDataAttached(candidate)).toBe(false)
    expect(formalAttachApplies(candidate)).toBe(true)
    expect(shouldDivertToAttach(candidate)).toBe(true)
    expect(canOpenTable1(candidate)).toBe(false)
    expect(canOpenSpecConfirm(candidate)).toBe(false)
    expect(canSubmitDirection(candidate)).toBe(false)
    expect(canRunEstimate(candidate)).toBe(false)
  })

  it('opens Table 1 / spec / direction / estimate only after dataAttached', () => {
    const attached = snapshotAttachFields({
      dataAttached: true,
      upload_readiness: 'READY',
      has_dataset: true,
    })
    expect(shouldDivertToAttach(attached)).toBe(false)
    expect(canOpenTable1(attached)).toBe(true)
    expect(canOpenSpecConfirm(attached)).toBe(true)
    expect(canSubmitDirection(attached)).toBe(true)
    expect(canRunEstimate(attached)).toBe(true)
  })

  it('keeps PREWRITE-PAUSE surfaces closed when dataAttached is false', () => {
    const unattached = snapshotAttachFields({
      dataAttached: false,
      upload_readiness: 'READY',
    })
    expect(canOpenTable1(unattached)).toBe(false)
    expect(canOpenSpecConfirm(unattached)).toBe(false)
    expect(canRunEstimate(unattached)).toBe(false)
  })

  it('does not gate the Card teaching path', () => {
    const card = snapshotAttachFields({
      upload_readiness: 'READY',
      dataAttached: false,
      research: { teaching_case: 'card_1995' },
    })
    expect(formalAttachApplies(card)).toBe(false)
    expect(shouldDivertToAttach(card)).toBe(false)
    expect(canRunEstimate(card)).toBe(true)
  })

  it('leaves pre-upload-era legacy sessions on the existing path', () => {
    const legacy = snapshotAttachFields({
      exists: true,
      has_dataset: true,
    })
    expect(formalAttachApplies(legacy)).toBe(false)
    expect(shouldDivertToAttach(legacy)).toBe(false)
    expect(canSubmitDirection(legacy)).toBe(true)
  })

  it('applies when the product flag is projected even without upload_readiness', () => {
    const projected = snapshotAttachFields({ dataAttached: false })
    expect(formalAttachApplies(projected)).toBe(true)
    expect(shouldDivertToAttach(projected)).toBe(true)
    expect(canRunEstimate(projected)).toBe(false)
  })

  it('parses 409 upload_not_ready and session_busy', () => {
    const notReady = parseAdmissionConflict(409, {
      detail: { code: 'upload_not_ready' },
    })
    expect(notReady).toBeInstanceOf(AdmissionConflictError)
    expect(notReady?.code).toBe('upload_not_ready')

    const busy = parseAdmissionConflict(409, {
      detail: { code: 'session_busy', run_id: 'run-9' },
    })
    expect(busy?.code).toBe('session_busy')
    expect(busy?.runId).toBe('run-9')
    expect(busy?.message).toContain('HTTP 409')

    expect(parseAdmissionConflict(409, { detail: 'conflict' })).toBeNull()
    expect(parseAdmissionConflict(400, { detail: { code: 'session_busy' } })).toBeNull()
  })
})
