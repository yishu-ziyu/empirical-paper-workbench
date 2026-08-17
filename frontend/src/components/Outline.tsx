// 左栏大纲组件 (T-06)
// - @dnd-kit/sortable 拖拽排序 (PointerSensor + KeyboardSensor)
// - 每章 type badge (不同颜色)
// - 删除章节 / 添加章节
// - "确认大纲" → onConfirm(outline)
// HITL: 前端展示 outline + 确认按钮，确认后调 POST /sessions/{id}/resume
//
// Stage D: 删除手写 OutlineChapter interface，改 import types/api.ts 的
// OutlineChapterResponse（与 POST /sessions/{id}/direction 返回体一致）。

import { useEffect, useRef, useState } from 'react'
import { useT } from '../lib/i18n'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { components } from '../types/api'

/** 大纲章节项，由 OpenAPI codegen 生成（components.schemas.OutlineChapterResponse）。 */
export type OutlineChapter = components['schemas']['OutlineChapterResponse']

export interface OutlineProps {
  body_chapters: OutlineChapter[]
  onConfirm?: (body_chapters: OutlineChapter[]) => void
}

const BADGE_COLORS: Record<string, string> = {
  intro: 'bg-blue-100 text-blue-800',
  lit_review: 'bg-purple-100 text-purple-800',
  data_desc: 'bg-green-100 text-green-800',
  methods: 'bg-orange-100 text-orange-800',
  results: 'bg-pink-100 text-pink-800',
  conclusion: 'bg-gray-200 text-gray-800',
}

interface InternalChapter extends OutlineChapter {
  id: string
}

function badgeClass(type: string): string {
  return BADGE_COLORS[type] ?? 'bg-gray-100 text-gray-700'
}

interface SortableChapterProps {
  chapter: InternalChapter
  onDelete: () => void
  onMoveUp: () => void
  onMoveDown: () => void
}

function SortableChapter({
  chapter,
  onDelete,
  onMoveUp,
  onMoveDown,
}: SortableChapterProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: chapter.id })
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }
  return (
    <li
      ref={setNodeRef}
      style={style}
      data-testid="chapter-item"
      className="flex items-center gap-2 rounded border border-border p-2"
    >
      <button
        type="button"
        data-testid="drag-handle"
        className="cursor-grab px-1 text-muted"
        aria-label={`拖拽 ${chapter.title}`}
        {...attributes}
        {...listeners}
      >
        ⠿
      </button>
      <span
        data-testid="type-badge"
        className={`rounded px-1.5 py-0.5 text-xs ${badgeClass(chapter.type)}`}
      >
        {chapter.type}
      </span>
      <span className="flex-1 text-sm">{chapter.title}</span>
      <button
        type="button"
        aria-label={`上移 ${chapter.title}`}
        onClick={onMoveUp}
        className="px-1 text-xs"
      >
        ↑
      </button>
      <button
        type="button"
        aria-label={`下移 ${chapter.title}`}
        onClick={onMoveDown}
        className="px-1 text-xs"
      >
        ↓
      </button>
      <button
        type="button"
        aria-label={`删除 ${chapter.title}`}
        onClick={onDelete}
        className="px-1 text-xs text-red-500"
      >
        ✕
      </button>
    </li>
  )
}

export default function Outline({ body_chapters, onConfirm }: OutlineProps) {
  const { t } = useT()
  const idCounter = useRef(0)
  const [items, setItems] = useState<InternalChapter[]>(() =>
    body_chapters.map((c, i) => ({ ...c, id: `ch-${i}` })),
  )

  useEffect(() => {
    setItems(body_chapters.map((c, i) => ({ ...c, id: `ch-${i}` })))
  }, [body_chapters])

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  )

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (!over || active.id === over.id) return
    setItems((prev) => {
      const oldIndex = prev.findIndex((it) => it.id === active.id)
      const newIndex = prev.findIndex((it) => it.id === over.id)
      if (oldIndex === -1 || newIndex === -1) return prev
      return arrayMove(prev, oldIndex, newIndex)
    })
  }

  function move(id: string, dir: -1 | 1) {
    setItems((prev) => {
      const i = prev.findIndex((it) => it.id === id)
      const j = i + dir
      if (i === -1 || j < 0 || j >= prev.length) return prev
      return arrayMove(prev, i, j)
    })
  }

  function deleteChapter(id: string) {
    setItems((prev) => prev.filter((it) => it.id !== id))
  }

  function addChapter() {
    const id = `ch-new-${idCounter.current++}`
    setItems((prev) => [...prev, { id, type: 'intro', title: t('outline.newChapter') }])
  }

  function confirm() {
    onConfirm?.(items)
  }

  return (
    <div data-testid="outline-content">
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={items.map((it) => it.id)}
          strategy={verticalListSortingStrategy}
        >
          <ul className="space-y-2">
            {items.map((it) => (
              <SortableChapter
                key={it.id}
                chapter={it}
                onDelete={() => deleteChapter(it.id)}
                onMoveUp={() => move(it.id, -1)}
                onMoveDown={() => move(it.id, 1)}
              />
            ))}
          </ul>
        </SortableContext>
      </DndContext>
      <button
        type="button"
        onClick={addChapter}
        className="mt-2 rounded border border-dashed border-border px-2 py-1 text-xs"
      >
        {t('outline.addChapter')}
      </button>
      <button
        type="button"
        onClick={confirm}
        className="mt-2 ml-2 rounded bg-accent px-3 py-1 text-xs text-white"
      >
        {t('outline.confirm')}
      </button>
    </div>
  )
}
