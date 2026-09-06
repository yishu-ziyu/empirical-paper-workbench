import { forwardRef, type ReactNode } from 'react'
import ResizableWorkspace, { type ResizableWorkspaceHandle } from './ResizableWorkspace'

export interface ThreeColumnProps {
  outline: ReactNode
  editor: ReactNode
  agent: ReactNode
}

/**
 * Workbench v2 三栏容器：左=项目 sidebar（可折叠/可调宽），
 * 中=视图工件，右=Agent 栏。布局持久化在 localStorage。
 */
const ThreeColumn = forwardRef<ResizableWorkspaceHandle, ThreeColumnProps>(
  function ThreeColumn({ outline, editor, agent }, ref) {
    return (
      <ResizableWorkspace
        ref={ref}
        storageKey="econpaper.workbench.layout.v3"
        testId="desk-columns"
        leftTestId="sidebar-panel"
        centerTestId="editor-panel"
        rightTestId="agent-panel"
        leftDefault={236}
        leftMin={208}
        leftMax={300}
        rightDefault={304}
        rightMin={252}
        rightMax={400}
        leftClassName="overflow-hidden border-r border-wb-line bg-wb-subtle"
        centerClassName="overflow-auto bg-wb-canvas"
        rightClassName="overflow-auto border-l border-wb-line bg-wb-subtle"
        left={outline}
        center={editor}
        right={agent}
      />
    )
  },
)

ThreeColumn.displayName = 'ThreeColumn'

export default ThreeColumn
