import { type ReactNode } from 'react'

export interface ThreeColumnProps {
  outline: ReactNode
  editor: ReactNode
  agent: ReactNode
}

export default function ThreeColumn({ outline, editor, agent }: ThreeColumnProps) {
  return (
    <main className="relative grid min-h-0 min-w-[760px] flex-1 grid-cols-[220px_minmax(0,1fr)_280px] xl:grid-cols-[248px_minmax(0,1fr)_300px]">
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
      >
        {agent}
      </aside>
    </main>
  )
}
