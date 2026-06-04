import { useCallback, useState } from "react";

/**
 * BriefPanel — 任务书 LLM 扩写面板 (L1 brief tab).
 *
 * BDD ref: spec §6.1 row 1
 * Given: 用户输入 topic (e.g. "工业机器人对城市制造业就业结构的影响——基于 CFPS 2010-2022")
 * When: 点 "生成研究简报" 按钮
 * Then: 4 段 markdown 渲染 + verdict badge + 回调 onComplete(markdown, path)
 */
export interface BriefResult {
  markdown: string;
  path: string;
}

export interface BriefPanelProps {
  topic: string;
  onComplete?: (brief: BriefResult) => void;
}

interface ApiResponse {
  brief_markdown: string;
  brief_path: string;
  verdict_passed: boolean;
}

type Status = "idle" | "loading" | "success" | "error";

export function BriefPanel({ topic, onComplete }: BriefPanelProps) {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<ApiResponse | null>(null);

  const handleGenerate = useCallback(async () => {
    setStatus("loading");
    setError(null);
    setResponse(null);
    try {
      const res = await fetch("/api/brief", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(`HTTP ${res.status}: ${detail}`);
      }
      const data = (await res.json()) as ApiResponse;
      setResponse(data);
      setStatus("success");
      if (data.verdict_passed && onComplete) {
        onComplete({ markdown: data.brief_markdown, path: data.brief_path });
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      setStatus("error");
    }
  }, [topic, onComplete]);

  return (
    <section aria-label="任务书扩写" className="task-brief">
      <div className="task-brief__main">
        <div className="task-brief__lead">
          <span className="eyebrow">第 1 阶段：研究简报</span>
          <h2>生成研究简报</h2>
          <p>研究题目：{topic || "（未填）"}</p>
        </div>

        <div className="task-brief__confirm-actions">
          <button
            type="button"
            className="btn btn--primary"
            onClick={handleGenerate}
            disabled={status === "loading" || !topic.trim()}
          >
            {status === "loading" ? "生成中…" : "生成研究简报"}
          </button>
        </div>

        {status === "error" && error && (
          <div className="task-brief__error" role="alert">
            <strong>错误：</strong> {error}
          </div>
        )}

        {status === "success" && response && (
          <div className="task-brief__result">
            <div className="task-brief__verdict">
              <span
                className={
                  response.verdict_passed
                    ? "checklist-status-badge checklist-status-badge--ready"
                    : "checklist-status-badge checklist-status-badge--pending"
                }
                data-testid="brief-verdict"
              >
                {response.verdict_passed ? "verdict passed" : "verdict failed"}
              </span>
              <span className="task-brief__path">文件：{response.brief_path}</span>
            </div>
            <pre
              className="task-brief__markdown"
              data-testid="brief-markdown"
            >
              {response.brief_markdown}
            </pre>
          </div>
        )}
      </div>
    </section>
  );
}

export default BriefPanel;
