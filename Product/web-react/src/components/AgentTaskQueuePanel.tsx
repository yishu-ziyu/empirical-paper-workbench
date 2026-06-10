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
type ReferenceSeedReviewAction = "approve_for_draft" | "needs_revision" | "reject";
type DispatchReviewAction = "approve" | "reject";
type ExecutionBackendId = "statspai" | "python_ols_adapter" | "stata_mcp" | "codex";
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

interface InternalSkillExecutionPacket {
  status?: string;
  artifact_path?: string;
  skill_id?: string;
  skill_name?: string;
  draft_layer?: string;
  expected_artifacts?: string[];
  review_gate?: string;
  formal_write_allowed?: boolean;
  writes_formal_layer?: boolean;
  next_action?: string;
  created_at?: string;
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

interface SelectedExecutionBackend {
  id?: ExecutionBackendId | string;
  label?: string;
  evidence_level?: string;
  availability_status?: string;
  selection_reason?: string;
  fallback_backend_ids?: string[];
  formal_write_allowed?: boolean;
  execution_boundary?: {
    kind?: string;
    output_boundary?: string;
    evidence_level?: string;
    formal_write_allowed?: boolean;
    can_enter_formal_layer_automatically?: boolean;
    requires_human_review_before_formal_layer?: boolean;
  };
}

interface ExecutionBackendBlocker {
  code?: string;
  backend_id?: string;
  label?: string;
  availability_status?: string;
  fallback_backend_ids?: string[];
  retry_action?: string;
  message?: string;
}

interface AgentTaskError {
  code?: string;
  message?: string;
  status?: string;
  student_message?: string;
}

interface AgentTaskAuditEvent {
  event?: string;
  actor?: string;
  timestamp?: string;
  run_id?: string;
  backend_id?: string;
  error_code?: string;
  note?: string;
}

interface ExecutionResult {
  status?: string;
  run_id?: string;
  engine?: string;
  evidence_level?: string;
  artifact_path?: string;
  output_path?: string;
  execution_kind?: string;
  formal_write_allowed?: boolean;
  writes_formal_layer?: boolean;
  student_message?: string;
  note?: string;
  error?: AgentTaskError;
  result_review?: {
    status?: string;
    title?: string;
    artifact_path?: string;
    review_gate?: string;
    next_action?: string;
    reference_state?: string;
    claims_verified_citations?: boolean;
    can_enter_formal_layer?: boolean;
    last_review_action?: string;
    review_focus?: string[];
  };
}

interface AgentTask {
  id: string;
  title?: string;
  role?: string;
  owner_agent?: string;
  status?: string;
  next_action?: string;
  can_execute?: boolean;
  run_id?: string;
  execution_result?: ExecutionResult;
  error?: AgentTaskError;
  audit_log?: AgentTaskAuditEvent[];
  blockers?: Array<{ code?: string; message?: string }>;
  primary_action?: QueuePrimaryAction;
  dispatch_review?: {
    status?: string;
    action?: string;
    reviewer?: string;
    note?: string;
    reviewed_at?: string;
    evidence_level?: string;
  };
  reference_seed_review?: {
    action?: string;
    status?: string;
    review_gate?: string;
    next_action_label?: string;
    note?: string;
    draft_layer_allowed?: boolean;
    formal_write_allowed?: boolean;
    reference_state?: string;
  };
  internal_skill_bindings?: InternalSkillBinding[];
  internal_skill_execution_packet?: InternalSkillExecutionPacket;
  llm_intervention_handoff?: LlmInterventionHandoff;
  selected_backend?: SelectedExecutionBackend;
  backend_blocker?: ExecutionBackendBlocker;
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
  internal_skill_execution_packet?: InternalSkillExecutionPacket;
}

interface AgentTaskQueuePanelProps {
  projectId: string;
}

const SERVICE_ERROR_MESSAGE = "任务队列暂时没连上，稍后重试。已保存材料不会丢。";
const EXECUTION_BACKEND_OPTIONS: Array<{
  id: ExecutionBackendId;
  label: string;
  purpose: string;
  boundary: string;
  recommended?: boolean;
}> = [
  {
    id: "statspai",
    label: "StatsPAI",
    purpose: "优先承接因果推断、稳健性和结构化结果输出。",
    boundary: "本地执行产物，正式层写入仍需人工审阅。",
    recommended: true,
  },
  {
    id: "python_ols_adapter",
    label: "Python OLS",
    purpose: "快速跑通基准回归或做 fallback 校验。",
    boundary: "生成本地结果、日志和可复查表格。",
  },
  {
    id: "stata_mcp",
    label: "Stata MCP",
    purpose: "适合需要 do-file、log 和 Stata 复现链路的任务。",
    boundary: "Stata 可用时执行，不可用时回落其他后端。",
  },
  {
    id: "codex",
    label: "Codex Subagent",
    purpose: "先生成可审阅脚本草案或修复执行计划。",
    boundary: "只进入草案层，不直接写入正式论文。",
  },
];

function statusLabel(status?: string): string {
  const labels: Record<string, string> = {
    empty: "未创建",
    ready_for_dispatch: "待派发",
    queued: "待审阅",
    dispatched: "已派发",
    reviewed_for_dispatch: "派工已审阅",
    blocked: "已阻断",
    needs_revision: "需要修订",
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
    draft_execution_packet_ready: "草案层执行包已生成",
    blocked_by_backend_unavailable: "后端不可用",
    backend_selected: "后端已选",
    formal_writeback_preflight_needs_revision: "正式写回预检需修订",
    formal_writeback_preflight_rejected: "正式写回预检已拒绝",
    reviewed_for_draft: "已确认进入草稿综述",
    rejected: "已拒绝",
    succeeded: "完成",
    failed: "失败",
  };
  return labels[status ?? ""] ?? status ?? "未知";
}

function actionLabel(action?: string): string {
  const labels: Record<string, string> = {
    create_agent_task_queue: "创建 Agent 任务队列",
    dispatch_review_required: "审阅派工",
    review_internal_skill_before_execution: "审阅 Skill 执行包",
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
    select_execution_backend: "选择执行后端",
    revise_dispatch_task: "修订派工任务",
    choose_fallback_backend: "选择备用后端",
    execute: "开始执行",
    review_literature_seed_package: "审阅候选来源",
    draft_literature_review: "进入草稿综述",
    revise_literature_search: "修订文献搜索",
    replace_literature_search: "替换文献搜索",
    draft_execution_packet_ready: "草案层执行包已生成",
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

function draftSectionTasksReviewActionLabel(action: DraftSectionTasksReviewAction): string {
  if (action === "reject") return "拒绝任务包";
  return reviewActionLabel(action);
}

function referenceSeedReviewActionLabel(action: ReferenceSeedReviewAction): string {
  if (action === "approve_for_draft") return "批准进入草稿综述";
  if (action === "needs_revision") return "要求修订";
  return "拒绝结果";
}

function dispatchReviewActionLabel(action: DispatchReviewAction): string {
  return action === "approve" ? "批准派工" : "退回修订";
}

function dispatchReviewErrorMessage(err: unknown): string {
  const message = err instanceof Error ? err.message : "";
  if (message.includes("internal_skill_execution_packet_required")) {
    return "先生成 Skill 执行包后再批准派工。";
  }
  if (message.includes("invalid_dispatch_review_action")) {
    return "派工审阅动作不合法，请刷新后重试。";
  }
  return "派工审阅没有写回成功，请稍后重试。";
}

function backendSelectionErrorMessage(err: unknown): string {
  const message = err instanceof Error ? err.message : "";
  if (message.includes("dispatch_review_required")) {
    return "请先完成人工派工审阅，再选择执行后端。";
  }
  if (message.includes("backend_not_available")) {
    return "这个执行后端当前不可用，请选择可用的 fallback 后端。";
  }
  if (message.includes("invalid_backend_id")) {
    return "执行后端不在当前支持范围内，请刷新后重试。";
  }
  return "执行后端没有写回成功，请稍后重试。";
}

function executionErrorMessage(err: unknown): string {
  const message = err instanceof Error ? err.message : "";
  if (message.includes("execution_backend_required")) {
    return "请先选择执行后端，再开始执行。";
  }
  if (message.includes("task_not_executable")) {
    return "当前任务还没有进入可执行状态，请先完成前置审阅。";
  }
  return "执行没有启动成功，请查看任务状态后重试。";
}

function referenceSeedReviewErrorMessage(err: unknown): string {
  const message = err instanceof Error ? err.message : "";
  if (message.includes("invalid_reference_seed_review_action")) {
    return "执行结果审阅动作不合法，请刷新后重试。";
  }
  if (message.includes("reference_seed_package_required")) {
    return "还没有可审阅的候选来源种子包。";
  }
  return "执行结果审阅没有写回成功，请稍后重试。";
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

function backendOptionLabel(backendId?: string): string {
  return EXECUTION_BACKEND_OPTIONS.find((backend) => backend.id === backendId)?.label ?? backendId ?? "待选后端";
}

function backendSelectionReason(task: AgentTask, backend: SelectedExecutionBackend): string {
  return (
    backend.selection_reason ??
    `为什么现在选它：${backendOptionLabel(backend.id)} 适合承接 ${task.role ?? task.owner_agent ?? "当前 Agent"} 的下一步执行。`
  );
}

function backendFallbackText(backend?: SelectedExecutionBackend, blocker?: ExecutionBackendBlocker): string {
  const fallbackIds = backend?.fallback_backend_ids?.length
    ? backend.fallback_backend_ids
    : blocker?.fallback_backend_ids ?? [];
  return fallbackIds.length ? fallbackIds.map(backendOptionLabel).join(" / ") : "暂无可用 fallback";
}

function executionArtifactPath(result?: ExecutionResult): string {
  return result?.artifact_path ?? result?.output_path ?? "等待产物路径";
}

function executionLogTrace(task: AgentTask): string {
  const logs = task.audit_log ?? [];
  const last = logs.length ? logs[logs.length - 1] : undefined;
  if (!last) return task.run_id ? `run_id=${task.run_id}` : "等待日志写入";
  return [last.event, last.actor, last.run_id ?? task.run_id, last.error_code].filter(Boolean).join(" · ");
}

function executionFailureText(task: AgentTask, localFailure?: { message: string }): string {
  return (
    task.execution_result?.student_message ??
    task.execution_result?.error?.message ??
    task.error?.student_message ??
    task.error?.message ??
    localFailure?.message ??
    "执行失败，请根据日志线索检查后端环境或选择备用后端。"
  );
}

function executionBackendName(task: AgentTask): string {
  return task.execution_result?.engine ?? task.selected_backend?.label ?? backendOptionLabel(task.selected_backend?.id);
}

function renderTaskSkillReview(
  task: AgentTask,
  options?: {
    generatingSkillPacket?: boolean;
    onGenerateSkillPacket?: (taskId: string) => void;
  },
) {
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
  const packet = task.internal_skill_execution_packet;
  const internalSkillPacketReady = packet?.status === "draft_execution_packet_ready";

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

      {skill ? (
        <div
          className={cn(
            "agent-task-skill-review__gate",
            internalSkillPacketReady ? "agent-task-skill-review__gate--ready" : undefined,
          )}
          data-testid="internal-skill-dispatch-gate"
        >
          <span>派工批准门槛</span>
          <strong>{internalSkillPacketReady ? "派工批准条件已满足" : "先生成执行包，派工批准才会开放"}</strong>
          <p>
            {internalSkillPacketReady
              ? "执行步骤、质量门和正式层边界已落盘，下一步可以进入派工审阅。"
              : "系统会先把 Skill 的操作步骤、质量门和正式层边界写成可审阅文件。"}
          </p>
        </div>
      ) : null}

      {packet ? (
        <div className="agent-task-skill-review__packet" data-testid="internal-skill-execution-packet">
          <div>
            <span className="eyebrow">草案层执行包</span>
            <strong>{statusLabel(packet.status)}</strong>
            <p>下一步：{actionLabel(packet.next_action)}</p>
          </div>
          {packet.artifact_path ? <code>{packet.artifact_path}</code> : null}
          <small>
            Skill：{packet.skill_name || packet.skill_id || skillDisplayName(skill, handoff)} · 正式层
            {packet.writes_formal_layer ? "会写入" : "不写入"}
          </small>
        </div>
      ) : skill ? (
        <div className="agent-task-skill-review__actions">
          <button
            className="btn btn--secondary"
            type="button"
            data-internal-skill-execution-packet-action
            onClick={() => options?.onGenerateSkillPacket?.(task.id)}
            disabled={options?.generatingSkillPacket}
          >
            {options?.generatingSkillPacket ? <Loader2 size={16} className="spin" /> : <FileCheck2 size={16} />}
            <span>{options?.generatingSkillPacket ? "生成中" : "生成 Skill 执行包"}</span>
          </button>
          <p>先把 Skill 的操作步骤、质量门和正式层边界落成本地文件，再进入派工审阅。</p>
        </div>
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
  const [dispatchReviewing, setDispatchReviewing] = useState<{ taskId: string; action: DispatchReviewAction } | null>(null);
  const [selectingBackend, setSelectingBackend] = useState<{ taskId: string; backendId: ExecutionBackendId } | null>(null);
  const [executingTaskId, setExecutingTaskId] = useState<string | null>(null);
  const [executionFailure, setExecutionFailure] = useState<{ taskId: string; message: string } | null>(null);
  const [referenceSeedReviewing, setReferenceSeedReviewing] = useState<{
    taskId: string;
    action: ReferenceSeedReviewAction;
  } | null>(null);
  const [generatingSectionDrafts, setGeneratingSectionDrafts] = useState<string | null>(null);
  const [generatingSkillPacketTaskId, setGeneratingSkillPacketTaskId] = useState<string | null>(null);
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

  const reviewAgentTaskDispatch = async (taskId: string, action: DispatchReviewAction) => {
    setDispatchReviewing({ taskId, action });
    try {
      const data = await fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/dispatch-review`, {
        method: "PUT",
        body: JSON.stringify({
          action,
          note:
            action === "approve"
              ? "执行包和派工边界已审阅，同意进入执行后端选择。"
              : "当前派工需要先修订，暂不进入执行。",
        }),
      });
      setQueue(data.agent_task_queue);
      setError(null);
    } catch (err) {
      setError(dispatchReviewErrorMessage(err));
    } finally {
      setDispatchReviewing(null);
    }
  };

  const selectAgentTaskBackend = async (taskId: string, backendId: ExecutionBackendId) => {
    setSelectingBackend({ taskId, backendId });
    try {
      const data = await fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/select-backend`, {
        method: "POST",
        body: JSON.stringify({ backend_id: backendId }),
      });
      setQueue(data.agent_task_queue);
      setError(null);
    } catch (err) {
      setError(backendSelectionErrorMessage(err));
    } finally {
      setSelectingBackend(null);
    }
  };

  const executeAgentTask = async (taskId: string) => {
    setExecutingTaskId(taskId);
    setExecutionFailure(null);
    setExpandedTaskId(taskId);
    try {
      const data = await fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/execute`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      setQueue(data.agent_task_queue);
      setError(null);
    } catch (err) {
      const message = executionErrorMessage(err);
      setExecutionFailure({ taskId, message });
      setError(message);
    } finally {
      setExecutingTaskId(null);
    }
  };

  const reviewReferenceSeedPackage = async (taskId: string, action: ReferenceSeedReviewAction) => {
    setReferenceSeedReviewing({ taskId, action });
    try {
      const data = await fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/reference-seed-review`, {
        method: "PUT",
        body: JSON.stringify({
          action,
          note:
            action === "approve_for_draft"
              ? "候选来源种子包已审阅，同意进入草稿综述；引用仍需后续核验。"
              : action === "needs_revision"
                ? "候选来源需要补充或调整。"
                : "当前候选来源结果不采用。",
        }),
      });
      setQueue(data.agent_task_queue);
      setError(null);
    } catch (err) {
      setError(referenceSeedReviewErrorMessage(err));
    } finally {
      setReferenceSeedReviewing(null);
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

  const generateInternalSkillExecutionPacket = async (taskId: string) => {
    setGeneratingSkillPacketTaskId(taskId);
    try {
      const data = await fetchJson(
        `/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/internal-skill-execution-packet`,
        {
          method: "POST",
          body: JSON.stringify({}),
        },
      );
      setQueue(data.agent_task_queue);
      setError(null);
    } catch {
      setError("Skill 执行包没有生成成功，请确认这个任务已经绑定内部 Skill。");
    } finally {
      setGeneratingSkillPacketTaskId(null);
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
            const generatingSkillPacket = generatingSkillPacketTaskId === task.id;
            const hasInternalSkillBinding = Boolean(task.internal_skill_bindings?.length);
            const internalSkillPacketReady = task.internal_skill_execution_packet?.status === "draft_execution_packet_ready";
            const dispatchReviewPending = task.dispatch_review?.status === "pending" || task.next_action === "dispatch_review_required";
            const dispatchReviewDone = task.dispatch_review?.status === "reviewed";
            const dispatchApproveDisabled = hasInternalSkillBinding && !internalSkillPacketReady;
            const dispatchBusy = dispatchReviewing?.taskId === task.id;
            const backendSelectionReady =
              task.status === "reviewed_for_dispatch" ||
              task.next_action === "select_execution_backend" ||
              task.status === "blocked_by_backend_unavailable" ||
              task.next_action === "choose_fallback_backend";
            const hasSelectedBackend = Boolean(task.selected_backend?.id);
            const backendSelectionDone = hasSelectedBackend && !backendSelectionReady;
            const backendSelectionDisabled = task.status !== "reviewed_for_dispatch" && !task.backend_blocker;
            const backendBusy = selectingBackend?.taskId === task.id;
            const executionReady = task.next_action === "execute" && task.can_execute !== false && hasSelectedBackend;
            const executingThisTask = executingTaskId === task.id;
            const localExecutionFailure = executionFailure?.taskId === task.id ? executionFailure : undefined;
            const executionFailed =
              task.status === "failed" || task.execution_result?.status === "failed" || Boolean(task.error) || Boolean(localExecutionFailure);
            const hasExecutionResult =
              Boolean(task.execution_result) || task.status === "succeeded" || task.status === "failed" || Boolean(localExecutionFailure);
            const executionResultReviewReady =
              task.execution_result?.execution_kind === "reference_chain_seed_package" &&
              (task.next_action === "review_literature_seed_package" ||
                task.execution_result?.result_review?.review_gate === "review_literature_seed_package") &&
              !task.reference_seed_review;
            const referenceSeedReviewBusy = referenceSeedReviewing?.taskId === task.id;
            const referenceSeedReviewFocus = task.execution_result?.result_review?.review_focus?.filter(Boolean) ?? [];
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
                hasPdfCandidateExport ||
                hasSelectedBackend ||
                hasExecutionResult ||
                executionResultReviewReady ? (
                  <div className="agent-task-card__body">
                    <div className="agent-task-card__action">
                      <span>下一步</span>
                      <strong>{actionLabel(task.next_action)}</strong>
                    </div>

                    {renderTaskSkillReview(task, {
                      generatingSkillPacket,
                      onGenerateSkillPacket: generateInternalSkillExecutionPacket,
                    })}

                    {dispatchReviewPending ? (
                      <div className="agent-task-dispatch-review" data-testid="agent-task-dispatch-review">
                        <div className="agent-task-dispatch-review__head">
                          <span className="eyebrow">派工审阅</span>
                          <h3>确认这个 Agent 任务是否进入执行</h3>
                          <p>批准后只进入执行后端选择；退回后任务停在修订状态，已保存的研究材料不会被覆盖。</p>
                        </div>
                        {dispatchApproveDisabled ? (
                          <p className="agent-task-dispatch-review__gate">先生成 Skill 执行包后再批准派工。</p>
                        ) : null}
                        <div className="agent-task-dispatch-review__actions">
                          <button
                            className="btn btn--primary"
                            type="button"
                            data-dispatch-review-action="approve"
                            onClick={() => void reviewAgentTaskDispatch(task.id, "approve")}
                            disabled={dispatchBusy || dispatchApproveDisabled}
                          >
                            {dispatchReviewing?.taskId === task.id && dispatchReviewing.action === "approve" ? (
                              <Loader2 size={15} className="spin" />
                            ) : (
                              <CheckCircle2 size={15} />
                            )}
                            <span>
                              {dispatchReviewing?.taskId === task.id && dispatchReviewing.action === "approve"
                                ? "写回中"
                                : dispatchReviewActionLabel("approve")}
                            </span>
                          </button>
                          <button
                            className="btn btn--secondary"
                            type="button"
                            data-dispatch-review-action="reject"
                            onClick={() => void reviewAgentTaskDispatch(task.id, "reject")}
                            disabled={dispatchBusy}
                          >
                            {dispatchReviewing?.taskId === task.id && dispatchReviewing.action === "reject" ? (
                              <Loader2 size={15} className="spin" />
                            ) : (
                              <XCircle size={15} />
                            )}
                            <span>
                              {dispatchReviewing?.taskId === task.id && dispatchReviewing.action === "reject"
                                ? "写回中"
                                : dispatchReviewActionLabel("reject")}
                            </span>
                          </button>
                        </div>
                      </div>
                    ) : dispatchReviewDone ? (
                      <div className="agent-task-dispatch-review agent-task-dispatch-review--done">
                        <span className="eyebrow">派工审阅结果</span>
                        <p>
                          {task.dispatch_review?.action === "approve" ? "已批准进入执行后端选择。" : "已退回修订。"}下一步：
                          {actionLabel(task.next_action)}。
                        </p>
                      </div>
                    ) : null}

                    {backendSelectionReady ? (
                      <div className="agent-task-backend-selection" data-testid="agent-task-backend-selection">
                        <div className="agent-task-backend-selection__head">
                          <div>
                            <span className="eyebrow">执行后端</span>
                            <h3>选择执行后端</h3>
                            <p>
                              这一步决定由哪个工具真正跑任务。选择后进入执行态；正式论文层仍由后续人工门控制。
                            </p>
                          </div>
                          {task.backend_blocker ? <span>需要备用</span> : <span>{actionLabel(task.next_action)}</span>}
                        </div>

                        {backendSelectionDisabled ? (
                          <p className="agent-task-backend-selection__gate">请先完成人工派工审阅。</p>
                        ) : null}

                        {task.backend_blocker ? (
                          <div className="agent-task-backend-selection__blocker">
                            <strong>{task.backend_blocker.message ?? "所选执行后端当前不可用。"}</strong>
                            <p>
                              失败后备选：{backendFallbackText(undefined, task.backend_blocker)}。可以直接选择下方备用后端继续。
                            </p>
                          </div>
                        ) : null}

                        <p className="agent-task-backend-selection__guide">
                          推荐先选 StatsPAI；如果本地环境不可用，用 Python OLS 先跑通基准结果，再进入复现和稳健性补强。
                        </p>

                        <div className="agent-task-backend-selection__grid">
                          {EXECUTION_BACKEND_OPTIONS.map((backend) => {
                            const selected = task.selected_backend?.id === backend.id;
                            const busy = backendBusy && selectingBackend?.backendId === backend.id;
                            return (
                              <button
                                key={`${task.id}-${backend.id}`}
                                className={cn(
                                  "agent-task-backend-selection__option",
                                  selected ? "agent-task-backend-selection__option--selected" : undefined,
                                )}
                                type="button"
                                data-backend-id={backend.id}
                                aria-label={`选择执行后端：${backend.label}`}
                                onClick={() => void selectAgentTaskBackend(task.id, backend.id)}
                                disabled={backendSelectionDisabled || backendBusy}
                              >
                                <span>
                                  {backend.label}
                                  {backend.recommended ? <em>推荐</em> : null}
                                </span>
                                <strong>{backend.purpose}</strong>
                                <small>{backend.boundary}</small>
                                {busy ? <em>写回中</em> : null}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    ) : backendSelectionDone ? (
                      <div className="agent-task-backend-selection agent-task-backend-selection--done" data-testid="agent-task-backend-selection">
                        <div className="agent-task-backend-selection__head">
                          <div>
                            <span className="eyebrow">执行后端已选</span>
                            <h3>{task.selected_backend?.label ?? backendOptionLabel(task.selected_backend?.id)}</h3>
                            <p>
                              <strong>为什么现在选它：</strong>
                              {backendSelectionReason(task, task.selected_backend ?? {})}
                            </p>
                          </div>
                          <span>{statusLabel(task.status)}</span>
                        </div>
                        <div className="agent-task-backend-selection__summary">
                          <div>
                            <small>证据等级</small>
                            <strong>{task.selected_backend?.evidence_level ?? "local_file"}</strong>
                          </div>
                          <div>
                            <small>可用状态</small>
                            <strong>{task.selected_backend?.availability_status ?? "ready"}</strong>
                          </div>
                          <div>
                            <small>失败后备选</small>
                            <strong>{backendFallbackText(task.selected_backend, task.backend_blocker)}</strong>
                          </div>
                          <div>
                            <small>正式层边界</small>
                            <strong>
                              {task.selected_backend?.execution_boundary?.requires_human_review_before_formal_layer === false
                                ? "可自动进入正式层"
                                : "需人工审阅"}
                            </strong>
                          </div>
                        </div>
                        <p className="agent-task-backend-selection__next">下一步：{actionLabel(task.next_action)}。</p>
                      </div>
                    ) : null}

                    {hasSelectedBackend ? (
                      <div
                        className={cn(
                          "agent-task-execution-console",
                          executionFailed ? "agent-task-execution-console--failed" : undefined,
                        )}
                        data-testid="agent-task-execution-console"
                      >
                        <div className="agent-task-execution-console__head">
                          <div>
                            <span className="eyebrow">执行控制台</span>
                            <h3>{hasExecutionResult ? (executionFailed ? "失败诊断" : "执行结果") : "准备开始执行"}</h3>
                            <p>
                              当前由 {executionBackendName(task)} 承接。执行结果会写回任务队列，并保留产物路径和日志线索。
                            </p>
                          </div>
                          <span>{hasExecutionResult ? statusLabel(task.status) : actionLabel(task.next_action)}</span>
                        </div>

                        <div className="agent-task-execution-console__grid">
                          <div>
                            <small>执行后端</small>
                            <strong>{executionBackendName(task)}</strong>
                          </div>
                          <div>
                            <small>证据等级</small>
                            <strong>{task.execution_result?.evidence_level ?? task.selected_backend?.evidence_level ?? "local_file"}</strong>
                          </div>
                          <div>
                            <small>产物路径</small>
                            <strong>{executionArtifactPath(task.execution_result)}</strong>
                          </div>
                          <div>
                            <small>日志线索</small>
                            <strong>{executionLogTrace(task)}</strong>
                          </div>
                        </div>

                        {executionFailed ? (
                          <div className="agent-task-execution-console__failure">
                            <strong>失败诊断</strong>
                            <p>{executionFailureText(task, localExecutionFailure)}</p>
                            <small>选择备用后端：{backendFallbackText(task.selected_backend, task.backend_blocker)}</small>
                          </div>
                        ) : hasExecutionResult ? (
                          <p className="agent-task-execution-console__note">
                            执行结果已落盘。下一步：{actionLabel(task.next_action)}。正式层写入仍按后续审阅门处理。
                          </p>
                        ) : (
                          <div className="agent-task-execution-console__actions">
                            <button
                              className="btn btn--primary"
                              type="button"
                              data-execute-agent-task-action
                              onClick={() => void executeAgentTask(task.id)}
                              disabled={!executionReady || executingThisTask}
                            >
                              {executingThisTask ? <Loader2 size={15} className="spin" /> : <FileCheck2 size={15} />}
                              <span>{executingThisTask ? "执行中" : "开始执行"}</span>
                            </button>
                            <p>
                              {executionReady
                                ? "执行会生成本地结果、日志和可复查产物。"
                                : "当前任务还在等待前置审阅或后端选择。"}
                            </p>
                          </div>
                        )}
                      </div>
                    ) : null}

                    {executionResultReviewReady ? (
                      <div
                        className="agent-task-execution-review"
                        data-testid="agent-task-execution-review-gate"
                      >
                        <div className="agent-task-execution-review__head">
                          <div>
                            <span className="eyebrow">审阅执行结果</span>
                            <h3>{task.execution_result?.result_review?.title ?? "候选来源种子包"}</h3>
                            <p>
                              执行结果已经落盘。先检查产物、审阅重点和正式层边界；通过后只进入草稿综述，不写正式层。
                            </p>
                          </div>
                          <span>{task.execution_result?.result_review?.status ?? "待人工判断"}</span>
                        </div>

                        <div className="agent-task-execution-review__grid">
                          <div>
                            <small>结果产物</small>
                            <code>
                              {task.execution_result?.result_review?.artifact_path ?? executionArtifactPath(task.execution_result)}
                            </code>
                          </div>
                          <div>
                            <small>引用状态</small>
                            <strong>{task.execution_result?.result_review?.reference_state ?? "candidate"}</strong>
                          </div>
                          <div>
                            <small>审阅门</small>
                            <strong>{task.execution_result?.result_review?.review_gate ?? "review_literature_seed_package"}</strong>
                          </div>
                          <div>
                            <small>正式层边界</small>
                            <strong>
                              {task.execution_result?.result_review?.can_enter_formal_layer ? "可进入正式层" : "不写正式层"}
                            </strong>
                          </div>
                        </div>

                        <div className="agent-task-execution-review__focus">
                          <strong>审阅重点</strong>
                          {referenceSeedReviewFocus.length ? (
                            <ul>
                              {referenceSeedReviewFocus.slice(0, 3).map((item) => (
                                <li key={`${task.id}-reference-focus-${item}`}>{item}</li>
                              ))}
                            </ul>
                          ) : (
                            <p>当前结果没有审阅摘要。请先查看产物路径和日志，再决定是否继续。</p>
                          )}
                        </div>

                        <div className="agent-task-execution-review__actions">
                          <button
                            className="btn btn--primary"
                            type="button"
                            data-reference-seed-review-action="approve_for_draft"
                            onClick={() => void reviewReferenceSeedPackage(task.id, "approve_for_draft")}
                            disabled={referenceSeedReviewBusy}
                          >
                            {referenceSeedReviewing?.taskId === task.id && referenceSeedReviewing.action === "approve_for_draft" ? (
                              <Loader2 size={15} className="spin" />
                            ) : (
                              <CheckCircle2 size={15} />
                            )}
                            <span>
                              {referenceSeedReviewing?.taskId === task.id && referenceSeedReviewing.action === "approve_for_draft"
                                ? "写回中"
                                : referenceSeedReviewActionLabel("approve_for_draft")}
                            </span>
                          </button>
                          <button
                            className="btn btn--secondary"
                            type="button"
                            data-reference-seed-review-action="needs_revision"
                            onClick={() => void reviewReferenceSeedPackage(task.id, "needs_revision")}
                            disabled={referenceSeedReviewBusy}
                          >
                            {referenceSeedReviewing?.taskId === task.id && referenceSeedReviewing.action === "needs_revision" ? (
                              <Loader2 size={15} className="spin" />
                            ) : (
                              <Pencil size={15} />
                            )}
                            <span>
                              {referenceSeedReviewing?.taskId === task.id && referenceSeedReviewing.action === "needs_revision"
                                ? "写回中"
                                : referenceSeedReviewActionLabel("needs_revision")}
                            </span>
                          </button>
                          <button
                            className="btn btn--secondary"
                            type="button"
                            data-reference-seed-review-action="reject"
                            onClick={() => void reviewReferenceSeedPackage(task.id, "reject")}
                            disabled={referenceSeedReviewBusy}
                          >
                            {referenceSeedReviewing?.taskId === task.id && referenceSeedReviewing.action === "reject" ? (
                              <Loader2 size={15} className="spin" />
                            ) : (
                              <XCircle size={15} />
                            )}
                            <span>
                              {referenceSeedReviewing?.taskId === task.id && referenceSeedReviewing.action === "reject"
                                ? "写回中"
                                : referenceSeedReviewActionLabel("reject")}
                            </span>
                          </button>
                        </div>
                      </div>
                    ) : task.reference_seed_review ? (
                      <div className="agent-task-execution-review agent-task-execution-review--done">
                        <span className="eyebrow">执行结果审阅结果</span>
                        <p>
                          {task.reference_seed_review.next_action_label ?? statusLabel(task.reference_seed_review.status)}。正式层
                          {task.reference_seed_review.formal_write_allowed ? "可继续审阅" : "仍锁定"}。
                        </p>
                      </div>
                    ) : null}

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
                                  : draftSectionTasksReviewActionLabel(action)}
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
