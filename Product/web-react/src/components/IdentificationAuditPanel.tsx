import { Lock, AlertCircle } from "lucide-react";

/**
 * 6th tab 占位：identification-audit（待解锁 / pre-registration 占位）。
 *
 * 包含 3 张 stub 卡片：
 * 1. Pre-trend test（事件研究图占位）
 * 2. Weak-IV diagnostics（Partial R² + AR p-value 两个数字字段）
 * 3. DAG visualization（文字占位）
 *
 * 所有交互 disabled（read-only）。完全脚手架，不调后端。
 *
 * 业务背景：用户的 1 大痛点是把 reduced-form 当 IV-2SLS 报告；
 * 未来此 tab 应驱动 pre-trend 检验、弱工具变量诊断、DAG 可视化。
 */
export function IdentificationAuditPanel() {
  return (
    <div className="identification-audit" data-testid="identification-audit-panel">
      <header className="identification-audit__header">
        <Lock size={16} />
        <h2>识别策略审计 (待解锁)</h2>
        <p className="identification-audit__subtitle">
          Pre-trend 检验 + 弱 IV 诊断 + DAG 可视化（pre-registration 占位）
        </p>
      </header>

      <div className="identification-audit__cards">
        {/* 1. Pre-trend test */}
        <section
          className="identification-audit__card"
          data-testid="audit-card-pretrend"
        >
          <h3>Pre-trend test</h3>
          <p className="identification-audit__hint">
            事件研究法：处理前各期系数应不显著
          </p>
          <div
            className="identification-audit__chart-placeholder"
            data-testid="audit-pretrend-plot-placeholder"
          >
            [图: pre-trend coefficient plot — 后续接入]
          </div>
          <fieldset disabled className="identification-audit__fieldset">
            <label>
              Pre-trend 检验 p 值（联合）
              <input
                type="number"
                step="0.01"
                defaultValue={0.42}
                readOnly
              />
            </label>
          </fieldset>
        </section>

        {/* 2. Weak-IV diagnostics */}
        <section
          className="identification-audit__card"
          data-testid="audit-card-weakiv"
        >
          <h3>Weak-IV diagnostics</h3>
          <p className="identification-audit__hint">
            第一阶段 F + Partial R² + Anderson-Rubin p
          </p>
          <fieldset disabled className="identification-audit__fieldset">
            <label>
              Partial R²
              <input
                type="number"
                step="0.01"
                defaultValue={0.47}
                readOnly
                data-testid="audit-weakiv-partial-r2"
              />
            </label>
            <label>
              AR p-value
              <input
                type="number"
                step="0.0001"
                defaultValue={0.000003}
                readOnly
                data-testid="audit-weakiv-ar-pvalue"
              />
            </label>
          </fieldset>
        </section>

        {/* 3. DAG */}
        <section
          className="identification-audit__card"
          data-testid="audit-card-dag"
        >
          <h3>DAG visualization</h3>
          <p className="identification-audit__hint">
            因果图：X → Y + 控制变量 + 工具变量
          </p>
          <pre
            className="identification-audit__dag"
            data-testid="audit-dag-placeholder"
          >
{`      [Y]
       ↑
       | β
       |
      [X] ← γ ← [Z: Bartik IV]
       ↑  ↘
       |    ↘
   [控制变量]  [ε]

占位：未来用 graphviz/d3 渲染。`}
          </pre>
        </section>
      </div>

      <footer className="identification-audit__footer">
        <AlertCircle size={14} />
        <span>
          此 tab 当前为脚手架 (scaffold)，所有字段为只读占位。未来接入 pre-registration 工作流时解锁。
        </span>
      </footer>

      <style>{`
        .identification-audit {
          padding: 1.25rem 1.5rem;
          background: #fafafa;
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          opacity: 0.85;
        }
        .identification-audit__header {
          display: flex;
          align-items: baseline;
          gap: 0.6rem;
        }
        .identification-audit__header h2 {
          margin: 0;
          font-size: 1.1rem;
          color: #4b5563;
        }
        .identification-audit__subtitle {
          margin: 0 0 0 auto;
          font-size: 0.8rem;
          color: #6b7280;
        }
        .identification-audit__cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 1rem;
        }
        .identification-audit__card {
          background: #f3f4f6;
          border-radius: 8px;
          padding: 0.9rem 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .identification-audit__card h3 {
          margin: 0;
          font-size: 0.95rem;
          color: #1f2937;
        }
        .identification-audit__hint {
          margin: 0;
          font-size: 0.8rem;
          color: #6b7280;
        }
        .identification-audit__chart-placeholder {
          background: #ffffff;
          border: 1px dashed #9ca3af;
          border-radius: 4px;
          padding: 1.5rem;
          text-align: center;
          color: #9ca3af;
          font-size: 0.8rem;
        }
        .identification-audit__dag {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 4px;
          padding: 0.8rem;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
          font-size: 0.75rem;
          color: #374151;
          margin: 0;
          white-space: pre-wrap;
        }
        .identification-audit__fieldset {
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
          border: none;
          padding: 0;
          margin: 0;
        }
        .identification-audit__fieldset label {
          display: flex;
          flex-direction: column;
          font-size: 0.8rem;
          color: #4b5563;
          gap: 0.2rem;
        }
        .identification-audit__fieldset input {
          padding: 0.3rem 0.5rem;
          border: 1px solid #d1d5db;
          border-radius: 4px;
          font-size: 0.85rem;
          background: #ffffff;
        }
        .identification-audit__footer {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.8rem;
          color: #6b7280;
          background: #fef3c7;
          padding: 0.5rem 0.75rem;
          border-radius: 6px;
        }
      `}</style>
    </div>
  );
}
