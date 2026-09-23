// ── Formal confirmation commands (FORMAL-CONFIRMATION-CHAIN-2) ──────
// The commands that propose/approve a design, bind data, record a prewrite
// confirmation or start the estimate are the formal chain's write surface.
// They all need the same two facts, so they live here instead of being
// copied into every workspace branch:
//
// - **ownership** (R4): the session id, the session epoch and the version of
//   the object being approved. A command captures them before its first
//   await and re-checks them before applying anything, so a response that
//   arrives after the user switched session — or after the candidate was
//   re-proposed / replaced in the same session — is dropped.
// - **a delivery credential** (review §3): one intention keeps one
//   `Idempotency-Key` until it completes, so retrying after a lost response
//   replays the same intention (same run, no second record) instead of
//   creating a new one.
//
// This module never talks to the network and never renders: the workspace
// keeps the snapshot, `waitForTrackedRun` and React state.

import { AdmissionConflictError, type AdmissionConflictCode } from './dataAttachedGate'
import { RunRequestError } from './runEvents'
import type { components } from '../types/api'

export type ConfirmationTarget = components['schemas']['ConfirmationTarget']

export type ConfirmationKind =
  | 'design_propose'
  | 'design_confirm'
  | 'attach'
  | 'attach_confirm'
  | 'prewrite_record'
  | 'prewrite_estimate'

/** #40 tri-state permission; `unknown` is neither a pass nor a forbid. */
export type ContinuePermission = 'allow' | 'confirm' | 'forbid' | 'unknown'

/** The one confirmation step the page is currently waiting for. */
export type PrewriteStep = 'sample' | 'setting' | 'risk' | 'ready' | 'forbidden'

/**
 * A definite refusal that names its reason (HTTP 4xx, `detail.code`).
 * Unknown deliveries (network failures, 408, 5xx) stay plain errors so the
 * caller has to read the server state back before judging them.
 */
export class CommandRefusalError extends RunRequestError {
  readonly code: string | null

  constructor(status: number, code: string | null) {
    super(status)
    this.code = code
  }
}

export function readDetailCode(payload: unknown): string | null {
  if (!payload || typeof payload !== 'object') return null
  const body = payload as Record<string, unknown>
  const detail = body.detail
  if (detail && typeof detail === 'object') {
    const code = (detail as Record<string, unknown>).code
    if (typeof code === 'string' && code) return code
  }
  if (typeof detail === 'string' && detail) return detail
  const code = body.code
  return typeof code === 'string' && code ? code : null
}

/**
 * Definite refusal versus unknown delivery. A refusal may be reported as such;
 * an unknown delivery must be resolved by reading the server back.
 */
export function classifyCommandFailure(error: unknown): 'refused' | 'unknown' {
  if (error instanceof AdmissionConflictError) return 'refused'
  if (error instanceof RunRequestError) {
    const { status } = error
    if (status >= 400 && status < 500 && status !== 408) return 'refused'
    return 'unknown'
  }
  return 'unknown'
}

const REFUSAL_KEYS: Record<string, string> = {
  confirmation_target_required: 'prewrite.refusedStale',
  confirmation_target_mismatch: 'prewrite.refusedStale',
  confirmations_stale: 'prewrite.refusedStale',
  idempotency_conflict: 'prewrite.refusedStale',
  preview_not_ready: 'prewrite.refusedPreviewNotReady',
  sample_confirmation_required: 'prewrite.refusedSampleFirst',
  confirmation_stale: 'prewrite.refusedStale',
  risk_confirmation_required: 'prewrite.refusedRiskRequired',
  risk_confirmation_not_applicable: 'prewrite.refusedRiskNotApplicable',
  estimate_blocked: 'prewrite.refusedBlocked',
  prewrite_not_ready: 'prewrite.refusedNotReady',
  identification_blocked: 'prewrite.refusedIdentification',
  confirms_incomplete: 'prewrite.startNeedBoth',
  session_busy: 'prewrite.refusedBusy',
  upload_not_ready: 'attach.confirmFailedNotReady',
  data_not_attached: 'app.directionBlockedNotAttached',
  design_unconfirmed: 'app.directionDesignUnconfirmed',
  design_revision_mismatch: 'design.revisionMismatch',
  design_not_proposed: 'designProposal.notProposed',
  design_execution_mismatch: 'app.directionDesignMismatch',
}

