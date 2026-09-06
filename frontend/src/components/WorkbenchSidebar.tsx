import type { ReactNode } from 'react'

export type WorkbenchViewId =
  | 'overview'
  | 'question'
  | 'data'
  | 'design'
  | 'evidence'
  | 'literature'
  | 'paper'

export interface SidebarItem {
  id: WorkbenchViewId
  label: string
  hint: string
  status: 'done' | 'active' | 'pending' | 'blocked'
}

export interface WorkbenchSidebarProps {
  items: SidebarItem[]
  activeId: string
  onSelect: (id: WorkbenchViewId) => void
  children?: ReactNode
}

function StatusDot({ status }: { status: SidebarItem['status'] }) {
  if (status === 'done') {
    return (
      <span
        aria-hidden
        className="h-1.5 w-1.5 shrink-0 rounded-full bg-wb-success"
      />
    )
  }
  if (status === 'active') {
    return (
      <span
        aria-hidden
        className="wb-dot-running h-1.5 w-1.5 shrink-0 rounded-full bg-wb-primary"
      />
    )
  }
  if (status === 'blocked') {
    return (
      <span
        aria-hidden
        className="h-1.5 w-1.5 shrink-0 rounded-full bg-wb-danger"
      />
    )
  }
  return (
    <span
      aria-hidden
      className="h-1.5 w-1.5 shrink-0 rounded-full border border-wb-line-strong"
    />
  )
}

/**
 * Workbench v2 左侧项目 sidebar（契约 C1）。七个视图入口，当前项高亮；
 * 状态点全部来自 snapshot 投影，不在本地另建业务状态。
 * 折叠/展开由 ResizableWorkspace 的左栏机制承载。
 */
export default function WorkbenchSidebar({
  items,
  activeId,
  onSelect,
  children,
}: WorkbenchSidebarProps) {
  return (
    <nav
      data-testid="workbench-sidebar"
      aria-label="项目导航"
      className="flex h-full min-h-0 flex-col"
    >
      <div className="flex items-center gap-2 px-4 pb-3 pt-4">
        <span
          aria-hidden
          className="flex h-6 w-6 items-center justify-center rounded-md bg-wb-ink font-serif text-[13px] font-semibold text-white"
        >
          e
        </span>
        <span className="text-[14px] font-semibold tracking-tight text-wb-ink">
          econpaper
        </span>
      </div>

      <p className="px-4 pb-1.5 pt-2 font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
        我的研究
      </p>
      <ul className="min-h-0 flex-1 space-y-0.5 overflow-y-auto px-2">
        {items.map((item) => {
          const active = activeId === item.id
          return (
            <li key={item.id}>
              <button
                type="button"
                data-testid={`rail-${item.id}`}
                data-status={item.status}
                aria-current={active ? 'true' : undefined}
                onClick={() => onSelect(item.id)}
                className={`wb-press flex w-full items-center gap-2 rounded-md px-2.5 py-[7px] text-left ${
                  active
                    ? 'bg-wb-surface text-wb-ink shadow-[0_1px_2px_rgba(0,0,0,0.05)] ring-1 ring-wb-line'
                    : 'text-wb-muted hover:bg-wb-surface/60 hover:text-wb-ink'
                }`}
              >
                <StatusDot status={item.status} />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[13px] leading-5 font-medium">
                    {item.label}
                  </span>
                  <span className="block truncate text-[11px] leading-4 text-wb-faint">
                    {item.hint}
                  </span>
                </span>
              </button>
            </li>
          )
        })}
      </ul>

      {children}

      <p className="border-t border-wb-line px-4 py-3 font-serif text-[12px] italic leading-5 text-wb-faint">
        先做事，不打扰，人决定下一步。
      </p>
    </nav>
  )
}
