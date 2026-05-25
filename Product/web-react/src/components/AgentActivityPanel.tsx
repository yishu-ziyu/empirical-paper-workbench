import { useState, useMemo } from "react";
import {
  Play,
  FileCheck,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  FileText,
  UserCheck,
  Lock,
  ArrowLeft,
} from "lucide-react";
import { cn } from "../lib/cn";

export interface ArtifactFile {
  name: string;
  path: string;
  kind:
    | "dataset_profile"
    | "literature_note"
    | "method_spec"
    | "run_precheck"
    | "table"
    | "figure"
    | "draft"
    | "audit_log";
  evidence_level: "mock" | "local_file" | "local_execution" | "external_source" | "unknown";
  size: string;
  created_at: string;
}

export interface AgentActivity {
  activity_id: string;
  agent: {
    id: string;
    name: string;
    role: string;
    avatar_fallback: string;
  };
  action: string;
  target: string;
  status: "queued" | "running" | "blocked" | "needs_review" | "ready_for_execution" | "completed_draft" | "failed";
  summary: string;
  timestamp: string;
  attention_required: boolean;
  artifacts: ArtifactFile[];
  inputs: string[];
  blockers: string[];
  risks: string[];
  audit_events: string[];
}

const DEFAULT_ACTIVITIES: AgentActivity[] = [
  {
    activity_id: "act_supervisor_01",
    agent: {
      id: "Supervisor",
      name: "Supervisor (科导)",
      role: "研究路线决策与全局调度",
      avatar_fallback: "SP",
    },
    action: "生成执行路线图",
    target: "SupervisorPlanDraft",
    status: "ready_for_execution",
    summary: "已完成因果路径识别与任务依赖分析，生成可执行计划。",
    timestamp: "1分钟前",
    attention_required: false,
    artifacts: [
      {
        name: "supervisor_plan_draft.json",
        path: "state/product/supervisor_plan_draft.json",
        kind: "method_spec",
        evidence_level: "mock",
        size: "4.8 KB",
        created_at: "1分钟前",
      },
    ],
    inputs: ["研究题目", "本地字典附件"],
    blockers: [],
    risks: ["由于没有时点变量，多期DID存在被降级为OLS的风险。"],
    audit_events: ["12:35:02 - Supervisor 监视器启动", "12:35:12 - 分析任务边界, 推荐数据优先路径"],
  },
  {
    activity_id: "act_literature_01",
    agent: {
      id: "LiteratureAgent",
      name: "LiteratureAgent (文献专员)",
      role: "理论综述与机制链提炼",
      avatar_fallback: "LA",
    },
    action: "提取研究假说",
    target: "机制综述草案",
    status: "completed_draft",
    summary: "检索并分析 CFPS 2020 相关教育回报率经典文献，识别 4 个关键机制假说。",
    timestamp: "3分钟前",
    attention_required: false,
    artifacts: [
      {
        name: "literature_synthesis_draft.md",
        path: "Manuscripts/literature_synthesis_draft.md",
        kind: "literature_note",
        evidence_level: "mock",
        size: "12.4 KB",
        created_at: "3分钟前",
      },
    ],
    inputs: ["学术搜索引擎接口", "核心词组"],
    blockers: [],
    risks: [],
    audit_events: ["12:32:10 - 启动外部学术数据库API检索", "12:33:45 - 完成 20 篇代表作摘要共性提炼"],
  },
  {
    activity_id: "act_data_01",
    agent: {
      id: "DataAgent",
      name: "DataAgent (数据专员)",
      role: "数据画像、样本清洗与变量解析",
      avatar_fallback: "DA",
    },
    action: "变量填充率计算与画像",
    target: "VariableRoleSetDraft",
    status: "needs_review",
    summary: "检测到本地数据字段 `edu` 与 `income` 缺失率较低，已生成变量角色候选表，等待用户核验。",
    timestamp: "5分钟前",
    attention_required: true,
    artifacts: [
      {
        name: "cfps2020_data_profile.csv",
        path: "Data/cfps2020_data_profile.csv",
        kind: "dataset_profile",
        evidence_level: "mock",
        size: "82.5 KB",
        created_at: "5分钟前",
      },
    ],
    inputs: ["本地样本数据字典"],
    blockers: [],
    risks: ["部分控制变量（如父亲受教育程度）存在 15% 以上的空值。"],
    audit_events: ["12:30:15 - 读取本地字典附件", "12:31:02 - 生成字段描述性统计画像表"],
  },
  {
    activity_id: "act_method_01",
    agent: {
      id: "MethodAgent",
      name: "MethodAgent (方法专员)",
      role: "模型识别设计与前置假定核验",
      avatar_fallback: "MA",
    },
    action: "前置条件平行趋势核验",
    target: "DesignSpecDraft",
    status: "blocked",
    summary: "双重差分 (DID) 前置平行趋势核验因数据缺少历史时间维时点受阻，推荐降级为 OLS 基准模型。",
    timestamp: "10分钟前",
    attention_required: true,
    artifacts: [
      {
        name: "parallel_trend_test_failed.json",
        path: "state/product/parallel_trend_test_failed.json",
        kind: "run_precheck",
        evidence_level: "mock",
        size: "1.2 KB",
        created_at: "10分钟前",
      },
    ],
    inputs: ["时间维度分布向量"],
    blockers: ["本地数据文件为截面字典, 缺乏多期历史追踪标识。"],
    risks: ["无法使用DID，必须切换为 OLS 控制固定效应或截面 IV 方法。"],
    audit_events: ["12:25:44 - 载入识别模型规则库", "12:26:15 - 平行趋势前置核验失败，记录阻塞记录"],
  },
  {
    activity_id: "act_execution_01",
    agent: {
      id: "ExecutionAgent",
      name: "ExecutionAgent (跑码专员)",
      role: "本地计算沙盒跑码与回归计算",
      avatar_fallback: "EA",
    },
    action: "实证计算回归",
    target: "RunPlanDraft",
    status: "queued",
    summary: "等待启动真实本地沙盒跑码与回归模型计算。",
    timestamp: "15分钟前",
    attention_required: false,
    artifacts: [],
    inputs: ["approved RunPlan"],
    blockers: ["等待全局‘开始真实数据与方法执行’指令解锁"],
    risks: [],
    audit_events: ["12:21:02 - 派工队列生成，进入等待运行状态"],
  },
  {
    activity_id: "act_reviewer_01",
    agent: {
      id: "ReviewerAgent",
      name: "ReviewerAgent (审核专员)",
      role: "健壮性检验与可复现性审计",
      avatar_fallback: "RA",
    },
    action: "审核结果健壮性",
    target: "FindingDraft",
    status: "queued",
    summary: "等待实证回归产出后审核统计健壮性与系数方向。",
    timestamp: "15分钟前",
    attention_required: false,
    artifacts: [],
    inputs: ["实证跑码输出报告"],
    blockers: ["前置跑码计算任务尚未完成"],
    risks: [],
    audit_events: ["12:21:02 - 注册进入流水线等待状态"],
  },
  {
    activity_id: "act_manuscript_01",
    agent: {
      id: "ManuscriptAgent",
      name: "ManuscriptAgent (文稿专员)",
      role: "学术表述与文稿起草",
      avatar_fallback: "MC",
    },
    action: "起草实证表述段落",
    target: "ManuscriptDraft",
    status: "queued",
    summary: "等待审核通过后起草 LaTeX/Word 格式的实证结果章节。",
    timestamp: "15分钟前",
    attention_required: false,
    artifacts: [],
    inputs: ["approved Finding 表格数据"],
    blockers: ["前置审核及数据结果尚未就绪"],
    risks: [],
    audit_events: ["12:21:02 - 注册文稿自动化管线"],
  },
  {
    activity_id: "act_export_01",
    agent: {
      id: "ExportAgent",
      name: "ExportAgent (导出专员)",
      role: "归档、导出与指纹签名",
      avatar_fallback: "XA",
    },
    action: "打包可复现资料",
    target: "ExportPackage",
    status: "queued",
    summary: "等待完整实证与论文草稿产出后，启动最终可复现性打包审计。",
    timestamp: "15分钟前",
    attention_required: false,
    artifacts: [],
    inputs: ["Manuscript", "完整执行 Trace"],
    blockers: ["上游任务尚未全部完成归档"],
    risks: [],
    audit_events: ["12:21:02 - 注册可复现包打包拦截服务"],
  },
];

