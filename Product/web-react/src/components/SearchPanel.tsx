import { useState } from "react";
import { cn } from "../lib/cn";
import { Search, FileText, Check, X, Loader2, AlertCircle } from "lucide-react";

export interface Paper {
  title: string;
  authors: string[];
  year: number;
  abstract: string;
  arxiv_id: string;
  relevance_score: number;
  accepted: boolean;
}

export interface SearchResponse {
  literature_markdown: string;
  literature_path: string;
  papers: Paper[];
  verdict_passed: boolean;
}

interface SearchPanelProps {
  /** 任务书 markdown 路径（必填）*/
  briefPath: string;
  /** 任务 slug（必填）*/
  topicSlug: string;
  /** 完成后回调（含 literature_path + papers）*/
  onComplete?: (papers: Paper[], literaturePath: string) => void;
}

interface RunState {
  loading: boolean;
  error: string | null;
  response: SearchResponse | null;
  /** 用户手动排除的 arxiv_id 集合 */
  excluded: Set<string>;
}

const SCORE_BADGE_CLASS = (s: number): string => {
  if (s >= 0.8) return "search-score search-score--high";
  if (s >= 0.5) return "search-score search-score--mid";
  return "search-score search-score--low";
};

export function SearchPanel({ briefPath, topicSlug, onComplete }: SearchPanelProps) {
  const [state, setState] = useState<RunState>({
    loading: false,
    error: null,
    response: null,
    excluded: new Set(),
  });

  const triggerSearch = async () => {
    setState({ loading: true, error: null, response: null, excluded: new Set() });
    try {
      // vite 7 http-proxy 不转 SSE, 同时 vite 的 public base URL (/react/)
      // 会拒绝 "/api/..." 这种绝对路径, 返回 404 "did you mean to visit /react/api/..."
      // 改用绝对 URL + 后端 CORS, 与 BriefPanel 一致 (SSE plumbing 必走绝对 URL)
      const base = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";
      const url = `${base}/api/search`;
      const resp = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic_slug: topicSlug, brief_path: briefPath }),
      });
      if (!resp.ok) {
        const detail = await resp.text();
        throw new Error(`HTTP ${resp.status}: ${detail}`);
      }
      const data = (await resp.json()) as SearchResponse;
      setState((prev) => ({ ...prev, loading: false, response: data }));
      if (data.verdict_passed && onComplete) {
        onComplete(data.papers, data.literature_path);
      }
    } catch (e) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: e instanceof Error ? e.message : String(e),
      }));
    }
  };

  const toggleExclude = (arxivId: string) => {
    setState((prev) => {
      const next = new Set(prev.excluded);
      if (next.has(arxivId)) {
        next.delete(arxivId);
      } else {
        next.add(arxivId);
      }
      return { ...prev, excluded: next };
    });
  };

  return (
    <section aria-label="递归搜索" className="search-panel" data-testid="search-panel">
      <header className="search-panel__header">
        <span className="eyebrow">第 2 阶段：递归搜索 arxiv + LLM 重排</span>
        <h2>从 arxiv 召回 8-12 篇相关论文</h2>
        <p>
          任务书已确认：<code data-testid="search-brief-path">{briefPath}</code>
        </p>
      </header>

      {!state.response && !state.loading && !state.error && (
        <div className="search-panel__cta">
          <p className="search-panel__hint">
            LLM 将基于研究简报生成 3-5 个英文 arxiv 检索词，命中 arxiv 后再由 LLM 重排打分。
          </p>
          <button
            className="btn btn--primary btn--large"
            type="button"
            onClick={triggerSearch}
            data-testid="search-trigger"
            disabled={!briefPath}
          >
            <Search size={16} />
            <span>开始搜索</span>
          </button>
        </div>
      )}

      {state.loading && (
        <div className="search-panel__loading" data-testid="search-loading">
          <Loader2 size={20} className="spin" />
          <span>arxiv 检索 + LLM 重排中...</span>
        </div>
      )}

      {state.error && (
        <div className="search-panel__error" data-testid="search-error" role="alert">
          <AlertCircle size={16} />
          <span>搜索失败：{state.error}</span>
          <button className="btn btn--ghost" type="button" onClick={triggerSearch}>
            重试
          </button>
        </div>
      )}

      {state.response && (
        <>
          <div className="search-panel__verdict">
            <span
              className={cn(
                "verdict-badge",
                state.response.verdict_passed
                  ? "verdict-badge--pass"
                  : "verdict-badge--fail",
              )}
              data-testid="search-verdict"
            >
              {state.response.verdict_passed ? "verdict pass" : "verdict fail"}
            </span>
            <span className="search-panel__count">
              {state.response.papers.length} 篇候选 / 已排除 {state.excluded.size} 篇
            </span>
            <button
              className="btn btn--ghost"
              type="button"
              onClick={triggerSearch}
              data-testid="search-retrigger"
            >
              重新搜索
            </button>
          </div>

          <ol className="search-panel__list" data-testid="search-paper-list">
            {state.response.papers.map((p) => {
              const excluded = state.excluded.has(p.arxiv_id);
              return (
                <li
                  key={p.arxiv_id}
                  className={cn("search-paper", excluded && "search-paper--excluded")}
                  data-testid="search-paper"
                >
                  <div className="search-paper__header">
                    <h3 className="search-paper__title">{p.title}</h3>
                    <span className={SCORE_BADGE_CLASS(p.relevance_score)}>
                      {p.relevance_score.toFixed(2)}
                    </span>
                  </div>
                  <div className="search-paper__meta">
                    <span>{p.authors.join(", ") || "未知作者"}</span>
                    <span>· {p.year}</span>
                    <span>· arXiv:{p.arxiv_id}</span>
                  </div>
                  <p className="search-paper__abstract">{p.abstract}</p>
                  <div className="search-paper__actions">
                    <button
                      className={cn(
                        "btn",
                        "btn--small",
                        excluded ? "btn--ghost" : "btn--primary",
                      )}
                      type="button"
                      onClick={() => toggleExclude(p.arxiv_id)}
                      data-testid="search-toggle-exclude"
                    >
                      {excluded ? (
                        <>
                          <X size={12} />
                          <span>已排除 · 恢复</span>
                        </>
                      ) : (
                        <>
                          <Check size={12} />
                          <span>采纳</span>
                        </>
                      )}
                    </button>
                  </div>
                </li>
              );
            })}
          </ol>

          {state.response.literature_markdown && (
            <details className="search-panel__markdown" data-testid="search-markdown">
              <summary>
                <FileText size={14} />
                <span>查看 literature.md 预览（已写入 {state.response.literature_path}）</span>
              </summary>
              <pre>{state.response.literature_markdown.slice(0, 4000)}</pre>
            </details>
          )}
        </>
      )}
    </section>
  );
}
