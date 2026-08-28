import { createElement, type ReactNode } from 'react'

const CAPTION_RE = /^(表|Table)\s*\d*\s*[—–-]/
const NOTES_RE = /^(Notes?:|注[：:])/i
const EQ_OPEN_RE = /^\\begin\{equation\*?\}/
const EQ_CLOSE_RE = /\\end\{equation\*?\}$/

export const journalEqBox =
  'my-6 flex items-center gap-3 rounded-lg bg-[#f3f3f3] px-4 py-3.5 sm:px-6'
export const journalEqMath =
  'min-w-0 flex-1 overflow-x-auto text-center font-mono text-[14.5px] leading-8 text-ink'
export const journalEqNum = 'shrink-0 font-serif text-[15px] tabular-nums text-ink/70'
export const journalCaption = 'mb-2 font-sans text-[13px] font-semibold tracking-tight text-ink'
export const journalTable =
  'w-full border-collapse text-left text-[13.5px] text-ink'
export const journalTheadRow = 'border-t-[2.5px] border-b border-ink'
export const journalTh = 'py-2 pr-3 font-sans text-[12.5px] font-semibold'
export const journalTd = 'py-2 pr-3'
export const journalNotes = 'mt-2 font-serif text-[12px] leading-6 text-ink/65'

export function JournalEquation({
  math,
  number,
}: {
  math: ReactNode
  number?: number | string | null
}) {
  return (
    <div data-testid="paper-equation" className={journalEqBox}>
      <div className={journalEqMath}>{math}</div>
      {number != null && number !== '' ? (
        <span className={journalEqNum}>({number})</span>
      ) : null}
    </div>
  )
}

function inlineNodes(text: string, keyPrefix: string): ReactNode[] {
  const nodes: ReactNode[] = []
  const pattern = /(\$[^$\n]+\$|\*\*[^*]+\*\*)/g
  let last = 0
  let match: RegExpExecArray | null
  let i = 0
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > last) {
      nodes.push(text.slice(last, match.index))
    }
    const token = match[0]
    if (token.startsWith('$')) {
      nodes.push(
        <span key={`${keyPrefix}-math-${i}`} className="font-mono text-[0.92em]">
          {token.slice(1, -1)}
        </span>,
      )
    } else {
      nodes.push(
        <strong key={`${keyPrefix}-b-${i}`}>{token.slice(2, -2)}</strong>,
      )
    }
    last = match.index + token.length
    i += 1
  }
  if (last < text.length) nodes.push(text.slice(last))
  return nodes
}

function isPipeRow(line: string): boolean {
  const t = line.trim()
  if (!t.includes('|')) return false
  return (t.match(/\|/g) || []).length >= 2
}

function isSeparatorRow(line: string): boolean {
  const cells = splitPipe(line)
  return cells.length > 0 && cells.every((cell) => /^:?-+:?$/.test(cell))
}

function splitPipe(line: string): string[] {
  let t = line.trim()
  if (t.startsWith('|')) t = t.slice(1)
  if (t.endsWith('|')) t = t.slice(0, -1)
  return t.split('|').map((cell) => cell.trim())
}

function headingClass(level: number): string {
  if (level === 1) return 'mb-4 mt-1 font-serif text-[1.7rem] font-semibold leading-snug'
  if (level === 2) return 'mb-3 mt-8 font-serif text-[1.35rem] font-semibold leading-snug'
  return 'mb-2 mt-6 font-serif text-[1.12rem] font-semibold leading-snug'
}

function stripDisplayMath(raw: string): { math: string; numbered: boolean } {
  let text = raw.trim()
  let numbered = true
  if (text.startsWith('$$') && text.endsWith('$$') && text.length >= 4) {
    return { math: text.slice(2, -2).trim(), numbered: true }
  }
  if (text.startsWith('\\[') && text.endsWith('\\]')) {
    return { math: text.slice(2, -2).trim(), numbered: true }
  }
  if (EQ_OPEN_RE.test(text)) {
    numbered = !text.startsWith('\\begin{equation*}')
    text = text.replace(EQ_OPEN_RE, '').replace(EQ_CLOSE_RE, '').trim()
    return { math: text, numbered }
  }
  if (text.startsWith('$') && text.endsWith('$') && text.length >= 3 && !text.slice(1, -1).includes('$')) {
    return { math: text.slice(1, -1).trim(), numbered: true }
  }
  return { math: text, numbered: true }
}

function standaloneEquation(body: string): string | null {
  const t = body.trim()
  if (/^\$\$.*\$\$$/s.test(t)) return t
  if (/^\\\[[\s\S]*\\\]$/.test(t)) return t
  if (EQ_OPEN_RE.test(t) && EQ_CLOSE_RE.test(t)) return t
  if (/^\$[^$\n]+\$\$?$/.test(t) && t.includes('=')) return t
  return null
}

