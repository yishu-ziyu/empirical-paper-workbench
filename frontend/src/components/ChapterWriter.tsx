// 章节写作器 (T-07 → T-08c 扩展)
// - 中栏用 CodeMirror 6 渲染流式 markdown（chunks 数组拼接）
// - 章节类型 badge（6 色：intro=蓝 / lit_review=紫 / data_desc=绿 /
//   methods=橙 / results=红 / conclusion=灰）
// - status === 'generated' | 'edited' 显示 4 按钮：重新生成 / 回滚 / {t('chapter.edit')} / {t('chapter.approve')}
// - status === 'streaming' 显示加载提示，不显示按钮
// - 回滚下拉：点"回滚"显示版本历史（VersionHistory 组件），选择版本 → onRollback
// - {t('chapter.edit')}模式：点"{t('chapter.edit')}" → CodeMirror 可{t('chapter.edit')} + 按钮变"{t('chapter.save')}"；点"{t('chapter.save')}" → onSaveEdit
// - onApprove / onRegenerate / onRollback / onSaveEdit 回调
//
// HITL 简化：节点完成后由 backend interrupt() 暂停 graph，前端{t('chapter.approve')} WS 收到
// status='generated' 后显示审批按钮，用户点"{t('chapter.approve')}" → POST /approve-chapter
// → graph resume 下一章。
//
// Stage D 修复漂移 4：删除手写 Chapter interface，改 import types/api.ts 的
// ChapterResponse。status 枚举由后端 OpenAPI 定义（generated | approved |
// edited | rolled_back），前端本地临时态再加 streaming / done。

