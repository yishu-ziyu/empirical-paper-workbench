import { useCallback, useEffect, useMemo, useState } from "react";
import { CheckCircle2, FileText, Play, RefreshCcw } from "lucide-react";
import { apiUrl } from "../lib/apiBase";

type ComponentStatus = "completed" | "ready" | "waiting_review" | "needs_revision" | "blocked" | "not_started" | string;

interface HeadlessAction {
  id?: string;
  label?: string;
  enabled?: boolean;
}

interface HeadlessBlocker {
  id?: string;
  message?: string;
}

interface HeadlessArtifact {
  path?: string;
}

interface ReviewPriority {
  id?: string;
  title?: string;
  detail?: string;
  owner?: string;
}

interface SectionGap {
  section?: string;
  status?: string;
  current_chinese_chars?: number;
  target_chinese_chars?: string;
}

interface ReviewSummary {
  decision?: string;
  headline?: string;
  current_chinese_chars?: number;
  target_chinese_chars?: string;
  top_priorities?: ReviewPriority[];
  section_gaps?: SectionGap[];
}

interface HeadlessComponent {
  component_id: string;
  label?: string;
  status: ComponentStatus;
  user_summary?: string;
  primary_action?: HeadlessAction;
  blockers?: HeadlessBlocker[];
  artifacts?: HeadlessArtifact[];
  evidence?: HeadlessArtifact[];
  audit?: unknown[];
  review_summary?: ReviewSummary;
}

interface HeadlessState {
  status?: string;
  user_summary?: string;
  primary_action?: HeadlessAction;
  components?: HeadlessComponent[];
  artifacts?: HeadlessArtifact[];
  audit?: unknown[];
  project?: {
    id?: string;
    title?: string;
  };
}

interface WorkflowSummary {
  id: string;
  title?: string;
  status?: string;
  progress?: number;
  project_id?: string;
  updated_at?: string;
}

interface WorkflowTask {
  id: string;
  agent_name?: string;
  role?: string;
  dimension?: string;
  dimension_number?: number;
  status?: string;
  progress?: number;
  summary?: string;
}

interface WorkflowArtifact {
  id?: string;
  path?: string;
  evidence_level?: string;
  kind?: string;
}

interface WorkflowBundle {
  workflow?: WorkflowSummary;
  tasks?: WorkflowTask[];
  artifacts?: WorkflowArtifact[];
}

interface PaperProductionStatusPanelProps {
  projectId: string;
  fallbackProjectId: string;
  topic: string;
}

const PIPELINE_AGENT_NAMES = [
  "ResearchIntentAgent",
  "LiteratureAgent",
  "DataAgent",
  "MethodAgent",
  "ExecutionAgent",
  "RobustnessAgent",
  "ManuscriptAgent",
  "ReviewerAgent",
  "ReplicationAgent",
  "ExportAgent",
];

const PIPELINE_AGENT_LABELS: Record<string, string> = {
  ResearchIntentAgent: "研究问题定型",
  LiteratureAgent: "文献与贡献",
  DataAgent: "数据与变量",
  MethodAgent: "识别策略",
  ExecutionAgent: "模型运行",
  RobustnessAgent: "稳健性检查",
  ManuscriptAgent: "论文写作",
  ReviewerAgent: "论文审阅",
  ReplicationAgent: "复现检查",
  ExportAgent: "PDF 与交付包",
};

const DELIVERY_COMPONENT_ORDER = [
  "draft_package",
  "delivery_package",
  "final_pdf",
  "course_paper_quality",
  "review_export",
];

function normalizeProjectId(projectId: string, fallbackProjectId: string): string {
  if (!projectId || projectId.startsWith("proj_topic_")) {
    return fallbackProjectId;
  }
  return projectId;
}

async function fetchJson<T>(path: string, init?: RequestInit, acceptedStatuses: number[] = []): Promise<T> {
  const response = await fetch(apiUrl(path), init);
  const body = await response.json().catch(() => ({}));
  if (!response.ok && !acceptedStatuses.includes(response.status)) {
    const message = body?.error?.message || body?.error?.code || `HTTP ${response.status}`;
    throw new Error(message);
  }
  return body as T;
}

