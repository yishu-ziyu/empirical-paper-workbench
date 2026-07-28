// 章节写作器 (T-07 → T-08c 扩展)
// - 中栏用 CodeMirror 6 渲染流式 markdown（chunks 数组拼接）
// - 章节类型 badge（6 色：intro=蓝 / lit_review=紫 / data_desc=绿 /
//   methods=橙 / results=红 / conclusion=灰）
// - status === 'generated' 显示 4 按钮：重新生成 / 回滚 / 编辑 / 通过
// - status === 'streaming' 显示加载提示，不显示按钮
// - 回滚下拉：点"回滚"显示版本历史（VersionHistory 组件），选择版本 → onRollback
// - 编辑模式：点"编辑" → CodeMirror 可编辑 + 按钮变"保存"；点"保存" → onSaveEdit
// - onApprove / onRegenerate / onRollback / onSaveEdit 回调
//
// HITL 简化：节点完成后由 backend interrupt() 暂停 graph，前端通过 WS 收到
// status='generated' 后显示审批按钮，用户点"通过" → POST /approve-chapter
// → graph resume 下一章。
//
// Stage D 修复漂移 4：删除手写 Chapter interface，改 import types/api.ts 的
// ChapterResponse。status 枚举由后端 OpenAPI 定义（generated | approved |
// edited | rolled_back），前端本地临时态再加 streaming / done。

