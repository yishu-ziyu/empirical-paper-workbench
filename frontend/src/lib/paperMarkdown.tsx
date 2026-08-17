import { createElement, type ReactNode } from 'react'

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
        <span key={`${keyPrefix}-math-${i}`} className="font-mono text-sm">
          {token}
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

export function renderPaperMarkdown(text: string): ReactNode[] {
  const source = (text || '').replace(/\r\n/g, '\n')
  const blocks: ReactNode[] = []
  const paragraph: string[] = []
  const listItems: string[] = []

  const flushParagraph = () => {
    if (!paragraph.length) return
    const body = paragraph.join('\n').trim()
    paragraph.length = 0
    if (!body) return
    const key = `p-${blocks.length}`
    blocks.push(
      <p key={key} className="mb-3">
        {inlineNodes(body, key)}
      </p>,
    )
  }

  const flushList = () => {
    if (!listItems.length) return
    const key = `ul-${blocks.length}`
    blocks.push(
      <ul key={key} className="mb-3 list-disc space-y-1 pl-6">
        {listItems.map((item, i) => (
          <li key={`${key}-${i}`}>{inlineNodes(item, `${key}-${i}`)}</li>
        ))}
      </ul>,
    )
    listItems.length = 0
  }

  for (const rawLine of source.split('\n')) {
    const line = rawLine.trimEnd()
    const heading = /^(#{1,3})\s+(.+)$/.exec(line.trim())
    if (heading) {
      flushList()
      flushParagraph()
      const level = heading[1].length
      const key = `h-${blocks.length}`
      blocks.push(
        createElement(
          `h${level}`,
          {
            key,
            className:
              level === 1
                ? 'mb-3 mt-1 font-serif text-xl font-semibold'
                : level === 2
                  ? 'mb-2 mt-5 font-serif text-lg font-semibold'
                  : 'mb-2 mt-4 font-serif text-base font-semibold',
          },
          inlineNodes(heading[2], key),
        ),
      )
      continue
    }
    const listItem = /^[-*]\s+(.+)$/.exec(line.trim())
    if (listItem) {
      flushParagraph()
      listItems.push(listItem[1])
      continue
    }
    if (!line.trim()) {
      flushList()
      flushParagraph()
      continue
    }
    flushList()
    paragraph.push(line.trim())
  }
  flushList()
  flushParagraph()
  return blocks
}