function statusLabel(status?: string): string {
  const labels: Record<string, string> = {
    completed: "已完成",
    ready: "可继续",
    waiting_review: "待审阅",
    needs_revision: "需修订",
    blocked: "受阻",
    not_started: "未开始",
    queued: "已排队",
    running: "运行中",
    planning: "规划中",
    researching: "研究中",
    synthesizing: "整合中",
    reviewing: "审阅中",
    cancelled: "已取消",
    failed: "失败",
    missing: "缺失",
    too_short: "过短",
    too_long: "过长",
  };
  return labels[status || ""] || status || "待刷新";
}

function statusTone(status?: string): string {
  if (status === "completed" || status === "ready" || status === "waiting_review") return "good";
  if (status === "needs_revision" || status === "blocked") return "warn";
  return "neutral";
}

function componentById(state: HeadlessState | null, componentId: string): HeadlessComponent | null {
  return state?.components?.find((component) => component.component_id === componentId) ?? null;
}

function sortTasks(tasks: WorkflowTask[]): WorkflowTask[] {
  return [...tasks].sort((a, b) => (a.dimension_number ?? 0) - (b.dimension_number ?? 0));
}

function taskForAgent(tasks: WorkflowTask[], agentName: string): WorkflowTask | null {
  return tasks.find((task) => task.agent_name === agentName) ?? null;
}

function userText(value?: string): string {
  return (value || "")
    .replaceAll("课程论文质量门", "论文审阅")
    .replaceAll("论文质量门", "论文审阅")
    .replaceAll("质量门", "审阅检查")
    .replaceAll("课程论文质量", "论文审阅");
}

