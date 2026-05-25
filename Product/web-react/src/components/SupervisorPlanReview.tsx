import { useState } from "react";
import { Check, AlertTriangle, ShieldAlert, FileCheck, RefreshCw, XCircle } from "lucide-react";
import { cn } from "../lib/cn";

interface StageNode {
  id: string;
  title: string;
  owner: string;
  status: "empty" | "draft" | "ready" | "running" | "completed" | "failed";
  reason: string;
  inputs: string[];
  outputs: string[];
}

const DEFAULT_STAGES: StageNode[] = [
  {
    id: "literature-search",
    title: "1. 文献检索与理论构建",
    owner: "LiteratureAgent",
    status: "ready",
    reason: "识别核心机制、经典文献中对该效应的理论建模，抽取关键机制假说。",
    inputs: ["研究题目", "文献数据库 API"],
    outputs: ["理论假说", "机制框架图"],
  },
  {
    id: "data-variables",
    title: "2. 数据检索与变量画像",
    owner: "DataAgent",
    status: "running",
    reason: "【推荐首选分支】已附带本地数据文件，优先对数据文件开展字段解析、缺失值评估与类型画像。",
    inputs: ["本地附件 (csv/dta)", "变量定义字典"],
    outputs: ["VariableRoleSet", "字段缺失值报告"],
  },
  {
    id: "method-design",
    title: "3. 因果识别与方法设计",
    owner: "MethodAgent",
    status: "draft",
    reason: "基于自变量与因变量的数据分布，设计双重差分 (DID) 或工具变量 (IV) 识别方程。",
    inputs: ["VariableRoleSet", "时点分布"],
    outputs: ["DesignSpec (方程设定)", "平行趋势前置条件"],
  },
  {
    id: "preflight-check",
    title: "4. 执行预检与沙盒模拟",
    owner: "Supervisor",
    status: "empty",
    reason: "静态解析 Stata/Python 代码块，开展因果依赖冲突、循环共线性等预检。",
    inputs: ["DesignSpec", "本地环境配置"],
    outputs: ["PreflightReport", "环境依赖树"],
  },
  {
    id: "experiment-run",
    title: "5. 实证跑码与实验运行",
    owner: "ExecutionAgent",
    status: "empty",
    reason: "启动本地 Stata/Python 进程，执行回归计算、稳健性检验并捕获完整输出。",
    inputs: ["approved RunPlan", "本地计算沙盒"],
    outputs: ["回归系数表", "异质性分析结果"],
  },
  {
    id: "findings-review",
    title: "6. 结果解释与证据审核",
    owner: "ReviewerAgent",
    status: "empty",
    reason: "审核回归结果是否显性、控制变量是否稳定，以及机制分析是否符合逻辑路径。",
    inputs: ["回归系数表", "机制分析结论"],
    outputs: ["approved Finding", "可复现证据包"],
  },
  {
    id: "manuscript-draft",
    title: "7. 论文草稿与学术表述",
    owner: "ManuscriptAgent",
    status: "empty",
    reason: "自动根据因果系数及机制审核包，起草实证部分的 LaTeX/Docx 段落及表格。",
    inputs: ["approved Finding", "LaTeX 模板"],
    outputs: ["Manuscript 草稿段落", "Word 数据附表"],
  },
  {
    id: "export-reproducibility",
    title: "8. 导出审计与可复现包",
    owner: "Supervisor",
    status: "empty",
    reason: "对最终论文段落、Stata dofile、原始数据画像及人工审核链进行完整打包，生成可复现指纹。",
    inputs: ["Manuscript", "完整执行 Trace"],
    outputs: ["可复现压缩包 (zip)", "数据指纹签名"],
  },
];

