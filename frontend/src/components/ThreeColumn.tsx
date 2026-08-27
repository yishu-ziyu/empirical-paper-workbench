import { type ReactNode } from 'react'

export interface ThreeColumnProps {
  outline: ReactNode
  editor: ReactNode
  agent: ReactNode
  leftOpen?: boolean
  rightOpen?: boolean
}

export default function ThreeColumn({
  outline,
  editor,
  agent,
  leftOpen = true,
  rightOpen = true,
}: ThreeColumnProps) {
  return (
    <main className="relative grid flex-1 grid-cols-1 lg:grid-cols-[248px_minmax(0,1fr)_300px]">
      <aside
        data-testid="outline-panel"
        className={`overflow-auto border-b border-border bg-cream p-5 transition-all duration-300 lg:border-b-0 lg:border-r ${
          leftOpen ? 'max-h-full opacity-100' : 'max-h-0 overflow-hidden opacity-0 lg:max-h-full lg:opacity-100'
        }`}
      >
        <div className="animate-fade-in">{outline}</div>
      </aside>
      <section data-testid="editor-panel" className="overflow-auto bg-bg">
        {editor}
      </section>
      <aside
        data-testid="agent-panel"
        className={`overflow-auto border-t border-border bg-cream p-5 transition-all duration-300 lg:border-l lg:border-t-0 ${
          rightOpen ? 'max-h-full opacity-100' : 'max-h-0 overflow-hidden opacity-0 lg:max-h-full lg:opacity-100'
        }`}
      >
        <div className="animate-fade-in">{agent}</div>
      </aside>
    </main>
  )
}