export function PaperProductionStatusPanel({
  projectId,
  fallbackProjectId,
  topic,
}: PaperProductionStatusPanelProps) {
  const [activeProjectId, setActiveProjectId] = useState(() => normalizeProjectId(projectId, fallbackProjectId));
  const [headlessState, setHeadlessState] = useState<HeadlessState | null>(null);
  const [workflowBundle, setWorkflowBundle] = useState<WorkflowBundle | null>(null);
  const [loadingState, setLoadingState] = useState(false);
  const [runningWorkflow, setRunningWorkflow] = useState(false);
  const [runningQuality, setRunningQuality] = useState(false);
  const [notice, setNotice] = useState<string>("");
  const [error, setError] = useState<string>("");

  const targetProjectId = useMemo(
    () => normalizeProjectId(projectId, fallbackProjectId),
    [fallbackProjectId, projectId],
  );

  const loadHeadlessState = useCallback(async () => {
    setLoadingState(true);
    setError("");
    try {
      const state = await fetchJson<HeadlessState>(
        `/api/v1/projects/${targetProjectId}/product-control/headless-state`,
      );
      setActiveProjectId(targetProjectId);
      setHeadlessState(state);
      if (targetProjectId !== projectId) {
        setNotice("当前题目还没有登记为独立项目，先接入主仓库论文生产内核。");
      } else {
        setNotice("");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "论文生产状态读取失败。");
    } finally {
      setLoadingState(false);
    }
  }, [projectId, targetProjectId]);

  const loadLatestWorkflow = useCallback(async () => {
    try {
      const list = await fetchJson<{ items?: WorkflowSummary[] }>("/api/v1/workflows");
      const workflows = list.items ?? [];
      const selected =
        workflows.find((workflow) => workflow.title === topic) ??
        workflows.find((workflow) => workflow.title?.includes(topic)) ??
        workflows.find((workflow) => workflow.project_id === targetProjectId) ??
        null;
      if (!selected) return;
      const bundle = await fetchJson<WorkflowBundle>(`/api/v1/workflows/${selected.id}`);
      setWorkflowBundle(bundle);
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "论文生产链状态暂时不可读。");
    }
  }, [targetProjectId, topic]);

  const refreshAll = useCallback(async () => {
    await loadHeadlessState();
    await loadLatestWorkflow();
  }, [loadHeadlessState, loadLatestWorkflow]);

  useEffect(() => {
    void refreshAll();
  }, [refreshAll]);

  const startPaperWorkflow = useCallback(async () => {
    setRunningWorkflow(true);
    setError("");
    try {
      const created = await fetchJson<WorkflowBundle>("/api/v1/workflows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: topic || "论文生产链",
          project_id: targetProjectId,
        }),
      });
      const workflowId = created.workflow?.id;
      if (!workflowId) throw new Error("论文生产链创建后没有返回 workflow id。");
      await fetchJson(`/api/v1/workflows/${workflowId}/start`, { method: "POST" });
      let bundle: WorkflowBundle = created;
      for (let i = 0; i < 5; i += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 300));
        bundle = await fetchJson<WorkflowBundle>(`/api/v1/workflows/${workflowId}`);
        if (bundle.workflow?.status === "completed") break;
      }
      setWorkflowBundle(bundle);
      await loadHeadlessState();
    } catch (err) {
      setError(err instanceof Error ? err.message : "论文生产链启动失败。");
    } finally {
      setRunningWorkflow(false);
    }
  }, [loadHeadlessState, targetProjectId, topic]);

  const runQualityGate = useCallback(async () => {
    setRunningQuality(true);
    setError("");
    try {
      await fetchJson(
        `/api/v1/projects/${activeProjectId}/product-control/course-paper-quality`,
        { method: "POST" },
        [409],
      );
      await loadHeadlessState();
    } catch (err) {
      setError(err instanceof Error ? userText(err.message) : "论文审阅报告生成失败。");
    } finally {
      setRunningQuality(false);
    }
  }, [activeProjectId, loadHeadlessState]);

  const tasks = useMemo(() => sortTasks(workflowBundle?.tasks ?? []), [workflowBundle]);
  const deliveryComponents = DELIVERY_COMPONENT_ORDER
    .map((componentId) => componentById(headlessState, componentId))
    .filter((component): component is HeadlessComponent => Boolean(component));
  const finalPdf = componentById(headlessState, "final_pdf");
  const courseQuality = componentById(headlessState, "course_paper_quality");
  const reviewSummary = courseQuality?.review_summary;
  const artifactCount = workflowBundle?.artifacts?.length ?? 0;

  return (
    <section className="paper-production-status" data-testid="paper-production-status">
      <div className="paper-production-status__header">
        <div>
          <span className="eyebrow">论文生产状态</span>
          <h2>从题目到 PDF 的生产链</h2>
          <p>{userText(headlessState?.user_summary || notice || "读取当前论文交付状态。")}</p>
        </div>
        <div className="paper-production-status__actions">
          <button type="button" onClick={refreshAll} disabled={loadingState}>
            <RefreshCcw size={16} aria-hidden="true" />
            刷新状态
          </button>
          <button type="button" onClick={startPaperWorkflow} disabled={runningWorkflow}>
            <Play size={16} aria-hidden="true" />
            {runningWorkflow ? "生产链运行中" : "启动论文生产链"}
          </button>
        </div>
      </div>

      {notice ? <p className="paper-production-status__notice">{userText(notice)}</p> : null}
      {error ? <p className="paper-production-status__error" role="alert">{userText(error)}</p> : null}

      <div className="paper-production-status__summary">
        <article>
          <FileText size={18} aria-hidden="true" />
          <span>最终 PDF</span>
          <strong>{statusLabel(finalPdf?.status)}</strong>
          <p>{userText(finalPdf?.user_summary || "还没有读取到 PDF 交付状态。")}</p>
        </article>
        <article>
          <CheckCircle2 size={18} aria-hidden="true" />
          <span>论文审阅</span>
          <strong>{statusLabel(courseQuality?.status)}</strong>
          <p>{userText(courseQuality?.user_summary || "等待生成审阅报告。")}</p>
        </article>
        <article>
          <span>生产链产物</span>
          <strong>{artifactCount} 个</strong>
          <p>
            {workflowBundle?.workflow
              ? `${statusLabel(workflowBundle.workflow.status)} · ${Math.round((workflowBundle.workflow.progress ?? 0) * 100)}%`
              : "还没有启动当前题目的十节点生产链。"}
          </p>
        </article>
      </div>

      {reviewSummary ? (
        <section className="paper-production-status__review-summary" aria-label="论文修订摘要">
          <div>
            <span className="eyebrow">修订优先级</span>
            <h3>{userText(reviewSummary.headline || "论文审阅结果已生成。")}</h3>
            <p>
              当前约 {reviewSummary.current_chinese_chars ?? 0} 个中文字符；目标区间 {reviewSummary.target_chinese_chars || "12000-18000"}。
            </p>
          </div>
          {reviewSummary.top_priorities?.length ? (
            <ol>
              {reviewSummary.top_priorities.slice(0, 3).map((priority) => (
                <li key={priority.id || priority.title}>
                  <strong>{userText(priority.title || "待修订")}</strong>
                  <p>{userText(priority.detail || "")}</p>
                </li>
              ))}
            </ol>
          ) : null}
          {reviewSummary.section_gaps?.length ? (
            <ul>
              {reviewSummary.section_gaps.slice(0, 4).map((gap) => (
                <li key={`${gap.section}-${gap.status}`}>
                  {gap.section}：{statusLabel(gap.status)}，当前 {gap.current_chinese_chars ?? 0} 字，目标 {gap.target_chinese_chars || "待确认"}
                </li>
              ))}
            </ul>
          ) : null}
        </section>
      ) : null}

      <div className="paper-production-status__body">
        <section className="paper-production-status__pipeline" aria-label="论文生产链">
          <div className="paper-production-status__section-head">
            <h3>十步论文生产链</h3>
            <p>这层对应 Agent 工作流；每个节点只声明业务产物和证据，不把 UI 写死。</p>
          </div>
          <ol>
            {PIPELINE_AGENT_NAMES.map((agentName, index) => {
              const task = taskForAgent(tasks, agentName);
              return (
                <li key={agentName}>
                  <span className="paper-production-status__step-index">{index + 1}</span>
                  <div>
                    <strong>{PIPELINE_AGENT_LABELS[agentName]}</strong>
                    <p>{userText(task?.summary || task?.role || "等待启动后生成本节点产物。")}</p>
                    <small>{agentName}</small>
                  </div>
                  <em className={`paper-production-status__status paper-production-status__status--${statusTone(task?.status)}`}>
                    {statusLabel(task?.status)}
                  </em>
                </li>
              );
            })}
          </ol>
        </section>

        <section className="paper-production-status__delivery" aria-label="交付状态">
          <div className="paper-production-status__section-head">
            <h3>交付与审阅</h3>
            <button type="button" onClick={runQualityGate} disabled={runningQuality || !courseQuality}>
              <RefreshCcw size={16} aria-hidden="true" />
              {runningQuality ? "审阅报告生成中" : "生成论文审阅报告"}
            </button>
          </div>
          <div className="paper-production-status__cards">
            {deliveryComponents.map((component) => (
              <article key={component.component_id}>
                <span>{userText(component.label || component.component_id)}</span>
                <strong>{statusLabel(component.status)}</strong>
                <p>{userText(component.user_summary)}</p>
                <small>{userText(component.primary_action?.label || "等待下一步")}</small>
                {component.blockers?.length ? (
                  <ul>
                    {component.blockers.slice(0, 2).map((blocker) => (
                      <li key={blocker.id || blocker.message}>{userText(blocker.message || blocker.id)}</li>
                    ))}
                  </ul>
                ) : null}
              </article>
            ))}
          </div>
          <p className="paper-production-status__contract-note">
            component_id / status / user_summary / primary_action / blockers / artifacts / evidence / audit
          </p>
        </section>
      </div>
    </section>
  );
}
