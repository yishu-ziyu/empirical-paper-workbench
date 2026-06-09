import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  FileCheck2,
  Loader2,
  ListChecks,
  Pencil,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { cn } from "../lib/cn";
import { apiUrl } from "../lib/apiBase";

type DraftSectionTasksReviewAction = "approve_for_writer_agent" | "needs_revision" | "reject";
type SectionDraftsReviewAction = "approve_for_formal_writeback_preflight" | "needs_revision" | "reject";
type FormalWritebackPreflightReviewAction = "approve_formal_writeback" | "needs_revision" | "reject";
type ReviewAction = DraftSectionTasksReviewAction | SectionDraftsReviewAction | FormalWritebackPreflightReviewAction;

interface QueueSummary {
  total_tasks?: number;
  queued_count?: number;
  blocked_count?: number;
  owner_agents?: string[];
}

interface QueuePrimaryAction {
  id?: string;
  label?: string;
  reason?: string;
  action?: string;
}

interface InternalSkillSource {
  name?: string;
  label?: string;
  type?: string;
  url?: string;
  note?: string;
}

interface InternalSkillBinding {
  id?: string;
  skill_id?: string;
  name?: string;
  owner_agent?: string;
  stage?: string;
  risk_level?: string;
  status?: string;
  matched_reason?: string;
  selection_source?: string;
  semantic_selection_reason?: string;
  why_this_skill?: string;
  llm_semantic_judgment?: {
    reason?: string;
    confidence?: string | number;
    missing_evidence?: string[];
    recommended_next_step?: string;
  };
  expected_artifacts?: string[];
  execution_boundary?: string;
  skill_sources?: InternalSkillSource[];
  can_execute_without_human_review?: boolean;
  quality_gates?: {
    machine_checkable?: string[];
    manual_review?: string[];
  };
  human_confirmation?: {
    required_before?: string[];
    approver_role?: string;
  };
  formal_write_targets?: string[];
  canonical_policy?: {
    auto_mode?: {
      can_generate_patch_proposal?: boolean;
      can_write_canonical?: boolean;
      proposal_status?: string;
    };
  };
  next_action?: string;
}

interface LlmInterventionHandoff {
  stage?: string;
  llm_role?: string;
  deterministic_owner?: string;
  handoff_condition?: string;
  human_gate?: string;
  formal_boundary?: string;
  selected_skill_id?: string;
  selected_skill_name?: string;
  selected_skill_reason?: string;
  selection_source?: string;
}

interface AgentTask {
  id: string;
  title?: string;
  role?: string;
  owner_agent?: string;
  status?: string;
  next_action?: string;
  blockers?: Array<{ code?: string; message?: string }>;
  primary_action?: QueuePrimaryAction;
  internal_skill_bindings?: InternalSkillBinding[];
  llm_intervention_handoff?: LlmInterventionHandoff;
  draft_section_tasks?: {
    status?: string;
    next_action?: string;
    artifact_path?: string;
    task_count?: number;
    section_count?: number;
    formal_layer_boundary?: {
      must_not_write?: string[];
      requires_human_review?: boolean;
    };
  };
  draft_section_tasks_review?: {
    action?: string;
    status?: string;
    next_action?: string;
    note?: string;
  };
  section_drafts?: {
    status?: string;
    next_action?: string;
    artifact_path?: string;
    source_artifact_path?: string;
    section_count?: number;
    requires_human_review?: boolean;
    formal_write_allowed?: boolean;
    writes_formal_layer?: boolean;
  };
  section_drafts_review?: {
    action?: string;
    status?: string;
    next_action?: string;
    note?: string;
    formal_writeback_preflight_allowed?: boolean;
  };
  formal_writeback_preflight?: {
    status?: string;
    artifact_path?: string;
    target_count?: number;
    requires_human_review?: boolean;
    formal_write_allowed?: boolean;
    writes_formal_layer?: boolean;
    next_action?: string;
  };
  formal_writeback_manifest?: {
    status?: string;
    artifact_path?: string;
    written_count?: number;
    target_count?: number;
    writes_formal_layer?: boolean;
  };
  formal_export_preflight?: {
    status?: string;
    source_review_gate?: string;
    source_task_id?: string;
    artifact_path?: string;
    review_path?: string;
    section_count?: number;
    missing_section_count?: number;
    blocker_count?: number;
    next_action?: string;
    writes_formal_layer?: boolean;
    wrote_pdf?: boolean;
    wrote_docx?: boolean;
  };
  pdf_candidate_export?: {
    status?: string;
    source_preflight_path?: string;
    artifact_path?: string;
    review_path?: string;
    pdf_candidate_path?: string;
    wrote_pdf_candidate?: boolean;
    wrote_final_pdf?: boolean;
    wrote_docx?: boolean;
    writes_formal_layer?: boolean;
    next_action?: string;
  };
  export_preflight_followups?: Array<{
    owner_agent?: string;
    title?: string;
    description?: string;
    target_path?: string;
  }>;
}

