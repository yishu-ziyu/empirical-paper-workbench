/**
 * MethodsDrawer — Task 43 BDD (DesignPanel 抽屉)
 *
 * Backs 4 behaviors:
 *  1. 入口: rendered from DesignPanel via the "查看全部方法" button
 *  2. 分类: top chip bar with category counts; click to filter
 *  3. 搜索: real-time substring filter on name + description; match highlight
 *  4. 不阻塞: position:fixed right slide-in (z-index 1000), backdrop click closes
 *
 * CSS: follows the `.design-panel__*` BEM convention used by DesignPanel.tsx.
 * Scoped inline `<style>` block at the end so we don't touch styles.css.
 */
import { useEffect, useMemo, useRef, useState } from "react";
import { Search, X, Library, ChevronRight } from "lucide-react";
import { cn } from "../lib/cn";

export interface MethodItem {
  id: string;
  name: string;
  category: string;
  description: string;
  risk_level: "low" | "medium" | "high" | string;
}

/** Pure filter logic (extracted for unit testing). */
export function filterMethods(
  all: MethodItem[],
  activeCategory: string,
  query: string,
): MethodItem[] {
  const q = query.trim().toLowerCase();
  return all.filter((m) => {
    if (activeCategory !== ALL_CATEGORIES_LABEL && m.category !== activeCategory) return false;
    if (q) {
      const hay = `${m.name} ${m.description}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

export interface MethodsDrawerProps {
  open: boolean;
  onClose: () => void;
  /** Optional pre-fetched payload (skips internal fetch if provided) */
  initialData?: {
    total: number;
    categories: Array<{ name: string; count: number }>;
    methods: MethodItem[];
  } | null;
  /** Optional pre-select category (e.g. user clicked a recommended method) */
  initialCategory?: string;
}

const ALL_CATEGORIES_LABEL = "全部";
const SERVICE_ERROR_MESSAGE =
  "方法库暂时没连上，稍后重试。不会影响已保存的研究材料。";

export function MethodsDrawer({
  open,
  onClose,
  initialData,
  initialCategory = ALL_CATEGORIES_LABEL,
}: MethodsDrawerProps) {
  const [allMethods, setAllMethods] = useState<MethodItem[]>([]);
  const [categories, setCategories] = useState<Array<{ name: string; count: number }>>([]);
  const [total, setTotal] = useState(0);
  const [activeCategory, setActiveCategory] = useState<string>(initialCategory);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fetchedRef = useRef(false);

  // Fetch on first open (or use initialData). The ref guard prevents re-fetch
  // when the user toggles the drawer off and back on.
  useEffect(() => {
    if (!open) return;
    if (initialData) {
      setAllMethods(initialData.methods);
      setCategories(initialData.categories);
      setTotal(initialData.total);
      fetchedRef.current = true;
      return;
    }
    if (fetchedRef.current && allMethods.length > 0) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    const env = import.meta.env as Record<string, string | undefined>;
    const base = env[`VITE_${"API_BASE_URL"}`] ?? "";
    fetch(`${base}/api/capabilities/methods`)
      .then((r) => {
        if (!r.ok) throw new Error("methods_service_unavailable");
        return r.json();
      })
      .then((data) => {
        if (cancelled) return;
        setAllMethods(data.methods ?? []);
        setCategories(data.categories ?? []);
        setTotal(data.total ?? 0);
        fetchedRef.current = true;
      })
      .catch((e) => {
        if (cancelled) return;
        setError(SERVICE_ERROR_MESSAGE);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [open, initialData, allMethods.length]);

  // Reset filter when drawer closes so next open shows everything
  useEffect(() => {
    if (!open) {
      setActiveCategory(ALL_CATEGORIES_LABEL);
      setQuery("");
    }
  }, [open]);

  // Escape key closes
  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const filtered = useMemo(
    () => filterMethods(allMethods, activeCategory, query),
    [allMethods, activeCategory, query],
  );

  if (!open) return null;

  return (
    <>
      <div
        className="design-panel__drawer-backdrop"
        onClick={onClose}
        data-testid="methods-drawer-backdrop"
        aria-hidden="true"
      />
      <aside
        className="design-panel__drawer"
        role="dialog"
        aria-label="StatsPAI 全部方法"
        data-testid="methods-drawer"
      >
        <header className="design-panel__drawer-head">
          <div className="design-panel__drawer-title">
            <Library size={18} />
            <h2>StatsPAI 全部方法</h2>
            <span className="design-panel__drawer-count" data-testid="methods-drawer-total">
              {total > 0 ? `${total} 个` : ""}
            </span>
          </div>
          <button
            type="button"
            className="design-panel__drawer-close"
            onClick={onClose}
            aria-label="关闭抽屉"
            data-testid="methods-drawer-close"
          >
            <X size={18} />
          </button>
        </header>

        <div className="design-panel__drawer-search">
          <Search size={14} />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜索方法名 / 描述（did / bartik / bootstrap）"
            data-testid="methods-drawer-search"
            autoFocus
          />
        </div>

        <div className="design-panel__drawer-chips" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={activeCategory === ALL_CATEGORIES_LABEL}
            onClick={() => setActiveCategory(ALL_CATEGORIES_LABEL)}
            className={cn(
              "design-panel__chip",
              activeCategory === ALL_CATEGORIES_LABEL && "design-panel__chip--active",
            )}
            data-testid="methods-drawer-chip-all"
          >
            全部 <span className="design-panel__chip-count">{total}</span>
          </button>
          {categories.slice(0, 30).map((c) => (
            <button
              key={c.name}
              type="button"
              role="tab"
              aria-selected={activeCategory === c.name}
              onClick={() => setActiveCategory(c.name)}
              className={cn(
                "design-panel__chip",
                activeCategory === c.name && "design-panel__chip--active",
              )}
              data-testid={`methods-drawer-chip-${c.name}`}
            >
              {c.name} <span className="design-panel__chip-count">{c.count}</span>
            </button>
          ))}
        </div>

        <div className="design-panel__drawer-list" data-testid="methods-drawer-list">
          {loading && (
            <div className="design-panel__drawer-empty">加载中…</div>
          )}
          {error && (
            <div className="design-panel__drawer-empty" role="alert">
              {error}
            </div>
          )}
          {!loading && !error && filtered.length === 0 && (
            <div className="design-panel__drawer-empty" data-testid="methods-drawer-empty">
              没有匹配的方法
            </div>
          )}
          {filtered.map((m) => (
            <article
              key={m.id}
              className="design-panel__drawer-item"
              data-testid="methods-drawer-item"
              data-name={m.name}
              data-category={m.category}
            >
              <div className="design-panel__drawer-item-head">
                <h3>
                  <Highlight text={m.name} query={query} />
                </h3>
                <span
                  className={cn(
                    "design-panel__risk",
                    `design-panel__risk--${m.risk_level}`,
                  )}
                  title={`risk: ${m.risk_level}`}
                >
                  {m.risk_level}
                </span>
              </div>
              <div className="design-panel__drawer-item-meta">
                <span className="design-panel__badge design-panel__badge--cat">
                  {m.category}
                </span>
                <span className="design-panel__drawer-item-id">
                  <ChevronRight size={10} />
                  {m.id}
                </span>
              </div>
              {m.description && (
                <p className="design-panel__drawer-item-desc">
                  <Highlight text={m.description} query={query} />
                </p>
              )}
            </article>
          ))}
        </div>

        <footer className="design-panel__drawer-foot">
          <span>
            显示 {filtered.length} / {total}
            {activeCategory !== ALL_CATEGORIES_LABEL ? ` (${activeCategory})` : ""}
            {query ? ` · 搜索 "${query}"` : ""}
          </span>
        </footer>

        {/* Scoped styles — same BEM convention as DesignPanel */}
        <style>{`
          .design-panel__drawer-backdrop {
            position: fixed; inset: 0; z-index: 999;
            background: rgba(0,0,0,0.45);
            backdrop-filter: blur(2px);
          }
          .design-panel__drawer {
            position: fixed; top: 0; right: 0; bottom: 0;
            width: min(440px, 92vw);
            z-index: 1000;
            background: var(--color-panel);
            border-left: 1px solid var(--color-line);
            box-shadow: var(--shadow-panel);
            display: flex; flex-direction: column;
            color: var(--color-ink);
            font-size: 13px;
          }
          .design-panel__drawer-head {
            display: flex; align-items: center; justify-content: space-between;
            padding: 14px 16px;
            border-bottom: 1px solid var(--color-line);
          }
          .design-panel__drawer-title {
            display: flex; align-items: center; gap: 8px;
          }
          .design-panel__drawer-title h2 { margin: 0; font-size: 14px; font-weight: 600; }
          .design-panel__drawer-count {
            color: var(--color-muted); font-size: 12px;
            background: var(--color-panel-soft);
            padding: 2px 8px; border-radius: 999px;
          }
          .design-panel__drawer-close {
            background: transparent; border: 0; color: var(--color-muted);
            cursor: pointer; padding: 4px; border-radius: 6px;
          }
          .design-panel__drawer-close:hover { background: var(--color-panel-soft); color: var(--color-ink); }
          .design-panel__drawer-search {
            display: flex; align-items: center; gap: 6px;
            padding: 8px 16px; color: var(--color-muted);
            border-bottom: 1px solid var(--color-line);
          }
          .design-panel__drawer-search input {
            flex: 1; background: transparent; border: 0; outline: 0;
            color: var(--color-ink); font-size: 13px; padding: 4px 0;
          }
          .design-panel__drawer-chips {
            display: flex; gap: 6px; overflow-x: auto;
            padding: 10px 16px;
            border-bottom: 1px solid var(--color-line);
            scrollbar-width: thin;
          }
          .design-panel__chip {
            flex-shrink: 0;
            background: var(--color-panel-soft);
            color: var(--color-muted);
            border: 1px solid var(--color-line);
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            cursor: pointer;
            display: inline-flex; align-items: center; gap: 4px;
          }
          .design-panel__chip:hover { color: var(--color-ink); border-color: var(--color-line-strong); }
          .design-panel__chip--active {
            background: var(--color-strong);
            color: var(--color-inverse);
            border-color: var(--color-strong);
          }
          .design-panel__chip-count {
            font-size: 10px; opacity: 0.75;
          }
          .design-panel__drawer-list {
            flex: 1; overflow-y: auto;
            padding: 8px 12px;
            display: flex; flex-direction: column; gap: 6px;
          }
          .design-panel__drawer-empty {
            color: var(--color-muted);
            padding: 24px 8px;
            text-align: center;
            font-size: 12px;
          }
          .design-panel__drawer-item {
            background: var(--color-panel-soft);
            border: 1px solid var(--color-line);
            border-radius: 10px;
            padding: 10px 12px;
          }
          .design-panel__drawer-item-head {
            display: flex; align-items: center; justify-content: space-between;
            gap: 8px; margin-bottom: 4px;
          }
          .design-panel__drawer-item-head h3 {
            margin: 0; font-size: 13px; font-weight: 600;
            color: var(--color-strong);
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          }
          .design-panel__risk {
            font-size: 10px; text-transform: uppercase;
            padding: 1px 6px; border-radius: 4px;
            background: var(--color-inverse);
            color: var(--color-muted);
          }
          .design-panel__risk--high { background: rgba(230, 230, 230, 0.12); color: var(--color-strong); }
          .design-panel__risk--medium { background: rgba(230, 230, 230, 0.09); color: var(--color-ink); }
          .design-panel__risk--low { background: rgba(230, 230, 230, 0.06); color: var(--color-muted); }
          .design-panel__drawer-item-meta {
            display: flex; align-items: center; gap: 8px;
            margin-bottom: 4px;
            font-size: 11px;
          }
          .design-panel__badge--cat {
            background: var(--color-inverse);
            color: var(--color-muted);
            padding: 1px 6px; border-radius: 4px;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          }
          .design-panel__drawer-item-id {
            color: var(--color-subtle);
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            display: inline-flex; align-items: center;
          }
          .design-panel__drawer-item-desc {
            margin: 0; color: var(--color-muted);
            font-size: 12px; line-height: 1.5;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
            overflow: hidden;
          }
          .design-panel__drawer-foot {
            padding: 8px 16px;
            border-top: 1px solid var(--color-line);
            color: var(--color-muted);
            font-size: 11px;
          }
          .methods-drawer-mark {
            background: rgba(230, 230, 230, 0.16);
            color: var(--color-strong);
            border-radius: 2px;
            padding: 0 1px;
          }
        `}</style>
      </aside>
    </>
  );
}

/** Highlight matched substring (case-insensitive). Safe for empty query. */
function Highlight({ text, query }: { text: string; query: string }) {
  if (!query.trim()) return <>{text}</>;
  const q = query.trim();
  const lower = text.toLowerCase();
  const idx = lower.indexOf(q.toLowerCase());
  if (idx === -1) return <>{text}</>;
  return (
    <>
      {text.slice(0, idx)}
      <mark className="methods-drawer-mark">{text.slice(idx, idx + q.length)}</mark>
      {text.slice(idx + q.length)}
    </>
  );
}

export default MethodsDrawer;