/**
 * i18n key for a definite refusal, or null when the failure gave no reason
 * (an unknown delivery must not be presented as a refusal).
 */
export function refusalMessageKey(error: unknown): string | null {
  if (error instanceof AdmissionConflictError) {
    return REFUSAL_KEYS[error.code as AdmissionConflictCode] ?? null
  }
  if (error instanceof CommandRefusalError) {
    return error.code ? REFUSAL_KEYS[error.code] ?? null : null
  }
  if (error instanceof RunRequestError) {
    if (classifyCommandFailure(error) !== 'refused') return null
    return error.status === 429 ? 'prewrite.refusedBusy' : null
  }
  return null
}

export function readContinuePermission(permissions: unknown): ContinuePermission {
  if (!permissions || typeof permissions !== 'object') return 'unknown'
  const raw = (permissions as Record<string, unknown>).continue_to_estimate
  if (raw === 'allow' || raw === 'confirm' || raw === 'forbid') return raw
  return 'unknown'
}

export function prewritePendingStep(input: {
  table1Confirmed: boolean
  specConfirmed: boolean
  continuePermission: ContinuePermission
  riskConfirmed: boolean
}): PrewriteStep {
  if (input.continuePermission === 'forbid') return 'forbidden'
  if (!input.table1Confirmed) return 'sample'
  if (!input.specConfirmed) return 'setting'
  if (input.continuePermission === 'confirm' && !input.riskConfirmed) return 'risk'
  return 'ready'
}

// ── Object versions an approval names ───────────────────────────────

export type DesignRevisionSource = { revision?: string | null } | null | undefined
export type DatasetVersionSource =
  | { version?: string | null }
  | null
  | undefined

function trimmed(value: unknown): string | null {
  return typeof value === 'string' && value.trim() ? value.trim() : null
}

/** The revision of a design draft. Confirming it keeps the same revision. */
export function designRevisionOf(design: DesignRevisionSource): string | null {
  if (!design || typeof design !== 'object') return null
  return trimmed(design.revision)
}

export function datasetSignatureOf(dataset: DatasetVersionSource): string | null {
  if (!dataset || typeof dataset !== 'object') return null
  return trimmed(dataset.version)
}

/**
 * The version of the sample/setting preview an approval is about: the design
 * revision, the data it was generated from and the equation shown. A moved
 * preview leaves the approvals behind.
 */
export function previewVersionOf(input: {
  targets: ConfirmationTarget | null | undefined
}): string | null {
  if (!input.targets?.preview) return null
  const { design, dataset, preview, diagnosis } = input.targets
  return JSON.stringify([design, dataset, preview, diagnosis])
}

/** Stable intention signature for attaching one chosen file. */
export async function attachIntentSignature(file: File): Promise<string> {
  const bytes = typeof file.arrayBuffer === 'function'
    ? await file.arrayBuffer()
    : await new Promise<ArrayBuffer>((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result as ArrayBuffer)
        reader.onerror = () => reject(reader.error)
        reader.readAsArrayBuffer(file)
      })
  const hash = await crypto.subtle.digest('SHA-256', bytes)
  const hex = Array.from(new Uint8Array(hash), (byte) => byte.toString(16).padStart(2, '0')).join('')
  return `attach:${file.name}:${hex}`
}

// ── Ownership registry ──────────────────────────────────────────────

export interface ConfirmationOwnership {
  readonly kind: ConfirmationKind
  readonly sessionId: string
  readonly epoch: number
  readonly operation: symbol
  readonly version: string | null
}

interface Flight {
  sessionId: string
  epoch: number
  operation: symbol
  version: string | null
  versionOf: () => string | null
}

interface BeginArgs {
  kind: ConfirmationKind
  sessionId: string
  /** Captured version, or a live getter re-read on every check. */
  version: string | null | (() => string | null)
  /** A newer candidate (another attach) supersedes the previous flight. */
  takeover?: boolean
}

interface IntentArgs {
  sessionId: string
  kind: ConfirmationKind
  signature: string
}