interface AgentTaskQueue {
  status: string;
  can_create?: boolean;
  blockers?: Array<{ code?: string; message?: string }>;
  summary?: QueueSummary;
  primary_action?: QueuePrimaryAction;
  tasks?: AgentTask[];
}

interface AgentTaskQueueResponse {
  agent_task_queue: AgentTaskQueue;
}

interface AgentTaskQueuePanelProps {
  projectId: string;
}

const SERVICE_ERROR_MESSAGE = "任务队列暂时没连上，稍后重试。已保存材料不会丢。";

function statusLabel(status?: string): string {
  const labels: Record<string, string> = {
    empty: "未创建",
    ready_for_dispatch: "待派发",
    queued: "待审阅",
    dispatched: "已派发",
    draft_section_tasks_ready: "章节任务包待审阅",
    draft_section_tasks_approved: "已交给 WriterAgent",
    draft_section_tasks_needs_revision: "需要修订",
    draft_section_tasks_rejected: "已拒绝",
    section_drafts_ready: "章节草稿待审阅",
    section_drafts_needs_revision: "章节草稿需修订",
    section_drafts_rejected: "章节草稿已拒绝",
    formal_writeback_preflight_ready: "正式写回预检待审阅",
    formal_sections_written: "正式章节已写入",
    formal_export_preflight_ready: "导出预检已通过",
    formal_export_preflight_blocked: "导出预检有阻断项",
    pdf_candidate_exported: "PDF 候选稿已生成",
    formal_writeback_preflight_needs_revision: "正式写回预检需修订",
    formal_writeback_preflight_rejected: "正式写回预检已拒绝",
    succeeded: "完成",
    failed: "失败",
  };
  return labels[status ?? ""] ?? status ?? "未知";
}

function actionLabel(action?: string): string {
  const labels: Record<string, string> = {
    create_agent_task_queue: "创建 Agent 任务队列",
    dispatch_review_required: "审阅派工",
    review_draft_section_tasks: "审阅章节任务包",
    generate_section_drafts: "生成章节草稿",
    review_section_drafts: "审阅章节草稿",
    review_formal_writeback_preflight: "审阅正式写回预检",
    prepare_export_preflight: "准备导出预检",
    run_pdf_export_preflight: "运行 PDF 导出预检",
    review_pdf_candidate: "审阅 PDF 候选稿",
    resolve_export_preflight_blockers: "处理导出阻断项",
    revise_draft_section_tasks: "修订章节任务包",
    replace_draft_section_tasks: "替换章节任务包",
    revise_section_drafts: "修订章节草稿",
    replace_section_drafts: "替换章节草稿",
    revise_formal_writeback_preflight: "修订正式写回预检",
  };
  return labels[action ?? ""] ?? action ?? "查看下一步";
}

function reviewActionLabel(action: ReviewAction): string {
  if (action === "approve_for_writer_agent") return "批准给 WriterAgent";
  if (action === "approve_for_formal_writeback_preflight") return "进入正式写回预检";
  if (action === "approve_formal_writeback") return "批准写入正式层";
  if (action === "needs_revision") return "要求修订";
  return "拒绝";
}

function textList(items?: string[]): string {
  return (items ?? []).filter(Boolean).join(" / ");
}

function skillDisplayName(skill?: InternalSkillBinding, handoff?: LlmInterventionHandoff): string {
  return skill?.name ?? handoff?.selected_skill_name ?? skill?.skill_id ?? handoff?.selected_skill_id ?? "待确认 Skill";
}

function skillSelectionReason(skill?: InternalSkillBinding, handoff?: LlmInterventionHandoff): string {
  return (
    skill?.why_this_skill ??
    skill?.semantic_selection_reason ??
    handoff?.selected_skill_reason ??
    skill?.matched_reason ??
    "等待 Supervisor 补充选择理由。"
  );
}

function skillQualityGateText(skill?: InternalSkillBinding): string {
  const machine = textList(skill?.quality_gates?.machine_checkable);
  const manual = textList(skill?.quality_gates?.manual_review);
  if (machine && manual) return `机器检查：${machine}；人工审阅：${manual}`;
  if (machine) return `机器检查：${machine}`;
  if (manual) return `人工审阅：${manual}`;
  return "等待队列生成质量门。";
}

