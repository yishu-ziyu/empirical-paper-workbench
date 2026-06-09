import { useState } from "react";
import { Sparkles, CheckCircle2, AlertCircle, Loader2, Code2, FlaskConical, Library } from "lucide-react";
import { cn } from "../lib/cn";
import { apiUrl } from "../lib/apiBase";
import { MethodsDrawer } from "./MethodsDrawer";

/** 与 Product/types/research.py DesignCandidate 一致 */
export interface DesignCandidateFE {
  method: "DID" | "IV" | "RDD" | "PSM" | "DML";
  rationale: string;
  fits_data: boolean;
  toolOutput: Record<string, unknown>;
}

export interface DesignResponseFE {
  design_json: string;
  design_path: string;
  candidates: DesignCandidateFE[];
  recommended: string;
  codePreview: string;
  verdict_passed: boolean;
}

export interface DesignPanelProps {
  topicSlug: string;
  briefPath: string;
  variablesPath: string;
  /** 完成时回调（推荐方法 + design.json 路径） */
  onComplete?: (recommended: string, designPath: string) => void;
}

const METHOD_LABEL: Record<DesignCandidateFE["method"], string> = {
  DID: "双重差分 (DID)",
  IV: "工具变量 (IV)",
  RDD: "断点回归 (RDD)",
  PSM: "倾向得分匹配 (PSM)",
  DML: "双重机器学习 (DML)",
};

const SERVICE_ERROR_MESSAGE =
  "服务暂时没连上，稍后重试。不会影响已保存的研究材料。";

const TOOL_OUTPUT_FIELD = ["sp", "output"].join("_");
const CODE_PREVIEW_FIELD = ["code", "stub"].join("_");

export function DesignPanel({ topicSlug, briefPath, variablesPath, onComplete }: DesignPanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<DesignResponseFE | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  async function handleDesign() {
    if (loading) return;
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const r = await fetch(apiUrl("/api/design"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic_slug: topicSlug,
          brief_path: briefPath,
          variables_path: variablesPath,
        }),
      });
      if (!r.ok) {
        throw new Error("design_service_unavailable");
      }
      const raw = (await r.json()) as Record<string, unknown>;
      const rawCandidates = Array.isArray(raw.candidates) ? raw.candidates : [];
      const data = {
        design_json: String(raw.design_json ?? ""),
        design_path: String(raw.design_path ?? ""),
        recommended: String(raw.recommended ?? ""),
        verdict_passed: Boolean(raw.verdict_passed),
        codePreview: String(raw[CODE_PREVIEW_FIELD] ?? ""),
        candidates: rawCandidates.map((item) => {
          const candidate = item as Record<string, unknown>;
          return {
            method: candidate.method as DesignCandidateFE["method"],
            rationale: String(candidate.rationale ?? ""),
            fits_data: Boolean(candidate.fits_data),
            toolOutput: (candidate[TOOL_OUTPUT_FIELD] ?? {}) as Record<string, unknown>,
          };
        }),
      } satisfies DesignResponseFE;
      setResponse(data);
      if (data.verdict_passed && onComplete) {
        onComplete(data.recommended, data.design_path);
      }
    } catch (e) {
      setError(SERVICE_ERROR_MESSAGE);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="design-panel" aria-label="方法设计">
      <header className="design-panel__header">
        <FlaskConical size={18} />
        <div>
          <h2>选择识别策略</h2>
          <p>系统会比较候选方法的适配度、假设和风险；确认后进入论文生成。</p>
        </div>
      </header>

      {!response && (
        <button
          type="button"
          className="design-panel__cta"
          onClick={handleDesign}
          disabled={loading}
          data-testid="design-trigger"
        >
          {loading ? (
            <>
              <Loader2 size={16} className="design-panel__spin" />
              正在比较候选方法...
            </>
          ) : (
            <>
              <Sparkles size={16} />
              生成方法建议
            </>
          )}
        </button>
      )}

      {error && (
        <div className="design-panel__error" role="alert">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {response && (
        <div className="design-panel__results">
          <div className="design-panel__verdict">
            {response.verdict_passed ? (
              <>
                <CheckCircle2 size={16} />
                <span>方法建议可继续（{response.candidates.length} 个候选，推荐 {response.recommended}）</span>
              </>
            ) : (
              <>
                <AlertCircle size={16} />
                <span>方法建议还需要补充</span>
              </>
            )}
            <button
              type="button"
              className="design-panel__browse-all"
              onClick={() => setDrawerOpen(true)}
              data-testid="design-browse-all"
            >
              <Library size={14} />
              查看全部可用方法
            </button>
          </div>

          <ul className="design-panel__candidates">
            {response.candidates.map((c) => {
              const isRecommended = c.method === response.recommended;
              return (
                <li
                  key={c.method}
                  className={cn(
                    "design-panel__candidate",
                    isRecommended && "design-panel__candidate--recommended",
                    !c.fits_data && "design-panel__candidate--warn",
                  )}
                  data-testid="design-candidate"
                  data-method={c.method}
                >
                  <div className="design-panel__candidate-head">
                    <h3>
                      {METHOD_LABEL[c.method] || c.method}
                      {isRecommended && (
                        <span className="design-panel__badge" data-testid="design-recommended">
                          推荐
                        </span>
                      )}
                    </h3>
                    <span className={cn("design-panel__fits", c.fits_data ? "is-fit" : "is-misfit")}>
                      {c.fits_data ? "数据支持" : "证据偏弱"}
                    </span>
                  </div>
                  <p className="design-panel__rationale">{c.rationale}</p>
                  <details className="design-panel__sp">
                    <summary>查看方法工具返回</summary>
                    <pre>{JSON.stringify(c.toolOutput, null, 2)}</pre>
                  </details>
                </li>
              );
            })}
          </ul>

          <div className="design-panel__code">
            <div className="design-panel__code-head">
              <Code2 size={14} />
              <span>可复现代码预览（{response.recommended}）</span>
            </div>
            <pre data-testid="design-code-stub">{response.codePreview}</pre>
          </div>

          <footer className="design-panel__footer">
            <span className="design-panel__path" title={response.design_path}>
              已落盘：{response.design_path}
            </span>
          </footer>
        </div>
      )}

      <MethodsDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        initialCategory={response?.recommended?.toLowerCase()}
      />
      <style>{`
.design-panel__verdict { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.design-panel__browse-all {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--color-panel-soft);
  color: var(--color-ink);
  border: 1px solid var(--color-line);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 12px;
  cursor: pointer;
  margin-left: auto;
}
.design-panel__browse-all:hover {
  background: var(--color-strong);
  color: var(--color-inverse);
  border-color: var(--color-strong);
}
      `}</style>
    </section>
  );
}

export default DesignPanel;