import { useMemo, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import VersionHistory from './VersionHistory'
import type { components } from '../types/api'
// TODO(T-07 followup): 安装 @codemirror/lang-markdown + @codemirror/language-data
// 后启用 markdown 语法高亮：
//   import { markdown, markdownLanguage } from '@codemirror/lang-markdown'
//   import { languages } from '@codemirror/language-data'
// 当前 @uiw/react-codemirror 已装但 lang-markdown 未装，先用 CodeMirror
// 纯文本模式渲染（仍是 CodeMirror 6，符合任务规格"用 CodeMirror 6 渲染流式
// markdown"的最小要求；流式 append 通过 value prop 控制）。

/** 章节类型，由 OpenAPI codegen 生成（components.schemas.ChapterResponse）。 */
type Chapter = components['schemas']['ChapterResponse']

export interface ChapterWriterProps {
  chapter: Chapter
  /** 流式 chunks：WS 推过来的 token 数组；非空时优先于 chapter.content 拼接显示 */
  chunks?: string[]
  onApprove?: (chapter: Chapter) => void
  onRegenerate?: (chapter: Chapter) => void
  /** T-08c: 会话 ID（用于回滚 / 编辑 API 路径，集成阶段使用） */
  sessionId?: string
  /** T-08c: 当前章索引 */
  chapterIndex?: number
  /** T-08c: 版本历史列表（用于回滚下拉） */
  versions?: string[]
  /** T-08c: 选择版本回滚回调（集成阶段调 POST /sessions/{id}/rollback） */
  onRollback?: (versionIndex: number) => void
  /** T-08c: 保存编辑回调（集成阶段调 POST /sessions/{id}/edit-chapter） */
  onSaveEdit?: (content: string) => void
}

// 6 色 badge（任务规格 §T-07：intro=蓝 / lit_review=紫 / data_desc=绿 /
// methods=橙 / results=红 / conclusion=灰）
const BADGE_COLORS: Record<string, string> = {
  intro: 'bg-blue-100 text-blue-800',
  lit_review: 'bg-purple-100 text-purple-800',
  data_desc: 'bg-green-100 text-green-800',
  methods: 'bg-orange-100 text-orange-800',
  results: 'bg-red-100 text-red-800',
  conclusion: 'bg-gray-200 text-gray-800',
}

function badgeClass(type: string): string {
  return BADGE_COLORS[type] ?? 'bg-gray-100 text-gray-700'
}

export default function ChapterWriter({
  chapter,
  chunks,
  onApprove,
  onRegenerate,
  versions,
  onRollback,
  onSaveEdit,
  // sessionId, chapterIndex — 接口保留供集成阶段直接 fetch 使用，
  // 当前组件走回调模式（onRollback / onSaveEdit），不在此解构以避免未使用告警。
}: ChapterWriterProps) {
  // 编辑模式状态
  const [isEditing, setIsEditing] = useState(false)
  // 编辑中的内容（进入编辑模式时初始化）
  const [editedContent, setEditedContent] = useState('')
  // 回滚下拉显示状态
  const [showVersions, setShowVersions] = useState(false)

  // chunks 非空时拼接显示（流式 append）；否则用 chapter.content
  const content = useMemo(() => {
    if (chunks && chunks.length > 0) {
      return chunks.join('')
    }
    return chapter.content ?? ''
  }, [chunks, chapter.content])

  const isStreaming = chapter.status === 'streaming'
  const isGenerated = chapter.status === 'generated'

  // 编辑模式显示的内容：编辑中用 editedContent，否则用 content
  const displayContent = isEditing ? editedContent : content

  // 进入编辑模式
  const handleEnterEdit = () => {
    setEditedContent(content)
    setIsEditing(true)
  }

  // 保存编辑
  const handleSaveEdit = () => {
    setIsEditing(false)
    onSaveEdit?.(editedContent)
  }

  // 选择版本回滚
  const handleSelectVersion = (idx: number) => {
    setShowVersions(false)
    onRollback?.(idx)
  }

  return (
    <div data-testid="chapter-writer" className="space-y-3">
      {/* header: badge + title */}
      <div className="flex items-center gap-2">
        <span
          data-testid="chapter-type-badge"
          className={`rounded px-2 py-0.5 text-xs font-mono ${badgeClass(chapter.type)}`}
        >
          {chapter.type}
        </span>
        <h3 className="text-sm font-semibold">{chapter.title}</h3>
      </div>

      {/* CodeMirror 6 markdown 流式渲染 */}
      <div data-testid="chapter-codemirror" className="border border-border rounded">
        <CodeMirror
          value={displayContent}
          extensions={[]}
          editable={isEditing}
          basicSetup={{ lineNumbers: false, foldGutter: false }}
          height="auto"
          onChange={(val) => {
            if (isEditing) {
              setEditedContent(val)
            }
          }}
        />
      </div>

      {/* streaming 提示 */}
      {isStreaming && (
        <div
          data-testid="chapter-streaming-hint"
          className="rounded bg-blue-50 p-2 text-xs text-blue-700"
        >
          正在生成…（流式接收中）
        </div>
      )}

      {/* 完成后审批按钮（4 按钮） */}
      {isGenerated && (
        <div className="space-y-2">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onRegenerate?.(chapter)}
              className="rounded border border-border px-3 py-1 text-xs"
            >
              重新生成
            </button>
            <button
              type="button"
              onClick={() => setShowVersions((v) => !v)}
              className="rounded border border-border px-3 py-1 text-xs"
            >
              回滚
            </button>
            {isEditing ? (
              <button
                type="button"
                onClick={handleSaveEdit}
                className="rounded border border-accent px-3 py-1 text-xs text-accent"
              >
                保存
              </button>
            ) : (
              <button
                type="button"
                onClick={handleEnterEdit}
                className="rounded border border-border px-3 py-1 text-xs"
              >
                编辑
              </button>
            )}
            <button
              type="button"
              onClick={() => onApprove?.(chapter)}
              className="rounded bg-accent px-3 py-1 text-xs text-white"
            >
              通过
            </button>
          </div>

          {/* 回滚版本历史下拉 */}
          {showVersions && versions && versions.length > 0 && (
            <VersionHistory
              versions={versions}
              onSelectVersion={handleSelectVersion}
            />
          )}
          {showVersions && (!versions || versions.length === 0) && (
            <VersionHistory
              versions={[]}
              onSelectVersion={handleSelectVersion}
            />
          )}
        </div>
      )}
    </div>
  )
}
