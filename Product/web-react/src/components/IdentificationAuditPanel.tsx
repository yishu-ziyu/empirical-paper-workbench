import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Loader2, XCircle } from "lucide-react";

/**
 * 6th tab — Identification Audit (real statspai diagnostics).
 *
 * Task 44 (ui-gap-fill) — 把占位的 3 张卡换成真实 statspai 输出.
 *
 * 数据流: resultsPath + designPath (来自 App.tsx executionResult / designResult)
 *   → POST /api/identification/audit
 *   → Product.backend.identification_audit_service
 *   → 返回 { pretrend, weak_iv, dag, method }
 *
 * 失败兜底 (BDD 行为 3):
 *   - 后端不可达 / statspai 没装 / results.json 缺字段
 *   - service 返回 { error, reason } + 各 card source=unavailable
 *   - 前端展示明确错误 + 各 card 显示 N/A, 不崩
 *
 * 业务背景: 用户 3 月草稿把 reduced-form 当 IV-2SLS 报告, 导致
 *   ISEI/兼职假显著. 此 tab 现在强提示 weak-IV + AR p-value,
 *   让用户必须先看 statspai 真实诊断, 再下结论.
 */

export interface IdentificationAuditPanelProps {
  resultsPath: string;
  designPath: string;
}

interface PretrendCoefficient {
  period: number;
  estimate: number;
  se: number;
  pvalue: number | null;
  ci_lower?: number | null;
  ci_upper?: number | null;
}

interface IdentificationAuditPayload {
  method?: string | null;
  pretrend: {
    source: "statspai" | "results_json" | "unavailable";
    joint_pvalue?: number | null;
    joint_statistic?: number | null;
    n_pre_periods?: number | null;
    coefficients?: PretrendCoefficient[];
  };
  weak_iv: {
    source: "statspai" | "results_json" | "unavailable";
    partial_r2?: number | null;
    f_statistic?: number | null;
    n_obs?: number | null;
    ar_pvalue?: number | null;
    ar_ci_lower?: number | null;
    ar_ci_upper?: number | null;
  };
  dag: {
    source: "statspai" | "design_json" | "default" | "unavailable";
    spec?: string;
    mermaid?: string;
    adjustment_sets?: string[][];
  };
  error?: string;
  reason?: string;
  warnings?: string[];
}

type FetchState =
  | { kind: "loading" }
  | { kind: "ok"; data: IdentificationAuditPayload }
  | { kind: "error"; message: string };

const API_PATH = "/api/identification/audit";