const inspectorDetails = {
  "inputs-used": [
    "用户输入研究方向: 中国家庭追踪调查(CFPS)数据中的教育回报率估计",
    "附件信息: 1个本地材料, 包含CFPS2020核心变量字典文本",
  ],
  assumptions: [
    "工具变量排他性约束: 假定工具变量仅通过内生变量影响结果变量",
    "面板数据平行趋势假定: 政策试点前处理组与对照组具有平行趋势",
  ],
  "evidence-required": [
    "数据字段画像完成率需达到 100%",
    "回归方程式设计必须明确控制个人、家庭和省份三级固定效应",
    "人工审阅确认 VariableRoleSet 方可启动正式跑码",
  ],
  risks: [
    "【风险提示】本地数据未识别到明显的处理时点变量，可能无法直接应用经典多期DID。",
    "【环境警告】本地未检测到可用的 R 语言环境，相关 DML 估算器将被降级为 Python 线性估算。",
  ],
  "formal-boundary": [
    "此步骤属于 Plan 草案评估阶段，完全运行在 Draft Layer",
    "未经人工核验通过, 绝不会向 Manuscripts 或 formal state 目录写入任何数据",
  ],
};

interface SupervisorPlanReviewProps {
  onApprove?: () => void;
  onReject?: () => void;
}

