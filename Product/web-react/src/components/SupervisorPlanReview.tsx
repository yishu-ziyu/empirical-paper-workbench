import { useState } from "react";
import { Check, AlertTriangle, ShieldAlert, FileCheck, RefreshCw, XCircle } from "lucide-react";
import { cn } from "../lib/cn";

export interface StageNode {
  id: string;
  title: string;
  owner: string;
  status: "empty" | "draft" | "ready" | "running" | "completed" | "failed";
  reason: string;
  inputs: string[];
  outputs: string[];
}

interface SupervisorPlanInspector {
  inputs_used?: string[];
  assumptions?: string[];
  evidence_required?: string[];
  risks?: string[];
  formal_boundary?: string[];
}

const DEFAULT_INSPECTOR_DETAILS: Required<SupervisorPlanInspector> = {
  inputs_used: ["研究题目和用户补充材料。"],
  assumptions: ["识别假定会在变量角色和方法方案确认后固定。"],
  evidence_required: [
    "数据来源、样本口径和变量角色需要进入审阅。",
    "方法前置条件需要由 MethodAgent 核验。",
    "产物需要绑定日志、文件路径和证据等级。",
  ],
  risks: ["如果数据、变量或文献证据不足，任务队列会先进入补证。"],
  formal_boundary: [
    "当前只生成任务计划和草案层材料。",
    "正式变量、方法、运行计划和论文正文写入需要显式确认。",
  ],
};

interface SupervisorPlanReviewProps {
  stages?: StageNode[] | null;
  inspector?: SupervisorPlanInspector | null;
  topic?: string;
  evidenceLevel?: string | null;
  approving?: boolean;
  approvalError?: string | null;
  intakeStatus?: "idle" | "registering" | "ready" | "failed";
  intakeMessage?: string | null;
  projectId?: string;
  onApprove?: () => void;
  onReject?: () => void;
}

function firstNonEmpty<T>(value: T[] | undefined, fallback: T[]): T[] {
  return value?.length ? value : fallback;
}

function statusLabel(status: StageNode["status"]): string {
  switch (status) {
    case "completed":
      return "已完成";
    case "running":
      return "进行中";
    case "ready":
      return "就绪";
    case "draft":
      return "草案";
    case "failed":
      return "失败";
    case "empty":
    default:
      return "未启动";
  }
}

