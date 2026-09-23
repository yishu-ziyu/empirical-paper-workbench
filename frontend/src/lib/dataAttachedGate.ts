// DC-FE-gate: formal-path dataAttached product gate.
// Confirm-attach must succeed before Table 1, spec confirm, direction, and estimate.
// Fail closed: only snapshot dataAttached === true opens those surfaces.
// Card teaching_case is another product path and is not gated here.
// Attach-panel chrome (找 / 选 / 传 / 确认挂接) is DC-FE-step; this module only consumes the flag.

export type FormalAttachReadiness =
  | 'PROCESSING'
  | 'READY'
  | 'FAILED'
  | 'CANCELLED'

export type FormalAttachSnapshot = {
  dataAttached?: boolean | null
  upload_readiness?: FormalAttachReadiness | null
  research?: { teaching_case?: string | null } | null
}

export type FormalAttachSurface = 'table1' | 'spec' | 'direction' | 'estimate'

export type AdmissionConflictCode =
  | 'upload_not_ready'
  | 'session_busy'
  | 'data_not_attached'
  | 'design_unconfirmed'

export class AdmissionConflictError extends Error {
  readonly status = 409
  readonly code: AdmissionConflictCode
  readonly runId?: string

  constructor(code: AdmissionConflictCode, runId?: string) {
    super(runId ? `HTTP 409 ${code} ${runId}` : `HTTP 409 ${code}`)
    this.code = code
    this.runId = runId
  }
}

export function isFormalEconpaperPath(
  snapshot: Pick<FormalAttachSnapshot, 'research'>,
): boolean {
  return !snapshot.research?.teaching_case
}

export function readDataAttached(snapshot: Pick<FormalAttachSnapshot, 'dataAttached'>): boolean {
  return snapshot.dataAttached === true
}

export function dataAttachedFieldPresent(snapshot: object): boolean {
  return Object.prototype.hasOwnProperty.call(snapshot, 'dataAttached')
}

/**
 * The new confirm-attach gate applies to formal TITLE/TOPIC sessions that are
 * upload-era / classic-5-era (explicit upload_readiness) or already project
 * the product flag. Card and pre-upload-era legacy sessions stay on the
 * existing readiness / KTD7 path.
 */
export function formalAttachApplies(snapshot: FormalAttachSnapshot): boolean {
  if (!isFormalEconpaperPath(snapshot)) return false
  return snapshot.upload_readiness != null || dataAttachedFieldPresent(snapshot)
}

export function shouldDivertToAttach(snapshot: FormalAttachSnapshot): boolean {
  return formalAttachApplies(snapshot) && !readDataAttached(snapshot)
}

export function canOpenFormalSurface(
  _surface: FormalAttachSurface,
  snapshot: FormalAttachSnapshot,
): boolean {
  return !shouldDivertToAttach(snapshot)
}

export function canOpenTable1(snapshot: FormalAttachSnapshot): boolean {
  return canOpenFormalSurface('table1', snapshot)
}

export function canOpenSpecConfirm(snapshot: FormalAttachSnapshot): boolean {
  return canOpenFormalSurface('spec', snapshot)
}

export function canSubmitDirection(snapshot: FormalAttachSnapshot): boolean {
  return canOpenFormalSurface('direction', snapshot)
}

export function canRunEstimate(snapshot: FormalAttachSnapshot): boolean {
  return canOpenFormalSurface('estimate', snapshot)
}

export function snapshotAttachFields(data: object): FormalAttachSnapshot {
  const record = data as FormalAttachSnapshot & { research?: { teaching_case?: string | null } }
  const fields: FormalAttachSnapshot = {
    upload_readiness: record.upload_readiness,
    research: record.research,
  }
  if (dataAttachedFieldPresent(data)) {
    fields.dataAttached = record.dataAttached === true
  }
  return fields
}

function conflictCode(value: unknown): AdmissionConflictCode | null {
  if (
    value === 'upload_not_ready' ||
    value === 'session_busy' ||
    value === 'data_not_attached' ||
    value === 'design_unconfirmed'
  ) {
    return value
  }
  return null
}

function readConflictRunId(value: unknown): string | undefined {
  if (!value || typeof value !== 'object') return undefined
  const runId = (value as { run_id?: unknown }).run_id
  return typeof runId === 'string' && runId ? runId : undefined
}

/** Consume backend 409 upload_not_ready / session_busy without inventing new codes. */
export function parseAdmissionConflict(
  status: number,
  payload: unknown,
): AdmissionConflictError | null {
  if (status !== 409) return null
  const body = payload && typeof payload === 'object' ? (payload as Record<string, unknown>) : null
  const detail = body?.detail
  const fromDetail =
    detail && typeof detail === 'object'
      ? conflictCode((detail as { code?: unknown }).code)
      : null
  const code = fromDetail || conflictCode(body?.code) || conflictCode(detail)
  if (!code) return null
  return new AdmissionConflictError(code, readConflictRunId(detail) ?? readConflictRunId(body))
}