export function IdentificationAuditPanel({
  resultsPath,
  designPath,
}: IdentificationAuditPanelProps) {
  const [state, setState] = useState<FetchState>({ kind: "loading" });

  useEffect(() => {
    const ctrl = new AbortController();
    const base = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";
    const url = `${base}${API_PATH}`;

    setState({ kind: "loading" });
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ results_path: resultsPath, design_path: designPath }),
      signal: ctrl.signal,
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${await res.text()}`);
        }
        return res.json() as Promise<IdentificationAuditPayload>;
      })
      .then((data) => {
        setState({ kind: "ok", data });
      })
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        const message = err instanceof Error ? err.message : String(err);
        setState({ kind: "error", message });
      });

    return () => ctrl.abort();
  }, [resultsPath, designPath]);

  return (
    <div className="identification-audit" data-testid="identification-audit-panel">
      <header className="identification-audit__header">
        <CheckCircle2 size={16} />
        <h2>识别策略审计</h2>
        <p className="identification-audit__subtitle">
          Pre-trend + 弱 IV 诊断 + DAG · 来自 statspai 真实输出
        </p>
      </header>

      {state.kind === "loading" ? <LoadingSkeleton /> : null}
      {state.kind === "error" ? <ErrorCard message={state.message} /> : null}
      {state.kind === "ok" ? (
        <OkContent payload={state.data} paths={{ resultsPath, designPath }} />
      ) : null}

      <style>{`
        .identification-audit {
          padding: 1.25rem 1.5rem;
          background: #fafafa;
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .identification-audit__header {
          display: flex;
          align-items: baseline;
          gap: 0.6rem;
        }
        .identification-audit__header h2 {
          margin: 0;
          font-size: 1.1rem;
          color: #1f2937;
        }
        .identification-audit__subtitle {
          margin: 0 0 0 auto;
          font-size: 0.8rem;
          color: #6b7280;
        }
        .identification-audit__cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 1rem;
        }
        .identification-audit__card {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 0.9rem 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.6rem;
        }
        .identification-audit__card h3 {
          margin: 0;
          font-size: 0.95rem;
          color: #1f2937;
          display: flex;
          align-items: center;
          gap: 0.4rem;
        }
        .identification-audit__hint {
          margin: 0;
          font-size: 0.78rem;
          color: #6b7280;
        }
        .identification-audit__source-tag {
          font-size: 0.7rem;
          padding: 0.15rem 0.45rem;
          border-radius: 999px;
          background: #e0e7ff;
          color: #3730a3;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
          margin-left: auto;
        }
        .identification-audit__source-tag--unavailable {
          background: #fee2e2;
          color: #991b1b;
        }
        .identification-audit__source-tag--default {
          background: #fef3c7;
          color: #92400e;
        }
        .identification-audit__kv {
          display: grid;
          grid-template-columns: max-content 1fr;
          gap: 0.3rem 0.8rem;
          font-size: 0.82rem;
        }
        .identification-audit__kv dt {
          color: #4b5563;
        }
        .identification-audit__kv dd {
          margin: 0;
          color: #111827;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
        }
        .identification-audit__coefs {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.78rem;
        }
        .identification-audit__coefs th,
        .identification-audit__coefs td {
          padding: 0.25rem 0.5rem;
          text-align: right;
          border-bottom: 1px solid #f3f4f6;
        }
        .identification-audit__coefs th {
          background: #f9fafb;
          color: #4b5563;
          font-weight: 500;
        }
        .identification-audit__coefs td:first-child,
        .identification-audit__coefs th:first-child {
          text-align: left;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
        }
        .identification-audit__coefs tr.is-pre td {
          color: #4b5563;
        }
        .identification-audit__coefs tr.is-post td {
          color: #111827;
          font-weight: 500;
        }
        .identification-audit__dag {
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 4px;
          padding: 0.7rem;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
          font-size: 0.75rem;
          color: #1f2937;
          margin: 0;
          white-space: pre-wrap;
          overflow-x: auto;
          max-height: 220px;
        }
        .identification-audit__skeleton {
          background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 50%, #f3f4f6 100%);
          background-size: 200% 100%;
          animation: ident-shimmer 1.2s ease-in-out infinite;
          border-radius: 6px;
          height: 120px;
        }
        @keyframes ident-shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
        .identification-audit__skeleton-row {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
          align-items: center;
          color: #6b7280;
          font-size: 0.82rem;
        }
        .identification-audit__error {
          background: #fef2f2;
          border: 1px solid #fecaca;
          color: #991b1b;
          padding: 0.7rem 0.9rem;
          border-radius: 6px;
          display: flex;
          align-items: flex-start;
          gap: 0.5rem;
          font-size: 0.85rem;
        }
        .identification-audit__error code {
          background: #fee2e2;
          padding: 0.1rem 0.3rem;
          border-radius: 3px;
          font-size: 0.78rem;
        }
        .identification-audit__warnings {
          background: #fffbeb;
          border: 1px solid #fde68a;
          color: #78350f;
          padding: 0.6rem 0.85rem;
          border-radius: 6px;
          font-size: 0.8rem;
        }
        .identification-audit__warnings ul {
          margin: 0.3rem 0 0 0;
          padding-left: 1.2rem;
        }
        .identification-audit__na {
          color: #9ca3af;
          font-style: italic;
          font-size: 0.82rem;
        }
        .identification-audit__paths {
          font-size: 0.72rem;
          color: #6b7280;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
        }
      `}</style>
    </div>
  );
}

// ── sub-views ────────────────────────────────────────────────────────────

function LoadingSkeleton() {
  return (
    <div data-testid="audit-loading" className="identification-audit__cards">
      {[0, 1, 2].map((i) => (
        <div key={i} className="identification-audit__skeleton" />
      ))}
    </div>
  );
}

function ErrorCard({ message }: { message: string }) {
  return (
    <div className="identification-audit__error" data-testid="audit-error">
      <XCircle size={16} />
      <div>
        <strong>审计 API 调用失败。</strong>
        <div style={{ marginTop: "0.2rem" }}>
          <code>{message}</code>
        </div>
        <div style={{ marginTop: "0.3rem", fontSize: "0.78rem" }}>
          6th tab 3 张卡将显示 N/A. 检查后端 <code>uvicorn Product.app:app</code> 是否运行, 以及
          <code> VITE_API_BASE_URL</code> 环境变量.
        </div>
      </div>
    </div>
  );
}

function OkContent({
  payload,
  paths,
}: {
  payload: IdentificationAuditPayload;
  paths: { resultsPath: string; designPath: string };
}) {
  return (
    <>
      {payload.error ? <TopError error={payload.error} reason={payload.reason} /> : null}

      {payload.warnings && payload.warnings.length > 0 ? (
        <div className="identification-audit__warnings" data-testid="audit-warnings">
          <strong>
            <AlertCircle size={12} style={{ verticalAlign: "middle" }} /> 注意事项
          </strong>
          <ul>
            {payload.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="identification-audit__cards" data-testid="audit-cards">
        <PretrendCard pretrend={payload.pretrend} method={payload.method} />
        <WeakIvCard weakIv={payload.weak_iv} />
        <DagCard dag={payload.dag} />
      </div>

      <div className="identification-audit__paths" data-testid="audit-paths">
        results: <code>{paths.resultsPath}</code> &nbsp;|&nbsp; design:{" "}
        <code>{paths.designPath}</code>
        {payload.method ? (
          <>
            {" "}
            | method: <code>{payload.method}</code>
          </>
        ) : null}
      </div>
    </>
  );
}

function TopError({ error, reason }: { error: string; reason?: string }) {
  return (
    <div className="identification-audit__error" data-testid="audit-top-error">
      <XCircle size={16} />
      <div>
        <strong>审计数据不完整: {error}</strong>
        {reason ? (
          <div style={{ marginTop: "0.2rem", fontSize: "0.8rem" }}>{reason}</div>
        ) : null}
      </div>
    </div>
  );
}

function SourceTag({ source }: { source: string }) {
  const cls =
    source === "unavailable"
      ? "identification-audit__source-tag--unavailable"
      : source === "default"
        ? "identification-audit__source-tag--default"
        : "";
  return (
    <span className={`identification-audit__source-tag ${cls}`} data-source={source}>
      {source}
    </span>
  );
}

function PretrendCard({
  pretrend,
  method,
}: {
  pretrend: IdentificationAuditPayload["pretrend"];
  method?: string | null;
}) {
  const coefs = pretrend.coefficients ?? [];
  const isUnavail = pretrend.source === "unavailable";
  return (
    <section
      className="identification-audit__card"
      data-testid="audit-card-pretrend"
    >
      <h3>
        Pre-trend test
        <SourceTag source={pretrend.source} />
      </h3>
      <p className="identification-audit__hint">
        事件研究：处理前各期系数应不显著
        {method ? ` (识别策略: ${method})` : null}
      </p>
      {isUnavail ? (
        <p className="identification-audit__na">N/A — statspai 诊断数据未生成</p>
      ) : coefs.length === 0 ? (
        <>
          <p className="identification-audit__na">无事件研究系数 (仅联合检验)</p>
          <dl className="identification-audit__kv">
            <dt>联合 p</dt>
            <dd data-testid="audit-pretrend-joint-pvalue">
              {formatP(pretrend.joint_pvalue)}
            </dd>
          </dl>
        </>
      ) : (
        <>
          <dl className="identification-audit__kv">
            <dt>联合 p</dt>
            <dd data-testid="audit-pretrend-joint-pvalue">
              {formatP(pretrend.joint_pvalue)}
            </dd>
            <dt>pre 期数</dt>
            <dd data-testid="audit-pretrend-n-pre">{pretrend.n_pre_periods ?? "?"}</dd>
          </dl>
          <table className="identification-audit__coefs" data-testid="audit-pretrend-table">
            <thead>
              <tr>
                <th>period</th>
                <th>est</th>
                <th>se</th>
                <th>p</th>
              </tr>
            </thead>
            <tbody>
              {coefs.map((c, i) => (
                <tr
                  key={`${c.period}-${i}`}
                  className={c.period < 0 ? "is-pre" : c.period === 0 ? "is-post" : "is-post"}
                >
                  <td>t={c.period >= 0 ? `+${c.period}` : c.period}</td>
                  <td>{formatNum(c.estimate)}</td>
                  <td>{formatNum(c.se)}</td>
                  <td>{formatP(c.pvalue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}

function WeakIvCard({
  weakIv,
}: {
  weakIv: IdentificationAuditPayload["weak_iv"];
}) {
  const isUnavail = weakIv.source === "unavailable";
  const arP = weakIv.ar_pvalue;
  const fStat = weakIv.f_statistic;
  // 业务规则: AR p 是 size-correct under weak IV 的核心信号
  const arFlag = arP == null ? null : arP < 0.05 ? "ok" : "weak";
  const fFlag = fStat == null ? null : fStat >= 10 ? "ok" : "weak";

  return (
    <section className="identification-audit__card" data-testid="audit-card-weakiv">
      <h3>
        Weak-IV diagnostics
        <SourceTag source={weakIv.source} />
      </h3>
      <p className="identification-audit__hint">
        第一阶段 F + Partial R² + Anderson-Rubin p (AR size-correct under weak IV)
      </p>
      {isUnavail ? (
        <p className="identification-audit__na">
          N/A — results.json 缺 first_stage 字段. 跑 statspai iv_diag 时填充.
        </p>
      ) : (
        <dl className="identification-audit__kv">
          <dt>Partial R²</dt>
          <dd data-testid="audit-weakiv-partial-r2">{formatNum(weakIv.partial_r2, 3)}</dd>
          <dt>F statistic</dt>
          <dd data-testid="audit-weakiv-f-statistic">
            {formatNum(fStat, 2)}{" "}
            {fFlag ? (
              <span
                style={{
                  color: fFlag === "ok" ? "#15803d" : "#b91c1c",
                  fontSize: "0.72rem",
                  marginLeft: "0.3rem",
                }}
              >
                {fFlag === "ok" ? "(F≥10, 强)" : "(F<10, 弱 IV 警示)"}
              </span>
            ) : null}
          </dd>
          <dt>N obs</dt>
          <dd>{weakIv.n_obs ?? "—"}</dd>
          <dt>AR p-value</dt>
          <dd data-testid="audit-weakiv-ar-pvalue">
            {formatP(arP)}{" "}
            {arFlag ? (
              <span
                style={{
                  color: arFlag === "ok" ? "#15803d" : "#b91c1c",
                  fontSize: "0.72rem",
                  marginLeft: "0.3rem",
                }}
              >
                {arFlag === "ok" ? "(拒绝 H₀)" : "(不拒绝 H₀)"}
              </span>
            ) : null}
          </dd>
          <dt>AR CI 95%</dt>
          <dd>
            [{formatNum(weakIv.ar_ci_lower, 3)}, {formatNum(weakIv.ar_ci_upper, 3)}]
          </dd>
        </dl>
      )}
    </section>
  );
}

function DagCard({ dag }: { dag: IdentificationAuditPayload["dag"] }) {
  const isUnavail = dag.source === "unavailable";
  const mermaid = dag.mermaid || "graph LR\n  X[未配置]";
  return (
    <section className="identification-audit__card" data-testid="audit-card-dag">
      <h3>
        DAG visualization
        <SourceTag source={dag.source} />
      </h3>
      <p className="identification-audit__hint">
        因果图: X → Y + 控制变量 + 工具变量 (mermaid text)
      </p>
      {isUnavail ? (
        <p className="identification-audit__na">N/A — design.json 缺 causal_graph 字段</p>
      ) : (
        <>
          {dag.spec ? (
            <div style={{ fontSize: "0.72rem", color: "#6b7280" }}>
              spec: <code>{dag.spec}</code>
            </div>
          ) : null}
          <pre
            className="identification-audit__dag"
            data-testid="audit-dag-mermaid"
          >
            {mermaid}
          </pre>
          {dag.adjustment_sets && dag.adjustment_sets.length > 0 ? (
            <div style={{ fontSize: "0.75rem", color: "#4b5563" }}>
              <strong>Adjustment sets:</strong>{" "}
              {dag.adjustment_sets.map((s, i) => (
                <code key={i} style={{ marginRight: "0.4rem" }}>
                  {`{${s.join(", ")}}`}
                </code>
              ))}
            </div>
          ) : null}
        </>
      )}
    </section>
  );
}

// ── formatters ───────────────────────────────────────────────────────────

function formatNum(v: number | null | undefined, digits = 3): string {
  if (v == null || Number.isNaN(v)) return "—";
  if (v === 0) return "0";
  if (Math.abs(v) < 0.001) return v.toExponential(2);
  return v.toFixed(digits);
}

function formatP(v: number | null | undefined): string {
  if (v == null || Number.isNaN(v)) return "—";
  if (v < 0.001) return "< 0.001";
  return v.toFixed(3);
}

// Avoid TS unused-import warning if Loader2 not used; keep available for future loading state
void Loader2;
