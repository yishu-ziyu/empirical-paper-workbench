/**
 * FD-FE-honesty grouping. Fixtures and toys never enter find-success lists.
 * Tiny names below are DATA-RIGOR bans (synthetic / teaching toys), not found data.
 */

import type {
  FindDataHonestyCandidate,
  FindDataHonestyInput,
  FindDataHonestyLists,
  FindDataSourceKind,
} from '../types/findDataHonesty'
import { FIND_DATA_SOURCE_KINDS, FIND_SUCCESS_KINDS } from '../types/findDataHonesty'

const SOURCE_KIND_SET: ReadonlySet<string> = new Set(FIND_DATA_SOURCE_KINDS)

/** DATA-RIGOR banned found-data filenames (synthetic; tests-only mentions). */
const BANNED_TOY_BASENAMES = new Set([
  'minimum_wage.csv',
  'course-panel.csv',
  'sanitized_sample.csv',
  'sample_wage.csv',
  'sample_panel_mini.csv',
  'wage_panel.csv',
])

const CLASSIC_CATALOG_IDS = new Set([
  'ck1994',
  'ck1994_long',
  'minimum-wage-employment',
  'barro1991_growth',
  'schooling-wages',
  'wage1',
])

const LAUNDERED_KINDS = new Set([
  'builtin_match',
  'recommended',
  'classic_found',
])

const CAPTAIN_SOURCE = 'captain-local-real'

export const FIND_DATA_FORBIDDEN_FOUND_COPY = [
  '找到了数据',
  '为你找到',
  'discovered dataset',
  'matched your study',
  'recommended data',
  'we found',
] as const

export function basenameOf(pathOrUrl: string): string {
  const trimmed = pathOrUrl.trim().split(/[?#]/)[0]
  const slash = trimmed.replace(/\\/g, '/')
  const parts = slash.split('/')
  return (parts[parts.length - 1] || '').toLowerCase()
}

export function isBannedToyCandidate(candidate: FindDataHonestyCandidate): boolean {
  const hay = `${candidate.source_id} ${candidate.url_or_fixture} ${candidate.title}`.toLowerCase()
  for (const name of BANNED_TOY_BASENAMES) {
    if (hay.includes(name)) return true
  }
  return BANNED_TOY_BASENAMES.has(basenameOf(candidate.url_or_fixture))
}

export function isInRepoFixtureSignal(candidate: FindDataHonestyCandidate): boolean {
  const id = candidate.source_id.trim()
  const url = candidate.url_or_fixture.replace(/\\/g, '/')
  if (id.startsWith('classic-5:')) return true
  if (CLASSIC_CATALOG_IDS.has(id) || CLASSIC_CATALOG_IDS.has(id.replace(/^classic-5:/, ''))) {
    return true
  }
  if (url.startsWith('fixtures/') || url.includes('/fixtures/')) return true
  if (url.includes('classic-5/') || url.includes('classic-5:')) return true
  return false
}

export function isCaptainLocalReal(candidate: FindDataHonestyCandidate): boolean {
  return (
    candidate.source_kind === 'captain_local_real' || candidate.source === CAPTAIN_SOURCE
  )
}

export function isKnownSourceKind(kind: string | null | undefined): kind is FindDataSourceKind {
  return typeof kind === 'string' && SOURCE_KIND_SET.has(kind)
}

export function isFindSuccessKind(kind: string | null | undefined): boolean {
  return isKnownSourceKind(kind) && FIND_SUCCESS_KINDS.has(kind)
}

function dedupeAppend(
  list: FindDataHonestyCandidate[],
  seen: Set<string>,
  row: FindDataHonestyCandidate,
) {
  if (seen.has(row.source_id)) return
  seen.add(row.source_id)
  list.push(row)
}

/**
 * Split candidates into honest regions. Missing kind, toys, and fixture-as-found
 * never land in findResults.
 */
export function groupFindDataHonesty(input: FindDataHonestyInput): FindDataHonestyLists {
  const lists: FindDataHonestyLists = {
    findResults: [],
    externalLinks: [],
    captainLocalReal: [],
    teachingShelf: [],
    userUploads: [],
    withheld: [],
  }
  const seen = new Set<string>()

  const place = (row: FindDataHonestyCandidate, fromShelf: boolean) => {
    if (isBannedToyCandidate(row)) {
      dedupeAppend(lists.withheld, seen, row)
      return
    }
    if (isCaptainLocalReal(row)) {
      dedupeAppend(lists.captainLocalReal, seen, row)
      return
    }
    const kind = row.source_kind
    const fixture = isInRepoFixtureSignal(row) || kind === 'teaching_fixture' || fromShelf
    if (fixture) {
      dedupeAppend(lists.teachingShelf, seen, row)
      return
    }
    if (!isKnownSourceKind(kind) || LAUNDERED_KINDS.has(String(kind))) {
      dedupeAppend(lists.withheld, seen, row)
      return
    }
    if (kind === 'external_link') {
      dedupeAppend(lists.externalLinks, seen, row)
      return
    }
    if (kind === 'user_upload') {
      dedupeAppend(lists.userUploads, seen, row)
      return
    }
    if (kind === 'discovered' || kind === 'fetched') {
      dedupeAppend(lists.findResults, seen, row)
      return
    }
    dedupeAppend(lists.withheld, seen, row)
  }

  for (const row of input.candidates ?? []) {
    place(row, false)
  }
  for (const row of input.teaching_shelf ?? []) {
    place(row, true)
  }

  return lists
}

export function honestyKindCopyKey(
  kind: string | null | undefined,
): 'findData.kind.discovered' | 'findData.kind.fetched' | 'findData.kind.externalLink' | 'findData.kind.teaching' | 'findData.kind.captainLocalReal' | 'findData.kind.userUpload' | null {
  switch (kind) {
    case 'discovered':
      return 'findData.kind.discovered'
    case 'fetched':
      return 'findData.kind.fetched'
    case 'external_link':
      return 'findData.kind.externalLink'
    case 'teaching_fixture':
      return 'findData.kind.teaching'
    case 'captain_local_real':
      return 'findData.kind.captainLocalReal'
    case 'user_upload':
      return 'findData.kind.userUpload'
    default:
      return null
  }
}

export function displayKindForGroup(
  row: FindDataHonestyCandidate,
  group: keyof FindDataHonestyLists,
): string | null {
  if (group === 'teachingShelf') return 'teaching_fixture'
  if (group === 'captainLocalReal') return 'captain_local_real'
  if (group === 'externalLinks') return 'external_link'
  if (group === 'userUploads') return 'user_upload'
  if (group === 'findResults') {
    return row.source_kind === 'fetched' ? 'fetched' : 'discovered'
  }
  return null
}
