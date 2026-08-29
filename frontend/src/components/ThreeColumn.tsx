import { type ReactNode } from 'react'
import ResizableWorkspace from './ResizableWorkspace'

export interface ThreeColumnProps {
  outline: ReactNode
  editor: ReactNode
  agent: ReactNode
}

export default function ThreeColumn({ outline, editor, agent }: ThreeColumnProps) {
  return (
    <ResizableWorkspace
      storageKey="econpaper.workbench.layout.v2"
      testId="desk-columns"
      leftTestId="outline-panel"
      centerTestId="editor-panel"
      rightTestId="agent-panel"
      leftDefault={220}
      rightDefault={280}
      leftClassName="overflow-auto border-r border-border bg-cream p-5"
      centerClassName="overflow-auto bg-bg"
      rightClassName="overflow-auto border-l border-border bg-cream p-5"
      left={outline}
      center={editor}
      right={agent}
    />
  )
}
