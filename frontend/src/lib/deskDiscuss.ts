export type DeskOption = {
  id: string
  label: string
}

export type DeskTurn = {
  question: string
  answer: string
  id?: string
}

export type DeskCard = {
  reflection: string
  title: string
  heard: string[]
  comparison: string
  outcome: string
  question: string
  options: DeskOption[]
  explain: string
  ready: boolean
  source: 'llm' | 'heuristic'
}

const API_BASE = 'http://localhost:8000'

export async function transcribeDesk(blob: Blob): Promise<string> {
  const body = new FormData()
  body.append('file', blob, 'clip.webm')
  const resp = await fetch(`${API_BASE}/desk/transcribe`, { method: 'POST', body })
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  const data = await resp.json()
  return String(data.text || '').trim()
}

export async function speakDesk(text: string): Promise<HTMLAudioElement> {
  const resp = await fetch(`${API_BASE}/desk/speak`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  const blob = await resp.blob()
  const url = URL.createObjectURL(blob)
  const audio = new Audio(url)
  audio.addEventListener('ended', () => URL.revokeObjectURL(url), { once: true })
  return audio
}

export async function discussDesk(notes: string, turns: DeskTurn[] = []): Promise<DeskCard> {
  const resp = await fetch(`${API_BASE}/desk/discuss`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes, turns }),
  })
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  const data = await resp.json()
  return {
    reflection: String(data.reflection || ''),
    title: String(data.title || ''),
    heard: Array.isArray(data.heard) ? data.heard.map(String) : [],
    comparison: String(data.comparison || '还没定'),
    outcome: String(data.outcome || '还没定'),
    question: String(data.question || ''),
    explain: String(data.explain || ''),
    options: Array.isArray(data.options)
      ? data.options
          .filter((item: { id?: string; label?: string }) => item && item.label)
          .map((item: { id?: string; label?: string }) => ({
            id: String(item.id || ''),
            label: String(item.label),
          }))
      : [],
    ready: Boolean(data.ready),
    source: data.source === 'llm' ? 'llm' : 'heuristic',
  }
}
