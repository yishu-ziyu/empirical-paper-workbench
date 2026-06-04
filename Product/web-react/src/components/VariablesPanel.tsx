import { useState, useEffect } from "react";
import {
  Database,
  Loader2,
  CheckCircle2,
  XCircle,
  FileText,
  Sparkles,
  AlertCircle,
} from "lucide-react";
import { cn } from "../lib/cn";

/** 与 Product/types/research.py 对齐 */
export type VariableRole = "X" | "Y" | "control" | "mediator" | "moderator";

export interface Variable {
  role: VariableRole;
  dataset_column: string;
  semantic_label: string;
  description: string;
  reference_papers: string[];
}

export interface VariablesResponse {
  variables_yaml: string;
  variables_path: string;
  variables: Variable[];
  verdict_passed: boolean;
}

export type DatasetName = "CFPS" | "CHIP" | "CHARLS" | "custom";

const DATASET_OPTIONS: { value: DatasetName; label: string; hint: string }[] = [
  { value: "CFPS", label: "CFPS (中国家庭追踪调查)", hint: "工业机器人/就业/工资研究主流" },
  { value: "CHIP", label: "CHIP (中国家庭收入调查)", hint: "收入不平等主题" },
  { value: "CHARLS", label: "CHARLS (中国健康与养老追踪调查)", hint: "中老年劳动参与" },
  { value: "custom", label: "自定义数据集", hint: "需在 data/{name}/schema.yaml 准备" },
];

const ROLE_BADGE: Record<VariableRole, { color: string; label: string }> = {
  X: { color: "var(--variables-x, #c1440e)", label: "X 解释变量" },
  Y: { color: "var(--variables-y, #1f6feb)", label: "Y 被解释变量" },
  control: { color: "var(--variables-control, #6e7681)", label: "控制变量" },
  mediator: { color: "var(--variables-mediator, #8b5cf6)", label: "中介变量" },
  moderator: { color: "var(--variables-moderator, #0e8a86)", label: "调节变量" },
};

export interface VariablesPanelProps {
  briefPath: string;
  topicSlug: string;
  /** 默认选中的数据集 */
  defaultDataset?: DatasetName;
  /** 识别完成时回调（传回 variables 列表 + 落盘路径） */
  onComplete?: (variables: Variable[], variablesPath: string) => void;
}

/**
 * L3 数据变量 tab: 用户选数据集 → 点"识别变量" → POST /api/variables
 * 拿到 list[Variable] 后渲染卡片网格 + verdict badge。
 */
