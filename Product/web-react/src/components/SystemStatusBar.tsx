/**
 * SystemStatusBar — Task 41 状态栏.
 *
 * 顶部常驻 5 个 pill: 能力 · 成本 · 产物 · 审计 · LLM.
 * - 每 30s 刷新一次当前项目状态
 * - 任一字段为 null → 显示 "—"
 * - 点击 pill 展开详情 (capabilities / cost / artifacts / observability / llm)
 *
 * 设计原则 (Tufte § chartjunk):
 * - 默认态: 4 pill 一行, 不带边框背景, 极简
 * - 展开态: 网格 2 列, 每列 2 张详情卡
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { Box, Brain, ChevronDown, ChevronUp, Cpu, DollarSign, FileText, ShieldCheck } from "lucide-react";
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

interface LlmSupervisorStatus {
  label: string;
  ready: boolean;
  primary_provider?: {
    provider_id?: string;
    provider_name?: string;
    model?: string;
    configured?: boolean;
  };
  attempts?: Array<{
    provider_id: string;
    provider_name: string;
    model: string;
    api_key_env: string;
    configured: boolean;
  }>;
  model_choices?: Array<{
    provider_id: string;
    provider_name: string;
    default_model: string;
    api_key_env: string;
    configured: boolean;
    current: boolean;
    activation_hint: string;
  }>;
  selection?: {
    current_provider_id: string;
    current_model: string;
    source: string;
    change_hint: string;
  };
  local_codex?: {
    label: string;
    available: boolean;
    version?: string | null;
    execution_enabled: boolean;
    execution_env: string;
    activation_hint: string;
  };
  primary_action?: {
    id: string;
    label: string;
    hint: string;
  };
}

interface SystemStatusBarProps {
  projectId: string;
  topicSlug: string;
  pollIntervalMs?: number;
}

interface LlmProbeResult {
  status: "ok" | "error";
  message: string;
  provider?: string;
  model?: string;
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

function llmGlyph(status: LlmSupervisorStatus | null): string {
  if (!status) return "—";
  return status.ready ? "ready" : "待配置";
}

function llmModelLabel(status: LlmSupervisorStatus | null): string {
  if (!status?.primary_provider) return "未连接模型";
  const provider = status.primary_provider.provider_name || status.primary_provider.provider_id;
  const model = status.primary_provider.model || "已配置模型";
  return provider ? `${provider} · ${model}` : model;
}

function llmCompactLabel(status: LlmSupervisorStatus | null): string {
  if (!status?.primary_provider) return "未连接";
  const provider = status.primary_provider.provider_name || status.primary_provider.provider_id;
  const model = status.primary_provider.model;
  if (provider && model) return `${provider} · ${model}`;
  return provider || model || "已连接";
}

function llmConfiguredAttempts(status: LlmSupervisorStatus | null): LlmSupervisorStatus["attempts"] {
  return (status?.attempts ?? []).filter((attempt) => attempt.configured);
}

function llmVisibleModelChoices(status: LlmSupervisorStatus | null): NonNullable<LlmSupervisorStatus["model_choices"]> {
  const choices = status?.model_choices ?? [];
  const current = choices.filter((choice) => choice.current);
  const openai = choices.filter((choice) => choice.provider_id === "openai" && !choice.current);
  const configured = choices.filter((choice) => choice.configured && !choice.current && choice.provider_id !== "openai");
  return [...current, ...openai, ...configured].slice(0, 5);
}

function llmOpenAiChoice(status: LlmSupervisorStatus | null) {
  return (status?.model_choices ?? []).find((choice) => choice.provider_id === "openai") ?? null;
}

export function SystemStatusBar({ projectId, topicSlug, pollIntervalMs = 30000 }: SystemStatusBarProps) {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [llmStatus, setLlmStatus] = useState<LlmSupervisorStatus | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [llmProbeResult, setLlmProbeResult] = useState<LlmProbeResult | null>(null);
  const [llmProbeRunning, setLlmProbeRunning] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const openAiChoice = llmOpenAiChoice(llmStatus);

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

    try {
      const llmResp = await fetch(apiUrl("/api/v1/providers/llm-supervisor"), {
        method: "GET",
        signal: controller.signal,
      });
      if (llmResp.ok) {
        const llmData: LlmSupervisorStatus = await llmResp.json();
        setLlmStatus(llmData);
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setLlmStatus(null);
      }
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

  const probeLlmSupervisor = useCallback(async () => {
    setLlmProbeRunning(true);
    setLlmProbeResult(null);
    try {
      const resp = await fetch(apiUrl("/api/v1/providers/llm-supervisor/probe"), {
        method: "POST",
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        setLlmProbeResult({
          status: "error",
          message: data?.error?.message || "测试失败：LLM Supervisor 当前不可用。",
        });
        return;
      }
      const provider = data?.provider?.provider_name || data?.provider?.provider_id || "LLM Supervisor";
      const model = data?.provider?.model || "已连接模型";
      setLlmProbeResult({
        status: "ok",
        message: "测试通过",
        provider,
        model,
      });
    } catch {
      setLlmProbeResult({
        status: "error",
        message: "测试失败：服务暂时没连上。",
      });
    } finally {
      setLlmProbeRunning(false);
    }
  }, []);

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
        <span className="system-status-bar__pill" data-testid="status-pill-llm">
          <Brain size={13} aria-hidden="true" />
          <strong data-testid="status-pill-llm-glyph">{llmGlyph(llmStatus)}</strong>
          <span data-testid="status-pill-llm-model">{llmCompactLabel(llmStatus)}</span>
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

          <DetailSection
            testId="status-detail-llm"
            title="LLM Supervisor"
            icon={<Brain size={14} />}
            empty={!llmStatus}
          >
            <div className="system-status-bar__llm-current" data-testid="status-detail-llm-current-provider">
              <span>当前接入</span>
              <strong>{llmModelLabel(llmStatus)}</strong>
              {llmStatus?.selection?.source ? <code>{llmStatus.selection.source}</code> : null}
            </div>
            {openAiChoice ? (
              <div className="system-status-bar__llm-current" data-testid="status-detail-llm-openai-gpt55">
                <span>GPT-5.5 状态</span>
                <strong>
                  {openAiChoice.configured
                    ? openAiChoice.current
                      ? "当前使用"
                      : "已配置，可切换"
                    : `未启用 · 需要 ${openAiChoice.api_key_env || "OPENAI_API_KEY"}`}
                </strong>
                {openAiChoice.activation_hint ? <small>{openAiChoice.activation_hint}</small> : null}
              </div>
            ) : null}
            <p className="system-status-bar__obs">
              主模型：<strong>{llmModelLabel(llmStatus)}</strong>
            </p>
            {llmStatus?.selection?.change_hint ? (
              <p className="system-status-bar__obs">{llmStatus.selection.change_hint}</p>
            ) : null}
            {llmConfiguredAttempts(llmStatus).length > 1 ? (
              <div className="system-status-bar__obs">
                <span>备用链：</span>
                <ul className="system-status-bar__list system-status-bar__list--compact">
                  {llmConfiguredAttempts(llmStatus)
                    .slice(1, 5)
                    .map((attempt) => (
                      <li key={`${attempt.provider_id}-${attempt.model}`}>
                        <code>{attempt.provider_name || attempt.provider_id}</code>
                        <span>{attempt.model}</span>
                      </li>
                    ))}
                </ul>
              </div>
            ) : null}
            {llmVisibleModelChoices(llmStatus).length > 0 ? (
              <div className="system-status-bar__obs">
                <span>可选模型：</span>
                <ul className="system-status-bar__list system-status-bar__list--compact">
                  {llmVisibleModelChoices(llmStatus).map((choice) => (
                    <li key={`${choice.provider_id}-${choice.default_model}`}>
                      <code>{choice.provider_name || choice.provider_id}</code>
                      <span>
                        {choice.default_model || "默认模型"}
                        {choice.current ? " · 当前" : choice.configured ? " · 已配置" : ` · 需 ${choice.api_key_env}`}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
            {llmStatus?.local_codex ? (
              <p className="system-status-bar__obs">
                本地 Codex：
                <strong>
                  {llmStatus.local_codex.available
                    ? llmStatus.local_codex.execution_enabled
                      ? "已启用"
                      : "已安装，未启用"
                    : "未安装"}
                </strong>
                {llmStatus.local_codex.version ? ` · ${llmStatus.local_codex.version}` : ""}
              </p>
            ) : null}
            {llmStatus?.local_codex?.activation_hint ? (
              <p className="system-status-bar__obs">{llmStatus.local_codex.activation_hint}</p>
            ) : null}
            <div className="system-status-bar__probe-row">
              <button
                className="system-status-bar__probe-button"
                data-testid="status-detail-llm-probe"
                type="button"
                disabled={llmProbeRunning}
                onClick={probeLlmSupervisor}
              >
                {llmProbeRunning ? "正在测试" : "测试当前 LLM"}
              </button>
              {llmProbeResult ? (
                <p
                  className={cn(
                    "system-status-bar__probe-result",
                    llmProbeResult.status === "ok" && "system-status-bar__probe-result--ok",
                    llmProbeResult.status === "error" && "system-status-bar__probe-result--error",
                  )}
                >
                  {llmProbeResult.message}
                  {llmProbeResult.provider || llmProbeResult.model ? (
                    <span>
                      {" "}
                      {llmProbeResult.provider}
                      {llmProbeResult.model ? ` · ${llmProbeResult.model}` : ""}
                    </span>
                  ) : null}
                </p>
              ) : null}
            </div>
            {llmStatus?.primary_action?.hint ? (
              <p className="system-status-bar__obs">{llmStatus.primary_action.hint}</p>
            ) : null}
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
