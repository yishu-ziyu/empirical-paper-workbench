// 中栏流式编辑器 - 接收 chunks 数组拼接显示，收到 interrupt 时显示暂停提示

export interface EditorProps {
  chapterId?: string
  chunks?: string[]
  interrupt?: string
}

export default function Editor({ chunks = [], interrupt }: EditorProps) {
  const content = chunks.join('')

  return (
    <div
      data-testid="editor-content"
      className="min-h-[60vh] rounded border border-dashed border-border p-4 text-sm"
    >
      <h2 className="mb-3 text-xs uppercase tracking-wider text-muted">Editor</h2>
      <div className="whitespace-pre-wrap">{content}</div>
      {interrupt && (
        <div className="mt-4 rounded bg-yellow-100 p-2 text-yellow-800">
          暂停 (paused): {interrupt}
        </div>
      )}
    </div>
  )
}
