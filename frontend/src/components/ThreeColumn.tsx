import { forwardRef, type ReactNode } from 'react'
import ResizableWorkspace, { type ResizableWorkspaceHandle } from './ResizableWorkspace'

export interface ThreeColumnProps {
  outline: ReactNode
  editor: ReactNode
  agent: ReactNode
}

const ThreeColumn = forwardRef<ResizableWorkspaceHandle, ThreeColumnProps>(
  function ThreeColumn({ outline, editor, agent }, ref) {
    return (
      <ResizableWorkspace
        ref={ref}
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
  },
)

ThreeColumn.displayName = 'ThreeColumn'

export default ThreeColumn