export function renderPaperMarkdown(text: string): ReactNode[] {
  const lines = (text || '').replace(/\r\n/g, '\n').split('\n')
  const blocks: ReactNode[] = []
  let eqCount = 0
  let pendingCaption: string | null = null
  let i = 0

  const flushCaptionAsParagraph = () => {
    if (!pendingCaption) return
    const key = `p-${blocks.length}`
    const caption = pendingCaption
    pendingCaption = null
    blocks.push(
      <p key={key} className="mb-4 text-justify indent-[2em]">
        {inlineNodes(caption, key)}
      </p>,
    )
  }

  const pushEquation = (raw: string) => {
    flushCaptionAsParagraph()
    const { math, numbered } = stripDisplayMath(raw)
    if (numbered) eqCount += 1
    const key = `eq-${blocks.length}`
    blocks.push(
      <JournalEquation key={key} math={math} number={numbered ? eqCount : null} />,
    )
  }

  const pushParagraph = (body: string) => {
    const trimmed = body.trim()
    if (!trimmed) return
    const display = standaloneEquation(trimmed)
    if (display) {
      pushEquation(display)
      return
    }
    if (CAPTION_RE.test(trimmed)) {
      flushCaptionAsParagraph()
      pendingCaption = trimmed
      return
    }
    flushCaptionAsParagraph()
    const key = `p-${blocks.length}`
    blocks.push(
      <p key={key} className="mb-4 text-justify indent-[2em]">
        {inlineNodes(trimmed, key)}
      </p>,
    )
  }

  const pushTable = (rowLines: string[]) => {
    const rows = rowLines.filter((line) => !isSeparatorRow(line)).map(splitPipe)
    if (!rows.length) return
    const header = rows[0]
    const body = rows.slice(1)
    const caption = pendingCaption
    pendingCaption = null
    const key = `tbl-${blocks.length}`
    const colCount = Math.max(...rows.map((r) => r.length), 1)
    blocks.push(
      <figure key={key} className="my-6">
        {caption ? <figcaption className={journalCaption}>{inlineNodes(caption, `${key}-cap`)}</figcaption> : null}
        <table data-testid="paper-table" className={journalTable}>
          <thead>
            <tr className={journalTheadRow}>
              {Array.from({ length: colCount }, (_, c) => (
                <th
                  key={`${key}-h-${c}`}
                  className={`${journalTh} ${c === 0 ? 'font-semibold' : 'text-center'}`}
                >
                  {header[c] ? inlineNodes(header[c], `${key}-h-${c}`) : null}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {body.map((row, r) => (
              <tr
                key={`${key}-r-${r}`}
                className={`even:bg-[#f6f6f6] ${r === body.length - 1 ? 'border-b-[2.5px] border-ink' : ''}`}
              >
                {Array.from({ length: colCount }, (_, c) => (
                  <td
                    key={`${key}-c-${r}-${c}`}
                    className={`${journalTd} ${c === 0 ? 'font-semibold' : 'text-center font-serif tabular-nums'}`}
                  >
                    {row[c] ? inlineNodes(row[c], `${key}-c-${r}-${c}`) : null}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </figure>,
    )
  }

  while (i < lines.length) {
    const trimmed = lines[i].trimEnd()
    if (!trimmed.trim()) {
      i += 1
      continue
    }

    const heading = /^(#{1,3})\s+(.+)$/.exec(trimmed.trim())
    if (heading) {
      flushCaptionAsParagraph()
      const level = heading[1].length
      const key = `h-${blocks.length}`
      blocks.push(
        createElement(
          `h${level}`,
          { key, className: headingClass(level) },
          inlineNodes(heading[2], key),
        ),
      )
      i += 1
      continue
    }

    const listItem = /^[-*]\s+(.+)$/.exec(trimmed.trim())
    if (listItem) {
      flushCaptionAsParagraph()
      const items: string[] = []
      while (i < lines.length) {
        const m = /^[-*]\s+(.+)$/.exec(lines[i].trim())
        if (!m) break
        items.push(m[1])
        i += 1
      }
      const key = `ul-${blocks.length}`
      blocks.push(
        <ul key={key} className="mb-4 list-disc space-y-1 pl-6">
          {items.map((item, idx) => (
            <li key={`${key}-${idx}`}>{inlineNodes(item, `${key}-${idx}`)}</li>
          ))}
        </ul>,
      )
      continue
    }

    if (isPipeRow(trimmed)) {
      const rowLines: string[] = []
      while (i < lines.length && isPipeRow(lines[i])) {
        rowLines.push(lines[i])
        i += 1
      }
      let j = i
      while (j < lines.length && !lines[j].trim()) j += 1
      if (j < lines.length && NOTES_RE.test(lines[j].trim())) {
        pushTable(rowLines)
        const note = lines[j].trim()
        i = j + 1
        const key = `note-${blocks.length}`
        blocks.push(
          <p key={key} className={journalNotes}>
            {inlineNodes(note, key)}
          </p>,
        )
      } else {
        pushTable(rowLines)
      }
      continue
    }

    const fenceStart = trimmed.trim()
    if (
      fenceStart === '$$' ||
      fenceStart.startsWith('$$') ||
      fenceStart.startsWith('\\[') ||
      EQ_OPEN_RE.test(fenceStart)
    ) {
      const buf: string[] = [trimmed]
      const oneLine =
        (fenceStart.startsWith('$$') && fenceStart.length > 2 && fenceStart.endsWith('$$')) ||
        (fenceStart.startsWith('\\[') && fenceStart.endsWith('\\]')) ||
        (EQ_OPEN_RE.test(fenceStart) && EQ_CLOSE_RE.test(fenceStart))
      i += 1
      if (!oneLine) {
        while (i < lines.length) {
          buf.push(lines[i])
          const end = lines[i].trim()
          i += 1
          if (end === '$$' || end.endsWith('$$') || end.endsWith('\\]') || EQ_CLOSE_RE.test(end)) break
        }
      }
      pushEquation(buf.join('\n'))
      continue
    }

    const para: string[] = [trimmed.trim()]
    i += 1
    while (i < lines.length) {
      const next = lines[i]
      if (!next.trim()) break
      if (/^(#{1,3})\s+/.test(next.trim())) break
      if (/^[-*]\s+/.test(next.trim())) break
      if (isPipeRow(next)) break
      const n = next.trim()
      if (n === '$$' || n.startsWith('\\[') || EQ_OPEN_RE.test(n)) break
      para.push(n)
      i += 1
    }
    pushParagraph(para.join('\n'))
  }
  flushCaptionAsParagraph()
  return blocks
}
