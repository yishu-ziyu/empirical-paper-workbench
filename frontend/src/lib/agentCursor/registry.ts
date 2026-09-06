import { parseSemanticId } from './control'

type RegistryListener = () => void

/**
 * Thin semantic id → Element map. Lookup is by id only.
 * Components register; Agent scripts never pass coordinates or selectors.
 */
export class SemanticTargetRegistry {
  private targets = new Map<string, Element>()
  private listeners = new Set<RegistryListener>()

  register(id: unknown, el: Element): () => void {
    const sid = parseSemanticId(id)
    this.targets.set(sid, el)
    this.emit()
    return () => this.unregister(sid, el)
  }

  unregister(id: unknown, el?: Element): void {
    const sid = parseSemanticId(id)
    const current = this.targets.get(sid)
    if (!current) return
    if (el && current !== el) return
    this.targets.delete(sid)
    this.emit()
  }

  lookup(id: unknown): Element | null {
    const sid = parseSemanticId(id)
    return this.targets.get(sid) ?? null
  }

  rect(id: unknown): DOMRect | null {
    const el = this.lookup(id)
    if (!el) return null
    return el.getBoundingClientRect()
  }

  has(id: unknown): boolean {
    try {
      return this.lookup(id) != null
    } catch {
      return false
    }
  }

  subscribe(listener: RegistryListener): () => void {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  clear(): void {
    this.targets.clear()
    this.emit()
  }

  private emit() {
    for (const listener of this.listeners) listener()
  }
}

export const semanticTargetRegistry = new SemanticTargetRegistry()
