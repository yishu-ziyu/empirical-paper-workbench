import { useEffect, useState } from "react";
import { FileArchive, FileText, ShieldCheck } from "lucide-react";

interface VisibleSummaryRow {
  id: string;
  label: string;
  value: string;
}

interface OpenTarget {
  id: string;
  label: string;
  path: string;
  absolute_path?: string;
  type: "pdf" | "docx" | string;
  bytes: number;
  sha256: string;
  open_command?: string[];
}

interface ManualAcceptanceItem {
  id: string;
  label: string;
}

interface FormalPackageSummary {
  status: "ready_for_manual_acceptance" | string;
  visible_summary: VisibleSummaryRow[];
  open_targets: OpenTarget[];
  manual_acceptance: {
    status: string;
    next_action?: string;
    checklist: ManualAcceptanceItem[];
  };
  consistency_checks: Record<string, boolean>;
  blocking_reasons: string[];
  _meta?: {
    service?: string;
    mode?: string;
  };
}

interface ApiErrorResponse {
  error?: {
    code?: string;
    message?: string;
  };
}

interface FormalPackageAcceptancePanelProps {
  projectId: string;
}

function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes)) return "未知大小";
  if (bytes < 1024) return `${bytes} bytes`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function shortSha(sha256: string): string {
  return sha256.length > 16 ? `${sha256.slice(0, 10)}…${sha256.slice(-6)}` : sha256;
}

export function FormalPackageAcceptancePanel({ projectId }: FormalPackageAcceptancePanelProps) {
  const [summary, setSummary] = useState<FormalPackageSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const endpoint = `/api/v1/projects/${projectId}/formal-submission-package-summary`;

    async function loadSummary() {
      setIsLoading(true);
      setErrorCode(null);
      setErrorMessage(null);

      try {
        const response = await fetch(endpoint);
        const payload = (await response.json()) as FormalPackageSummary | ApiErrorResponse;

        if (!response.ok) {
          const apiError = payload as ApiErrorResponse;
          throw {
            code: apiError.error?.code || "formal_package_summary_unavailable",
            message: apiError.error?.message || "正式包验收摘要暂时不可读取。",
          };
        }

        if (!cancelled) {
          setSummary(payload as FormalPackageSummary);
        }
      } catch (error) {
        const fallback = error as { code?: string; message?: string };
        if (!cancelled) {
          setSummary(null);
          setErrorCode(fallback.code || "formal_package_summary_unavailable");
          setErrorMessage(fallback.message || "无法读取正式包验收摘要。");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadSummary();

    return () => {
      cancelled = true;
    };
  }, [projectId]);

  const isSummaryRequired = errorCode === "formal_submission_package_summary_required";
  const blockers = summary?.blocking_reasons ?? [];
  const openTargets = summary?.open_targets ?? [];

  return (
    <section className="formal-package-acceptance" aria-label="正式投稿包验收台">
      <div className="formal-package-acceptance__header">
        <div>
          <span className="eyebrow">只读验收摘要</span>
          <h3>正式投稿包验收台</h3>
        </div>
        <span className="formal-package-acceptance__mode">
          {summary?._meta?.mode || "read_only"}
        </span>
      </div>

      {isLoading && <p className="formal-package-acceptance__state">正在读取正式包 summary API...</p>}

      {!isLoading && errorCode && (
        <div className="formal-package-acceptance__waiting" role="status">
          <strong>{isSummaryRequired ? "等待生成 P6-E1 summary" : "暂时无法读取验收摘要"}</strong>
          <p>{errorMessage}</p>
        </div>
      )}

      {!isLoading && summary && (
        <>
          <div className="formal-package-acceptance__summary">
            {summary.visible_summary.map((row) => (
              <div key={row.id} className="formal-package-acceptance__summary-row">
                <span>{row.label}</span>
                <strong>{row.value}</strong>
              </div>
            ))}
          </div>

          <div className="formal-package-acceptance__targets">
            {openTargets.map((target) => (
              <article key={target.id} className="formal-package-acceptance__target">
                {target.type === "pdf" ? <FileText size={16} /> : <FileArchive size={16} />}
                <div>
                  <strong>{target.type === "pdf" ? "打开 PDF" : target.type === "docx" ? "打开 DOCX" : target.label}</strong>
                  <span>{target.path}</span>
                  <code>{formatBytes(target.bytes)} · {shortSha(target.sha256)}</code>
                  <code>{(target.open_command || ["open", target.path]).join(" ")}</code>
                </div>
              </article>
            ))}
          </div>

          <div className="formal-package-acceptance__grid">
            <div className="formal-package-acceptance__checklist">
              <strong>人工验收清单</strong>
              <ul>
                {summary.manual_acceptance.checklist.map((item) => (
                  <li key={item.id}>{item.label}</li>
                ))}
              </ul>
            </div>

            <div className="formal-package-acceptance__checks">
              <strong>一致性检查</strong>
              <ul>
                {Object.entries(summary.consistency_checks).map(([key, passed]) => (
                  <li key={key}>
                    <ShieldCheck size={13} />
                    <span>{key}</span>
                    <em>{passed ? "通过" : "待处理"}</em>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="formal-package-acceptance__blockers">
            <strong>阻断原因</strong>
            {blockers.length > 0 ? (
              <ul>
                {blockers.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            ) : (
              <p>当前没有阻断原因，可以进入人工打开检查。</p>
            )}
          </div>
        </>
      )}
    </section>
  );
}
