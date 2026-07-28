// 三栏布局 - 左 Outline / 中 Editor / 右 Agent
// 每栏带 data-testid 供测试断言

import type { ReactNode } from 'react'

export interface ThreeColumnProps {
  outline: ReactNode
  editor: ReactNode
  agent: ReactNode
}

export default function ThreeColumn({ outline, editor, agent }: ThreeColumnProps) {
  return (
    <main className="grid flex-1 grid-cols-[260px_1fr_320px] divide-x divide-border">
      <aside data-testid="outline-panel" className="overflow-auto bg-panel p-4">
        {outline}
      </aside>
      <section data-testid="editor-panel" className="overflow-auto p-6">
        {editor}
      </section>
      <aside data-testid="agent-panel" className="overflow-auto bg-panel p-4">
        {agent}
      </aside>
    </main>
  )
}