export function SupervisorPlanReview({ onApprove, onReject }: SupervisorPlanReviewProps) {
  const [expandedStages, setExpandedStages] = useState<Record<string, boolean>>({
    "data-variables": true, // Recommended stage expanded by default
  });
  const [selectedSection, setSelectedSection] = useState<string>("data-variables");
  const [note, setNote] = useState("");
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [showRevisionSuccess, setShowRevisionSuccess] = useState(false);
  const [submittedRevisionNote, setSubmittedRevisionNote] = useState("");

  const toggleStage = (id: string) => {
    setExpandedStages((prev) => ({ ...prev, [id]: !prev[id] }));
    setSelectedSection(id);
  };

  const handleApprove = () => {
    onApprove?.();
  };

  const handleReject = () => {
    onReject?.();
  };

  const handleRequestRevision = () => {
    setShowRevisionModal(true);
  };

  const submitRevision = () => {
    setSubmittedRevisionNote(note);
    setShowRevisionSuccess(true);
    setShowRevisionModal(false);
    setNote("");
  };

  return (
    <div className="task-brief supervisor-plan">
      {/* Main Plan Canvas */}
      <section className="task-brief__main supervisor-plan__canvas">
        <div className="task-brief__lead">
          <span className="eyebrow">SupervisorPlan 决策中心</span>
          <h2>审阅实证规划路线图</h2>
          <p>
            Supervisor 深度评测了您的材料，建议采用 <strong className="text-highlight">数据优先 (Data-First)</strong> 路径。请确认首选分支并审阅步骤树。
          </p>
        </div>

        {/* Plan Route Overview */}
        <div className="supervisor-plan__route-card" onClick={() => setSelectedSection("assumptions")}>
          <div className="route-header">
            <span className="badge badge--recommended">首选分支：数据与变量优先</span>
            <span className="badge badge--readiness">就绪状态: 2个风险警告</span>
          </div>
          <h3>推荐路径理由</h3>
          <p>
            由于您已上传了本地核心字典数据，最稳健的科学决策是跳过泛化的文献库拉取，优先将本地材料进行画像解析，确定控制变量与处理变量的填充率。评估数据质量后再决策是使用经典 OLS 还是双重差分 (DID)。
          </p>
        </div>

        {/* Collapsible Stage Tree */}
        <div className="supervisor-plan__tree-wrapper">
          <h3 className="tree-title">阶段规划任务树 (Expandable Stage Tree)</h3>
          <div className="supervisor-plan__tree">
            {DEFAULT_STAGES.map((stage) => {
              const isExpanded = !!expandedStages[stage.id];
              return (
                <div
                  key={stage.id}
                  className={cn(
                    "supervisor-plan__stage-node",
                    isExpanded && "supervisor-plan__stage-node--expanded",
                    stage.id === "data-variables" && "supervisor-plan__stage-node--recommended"
                  )}
                  onClick={() => toggleStage(stage.id)}
                >
                  <div className="stage-node-header">
                    <span className="stage-node-title">{stage.title}</span>
                    <div className="stage-node-meta">
                      <span className="stage-node-owner">{stage.owner}</span>
                      <span className={cn("stage-node-status", `stage-node-status--${stage.status}`)}>
                        {stage.status === "running" ? "画像中" : stage.status === "ready" ? "就绪" : stage.status === "draft" ? "草案" : "未启动"}
                      </span>
                    </div>
                  </div>
                  <p className="stage-node-rationale">{stage.reason}</p>

                  {isExpanded && (
                    <div className="stage-node-details" onClick={(e) => e.stopPropagation()}>
                      <div className="detail-group">
                        <strong>前置输入 (Required Inputs)</strong>
                        <ul>
                          {stage.inputs.map((input) => (
                            <li key={input}>{input}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="detail-group">
                        <strong>预期输出 (Expected Outputs)</strong>
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
            })}
          </div>
        </div>

        {/* Action Controls */}
        <div className="supervisor-plan__actions">
          <button className="btn btn--secondary" type="button" onClick={handleReject}>
            <XCircle size={16} />
            <span>否决计划</span>
          </button>
          <button className="btn btn--secondary" type="button" onClick={handleRequestRevision}>
            <RefreshCw size={16} />
            <span>请求修订</span>
          </button>
          <button className="btn btn--primary" type="button" onClick={handleApprove}>
            <Check size={16} />
            <span>批准路线并派发</span>
          </button>
        </div>
      </section>

      {/* Right Inspector Panel */}
      <aside aria-label="检查器" className="task-brief__inspector supervisor-plan__inspector">
        {/* Inputs Used */}
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
            {inspectorDetails["inputs-used"].map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </details>

        {/* Key Assumptions */}
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
            {inspectorDetails.assumptions.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </details>

        {/* Evidence Required */}
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
            {inspectorDetails["evidence-required"].map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </details>

        {/* Risks & Warnings */}
        <details
          className={cn("task-brief__inspector-section", selectedSection === "risks" && "section--highlighted")}
          open={selectedSection === "risks" || selectedSection === "data-variables"}
          onClick={() => setSelectedSection("risks")}
        >
          <summary>
            <div className="inspector-summary-title">
              <ShieldAlert size={14} />
              <span>研究局限与环境风险</span>
            </div>
          </summary>
          <ul className="inspector-list">
            {inspectorDetails.risks.map((item, idx) => (
              <li key={idx} className="risk-text">{item}</li>
            ))}
          </ul>
        </details>

        {/* Formal Layer Boundary */}
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
            {inspectorDetails["formal-boundary"].map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </details>
      </aside>

      {/* Revision Modal Dialog */}
      {showRevisionModal && (
        <div className="modal-overlay" onClick={() => setShowRevisionModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>填写重置/修订意见</h3>
            <p>请告诉 Supervisor 您希望如何调整目前的任务路由规划：</p>
            <textarea
              className="modal-textarea"
              placeholder="例如：我希望先开展文献综述(Literature-First)，帮我梳理因果假定后再进行数据画像。"
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

      {/* Revision Success Modal Dialog */}
      {showRevisionSuccess && (
        <div className="modal-overlay" onClick={() => setShowRevisionSuccess(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>修订意见已提交</h3>
            <p>您的反馈已成功同步至 Supervisor：</p>
            <blockquote style={{ background: "rgba(255,255,255,0.03)", padding: "12px", borderLeft: "2px solid rgba(230,230,230,0.3)", borderRadius: "4px", margin: "0", fontStyle: "italic", fontSize: "13px" }}>
              "{submittedRevisionNote}"
            </blockquote>
            <p>Supervisor 正在根据修订约束重新开展因果识别评估与计算路径规划，生成新版 SupervisorPlan。</p>
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
