import { type CSSProperties, type ReactNode } from 'react'

export interface ThreeColumnProps {
  outline: ReactNode
  editor: ReactNode
  agent: ReactNode
}

const DESK_GRID: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '220px minmax(0, 1fr) 280px',
  minWidth: 760,
}

export default function ThreeColumn({ outline, editor, agent }: ThreeColumnProps) {
  return (
    <main data-testid="desk-columns" className="desk-columns relative min-h-0 flex-1" style={DESK_GRID}>
      <aside
        data-testid="outline-panel"
        className="min-h-0 min-w-0 overflow-auto border-r border-border bg-cream p-5"
      >
        {outline}
      </aside>
      <section data-testid="editor-panel" className="min-h-0 min-w-0 overflow-auto bg-bg">
        {editor}
      </section>
      <aside
        data-testid="agent-panel"
        className="min-h-0 min-w-0 overflow-auto border-l border-border bg-cream p-5"
        style={{ minWidth: 280 }}
      >
        {agent}
      </aside>
    </main>
  )
}