function renderTaskSkillReview(task: AgentTask) {
  const skill = task.internal_skill_bindings?.[0];
  const handoff = task.llm_intervention_handoff;
  if (!skill && !handoff) return null;

  const llmJudgment =
    skill?.llm_semantic_judgment?.reason ??
    handoff?.llm_role ??
    "Supervisor 根据研究阶段、任务角色和内部方法库匹配当前 Skill。";
  const humanGate =
    textList(skill?.human_confirmation?.required_before) ||
    handoff?.human_gate ||
    "review_internal_skill_before_execution";
  const expectedArtifacts = textList(skill?.expected_artifacts) || "等待任务执行后生成。";
  const executionBoundary = skill?.execution_boundary ?? handoff?.formal_boundary ?? "draft_only_until_human_review";
  const sources = skill?.skill_sources ?? [];
  const canWriteCanonical = skill?.canonical_policy?.auto_mode?.can_write_canonical;

  return (
    <div className="agent-task-skill-review" data-testid="agent-task-skill-review">
      <div className="agent-task-skill-review__head">
        <div>
          <span className="eyebrow">Skill 审阅台</span>
          <h3>{skillDisplayName(skill, handoff)}</h3>
          <p>
            <strong>为什么选这个 Skill：</strong>
            {skillSelectionReason(skill, handoff)}
          </p>
        </div>
        <span>{skill?.selection_source ?? handoff?.selection_source ?? "SupervisorPlan"}</span>
      </div>

      <div className="agent-task-skill-review__grid">
        <div>
          <small>LLM 判断</small>
          <strong>{llmJudgment}</strong>
          {skill?.llm_semantic_judgment?.confidence ? (
            <em>置信度：{skill.llm_semantic_judgment.confidence}</em>
          ) : null}
        </div>
        <div>
          <small>执行边界</small>
          <strong>{executionBoundary}</strong>
        </div>
        <div>
          <small>人工确认点</small>
          <strong>{humanGate}</strong>
          {skill?.human_confirmation?.approver_role ? <em>{skill.human_confirmation.approver_role}</em> : null}
        </div>
        <div>
          <small>预期产物</small>
          <strong>{expectedArtifacts}</strong>
        </div>
        <div>
          <small>质量门</small>
          <strong>{skillQualityGateText(skill)}</strong>
        </div>
        <div>
          <small>缺失证据</small>
          <strong>{textList(skill?.llm_semantic_judgment?.missing_evidence) || "暂无额外缺口。"}</strong>
        </div>
      </div>

      <div className="agent-task-skill-review__sources">
        <strong>Skill 来源</strong>
        {sources.length ? (
          sources.map((source) =>
            source.url ? (
              <a key={`${task.id}-${source.url}`} href={source.url} target="_blank" rel="noreferrer">
                {source.name ?? source.label ?? source.type ?? source.url}
              </a>
            ) : (
              <span key={`${task.id}-${source.name ?? source.label ?? source.type}`}>
                {source.name ?? source.label ?? source.type}
              </span>
            ),
          )
        ) : (
          <span>{skill?.selection_source ?? handoff?.selection_source ?? "internal_skill_registry"}</span>
        )}
      </div>

      {canWriteCanonical === false ? (
        <p className="agent-task-skill-review__note">
          Auto Mode 可以生成 patch proposal；canonical 规则库需人工 review 后合并。
        </p>
      ) : null}
    </div>
  );
}

async function fetchJson(url: string, init?: RequestInit): Promise<AgentTaskQueueResponse> {
  const response = await fetch(apiUrl(url), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || SERVICE_ERROR_MESSAGE);
  }
  return response.json() as Promise<AgentTaskQueueResponse>;
}