interface AgentActivityPanelProps {
  onStartExecution?: () => void;
  onBack?: () => void;
  executionStarted?: boolean;
}

export function AgentActivityPanel({ onStartExecution, onBack, executionStarted = false }: AgentActivityPanelProps) {
  const [activities] = useState<AgentActivity[]>(DEFAULT_ACTIVITIES);
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [selectedActivityId, setSelectedActivityId] = useState<string>("act_data_01");
  const [expandedActivities, setExpandedActivities] = useState<Record<string, boolean>>({
    act_data_01: true,
  });
  const [showAuditModal, setShowAuditModal] = useState(false);
  const [showStartExecutionModal, setShowStartExecutionModal] = useState(false);
  const [auditModalTitle, setAuditModalTitle] = useState("");
  const [auditModalEvents, setAuditModalEvents] = useState<string[]>([]);

  const selectedActivity = useMemo(() => {
    return activities.find((act) => act.activity_id === selectedActivityId) || activities[0];
  }, [activities, selectedActivityId]);

  const toggleExpand = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedActivities((prev) => ({ ...prev, [id]: !prev[id] }));
    setSelectedActivityId(id);
  };

  const filteredActivities = useMemo(() => {
    return activities.filter((act) => {
      if (activeFilter === "all") return true;
      if (activeFilter === "needs_review") return act.status === "needs_review";
      if (activeFilter === "running") return act.status === "running";
      if (activeFilter === "blocked") return act.status === "blocked";
      if (activeFilter === "artifacts") return act.artifacts.length > 0;
      return true;
    });
  }, [activities, activeFilter]);

  const filterSummary = useMemo(() => {
    return {
      all: activities.length,
      needs_review: activities.filter((act) => act.status === "needs_review").length,
      running: activities.filter((act) => act.status === "running").length,
      blocked: activities.filter((act) => act.status === "blocked").length,
      artifacts: activities.filter((act) => act.artifacts.length > 0).length,
    };
  }, [activities]);

  const handleStartExecution = () => {
    if (executionStarted) return;
    setShowStartExecutionModal(true);
  };

  const confirmStartExecution = () => {
    setShowStartExecutionModal(false);
    onStartExecution?.();
  };

  return (
    <div className="task-brief agent-console">
      {/* Main Activity Canvas */}
      <section className="task-brief__main agent-console__canvas">
        {/* Header Summary */}
        <div className="task-brief__lead">
          <div className="agent-console__back-row">
            <button className="analysis-workspace__back" type="button" onClick={onBack}>
              <ArrowLeft size={14} />
              <span>返回路线图</span>
            </button>
          </div>
          <span className="eyebrow">Agent 运作账本 (Activity Log)</span>
          <h2>任务队列就绪，等待确认真实数据执行</h2>
          <p>
            SupervisorPlan 已批准，子 Agent 队列已成功规划。当前安全阻断在真实数据与方法执行门槛前。
          </p>
        </div>

        {/* Tab Filters */}
        <div className="agent-console__filters">
          <button
            className={cn("filter-tab", activeFilter === "all" && "filter-tab--active")}
            type="button"
            onClick={() => setActiveFilter("all")}
          >
            <span>全部</span>
            <small>{filterSummary.all}</small>
          </button>
          <button
            className={cn("filter-tab", activeFilter === "needs_review" && "filter-tab--active")}
            type="button"
            onClick={() => setActiveFilter("needs_review")}
          >
            <span>待确认</span>
            <small className="badge-count--alert">{filterSummary.needs_review}</small>
          </button>
          <button
            className={cn("filter-tab", activeFilter === "running" && "filter-tab--active")}
            type="button"
            onClick={() => setActiveFilter("running")}
          >
            <span>进行中</span>
            <small>{filterSummary.running}</small>
          </button>
          <button
            className={cn("filter-tab", activeFilter === "blocked" && "filter-tab--active")}
            type="button"
            onClick={() => setActiveFilter("blocked")}
          >
            <span>阻塞</span>
            <small className="badge-count--alert">{filterSummary.blocked}</small>
          </button>
          <button
            className={cn("filter-tab", activeFilter === "artifacts" && "filter-tab--active")}
            type="button"
            onClick={() => setActiveFilter("artifacts")}
          >
            <span>有产物</span>
            <small>{filterSummary.artifacts}</small>
          </button>
        </div>

        {/* Activity Work Ledger List */}
        <div className="agent-console__list">
          {filteredActivities.map((act) => {
            const isExpanded = !!expandedActivities[act.activity_id];
            const isSelected = selectedActivityId === act.activity_id;

            return (
              <div
                key={act.activity_id}
                className={cn(
                  "agent-console__item",
                  isSelected && "agent-console__item--selected",
                  act.status === "blocked" && "agent-console__item--blocked",
                  act.status === "needs_review" && "agent-console__item--attention"
                )}
                onClick={() => setSelectedActivityId(act.activity_id)}
              >
                <div className="agent-console__item-header">
                  <div className="agent-avatar-wrap">
                    <span className="agent-avatar">{act.agent.avatar_fallback}</span>
                    <div>
                      <strong className="agent-name">{act.agent.name}</strong>
                      <span className="agent-action-desc">
                        {act.action} · <span className="text-target">{act.target}</span>
                      </span>
                    </div>
                  </div>
                  <div className="agent-item-meta">
                    <span className={cn("stage-node-status", `stage-node-status--${act.status}`)}>
                      {act.status === "needs_review"
                        ? "待核验"
                        : act.status === "ready_for_execution"
                        ? "就绪"
                        : act.status === "completed_draft"
                        ? "草稿就绪"
                        : act.status === "blocked"
                        ? "受阻"
                        : act.status === "running"
                        ? "运行中"
                        : "等待启动"}
                    </span>
                    <span className="agent-item-time">{act.timestamp}</span>
                    {act.attention_required && <span className="attention-dot" title="需用户注意" />}
                    <button
                      className="expand-trigger"
                      type="button"
                      onClick={(e) => toggleExpand(act.activity_id, e)}
                    >
                      {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </button>
                  </div>
                </div>
                <p className="agent-item-summary">{act.summary}</p>

                {isExpanded && (
                  <div className="agent-item-details" onClick={(e) => e.stopPropagation()}>
                    {/* Blocker Group */}
                    {act.blockers.length > 0 && (
                      <div className="detail-row detail-row--blocked">
                        <strong>阻塞项 (Blockers)</strong>
                        <ul>
                          {act.blockers.map((b, idx) => (
                            <li key={idx}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Risk Group */}
                    {act.risks.length > 0 && (
                      <div className="detail-row detail-row--risk">
                        <strong>局限与风险 (Risks)</strong>
                        <ul>
                          {act.risks.map((r, idx) => (
                            <li key={idx} className="risk-text">
                              {r}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Evidences and Artifacts */}
                    <div className="agent-item-io">
                      <div className="detail-group">
                        <strong>输入证据 (Inputs)</strong>
                        <ul>
                          {act.inputs.map((i, idx) => (
                            <li key={idx}>{i}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="detail-group">
                        <strong>输出产物 (Artifacts)</strong>
                        {act.artifacts.length > 0 ? (
                          <div className="artifact-list">
                            {act.artifacts.map((art, idx) => (
                              <div key={idx} className="artifact-card">
                                <FileText size={16} />
                                <div>
                                  <strong title={art.name}>{art.name}</strong>
                                  <span>
                                    {art.size} · {art.evidence_level}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <span className="empty-text">尚无输出</span>
                        )}
                      </div>
                    </div>

                    {/* Audit trail link */}
                    <div className="agent-item-footer">
                      <span className="task-id">任务 ID: {act.activity_id}</span>
                      <button
                        className="btn btn--secondary btn--xs"
                        type="button"
                        onClick={() => {
                          setAuditModalTitle(act.agent.name);
                          setAuditModalEvents(act.audit_events);
                          setShowAuditModal(true);
                        }}
                      >
                        审计轨迹入口 (Audit Log)
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Global Action Confirmation Button */}
        <div className="agent-console__global-actions">
          <div className="pre-execution-warning">
            <ShieldAlert size={14} className="risk-text" />
            <span>
              {executionStarted
                ? "真实执行授权已记录，队列保持在执行账本中等待后端执行器接管。"
                : "开始真实执行前，需要先确认范围、证据、正式层边界和已知风险。"}
            </span>
          </div>
          <button className="btn btn--primary btn--large" type="button" onClick={handleStartExecution} disabled={executionStarted}>
            <Play size={16} />
            <span>{executionStarted ? "真实执行已授权" : "开始真实数据与方法执行"}</span>
          </button>
        </div>
      </section>

      {/* Right Inspector Panel */}
      <aside aria-label="检查器" className="task-brief__inspector agent-console__inspector">
        <div className="inspector-sticky-header">
          <h3>选中 Agent 账本详情</h3>
          <p className="task-id">{selectedActivity.agent.name}</p>
        </div>

        {/* Agent Role Info */}
        <details className="task-brief__inspector-section" open>
          <summary>
            <div className="inspector-summary-title">
              <UserCheck size={14} />
              <span>Agent 角色权限说明</span>
            </div>
          </summary>
          <div className="inspector-content">
            <p>
              <strong>主责角色</strong>: {selectedActivity.agent.role}
            </p>
            <p>
              <strong>当前动作</strong>: {selectedActivity.action}
            </p>
            <p>
              <strong>当前目标</strong>: {selectedActivity.target}
            </p>
          </div>
        </details>

        {/* Inputs Used in Detail */}
        {selectedActivity.inputs.length > 0 && (
          <details className="task-brief__inspector-section" open>
            <summary>
              <div className="inspector-summary-title">
                <FileText size={14} />
                <span>输入依据与证据级别</span>
              </div>
            </summary>
            <ul className="inspector-list">
              {selectedActivity.inputs.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </details>
        )}

        {/* Outputs Produced */}
        <details className="task-brief__inspector-section" open>
          <summary>
            <div className="inspector-summary-title">
              <FileCheck size={14} />
              <span>输出要求与产生证据</span>
            </div>
          </summary>
          {selectedActivity.artifacts.length > 0 ? (
            <div className="inspector-artifacts">
              {selectedActivity.artifacts.map((art, idx) => (
                <div key={idx} className="inspector-artifact-item">
                  <strong>{art.name}</strong>
                  <span>路径: {art.path}</span>
                  <span>级别: {art.evidence_level} ({art.size})</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-text">未产生任何文件资产</p>
          )}
        </details>

        {/* Risks & Limitations */}
        {selectedActivity.risks.length > 0 && (
          <details className="task-brief__inspector-section" open>
            <summary>
              <div className="inspector-summary-title">
                <ShieldAlert size={14} />
                <span>已知风险与局限核验</span>
              </div>
            </summary>
            <ul className="inspector-list">
              {selectedActivity.risks.map((item, idx) => (
                <li key={idx} className="risk-text">
                  {item}
                </li>
              ))}
            </ul>
          </details>
        )}

        {/* Audit Log Trail */}
        {selectedActivity.audit_events.length > 0 && (
          <details className="task-brief__inspector-section" open>
            <summary>
              <div className="inspector-summary-title">
                <Lock size={14} />
                <span>本任务可信链审计痕迹</span>
              </div>
            </summary>
            <ul className="inspector-list font-monospace">
              {selectedActivity.audit_events.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </details>
        )}
      </aside>

      {/* Audit Log Modal Dialog */}
      {showAuditModal && (
        <div className="modal-overlay" onClick={() => setShowAuditModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>审计可信轨迹 · {auditModalTitle}</h3>
            <p>该 Agent 在当前实证周期的全部可追溯安全审计日志 (Lock Signature Chain)：</p>
            <div className="modal-audit-list" style={{ maxHeight: "250px", overflowY: "auto", border: "1px solid rgba(230,230,230,0.1)", borderRadius: "8px", padding: "10px" }}>
              {auditModalEvents.length > 0 ? (
                <ul className="inspector-list font-monospace">
                  {auditModalEvents.map((event, idx) => (
                    <li key={idx} style={{ padding: "6px 0", borderBottom: "1px solid rgba(230,230,230,0.06)", fontSize: "12px" }}>{event}</li>
                  ))}
                </ul>
              ) : (
                <p className="empty-text">无相关审计链记录</p>
              )}
            </div>
            <div className="modal-actions">
              <button className="btn btn--primary" type="button" onClick={() => setShowAuditModal(false)}>
                关闭审计日志
              </button>
            </div>
          </div>
        </div>
      )}

      {showStartExecutionModal && (
        <div className="modal-overlay" onClick={() => setShowStartExecutionModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>确认开始真实执行</h3>
            <p>这一步会授权子 Agent 进入本地计算沙盒，并把后续日志、产物和审计链写回执行账本。</p>
            <div className="modal-audit-list">
              <dl className="execution-confirmation-list">
                <div>
                  <dt>执行范围</dt>
                  <dd>启动本地数据画像、方法预检与回归沙盒执行。</dd>
                </div>
                <div>
                  <dt>证据要求</dt>
                  <dd>变量角色、数据来源、方法前置条件和人工确认记录将进入执行输入。</dd>
                </div>
                <div>
                  <dt>正式层边界</dt>
                  <dd>执行产物默认进入 draft / exploratory / needs_human_review；正式层写回仍需后续批准。</dd>
                </div>
                <div>
                  <dt>已知风险</dt>
                  <dd>当前队列包含阻塞与待确认项，执行前需接受这些限制。</dd>
                </div>
              </dl>
            </div>
            <div className="modal-actions">
              <button className="btn btn--secondary" type="button" onClick={() => setShowStartExecutionModal(false)}>
                返回队列
              </button>
              <button className="btn btn--primary" type="button" onClick={confirmStartExecution}>
                确认授权执行
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
