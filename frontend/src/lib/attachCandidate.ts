/** TITLE/TOPIC attach-panel candidate. Pick/upload is not confirm-attach. */

export type AttachSource = 'classic-5' | 'file'

export type AttachCandidate = {
  source: AttachSource
  id: string
  label: string
}

export function candidateKey(candidate: AttachCandidate): string {
  return `${candidate.source}:${candidate.id}`
}

export function fileCandidate(fileName: string): AttachCandidate {
  return { source: 'file', id: fileName, label: fileName }
}

export function isIngestBlocking(
  readiness: 'READY' | 'PROCESSING' | 'FAILED' | 'CANCELLED' | undefined,
): boolean {
  return readiness === 'PROCESSING' || readiness === 'FAILED' || readiness === 'CANCELLED'
}
