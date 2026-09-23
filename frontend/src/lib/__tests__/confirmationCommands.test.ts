import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  attachIntentSignature,
  classifyCommandFailure,
  createConfirmationRegistry,
  designRevisionOf,
  prewritePendingStep,
  previewVersionOf,
  readContinuePermission,
} from '../confirmationCommands'
import { AdmissionConflictError } from '../dataAttachedGate'
import { RunRequestError } from '../runEvents'

const DESIGN = {
  status: 'draft',
  confirmed: false,
  proposed_at: '2026-09-17T10:00:00Z',
  source: { title: '教育年限与工资', question: '' },
}

it('distinguishes different bytes even when filename, size and timestamp match', async () => {
  const a = new File(['y,x\n1,2\n'], 'same.csv', { lastModified: 42 })
  const b = new File(['y,x\n9,2\n'], 'same.csv', { lastModified: 42 })
  const again = new File(['y,x\n1,2\n'], 'same.csv', { lastModified: 43 })
  expect(a.size).toBe(b.size)
  expect(await attachIntentSignature(a)).not.toBe(await attachIntentSignature(b))
  expect(await attachIntentSignature(a)).toBe(await attachIntentSignature(again))
})

describe('confirmationCommands ownership registry', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('is single flight per command kind', () => {
    const registry = createConfirmationRegistry()
    const first = registry.begin({
      kind: 'design_confirm',
      sessionId: 'A',
      version: null,
    })
    expect(first).not.toBeNull()
    expect(registry.isBusy('design_confirm')).toBe(true)
    expect(
      registry.begin({ kind: 'design_confirm', sessionId: 'A', version: null }),
    ).toBeNull()
    // A different kind is not blocked by another kind's flight.
    expect(
      registry.begin({ kind: 'attach_confirm', sessionId: 'A', version: null }),
    ).not.toBeNull()
    registry.finish(first!)
    expect(registry.isBusy('design_confirm')).toBe(false)
  })

  it('separates ownership from the object version it approves', () => {
    const registry = createConfirmationRegistry()
    let revision = 'draft-A'
    const ownership = registry.begin({
      kind: 'prewrite_estimate',
      sessionId: 'A',
      version: () => revision,
    })!
    revision = 'draft-B'
    // The version moved: the approval claim is stale...
    expect(registry.isCurrent(ownership)).toBe(false)
    // ...but the command still belongs to this session epoch, so a durable run
    // it already queued may still be followed.
    expect(registry.isOwned(ownership)).toBe(true)
    registry.invalidateAll()
    expect(registry.isOwned(ownership)).toBe(false)
  })

  it('lets a newer candidate flight take over an in-flight attach', () => {
    const registry = createConfirmationRegistry()
    const first = registry.begin({ kind: 'attach', sessionId: 'A', version: null })!
    const second = registry.begin({
      kind: 'attach',
      sessionId: 'A',
      version: null,
      takeover: true,
    })!
    expect(second).not.toBeNull()
    expect(registry.isCurrent(first)).toBe(false)
    expect(registry.isCurrent(second)).toBe(true)
  })

  it('drops ownership on session switch (epoch bump)', () => {
    const registry = createConfirmationRegistry()
    const ownership = registry.begin({
      kind: 'design_confirm',
      sessionId: 'A',
      version: null,
    })!
    expect(registry.isCurrent(ownership)).toBe(true)
    registry.invalidateAll()
    expect(registry.isCurrent(ownership)).toBe(false)
    expect(registry.isBusy('design_confirm')).toBe(false)
    // A new session starts from a clean slate.
    expect(
      registry.begin({ kind: 'design_confirm', sessionId: 'B', version: null }),
    ).not.toBeNull()
  })

  it('drops ownership when the live object version moved within the same session', () => {
    const registry = createConfirmationRegistry()
    let revision = 'draft-A'
    const ownership = registry.begin({
      kind: 'design_confirm',
      sessionId: 'A',
      version: () => revision,
    })!
    expect(ownership.version).toBe('draft-A')
    expect(registry.isCurrent(ownership)).toBe(true)
    revision = 'draft-B'
    expect(registry.isCurrent(ownership)).toBe(false)
  })

  it('invalidates one kind without touching the others', () => {
    const registry = createConfirmationRegistry()
    const record = registry.begin({
      kind: 'prewrite_record',
      sessionId: 'A',
      version: null,
    })!
    const estimate = registry.begin({
      kind: 'prewrite_estimate',
      sessionId: 'A',
      version: null,
    })!
    registry.invalidateKind('prewrite_record')
    expect(registry.isCurrent(record)).toBe(false)
    expect(registry.isCurrent(estimate)).toBe(true)
  })
})