export function AgentTaskQueuePanel({ projectId }: AgentTaskQueuePanelProps) {
  const [queue, setQueue] = useState<AgentTaskQueue | null>(null);
  const [expandedTaskId, setExpandedTaskId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [reviewing, setReviewing] = useState<{ taskId: string; action: ReviewAction } | null>(null);
  const [generatingSectionDrafts, setGeneratingSectionDrafts] = useState<string | null>(null);
  const [generatingFormalExportPreflightTaskId, setGeneratingFormalExportPreflightTaskId] = useState<string | null>(null);
  const [generatingPdfCandidateExportTaskId, setGeneratingPdfCandidateExportTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const loadQueue = useCallback(async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    try {
      const data = await fetchJson(`/api/v1/projects/${projectId}/agent-task-queue`, {
        method: "GET",
        signal: controller.signal,
      });
      setQueue(data.agent_task_queue);
      setError(null);
    } catch (err) {
      if ((err as Error).name !== "AbortError") setError(SERVICE_ERROR_MESSAGE);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void loadQueue();
    return () => abortRef.current?.abort();
  }, [loadQueue]);

  const createQueue = async () => {
    setCreating(true);
    try {
      const data = await fetchJson(`/api/v1/projects/${projectId}/agent-task-queue`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      setQueue(data.agent_task_queue);
      setError(null);
    } catch {
      setError("还不能创建队列。请先确认 SupervisorPlan 和必要研究状态。");
    } finally {
      setCreating(false);
    }
  };

  const reviewDraftSectionTasks = async (taskId: string, action: DraftSectionTasksReviewAction) => {
    setReviewing({ taskId, action });
    try {
      const data = await fetchJson(
        `/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/draft-section-tasks-review`,
        {
          method: "PUT",
          body: JSON.stringify({
            action,
            note:
              action === "approve_for_writer_agent"
                ? "章节任务包已审阅，同意交给 WriterAgent 生成草稿层章节。"
                : "",
          }),
        },
      );
      setQueue(data.agent_task_queue);
      setError(null);
    } catch {
      setError("章节任务包审阅没有写回成功，请稍后重试。");
    } finally {
      setReviewing(null);
    }
  };

  const reviewSectionDrafts = async (taskId: string, action: SectionDraftsReviewAction) => {
    setReviewing({ taskId, action });
    try {
      const data = await fetchJson(
        `/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/section-drafts-review`,
        {
          method: "PUT",
          body: JSON.stringify({
            action,
            note:
              action === "approve_for_formal_writeback_preflight"
                ? "章节草稿已审阅，同意生成正式写回预检。"
                : "",
          }),
        },
      );
      setQueue(data.agent_task_queue);
      setError(null);
    } catch {
      setError("章节草稿审阅没有写回成功，请确认草稿已经生成。");
    } finally {
      setReviewing(null);
    }
  };

  const reviewFormalWritebackPreflight = async (taskId: string, action: FormalWritebackPreflightReviewAction) => {
    setReviewing({ taskId, action });
    try {
      const data = await fetchJson(
        `/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/formal-writeback-preflight-review`,
        {
          method: "PUT",
          body: JSON.stringify({
            action,
            note: action === "approve_formal_writeback" ? "正式写回预检已审阅，同意写入正式层章节。" : "",
          }),
        },
      );
      setQueue(data.agent_task_queue);
      setError(null);
    } catch {
      setError("正式写回预检审阅没有写回成功，请确认预检清单已经生成。");
    } finally {
      setReviewing(null);
    }
  };

  const generateSectionDrafts = async (taskId: string) => {
    setGeneratingSectionDrafts(taskId);
    try {
      const data = await fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/section-drafts`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      setQueue(data.agent_task_queue);
      setError(null);
    } catch {
      setError("章节草稿没有生成成功，请确认章节任务包已经批准。");
    } finally {
      setGeneratingSectionDrafts(null);
    }
  };

  const generateFormalExportPreflight = async (taskId: string) => {
    setGeneratingFormalExportPreflightTaskId(taskId);
    try {
      const data = await fetchJson(
        `/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/formal-export-preflight`,
        {
          method: "POST",
          body: JSON.stringify({ note: "正式章节已写入，检查 PDF/DOCX 导出前置条件。" }),
        },
      );
      setQueue(data.agent_task_queue);
      setError(null);
    } catch {
      setError("导出预检没有生成成功，请确认正式章节已经写入。");
    } finally {
      setGeneratingFormalExportPreflightTaskId(null);
    }
  };

  const generatePdfCandidateExport = async (taskId: string) => {
    setGeneratingPdfCandidateExportTaskId(taskId);
    try {
      const data = await fetchJson(
        `/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/pdf-candidate-export`,
        {
          method: "POST",
          body: JSON.stringify({ note: "生成 PDF 候选稿，供人工检查排版、章节和引用边界。" }),
        },
      );
      setQueue(data.agent_task_queue);
      setError(null);
    } catch {
      setError("PDF 候选稿没有生成成功，请先确认导出预检已经通过。");
    } finally {
      setGeneratingPdfCandidateExportTaskId(null);
    }
  };

  const summary = queue?.summary ?? {};
  const tasks = queue?.tasks ?? [];
  const currentAction = queue?.primary_action?.id ?? queue?.primary_action?.action;
  const ownerAgents = useMemo(() => (summary.owner_agents ?? []).slice(0, 4), [summary.owner_agents]);

  return (
    <section className="agent-task-queue-panel" data-testid="agent-task-queue-panel" aria-label="Agent 任务队列">
      <div className="agent-task-queue-panel__header">
        <div>
          <span className="eyebrow">智能体任务队列</span>
          <h2>把计划拆成可审阅任务</h2>
          <p>先看当前动作和阻塞点；需要细节时再展开任务。</p>
        </div>
        <button className="btn btn--secondary" type="button" onClick={() => void loadQueue()} disabled={loading}>
          {loading ? <Loader2 size={15} className="spin" /> : <RefreshCw size={15} />}
          <span>刷新</span>
        </button>
      </div>

      <div className="agent-task-queue-panel__summary" data-testid="agent-task-queue-summary">
        <span>
          <strong>{statusLabel(queue?.status)}</strong>
          <small>队列状态</small>
        </span>
        <span>
          <strong>{summary.total_tasks ?? 0}</strong>
          <small>任务</small>
        </span>
        <span>
          <strong>{summary.blocked_count ?? 0}</strong>
          <small>阻塞</small>
        </span>
        <span>
          <strong>{ownerAgents.length ? ownerAgents.join(" / ") : "待派工"}</strong>
          <small>负责方</small>
        </span>
      </div>

      <div className="agent-task-queue-panel__current">
        <ListChecks size={16} />
        <div>
          <span>当前建议动作</span>
          <strong>{actionLabel(currentAction)}</strong>
          {queue?.primary_action?.reason ? <p>{queue.primary_action.reason}</p> : null}
        </div>
      </div>

      {error ? (
        <div className="agent-task-queue-panel__error" role="alert">
          {error}
        </div>
      ) : null}

      {tasks.length === 0 ? (
        <div className="agent-task-queue-empty" data-testid="agent-task-queue-empty">
          <p>
            {queue?.blockers?.[0]?.message ??
              "确认 SupervisorPlan 后，系统会在这里生成 LiteratureAgent、DataAgent、MethodAgent 和 WriterAgent 的任务队列。"}
          </p>
          <button
            className="btn btn--primary"
            type="button"
            onClick={() => void createQueue()}
            disabled={!queue?.can_create || creating}
          >
            {creating ? <Loader2 size={15} className="spin" /> : <FileCheck2 size={15} />}
            <span>{creating ? "创建中" : "创建 Agent 任务队列"}</span>
          </button>
        </div>
      ) : (
        <div className="agent-task-queue-list">
          {tasks.map((task) => {
            const expanded = expandedTaskId === task.id;
            const reviewReady = task.status === "draft_section_tasks_ready" && !!task.draft_section_tasks;
            const generationReady = task.status === "draft_section_tasks_approved";
            const hasSectionDrafts = !!task.section_drafts;
            const sectionDraftReviewReady = task.status === "section_drafts_ready" && hasSectionDrafts;
            const hasPreflight = !!task.formal_writeback_preflight;
            const hasFormalWriteback = !!task.formal_writeback_manifest;
            const hasExportPreflight = !!task.formal_export_preflight;
            const hasPdfCandidateExport = !!task.pdf_candidate_export;
            const formalWritebackReviewReady = task.status === "formal_writeback_preflight_ready" && hasPreflight;
            const generatingDrafts = generatingSectionDrafts === task.id;
            const exportPreflightReady = hasFormalWriteback && task.status === "formal_sections_written";
            const generatingExportPreflight = generatingFormalExportPreflightTaskId === task.id;
            const canGeneratePdfCandidateExport =
              task.status === "formal_export_preflight_ready" &&
              task.formal_export_preflight?.status === "formal_export_preflight_ready";
            const generatingPdfCandidateExport = generatingPdfCandidateExportTaskId === task.id;
            return (
              <article key={task.id} className="agent-task-card" data-status={task.status}>
                <button
                  className="agent-task-card__top"
                  type="button"
                  onClick={() => setExpandedTaskId(expanded ? null : task.id)}
                  aria-expanded={expanded}
                >
                  <span>
                    <strong>{task.title ?? task.id}</strong>
                    <small>{task.role ?? task.owner_agent ?? "Agent"}</small>
                  </span>
                  <span className="agent-task-card__state">
                    {statusLabel(task.status)}
                    {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                  </span>
                </button>

                {expanded ||
                reviewReady ||
                generationReady ||
                hasSectionDrafts ||
                hasPreflight ||
                hasFormalWriteback ||
                hasExportPreflight ||
                hasPdfCandidateExport ? (
                  <div className="agent-task-card__body">
                    <div className="agent-task-card__action">
                      <span>下一步</span>
                      <strong>{actionLabel(task.next_action)}</strong>
                    </div>

                    {renderTaskSkillReview(task)}

                    {reviewReady ? (
                      <div className="agent-task-queue-review" data-testid="draft-section-tasks-review">
                        <div>
                          <span className="eyebrow">章节任务包审阅</span>
                          <h3>先审任务包，再让 WriterAgent 写章节草稿</h3>
                          <p>
                            任务数 {task.draft_section_tasks?.task_count ?? "—"}，章节数{" "}
                            {task.draft_section_tasks?.section_count ?? "—"}。正式层仍保持锁定，批准后只开放草稿层写作。
                          </p>
                          {task.draft_section_tasks?.artifact_path ? (
                            <code>{task.draft_section_tasks.artifact_path}</code>
                          ) : null}
                        </div>
                        <div className="agent-task-queue-review__actions">
                          {(["approve_for_writer_agent", "needs_revision", "reject"] as DraftSectionTasksReviewAction[]).map((action) => (
                            <button
                              key={action}
                              className={cn("btn", action === "approve_for_writer_agent" ? "btn--primary" : "btn--secondary")}
                              type="button"
                              onClick={() => void reviewDraftSectionTasks(task.id, action)}
                              disabled={reviewing?.taskId === task.id}
                            >
                              {action === "approve_for_writer_agent" ? (
                                <CheckCircle2 size={15} />
                              ) : action === "needs_revision" ? (
                                <Pencil size={15} />
                              ) : (
                                <XCircle size={15} />
                              )}
                              <span>
                                {reviewing?.taskId === task.id && reviewing.action === action
                                  ? "写回中"
                                  : reviewActionLabel(action)}
                              </span>
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : task.draft_section_tasks_review ? (
                      <div className="agent-task-queue-review agent-task-queue-review--done">
                        <span className="eyebrow">审阅结果</span>
                        <p>
                          {statusLabel(task.status)}。下一步：{actionLabel(task.draft_section_tasks_review.next_action)}。
                        </p>
                      </div>
                    ) : null}

                    {generationReady ? (
                      <div className="agent-task-queue-drafts" data-testid="section-drafts-generate">
                        <div>
                          <span className="eyebrow">章节草稿</span>
                          <h3>WriterAgent 只写草稿层章节</h3>
                          <p>章节任务包已批准。点击后会生成草稿层章节文件，正式层仍保持锁定。</p>
                        </div>
                        <div className="agent-task-queue-drafts__actions">
                          <button
                            className="btn btn--primary"
                            type="button"
                            onClick={() => void generateSectionDrafts(task.id)}
                            disabled={generatingDrafts}
                          >
                            {generatingDrafts ? <Loader2 size={15} className="spin" /> : <FileCheck2 size={15} />}
                            <span>{generatingDrafts ? "生成中" : "生成章节草稿"}</span>
                          </button>
                        </div>
                      </div>
                    ) : null}

                    {hasSectionDrafts ? (
                      <div className="agent-task-queue-drafts agent-task-queue-drafts--ready" data-testid="section-drafts-result">
                        <span className="eyebrow">草稿产物</span>
                        <h3>章节草稿已生成</h3>
                        <p>等待人工审阅。正式层仍保持锁定。</p>
                        {task.section_drafts?.artifact_path ? <code>{task.section_drafts.artifact_path}</code> : null}
                        <small>
                          章节数 {task.section_drafts?.section_count ?? "—"} · 下一步{" "}
                          {actionLabel(task.section_drafts?.next_action ?? task.next_action)}
                        </small>
                      </div>
                    ) : null}

                    {sectionDraftReviewReady ? (
                      <div className="agent-task-queue-review agent-task-queue-drafts__review" data-testid="section-drafts-review">
                        <div>
                          <span className="eyebrow">章节草稿审阅</span>
                          <h3>确认草稿是否进入正式写回预检</h3>
                          <p>这里不会写入正式层，只会生成候选写回清单，供下一道人工门继续确认。</p>
                        </div>
                        <div className="agent-task-queue-review__actions">
                          {(["approve_for_formal_writeback_preflight", "needs_revision", "reject"] as SectionDraftsReviewAction[]).map((action) => (
                            <button
                              key={action}
                              className={cn(
                                "btn",
                                action === "approve_for_formal_writeback_preflight" ? "btn--primary" : "btn--secondary",
                              )}
                              type="button"
                              onClick={() => void reviewSectionDrafts(task.id, action)}
                              disabled={reviewing?.taskId === task.id}
                            >
                              {action === "approve_for_formal_writeback_preflight" ? (
                                <CheckCircle2 size={15} />
                              ) : action === "needs_revision" ? (
                                <Pencil size={15} />
                              ) : (
                                <XCircle size={15} />
                              )}
                              <span>
                                {reviewing?.taskId === task.id && reviewing.action === action
                                  ? "写回中"
                                  : reviewActionLabel(action)}
                              </span>
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : task.section_drafts_review ? (
                      <div className="agent-task-queue-review agent-task-queue-review--done">
                        <span className="eyebrow">章节草稿审阅结果</span>
                        <p>
                          {statusLabel(task.status)}。下一步：{actionLabel(task.section_drafts_review.next_action)}。
                        </p>
                      </div>
                    ) : null}

                    {hasPreflight ? (
                      <div className="agent-task-queue-preflight" data-testid="formal-writeback-preflight-result">
                        <span className="eyebrow">正式写回预检</span>
                        <h3>正式写回预检已准备</h3>
                        <p>系统已列出草稿章节到正式文件的候选映射；正式层仍未写入。</p>
                        {task.formal_writeback_preflight?.artifact_path ? (
                          <code>{task.formal_writeback_preflight.artifact_path}</code>
                        ) : null}
                        <small>
                          候选目标 {task.formal_writeback_preflight?.target_count ?? "—"} · 下一步{" "}
                          {actionLabel(task.formal_writeback_preflight?.next_action ?? task.next_action)}
                        </small>
                        {formalWritebackReviewReady ? (
                          <div
                            className="agent-task-queue-review agent-task-queue-formal-writeback__review"
                            data-testid="formal-writeback-preflight-review"
                          >
                            <span className="eyebrow">正式层写入决定</span>
                            <p>批准后会写入 Manuscripts/sections；修订或拒绝都不会改正式章节。</p>
                            <div className="agent-task-queue-review__actions">
                              {(["approve_formal_writeback", "needs_revision", "reject"] as FormalWritebackPreflightReviewAction[]).map((action) => (
                                <button
                                  key={`${task.id}-${action}`}
                                  className={cn(
                                    "btn",
                                    action === "approve_formal_writeback" ? "btn--primary" : "btn--secondary",
                                  )}
                                  type="button"
                                  onClick={() => void reviewFormalWritebackPreflight(task.id, action)}
                                  disabled={reviewing?.taskId === task.id}
                                >
                                  {reviewing?.taskId === task.id && reviewing.action === action ? (
                                    <Loader2 size={14} className="spin" />
                                  ) : action === "approve_formal_writeback" ? (
                                    <CheckCircle2 size={14} />
                                  ) : action === "needs_revision" ? (
                                    <Pencil size={14} />
                                  ) : (
                                    <XCircle size={14} />
                                  )}
                                  <span>{reviewActionLabel(action)}</span>
                                </button>
                              ))}
                            </div>
                          </div>
                        ) : null}
                      </div>
                    ) : null}

                    {hasFormalWriteback ? (
                      <div className="agent-task-queue-formal-writeback" data-testid="formal-writeback-result">
                        <span className="eyebrow">正式章节已写入</span>
                        <h3>正式章节已写入</h3>
                        <p>
                          已写入 {task.formal_writeback_manifest?.written_count ?? "—"} /{" "}
                          {task.formal_writeback_manifest?.target_count ?? "—"} 个正式章节。下一步：{actionLabel(task.next_action)}
                        </p>
                        {task.formal_writeback_manifest?.artifact_path ? (
                          <code>{task.formal_writeback_manifest.artifact_path}</code>
                        ) : null}
                        {exportPreflightReady ? (
                          <div className="agent-task-queue-formal-writeback__actions">
                            <button
                              className="btn btn--primary"
                              type="button"
                              data-formal-export-preflight-action
                              onClick={() => void generateFormalExportPreflight(task.id)}
                              disabled={generatingExportPreflight}
                            >
                              {generatingExportPreflight ? <Loader2 size={15} className="spin" /> : <FileCheck2 size={15} />}
                              <span>{generatingExportPreflight ? "预检中" : "生成导出预检台"}</span>
                            </button>
                          </div>
                        ) : null}
                      </div>
                    ) : null}

                    {hasExportPreflight ? (
                      <div className="agent-task-queue-export-preflight" data-testid="agent-task-queue-export-preflight">
                        <div className="agent-task-queue-export-preflight__head">
                          <div>
                            <span className="eyebrow">导出预检台</span>
                            <h3>{statusLabel(task.formal_export_preflight?.status)}</h3>
                            <p>
                              {task.formal_export_preflight?.status === "formal_export_preflight_blocked"
                                ? "先处理正式章节缺口，再进入 PDF/DOCX 导出。"
                                : "正式章节基础检查已通过，可以生成 PDF 候选稿供人工审阅。"}
                            </p>
                          </div>
                          <span className="agent-task-queue-export-preflight__pill">
                            {actionLabel(task.formal_export_preflight?.next_action ?? task.next_action)}
                          </span>
                        </div>
                        <div className="agent-task-queue-export-preflight__grid">
                          <div>
                            <small>正式章节</small>
                            <strong>{task.formal_export_preflight?.section_count ?? "—"}</strong>
                          </div>
                          <div>
                            <small>缺失章节</small>
                            <strong>{task.formal_export_preflight?.missing_section_count ?? "—"}</strong>
                          </div>
                          <div>
                            <small>PDF/DOCX</small>
                            <strong>
                              {task.formal_export_preflight?.wrote_pdf || task.formal_export_preflight?.wrote_docx ? "已生成" : "未生成"}
                            </strong>
                          </div>
                          <div>
                            <small>正式层写入</small>
                            <strong>{task.formal_export_preflight?.writes_formal_layer ? "会写入" : "不写入"}</strong>
                          </div>
                        </div>
                        {task.formal_export_preflight?.artifact_path ? <code>{task.formal_export_preflight.artifact_path}</code> : null}
                        {task.formal_export_preflight?.review_path ? <code>{task.formal_export_preflight.review_path}</code> : null}
                        {(task.blockers ?? []).length > 0 ? (
                          <div className="agent-task-queue-export-preflight__blockers">
                            <strong>需要先处理</strong>
                            <ul>
                              {(task.blockers ?? []).map((blocker) => (
                                <li key={`${task.id}-export-${blocker.code}`}>{blocker.message ?? blocker.code}</li>
                              ))}
                            </ul>
                          </div>
                        ) : (
                          <p className="agent-task-queue-export-preflight__clear">没有发现正式章节缺口。</p>
                        )}
                        {canGeneratePdfCandidateExport ? (
                          <div className="agent-task-queue-export-preflight__actions">
                            <button
                              className="btn btn--primary"
                              type="button"
                              data-pdf-candidate-export-action
                              onClick={() => void generatePdfCandidateExport(task.id)}
                              disabled={generatingPdfCandidateExport}
                            >
                              {generatingPdfCandidateExport ? <Loader2 size={15} className="spin" /> : <FileCheck2 size={15} />}
                              <span>{generatingPdfCandidateExport ? "生成中" : "生成 PDF 候选稿"}</span>
                            </button>
                          </div>
                        ) : null}
                        {(task.export_preflight_followups ?? []).length > 0 ? (
                          <div className="agent-task-queue-export-preflight__followups">
                            <strong>后续 Agent 任务</strong>
                            {(task.export_preflight_followups ?? []).map((followup) => (
                              <p key={`${task.id}-export-followup-${followup.target_path ?? followup.title}`}>
                                {followup.owner_agent ?? "Agent"} · {followup.title ?? "补齐导出前置条件"}：
                                {followup.description ?? followup.target_path}
                              </p>
                            ))}
                          </div>
                        ) : null}
                      </div>
                    ) : null}

                    {hasPdfCandidateExport ? (
                      <div className="agent-task-queue-pdf-candidate" data-testid="agent-task-queue-pdf-candidate">
                        <div className="agent-task-queue-pdf-candidate__head">
                          <div>
                            <span className="eyebrow">PDF 候选稿</span>
                            <h3>{statusLabel(task.pdf_candidate_export?.status)}</h3>
                            <p>先检查排版、章节完整性、引用边界和复现说明；通过后再进入正式 PDF/DOCX 导出。</p>
                          </div>
                          <span className="agent-task-queue-pdf-candidate__pill">
                            {actionLabel(task.pdf_candidate_export?.next_action ?? task.next_action)}
                          </span>
                        </div>
                        <div className="agent-task-queue-pdf-candidate__grid">
                          <div>
                            <small>PDF 候选稿</small>
                            <code>{task.pdf_candidate_export?.pdf_candidate_path ?? "Submissions/formal_package/paper_candidate.pdf"}</code>
                          </div>
                          <div>
                            <small>候选清单</small>
                            <code>{task.pdf_candidate_export?.artifact_path ?? "Submissions/formal_package/pdf_candidate_manifest.json"}</code>
                          </div>
                          <div>
                            <small>审阅文档</small>
                            <code>{task.pdf_candidate_export?.review_path ?? "Reviews/pdf_candidate_export_review.md"}</code>
                          </div>
                          <div>
                            <small>正式层</small>
                            <strong>{task.pdf_candidate_export?.writes_formal_layer ? "会写入" : "不写入"}</strong>
                          </div>
                        </div>
                        <p className="agent-task-queue-pdf-candidate__note">候选稿不覆盖 paper.pdf / paper.docx；人工审阅通过后再进入正式导出。</p>
                      </div>
                    ) : null}

                    {(task.blockers ?? []).length > 0 ? (
                      <ul className="agent-task-card__blockers">
                        {(task.blockers ?? []).map((blocker) => (
                          <li key={`${task.id}-${blocker.code}`}>{blocker.message ?? blocker.code}</li>
                        ))}
                      </ul>
                    ) : null}
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
