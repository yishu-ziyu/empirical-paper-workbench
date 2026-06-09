/**
 * SystemStatusBar — Task 41 状态栏.
 *
 * 顶部常驻 4 个 pill: 能力 · 成本 · 产物 · 审计.
 * - 每 30s 刷新一次当前项目状态
 * - 任一字段为 null → 显示 "—"
 * - 点击 pill 展开详情 (4 个 section: capabilities / cost / artifacts / observability)
 *
 * 设计原则 (Tufte § chartjunk):
 * - 默认态: 4 pill 一行, 不带边框背景, 极简
 * - 展开态: 网格 2 列, 每列 2 张详情卡
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { Box, ChevronDown, ChevronUp, Cpu, DollarSign, FileText, ShieldCheck } from "lucide-react";
import { apiUrl } from "../lib/apiBase";
import { cn } from "../lib/cn";

interface SystemStatus {
  cap_count: number | null;
  cost_total: number | null;
  artifact_count: number | null;
  obs_status: string | null;
  capabilities?: Array<{
    id: string;
    name: string;
    category: string;
    risk_level: string;
  }>;
  artifacts?: Array<{
    name: string;
    path: string;
    size: number;
    created_at: string;
  }>;
  cost_breakdown?: Array<{ service: string; amount: number }>;
}

interface SystemStatusBarProps {
  projectId: string;
  topicSlug: string;
  pollIntervalMs?: number;
}

const SERVICE_ERROR_MESSAGE =
  "状态暂时没连上，稍后会自动重试。不会影响已保存的研究材料。";

function formatUsd(value: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `$${value.toFixed(2)}`;
}

function formatCount(value: number | null): string {
  if (value === null || value === undefined) return "—";
  return String(value);
}

function obsGlyph(status: string | null): string {
  if (!status) return "—";
  const normalized = status.toLowerCase();
  if (normalized === "completed" || normalized === "succeeded") return "✓";
  if (normalized === "failed") return "✗";
  if (normalized === "running" || normalized === "in_progress") return "…";
  return status;
}

export function SystemStatusBar({ projectId, topicSlug, pollIntervalMs = 30000 }: SystemStatusBarProps) {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const fetchStatus = useCallback(async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const resp = await fetch(apiUrl("/api/system/status"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId, topic_slug: topicSlug }),
        signal: controller.signal,
      });
      if (!resp.ok) {
        setFetchError(SERVICE_ERROR_MESSAGE);
        return;
      }
      const data: SystemStatus = await resp.json();
      setStatus(data);
      setFetchError(null);
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      setFetchError(SERVICE_ERROR_MESSAGE);
    }
  }, [projectId, topicSlug]);

  useEffect(() => {
    void fetchStatus();
    const id = window.setInterval(() => {
      void fetchStatus();
    }, pollIntervalMs);
    return () => {
      window.clearInterval(id);
      abortRef.current?.abort();
    };
  }, [fetchStatus, pollIntervalMs]);

  return (
    <div
      className={cn("system-status-bar", expanded && "system-status-bar--expanded")}
      data-testid="system-status-bar"
      data-fetch-error={fetchError ?? ""}
    >
      <button
        aria-expanded={expanded}
        className="system-status-bar__pills"
        data-testid="system-status-bar-toggle"
        type="button"
        onClick={() => setExpanded((current) => !current)}
      >
        <span className="system-status-bar__pill" data-testid="status-pill-capabilities">
          <Box size={13} aria-hidden="true" />
          <strong data-testid="status-pill-cap-count">{formatCount(status?.cap_count ?? null)}</strong>
          <span>能力</span>
        </span>
        <span className="system-status-bar__pill" data-testid="status-pill-cost">
          <DollarSign size={13} aria-hidden="true" />
          <strong data-testid="status-pill-cost-total">{formatUsd(status?.cost_total ?? null)}</strong>
          <span>成本</span>
        </span>
        <span className="system-status-bar__pill" data-testid="status-pill-artifacts">
          <FileText size={13} aria-hidden="true" />
          <strong data-testid="status-pill-artifact-count">{formatCount(status?.artifact_count ?? null)}</strong>
          <span>产物</span>
        </span>
        <span className="system-status-bar__pill" data-testid="status-pill-obs">
          <ShieldCheck size={13} aria-hidden="true" />
          <strong data-testid="status-pill-obs-glyph">{obsGlyph(status?.obs_status ?? null)}</strong>
          <span>审计</span>
        </span>
        {expanded ? <ChevronUp size={14} aria-hidden="true" /> : <ChevronDown size={14} aria-hidden="true" />}
      </button>

      {expanded ? (
        <div className="system-status-bar__details" data-testid="system-status-bar-details">
          <DetailSection
            testId="status-detail-capabilities"
            title="能力清单"
            icon={<Cpu size={14} />}
            empty={!status?.capabilities || status.capabilities.length === 0}
          >
            <ul className="system-status-bar__list">
              {(status?.capabilities ?? []).slice(0, 12).map((cap) => (
                <li key={cap.id}>
                  <code>{cap.id}</code>
                  <span>{cap.category}</span>
                  <em>{cap.risk_level}</em>
                </li>
              ))}
            </ul>
          </DetailSection>

          <DetailSection
            testId="status-detail-cost"
            title="成本明细"
            icon={<DollarSign size={14} />}
            empty={!status?.cost_breakdown || status.cost_breakdown.length === 0}
          >
            <ul className="system-status-bar__list">
              {(status?.cost_breakdown ?? []).map((row) => (
                <li key={row.service}>
                  <code>{row.service}</code>
                  <span>{formatUsd(row.amount)}</span>
                </li>
              ))}
            </ul>
          </DetailSection>

          <DetailSection
            testId="status-detail-artifacts"
            title="产物记录"
            icon={<FileText size={14} />}
            empty={!status?.artifacts || status.artifacts.length === 0}
          >
            <ul className="system-status-bar__list">
              {(status?.artifacts ?? []).map((art) => (
                <li key={`${art.path}-${art.created_at}`}>
                  <code title={art.path}>{art.name}</code>
                  <span>{art.created_at.slice(0, 10)}</span>
                </li>
              ))}
            </ul>
          </DetailSection>

          <DetailSection
            testId="status-detail-obs"
            title="审计状态"
            icon={<ShieldCheck size={14} />}
            empty={!status?.obs_status}
          >
            <p className="system-status-bar__obs">
              状态：<strong>{status?.obs_status ?? "—"}</strong>
            </p>
          </DetailSection>
        </div>
      ) : null}
    </div>
  );
}

function DetailSection({
  testId,
  title,
  icon,
  empty,
  children,
}: {
  testId: string;
  title: string;
  icon: React.ReactNode;
  empty: boolean;
  children: React.ReactNode;
}) {
  return (
    <section className="system-status-bar__section" data-testid={testId}>
      <header>
        {icon}
        <h4>{title}</h4>
      </header>
      {empty ? <p className="system-status-bar__empty">暂无数据</p> : children}
    </section>
  );
}
