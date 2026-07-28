import { useState } from 'react'
import EdaSidebar from './components/EdaSidebar'
import Outline from './components/Outline'
import type { OutlineChapter } from './components/Outline'
import Editor from './components/Editor'
import AgentPanel from './components/AgentPanel'

function App() {
  // TODO: 后续接 upload 返回的真实 sessionId
  const [sessionId] = useState('demo-session')
  const [edaOpen, setEdaOpen] = useState(true)
  const [bodyChapters, setBodyChapters] = useState<OutlineChapter[]>([
    { type: 'intro', title: 'Title' },
  ])

  return (
    <div className="flex min-h-screen flex-col bg-bg text-ink font-sans">
      <header className="flex items-center justify-between border-b border-border px-6 py-3">
        <h1 className="text-lg font-semibold tracking-tight">
          econpaper <span className="text-accent">v0</span>
        </h1>
      </header>

      <main className="grid flex-1 grid-cols-[260px_1fr_320px] divide-x divide-border">
        <aside className="overflow-auto bg-panel p-4">
          <h2 className="mb-3 text-xs uppercase tracking-wider text-muted">Outline</h2>
          {edaOpen ? (
            <EdaSidebar sessionId={sessionId} onClose={() => setEdaOpen(false)} />
          ) : (
            <button
              onClick={() => setEdaOpen(true)}
              className="text-sm text-accent"
            >
              Open EDA
            </button>
          )}
        </aside>
        <section data-testid="editor-panel" className="overflow-auto p-6">
          <Outline body_chapters={bodyChapters} onConfirm={(c) => setBodyChapters(c)} />
          <div className="mt-6">
            <Editor chunks={[]} />
          </div>
        </section>
        <aside data-testid="agent-panel" className="overflow-auto bg-panel p-4">
          <AgentPanel currentNode="" connectionState="disconnected" />
        </aside>
      </main>
    </div>
  )
}

export default App