import { useEffect, useMemo, useRef, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { useT } from '../lib/i18n'
import { renderPaperMarkdown } from '../lib/paperMarkdown'
import VersionHistory from './VersionHistory'
import ApprovalBadge from './ApprovalBadge'
import type { components } from '../types/api'
// TODO(T-07 followup): 安装 @codemirror/lang-markdown + @codemirror/language-data
// 后启用 markdown 语法高亮：
//   import { markdown, markdownLanguage } from '@codemirror/lang-markdown'
//   import { languages } from '@codemirror/language-data'
// 当前 @uiw/react-codemirror 已装但 lang-markdown 未装，先用 CodeMirror
// 纯文本模式渲染（仍是 CodeMirror 6，符合任务规格"用 CodeMirror 6 渲染流式
// markdown"的最小要求；流式 append {t('chapter.approve')} value prop 控制）。

/** 章节类型，由 OpenAPI codegen 生成（components.schemas.ChapterResponse）。 */
type Chapter = components['schemas']['ChapterResponse']

export interface ChapterWriterProps {
  chapter: Chapter
  /** 流式 chunks：WS 推过来的 token 数组；非空时优先于 chapter.content 拼接显示 */
  chunks?: string[]
  onApprove?: (chapter: Chapter) => void
  onRegenerate?: (chapter: Chapter) => void
  /** T-08c: 会话 ID（用于回滚 / {t('chapter.edit')} API 路径，集成阶段使用） */
  sessionId?: string
  /** T-08c: 当前章索引 */
  chapterIndex?: number
  /** T-08c: 版本历史列表（用于回滚下拉） */
  versions?: string[]
  /** T-08c: 选择版本回滚回调（集成阶段调 POST /sessions/{id}/rollback） */
  onRollback?: (versionIndex: number) => void
  /** T-08c: {t('chapter.save')}{t('chapter.edit')}回调（集成阶段调 POST /sessions/{id}/edit-chapter）。失败请 reject，组件会留在编辑态保住草稿。第二个参数是进入编辑时的章节序号，避免切章后写到新选中的章。 */
  onSaveEdit?: (content: string, chapterIndex?: number) => void | Promise<void>
  onJumpToClaim?: () => void
}

const BADGE_CLASS = 'bg-paper text-muted border border-border'

function badgeClass(_type: string): string {
  return BADGE_CLASS
}

export default function ChapterWriter({
  chapter,
  chunks,
  onApprove,
  onRegenerate,
  versions,
  onRollback,
  onSaveEdit,
  chapterIndex,
  onJumpToClaim,
  // sessionId — 接口保留供集成阶段直接 fetch 使用，当前组件走回调模式。
}: ChapterWriterProps) {
  const { t } = useT()
  // {t('chapter.edit')}模式状态
  const [isEditing, setIsEditing] = useState(false)
  // {t('chapter.edit')}中的内容（进入{t('chapter.edit')}模式时初始化）
  const [editedContent, setEditedContent] = useState('')
  // 回滚下拉显示状态
  const [showVersions, setShowVersions] = useState(false)
  const boundChapterIndexRef = useRef<number | undefined>(chapterIndex)
  const chapterIdentity = `${chapter.type}:${chapter.chapter_index ?? chapterIndex ?? ''}`

  useEffect(() => {
    setIsEditing(false)
    setEditedContent('')
    setShowVersions(false)
    boundChapterIndexRef.current = chapterIndex
  }, [chapterIdentity, chapterIndex])

  // chunks 非空时拼接显示（流式 append）；否则用 chapter.content
  const content = useMemo(() => {
    if (chunks && chunks.length > 0) {
      return chunks.join('')
    }
    return chapter.content ?? ''
  }, [chunks, chapter.content])

  const isStreaming = chapter.status === 'streaming'
  const showToolbar = chapter.status === 'generated' || chapter.status === 'edited'

  // {t('chapter.edit')}模式显示的内容：{t('chapter.edit')}中用 editedContent，否则用 content
  const displayContent = isEditing ? editedContent : content

  // 进入{t('chapter.edit')}模式
  const handleEnterEdit = () => {
    boundChapterIndexRef.current = chapterIndex
    setEditedContent(content)
    setIsEditing(true)
  }

  // {t('chapter.save')}{t('chapter.edit')}：POST 成功才退出编辑，失败保住草稿。
  const handleSaveEdit = async () => {
    try {
      await onSaveEdit?.(editedContent, boundChapterIndexRef.current)
      setIsEditing(false)
    } catch {
      // keep isEditing + editedContent
    }
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
          {t(`chapter.type.${chapter.type}`)}
        </span>
        <h3 className="text-sm font-semibold">{chapter.title}</h3>
        <ApprovalBadge chapter={chapter} />
      </div>

      {chapter.stale || chapter.needs_regeneration ? (
        <p
          data-testid="chapter-stale"
          className="rounded-md border border-wb-line bg-wb-subtle px-3 py-2 text-[12px] text-wb-muted"
        >
          Stale · needs regeneration
        </p>
      ) : null}

      {onJumpToClaim ? (
        <div className="flex items-center gap-2">
          <span
            data-testid="paper-grounded-badge"
            className={`rounded-full px-2 py-0.5 text-[10.5px] font-medium ${
              chapter.grounded !== false
                ? 'bg-wb-success-soft text-wb-success'
                : 'bg-wb-warning-soft text-wb-warning'
            }`}
          >
            {chapter.grounded !== false ? '基于证据' : '未 grounded'}
          </span>
          <button
            type="button"
            data-testid="paper-claim-link"
            onClick={onJumpToClaim}
            className="text-[12px] text-wb-muted underline-offset-2 hover:text-wb-ink hover:underline"
          >
            View Claim / Evidence
          </button>
        </div>
      ) : null}

      {isEditing || isStreaming ? (
        <div data-testid="chapter-codemirror" className="rounded border border-border">
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
      ) : (
        <article
          data-testid="chapter-paper"
          className="journal-page"
        >
          {renderPaperMarkdown(displayContent)}
        </article>
      )}

      {isStreaming && (
        <div
          data-testid="chapter-streaming-hint"
          className="rounded bg-accent/10 p-2 text-xs text-accent"
        >
          {t('chapter.streaming')}
        </div>
      )}

      {/* 完成后审批按钮（4 按钮） */}
      {showToolbar && (
        <div className="space-y-2">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onRegenerate?.(chapter)}
              className="rounded border border-border px-3 py-1 text-xs"
            >
              {t('chapter.regenerate')}
            </button>
            <button
              type="button"
              onClick={() => setShowVersions((v) => !v)}
              className="rounded border border-border px-3 py-1 text-xs"
            >
              {t('chapter.rollback')}
            </button>
            {isEditing ? (
              <button
                type="button"
                onClick={handleSaveEdit}
                className="rounded border border-accent px-3 py-1 text-xs text-accent"
              >
                {t('chapter.save')}
              </button>
            ) : (
              <button
                type="button"
                onClick={handleEnterEdit}
                className="rounded border border-border px-3 py-1 text-xs"
              >
                {t('chapter.edit')}
              </button>
            )}
            <button
              type="button"
              onClick={() => onApprove?.(chapter)}
              className="rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-white"
            >
              {t('chapter.approve')}
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
