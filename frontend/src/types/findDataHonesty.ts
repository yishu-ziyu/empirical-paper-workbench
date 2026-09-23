/**
 * FIND-DATA honesty types (FD-FE-honesty).
 * docs/contracts/real-fetch-contract.md §2–§3. Not OpenAPI; backend honesty owns the public shape.
 */

export const FIND_DATA_SOURCE_KINDS = [
  'discovered',
  'teaching_fixture',
  'external_link',
  'fetched',
  'captain_local_real',
  'user_upload',
] as const

export type FindDataSourceKind = (typeof FIND_DATA_SOURCE_KINDS)[number]

export type FindDataFetchStatus = 'into_session' | 'link_only' | 'not_applicable'

export type FindDataFetchProjection = {
  status: FindDataFetchStatus
  session_path?: string | null
  reason?: string
}

/** DECIDE-7 candidate fields plus DECIDE-10 provenance. Missing source_kind fails closed. */
export type FindDataHonestyCandidate = {
  source_id: string
  title: string
  url_or_fixture: string
  license: string
  suggested_cols?: string[]
  design_fit?: Record<string, unknown>
  source_kind?: string | null
  /** Projection of captain_local_real. */
  source?: string
  fetch?: FindDataFetchProjection
}

export type FindDataHonestyInput = {
  candidates?: FindDataHonestyCandidate[]
  teaching_shelf?: FindDataHonestyCandidate[]
}

export const FIND_DATA_HONESTY_GROUPS = [
  'find_results',
  'external_link',
  'captain_local_real',
  'teaching_shelf',
  'user_upload',
  'withheld',
] as const

export type FindDataHonestyGroupId = (typeof FIND_DATA_HONESTY_GROUPS)[number]

export type FindDataHonestyLists = {
  findResults: FindDataHonestyCandidate[]
  externalLinks: FindDataHonestyCandidate[]
  captainLocalReal: FindDataHonestyCandidate[]
  teachingShelf: FindDataHonestyCandidate[]
  userUploads: FindDataHonestyCandidate[]
  withheld: FindDataHonestyCandidate[]
}

export const FIND_SUCCESS_KINDS: ReadonlySet<FindDataSourceKind> = new Set([
  'discovered',
  'fetched',
])
