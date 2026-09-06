import { useCallback, useEffect, useRef } from 'react'
import { semanticTargetRegistry } from './registry'

export function useSemanticTargets(ids: Array<string | null | undefined>) {
  const nodeRef = useRef<Element | null>(null)
  const registeredRef = useRef<string[]>([])
  const idsRef = useRef(ids)
  idsRef.current = ids
  const idsKey = ids.filter(Boolean).join('|')

  const bind = useCallback((node: Element | null) => {
    const nextIds = idsRef.current.filter((id): id is string => Boolean(id))
    if (nodeRef.current) {
      for (const id of registeredRef.current) {
        semanticTargetRegistry.unregister(id, nodeRef.current)
      }
    }
    nodeRef.current = node
    registeredRef.current = nextIds
    if (node) {
      for (const id of nextIds) semanticTargetRegistry.register(id, node)
    }
  }, [])

  useEffect(() => {
    if (nodeRef.current) bind(nodeRef.current)
    return () => {
      const node = nodeRef.current
      if (!node) return
      for (const id of registeredRef.current) semanticTargetRegistry.unregister(id, node)
      registeredRef.current = []
    }
  }, [bind, idsKey])

  return bind
}

export function useSemanticTarget(id: string | null | undefined) {
  return useSemanticTargets([id])
}