export function SupervisorPlanReview({
  stages,
  inspector,
  topic,
  evidenceLevel,
  approving = false,
  approvalError,
  intakeStatus = "idle",
  intakeMessage,
  projectId,
  onApprove,
  onReject,
}: SupervisorPlanReviewProps) {
  const hasStages = Boolean(stages?.length);
  const stagesToRender = stages ?? [];
  const firstStageId = stagesToRender[0]?.id ?? "empty";
  const activeStage =
    stagesToRender.find((stage) => stage.status === "running") ??
    stagesToRender.find((stage) => stage.status === "ready") ??
    stagesToRender[0] ??
    null;
  const [expandedStages, setExpandedStages] = useState<Record<string, boolean>>({
    [activeStage?.id ?? firstStageId]: true,
  });
  const [selectedSection, setSelectedSection] = useState<string>("inputs-used");
  const [note, setNote] = useState("");
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [showRevisionSuccess, setShowRevisionSuccess] = useState(false);
  const [submittedRevisionNote, setSubmittedRevisionNote] = useState("");

  const inputsUsed = firstNonEmpty(inspector?.inputs_used, DEFAULT_INSPECTOR_DETAILS.inputs_used);
  const assumptions = firstNonEmpty(inspector?.assumptions, DEFAULT_INSPECTOR_DETAILS.assumptions);
  const evidenceRequired = firstNonEmpty(
    inspector?.evidence_required,
    DEFAULT_INSPECTOR_DETAILS.evidence_required,
  );
  const risks = firstNonEmpty(inspector?.risks, DEFAULT_INSPECTOR_DETAILS.risks);
  const formalBoundary = firstNonEmpty(inspector?.formal_boundary, DEFAULT_INSPECTOR_DETAILS.formal_boundary);

  const toggleStage = (id: string) => {
    setExpandedStages((prev) => ({ ...prev, [id]: !prev[id] }));
    setSelectedSection(id);
  };

  const submitRevision = () => {
    setSubmittedRevisionNote(note);
    setShowRevisionSuccess(true);
    setShowRevisionModal(false);
    setNote("");
  };

  const intakeLabel =
    intakeStatus === "registering"
      ? "正在登记题目和任务路线"
      : intakeStatus === "ready"
        ? "已登记项目"
        : intakeStatus === "failed"
          ? "登记失败"
          : "等待确认路线";
  const approveLabel =
    intakeStatus === "failed"
      ? "重新登记并创建队列"
      : approving
        ? "正在创建队列"
        : "批准路线并创建队列";

  return (
    <div className="task-brief supervisor-plan">
      <section className="task-brief__main supervisor-plan__canvas">
        <div className="task-brief__lead">
          <span className="eyebrow">SupervisorPlan 决策中心</span>
          <h2>先确认路线，再派发 Agent</h2>
          <p>这一步只需要你判断：题目、证据要求、风险和派工顺序是否合理。通过后再进入 Agent 任务队列。</p>
        </div>

        <div className="supervisor-plan__route-card" onClick={() => setSelectedSection("evidence-required")}>
          <div className="route-header">
            <span className="badge badge--recommended">研究题目：{topic || "待确认"}</span>
            <span className="badge badge--readiness">证据等级：{evidenceLevel || "draft"}</span>
            <span className="badge badge--readiness">阶段数：{hasStages ? stagesToRender.length : 0}</span>
          </div>
          <h3>当前路线理由</h3>
          <p>{activeStage?.reason || "Supervisor 已生成可审阅路线，等待确认后再进入任务队列。"}</p>
        </div>

        <div
          className={cn("supervisor-plan__intake-status", `supervisor-plan__intake-status--${intakeStatus}`)}
          data-testid="plan-intake-status"
        >
          <strong>{intakeLabel}</strong>
          <span>
            {intakeStatus === "ready"
              ? projectId || intakeMessage
              : intakeMessage || "点击批准后会先登记题目，再创建 Agent 任务队列。"}
          </span>
        </div>

        <div className="supervisor-plan__tree-wrapper">
          <h3 className="tree-title">阶段规划任务树</h3>
          <div className="supervisor-plan__tree">
            {hasStages ? stagesToRender.map((stage) => {
              const isExpanded = !!expandedStages[stage.id];
              return (
                <div
                  key={stage.id}
                  className={cn(
                    "supervisor-plan__stage-node",
                    isExpanded && "supervisor-plan__stage-node--expanded",
                    stage.id === activeStage?.id && "supervisor-plan__stage-node--recommended",
                  )}
                  onClick={() => toggleStage(stage.id)}
                >
                  <div className="stage-node-header">
                    <span className="stage-node-title">{stage.title}</span>
                    <div className="stage-node-meta">
                      <span className="stage-node-owner">{stage.owner}</span>
                      <span className={cn("stage-node-status", `stage-node-status--${stage.status}`)}>
                        {statusLabel(stage.status)}
                      </span>
                    </div>
                  </div>
                  <p className="stage-node-rationale">{stage.reason}</p>

                  {isExpanded && (
                    <div className="stage-node-details" onClick={(e) => e.stopPropagation()}>
                      <div className="detail-group">
                        <strong>前置输入</strong>
                        <ul>
                          {stage.inputs.map((input) => (
                            <li key={input}>{input}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="detail-group">
                        <strong>预期输出</strong>
                        <ul>
                          {stage.outputs.map((output) => (
                            <li key={output}>{output}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              );
            }) : (
              <div className="supervisor-plan__empty-state" data-testid="supervisor-plan-empty-state">
                <strong>等待题目登记后的真实路线</strong>
                <p>点击下方按钮后，系统会先保存研究题目和 SupervisorPlan，再展示可派发的阶段任务树。</p>
              </div>
            )}
          </div>
        </div>

        {approvalError ? (
          <div className="supervisor-plan__approval-error" role="alert" data-testid="plan-approval-error">
            <strong>还不能创建队列：</strong>
            <span>{approvalError}</span>
          </div>
        ) : null}

        <div className="supervisor-plan__actions">
          <button className="btn btn--secondary" type="button" disabled={approving} onClick={onReject}>
            <XCircle size={16} />
            <span>否决计划</span>
          </button>
          <button
            className="btn btn--secondary"
            type="button"
            disabled={approving}
            onClick={() => setShowRevisionModal(true)}
          >
            <RefreshCw size={16} />
            <span>请求修订</span>
          </button>
          <button className="btn btn--primary" type="button" disabled={approving} onClick={onApprove}>
            <Check size={16} />
            <span>{approveLabel}</span>
          </button>
        </div>
      </section>

      <aside aria-label="检查器" className="task-brief__inspector supervisor-plan__inspector">
        <details
          className={cn("task-brief__inspector-section", selectedSection === "inputs-used" && "section--highlighted")}
          open={selectedSection === "inputs-used"}
          onClick={() => setSelectedSection("inputs-used")}
        >
          <summary>
            <div className="inspector-summary-title">
              <FileCheck size={14} />
              <span>本轮输入依据</span>
            </div>
          </summary>
          <ul className="inspector-list">
            {inputsUsed.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </details>

        <details
          className={cn("task-brief__inspector-section", selectedSection === "assumptions" && "section--highlighted")}
          open={selectedSection === "assumptions"}
          onClick={() => setSelectedSection("assumptions")}
        >
          <summary>
            <div className="inspector-summary-title">
              <AlertTriangle size={14} />
              <span>关键识别假定</span>
            </div>
          </summary>
          <ul className="inspector-list">
            {assumptions.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </details>

        <details
          className={cn("task-brief__inspector-section", selectedSection === "evidence-required" && "section--highlighted")}
          open={selectedSection === "evidence-required"}
          onClick={() => setSelectedSection("evidence-required")}
        >
          <summary>
            <div className="inspector-summary-title">
              <FileCheck size={14} />
              <span>正式层核验条件</span>
            </div>
          </summary>
          <ul className="inspector-list">
            {evidenceRequired.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </details>

        <details
          className={cn("task-brief__inspector-section", selectedSection === "risks" && "section--highlighted")}
          open={selectedSection === "risks"}
          onClick={() => setSelectedSection("risks")}
        >
          <summary>
            <div className="inspector-summary-title">
              <ShieldAlert size={14} />
              <span>研究局限与环境风险</span>
            </div>
          </summary>
          <ul className="inspector-list">
            {risks.map((item, idx) => (
              <li key={idx} className="risk-text">{item}</li>
            ))}
          </ul>
        </details>

        <details
          className={cn("task-brief__inspector-section", selectedSection === "formal-boundary" && "section--highlighted")}
          open={selectedSection === "formal-boundary"}
          onClick={() => setSelectedSection("formal-boundary")}
        >
          <summary>
            <div className="inspector-summary-title">
              <ShieldAlert size={14} />
              <span>正式层隔离边界</span>
            </div>
          </summary>
          <ul className="inspector-list">
            {formalBoundary.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </details>
      </aside>

      {showRevisionModal && (
        <div className="modal-overlay" onClick={() => setShowRevisionModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>填写修订意见</h3>
            <p>告诉 Supervisor 你希望如何调整当前路线。</p>
            <textarea
              className="modal-textarea"
              placeholder="例如：先补充中文核心文献，再进入变量画像。"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={4}
            />
            <div className="modal-actions">
              <button className="btn btn--secondary" type="button" onClick={() => setShowRevisionModal(false)}>
                取消
              </button>
              <button className="btn btn--primary" type="button" disabled={!note.trim()} onClick={submitRevision}>
                提交修订
              </button>
            </div>
          </div>
        </div>
      )}

      {showRevisionSuccess && (
        <div className="modal-overlay" onClick={() => setShowRevisionSuccess(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>修订意见已记录</h3>
            <p>这条约束会进入下一轮 SupervisorPlan：</p>
            <blockquote className="modal-quote">"{submittedRevisionNote}"</blockquote>
            <div className="modal-actions">
              <button className="btn btn--primary" type="button" onClick={() => setShowRevisionSuccess(false)}>
                确认
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