describe('confirmationCommands delivery credentials', () => {
  afterEach(() => {
    sessionStorage.clear()
    vi.restoreAllMocks()
  })

  it('reuses one idempotency key for the same intention until it completes', () => {
    const randomUUID = vi
      .spyOn(crypto, 'randomUUID')
      .mockReturnValueOnce('11111111-1111-4111-8111-111111111111' as `${string}-${string}-${string}-${string}-${string}`)
      .mockReturnValueOnce('22222222-2222-4222-8222-222222222222' as `${string}-${string}-${string}-${string}-${string}`)
      .mockReturnValue('99999999-9999-4999-8999-999999999999' as `${string}-${string}-${string}-${string}-${string}`)
    const registry = createConfirmationRegistry()

    const first = registry.intentKey({
      sessionId: 'A',
      kind: 'prewrite_estimate',
      signature: 'preview-1',
    })
    const retry = registry.intentKey({
      sessionId: 'A',
      kind: 'prewrite_estimate',
      signature: 'preview-1',
    })
    expect(retry).toBe(first)
    expect(first).toBe('11111111-1111-4111-8111-111111111111')

    // A different intention (new preview) gets a new credential.
    const next = registry.intentKey({
      sessionId: 'A',
      kind: 'prewrite_estimate',
      signature: 'preview-2',
    })
    expect(next).not.toBe(first)

    // After completion the next intention mints a fresh key.
    registry.clearIntent({ sessionId: 'A', kind: 'prewrite_estimate' })
    const afterCompletion = registry.intentKey({
      sessionId: 'A',
      kind: 'prewrite_estimate',
      signature: 'preview-2',
    })
    expect(afterCompletion).not.toBe(next)
    randomUUID.mockRestore()
  })

  it('survives a reload (credentials live in session storage)', () => {
    const registry = createConfirmationRegistry()
    const key = registry.intentKey({
      sessionId: 'A',
      kind: 'attach',
      signature: 'file-1',
    })
    const reloaded = createConfirmationRegistry()
    expect(
      reloaded.intentKey({ sessionId: 'A', kind: 'attach', signature: 'file-1' }),
    ).toBe(key)
    // Another session never borrows it.
    expect(
      reloaded.intentKey({ sessionId: 'B', kind: 'attach', signature: 'file-1' }),
    ).not.toBe(key)
  })

  it('clears every credential on request', () => {
    const registry = createConfirmationRegistry()
    const first = registry.intentKey({
      sessionId: 'A',
      kind: 'attach',
      signature: 'file-1',
    })
    registry.clearAllIntents()
    expect(
      registry.intentKey({ sessionId: 'A', kind: 'attach', signature: 'file-1' }),
    ).not.toBe(first)
  })
})

describe('confirmationCommands failure classification', () => {
  it('separates a definite refusal from an unknown delivery', () => {
    expect(classifyCommandFailure(new AdmissionConflictError('session_busy'))).toBe('refused')
    expect(classifyCommandFailure(new RunRequestError(409))).toBe('refused')
    expect(classifyCommandFailure(new RunRequestError(422))).toBe('refused')
    expect(classifyCommandFailure(new RunRequestError(429))).toBe('refused')
    expect(classifyCommandFailure(new RunRequestError(408))).toBe('unknown')
    expect(classifyCommandFailure(new RunRequestError(500))).toBe('unknown')
    expect(classifyCommandFailure(new TypeError('response lost'))).toBe('unknown')
    expect(classifyCommandFailure(new DOMException('aborted', 'AbortError'))).toBe('unknown')
  })
})

describe('confirmationCommands permission + pending fact', () => {
  it('reads the #40 tri-state without turning unknown into a pass', () => {
    expect(readContinuePermission({ continue_to_estimate: 'allow' })).toBe('allow')
    expect(readContinuePermission({ continue_to_estimate: 'confirm' })).toBe('confirm')
    expect(readContinuePermission({ continue_to_estimate: 'forbid' })).toBe('forbid')
    expect(readContinuePermission({})).toBe('unknown')
    expect(readContinuePermission(null)).toBe('unknown')
    expect(readContinuePermission(undefined)).toBe('unknown')
    expect(readContinuePermission({ continue_to_estimate: null })).toBe('unknown')
    expect(readContinuePermission({ continue_to_estimate: 'maybe' })).toBe('unknown')
  })

  it('names the one pending confirmation step the page must show', () => {
    const base = {
      table1Confirmed: false,
      specConfirmed: false,
      continuePermission: 'allow' as const,
      riskConfirmed: false,
    }
    expect(prewritePendingStep(base)).toBe('sample')
    expect(prewritePendingStep({ ...base, table1Confirmed: true })).toBe('setting')
    expect(
      prewritePendingStep({ ...base, table1Confirmed: true, specConfirmed: true }),
    ).toBe('ready')
    expect(
      prewritePendingStep({
        ...base,
        table1Confirmed: true,
        specConfirmed: true,
        continuePermission: 'confirm',
      }),
    ).toBe('risk')
    expect(
      prewritePendingStep({
        ...base,
        table1Confirmed: true,
        specConfirmed: true,
        continuePermission: 'confirm',
        riskConfirmed: true,
      }),
    ).toBe('ready')
    expect(
      prewritePendingStep({
        ...base,
        table1Confirmed: true,
        specConfirmed: true,
        continuePermission: 'forbid',
      }),
    ).toBe('forbidden')
    // Unknown permission never adds a gate of its own and never counts as passed.
    expect(prewritePendingStep({ ...base, continuePermission: 'unknown' })).toBe('sample')
  })

  it('uses server-issued identities, never names, dimensions or a clock', () => {
    expect(designRevisionOf({ ...DESIGN, revision: 'design-a' })).toBe('design-a')
    expect(designRevisionOf(null)).toBeNull()
    expect(designRevisionOf({ source: { title: 'x' } } as never)).toBeNull()
    expect(designRevisionOf({ proposed_at: DESIGN.proposed_at } as never)).toBeNull()
    const targets = { design: 'design-a', dataset: 'bytes-a', preview: 'preview-a', diagnosis: 'diag-a' }
    const first = previewVersionOf({ targets })
    const again = previewVersionOf({ targets: { ...targets } })
    const movedData = previewVersionOf({ targets: { ...targets, dataset: 'bytes-b' } })
    const movedDesign = previewVersionOf({ targets: { ...targets, design: 'design-b' } })
    expect(first).toBe(again)
    expect(first).not.toBe(movedData)
    expect(first).not.toBe(movedDesign)
    expect(first).not.toBe(previewVersionOf({ targets: { ...targets, diagnosis: 'diag-b' } }))
    expect(previewVersionOf({ targets: null })).toBeNull()
  })
})