export function VariablesPanel({
  briefPath,
  topicSlug,
  defaultDataset = "CFPS",
  onComplete,
}: VariablesPanelProps) {
  const [dataset, setDataset] = useState<DatasetName>(defaultDataset);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<VariablesResponse | null>(null);
  const [autoFired, setAutoFired] = useState(false);

  // 首次进入自动触发一次（确认 brief 后立即跑变量识别）
  useEffect(() => {
    if (autoFired) return;
    if (!briefPath || !topicSlug) return;
    setAutoFired(true);
    void run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [briefPath, topicSlug]);

  async function run() {
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch("/api/variables", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic_slug: topicSlug,
          brief_path: briefPath,
          dataset_name: dataset,
        }),
      });
      if (!resp.ok) {
        const detail = await resp.text();
        throw new Error(`HTTP ${resp.status}: ${detail || resp.statusText}`);
      }
      const data = (await resp.json()) as VariablesResponse;
      setResponse(data);
      if (data.verdict_passed) {
        onComplete?.(data.variables, data.variables_path);
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  function changeDataset(next: DatasetName) {
    setDataset(next);
    setResponse(null);
    setError(null);
  }

  const variables = response?.variables ?? [];
  const rolesPresent = new Set(variables.map((v) => v.role));

  return (
    <div className="variables-panel" data-testid="variables-panel">
      {/* ── 顶部：数据集选择 + 状态 ── */}
      <div className="variables-panel__header">
        <div className="variables-panel__heading">
          <Database className="variables-panel__icon" aria-hidden />
          <div>
            <h2>识别研究变量</h2>
            <p className="variables-panel__hint">
              基于数据集 schema + 研究简报，由 LLM 把列名映射到研究变量。
            </p>
          </div>
        </div>

        <div className="variables-panel__controls">
          <label className="variables-panel__dataset-label">
            <span>数据集</span>
            <select
              className="variables-panel__select"
              value={dataset}
              onChange={(e) => changeDataset(e.target.value as DatasetName)}
              disabled={loading}
              data-testid="variables-dataset-select"
            >
              {DATASET_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="variables-panel__button"
            onClick={() => void run()}
            disabled={loading}
            data-testid="variables-run-button"
          >
            {loading ? (
              <>
                <Loader2 className="variables-panel__spinner" aria-hidden />
                识别中…
              </>
            ) : (
              <>
                <Sparkles aria-hidden />
                {response ? "重新识别变量" : "识别变量"}
              </>
            )}
          </button>
        </div>
        <p className="variables-panel__dataset-hint">
          {DATASET_OPTIONS.find((o) => o.value === dataset)?.hint}
        </p>
      </div>

      {/* ── 错误 / 状态条 ── */}
      {error ? (
        <div className="variables-panel__error" role="alert" data-testid="variables-error">
          <AlertCircle aria-hidden />
          <span>{error}</span>
        </div>
      ) : null}

      {loading ? (
        <div className="variables-panel__loading" data-testid="variables-loading">
          <Loader2 className="variables-panel__spinner" aria-hidden />
          <span>LLM 解析 schema 中…</span>
        </div>
      ) : null}

      {/* ── Verdict + 产物路径 ── */}
      {response ? (
        <div className="variables-panel__verdict" data-testid="variables-verdict">
          {response.verdict_passed ? (
            <span className="variables-panel__verdict-passed">
              <CheckCircle2 aria-hidden /> verdict 通过
            </span>
          ) : (
            <span className="variables-panel__verdict-failed">
              <XCircle aria-hidden /> verdict 未通过（变量数不足或 role 非法）
            </span>
          )}
          <span className="variables-panel__verdict-path" title={response.variables_path}>
            <FileText aria-hidden /> {response.variables_path}
          </span>
        </div>
      ) : null}

      {/* ── 变量卡片网格 ── */}
      {variables.length > 0 ? (
        <div className="variables-panel__grid" data-testid="variables-grid">
          {variables.map((v, idx) => {
            const badge = ROLE_BADGE[v.role];
            return (
              <article
                key={`${v.dataset_column}-${idx}`}
                className="variables-card"
                data-testid={`variables-card-${v.role}`}
                style={{ borderLeftColor: badge.color }}
              >
                <header className="variables-card__header">
                  <span
                    className="variables-card__role"
                    style={{ backgroundColor: badge.color }}
                    title={badge.label}
                  >
                    {v.role}
                  </span>
                  <h3 className="variables-card__label">{v.semantic_label}</h3>
                </header>
                <dl className="variables-card__meta">
                  <dt>列名</dt>
                  <dd>
                    <code>{v.dataset_column}</code>
                  </dd>
                </dl>
                <p className="variables-card__description">{v.description}</p>
                {v.reference_papers.length > 0 ? (
                  <div className="variables-card__papers">
                    <span className="variables-card__papers-title">引用文献</span>
                    <ul>
                      {v.reference_papers.map((p, i) => (
                        <li key={i}>{p}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      ) : null}

      {/* ── 底部 role 覆盖提示 ── */}
      {variables.length > 0 ? (
        <footer className="variables-panel__footer" data-testid="variables-footer">
          <span>已覆盖 role: </span>
          {(["X", "Y", "control", "mediator", "moderator"] as VariableRole[]).map((r) => {
            const present = rolesPresent.has(r);
            return (
              <span
                key={r}
                className={cn(
                  "variables-panel__role-chip",
                  present && "variables-panel__role-chip--present"
                )}
              >
                {present ? <CheckCircle2 aria-hidden /> : <XCircle aria-hidden />}
                {r}
              </span>
            );
          })}
        </footer>
      ) : null}
    </div>
  );
}

export default VariablesPanel;