export interface ConfirmationRegistry {
  begin(args: BeginArgs): ConfirmationOwnership | null
  /** Owned by this session epoch and still the active operation of its kind. */
  isOwned(ownership: ConfirmationOwnership): boolean
  /** Owned *and* the object version it was started for has not moved. */
  isCurrent(ownership: ConfirmationOwnership): boolean
  finish(ownership: ConfirmationOwnership): void
  isBusy(kind: ConfirmationKind): boolean
  invalidateAll(): void
  invalidateKind(kind: ConfirmationKind): void
  intentKey(args: IntentArgs): string
  clearIntent(args: { sessionId: string; kind: ConfirmationKind; signature?: string }): void
  clearAllIntents(): void
}

const INTENT_KEY_PREFIX = 'econpaper_confirmation_intent'
const INTENT_RING_LIMIT = 8

function defaultStorage(): Storage | null {
  try {
    return typeof sessionStorage === 'undefined' ? null : sessionStorage
  } catch {
    return null
  }
}

function readRing(store: Storage | null, storageKey: string): Record<string, string> {
  if (!store) return {}
  const raw = store.getItem(storageKey)
  if (!raw) return {}
  try {
    const parsed = JSON.parse(raw)
    return parsed && typeof parsed === 'object' ? (parsed as Record<string, string>) : {}
  } catch {
    return {}
  }
}

/**
 * Delivery credentials for the confirmation commands, scoped to the browser
 * session so a reload keeps the same intention (§ C6/C7 recovery).
 */
export function createConfirmationRegistry(storage?: Storage): ConfirmationRegistry {
  const store = storage === undefined ? defaultStorage() : storage
  const flights = new Map<ConfirmationKind, Flight>()
  let epoch = 0

  const storageKeyFor = (sessionId: string, kind: ConfirmationKind) =>
    `${INTENT_KEY_PREFIX}:${sessionId}:${kind}`

  return {
    begin({ kind, sessionId, version, takeover = false }) {
      if (flights.has(kind) && !takeover) return null
      const versionOf = typeof version === 'function' ? version : () => version
      const flight: Flight = {
        sessionId,
        epoch,
        operation: Symbol(kind),
        version: versionOf(),
        versionOf,
      }
      flights.set(kind, flight)
      return {
        kind,
        sessionId,
        epoch: flight.epoch,
        operation: flight.operation,
        version: flight.version,
      }
    },

    isOwned(ownership) {
      const flight = flights.get(ownership.kind)
      if (!flight || flight.operation !== ownership.operation) return false
      return flight.epoch === epoch && flight.sessionId === ownership.sessionId
    },

    isCurrent(ownership) {
      const flight = flights.get(ownership.kind)
      if (!flight || flight.operation !== ownership.operation) return false
      if (flight.epoch !== epoch || flight.sessionId !== ownership.sessionId) return false
      return flight.version === flight.versionOf()
    },

    finish(ownership) {
      const flight = flights.get(ownership.kind)
      if (flight?.operation === ownership.operation) flights.delete(ownership.kind)
    },

    isBusy(kind) {
      return flights.has(kind)
    },

    invalidateAll() {
      epoch += 1
      flights.clear()
    },

    invalidateKind(kind) {
      flights.delete(kind)
    },

    intentKey({ sessionId, kind, signature }) {
      const storageKey = storageKeyFor(sessionId, kind)
      const ring = readRing(store, storageKey)
      const existing = ring[signature]
      if (typeof existing === 'string' && existing) return existing
      const key = crypto.randomUUID()
      const entries = Object.entries({ ...ring, [signature]: key }).slice(-INTENT_RING_LIMIT)
      try {
        store?.setItem(storageKey, JSON.stringify(Object.fromEntries(entries)))
      } catch {
        /* a full or unavailable store only costs the replay credential */
      }
      return key
    },

    clearIntent({ sessionId, kind, signature }) {
      const storageKey = storageKeyFor(sessionId, kind)
      if (signature === undefined) {
        store?.removeItem(storageKey)
        return
      }
      const ring = readRing(store, storageKey)
      if (!(signature in ring)) return
      delete ring[signature]
      try {
        if (Object.keys(ring).length === 0) store?.removeItem(storageKey)
        else store?.setItem(storageKey, JSON.stringify(ring))
      } catch {
        /* ignore */
      }
    },

    clearAllIntents() {
      if (!store) return
      for (const existing of Object.keys(store)) {
        if (existing.startsWith(`${INTENT_KEY_PREFIX}:`)) store.removeItem(existing)
      }
    },
  }
}
