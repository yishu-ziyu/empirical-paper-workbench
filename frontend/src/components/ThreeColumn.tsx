// 三栏布局 - 左 Outline / 中 Editor / 右 Agent
// 带 motion 过渡动画 + 响应式折叠
// 每栏带 data-testid 供测试断言

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
    <main className="relative grid flex-1 grid-cols-1 divide-x divide-border lg:grid-cols-[260px_1fr_320px]">
      {/* 左栏 */}
      <aside
        data-testid="outline-panel"
        className={`overflow-auto bg-panel p-4 transition-all duration-300 ${
          leftOpen ? 'max-h-full opacity-100' : 'max-h-0 overflow-hidden opacity-0 lg:max-h-full lg:opacity-100'
        }`}
      >
        <div className="animate-fade-in">{outline}</div>
      </aside>

      {/* 中栏 */}
      <section
        data-testid="editor-panel"
        className="overflow-auto p-6 transition-all duration-300"
      >
        {editor}
      </section>

      {/* 右栏 */}
      <aside
        data-testid="agent-panel"
        className={`overflow-auto bg-panel p-4 transition-all duration-300 ${
          rightOpen ? 'max-h-full opacity-100' : 'max-h-0 overflow-hidden opacity-0 lg:max-h-full lg:opacity-100'
        }`}
      >
        <div className="animate-fade-in">{agent}</div>
      </aside>
    </main>
  )
}