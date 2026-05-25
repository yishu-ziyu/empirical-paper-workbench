import { useState } from "react";
import type { SemanticDraft } from "./SemanticGlowCards";
import { cn } from "../lib/cn";
import { HelpCircle, ShieldAlert, CheckSquare, FileText } from "lucide-react";

interface TaskBriefDemoProps {
  draft: SemanticDraft;
  onApprove?: () => void;
}

function firstLine(message: string): string {
  const trimmed = message.trim();
  if (!trimmed) return "等待确认研究题目";
  return trimmed.split(/\n+/)[0] || trimmed;
}

function detectBoundary(draft: SemanticDraft): string {
  if (draft.fileCount > 0) return "以已附本地材料为边界，先做数据画像和字段匹配。";
  if (draft.pastedCount > 0) return "以粘贴材料为边界，先抽取题目、变量和方法约束。";
  return "当前只有题目，数据、样本和时间范围仍需下一步确认。";
}

function detectDataClue(draft: SemanticDraft): string {
  const normalized = draft.message.toLowerCase();
  if (draft.fileCount > 0) return `${draft.fileCount} 个文件待画像`;
  if (normalized.includes("cfps")) return "CFPS 数据线索";
  if (normalized.includes("chns")) return "CHNS 数据线索";
  if (normalized.includes("cgss")) return "CGSS 数据线索";
  if (normalized.includes("数据")) return "题目含数据线索";
  return "待绑定数据";
}

function detectMethodClue(message: string): string {
  const normalized = message.toLowerCase();
  if (normalized.includes("did") || normalized.includes("双重差分")) return "DID 候选";
  if (normalized.includes("iv") || normalized.includes("工具变量")) return "IV 候选";
  if (normalized.includes("rdd") || normalized.includes("断点")) return "RDD 候选";
  if (normalized.includes("psm") || normalized.includes("匹配")) return "PSM 候选";
  return "先做描述统计与基准模型";
}

const inspectorSections = [
  {
    id: "evidence",
    title: "证据要求",
    body: "题目、数据来源、变量角色、方法前置条件和人工确认记录必须在进入正式层前补齐。",
  },
  {
    id: "risks",
    title: "风险",
    body: "选题及数据边界需严格把控，因控制变量遗漏可能影响后续因果识别模型的可信度与估计有效性。",
  },
  {
    id: "formal",
    title: "正式层边界",
    body: "不会自动改写 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan、Finding 或 Manuscript，一切以显式批准为准。",
  },
  {
    id: "dispatch",
    title: "派工说明",
    body: "本阶段任务书确认后，将自动调度 Supervisor (科导) 模块进行最优任务依赖和研究路径的规划。",
  },
];

export function TaskBriefDemo({ draft, onApprove }: TaskBriefDemoProps) {
  const [selectedSection, setSelectedSection] = useState<string>("evidence");

  const decisions = [
    {
      id: "dispatch",
      label: "研究题目",
      value: firstLine(draft.message),
      meta: "用户原始输入",
    },
    {
      id: "formal",
      label: "研究边界",
      value: detectBoundary(draft),
      meta: "草案层判断",
    },
    {
      id: "evidence",
      label: "数据线索",
      value: detectDataClue(draft),
      meta: draft.fileCount || draft.pastedCount ? "本地材料" : "待确认",
    },
    {
      id: "risks",
      label: "方法倾向",
      value: detectMethodClue(draft.message),
      meta: "候选，不写回",
    },
    {
      id: "evidence",
      label: "下一步",
      value: "生成任务书并进入人工确认",
      meta: draft.mode,
    },
  ];

  return (
    <section aria-label="任务书" className="task-brief">
      <div className="task-brief__main">
        <div className="task-brief__lead">
          <span className="eyebrow">任务书与边界确认 (Task Brief)</span>
          <h2>先确认研究问题，再展开深度分析</h2>
          <p>主屏显示当前必须确认的五个决策信号，点击信号卡片可在右侧 Inspector 聚焦查看详情。</p>
        </div>

        <div className="task-brief__decisions">
          {decisions.map((decision, index) => (
            <article
              className={cn(
                "task-brief__decision",
                selectedSection === decision.id && "task-brief__decision--selected"
              )}
              key={`${decision.label}-${index}`}
              onClick={() => setSelectedSection(decision.id)}
            >
              <span>{decision.label}</span>
              <strong>{decision.value}</strong>
              <small>{decision.meta}</small>
            </article>
          ))}
        </div>

        <div className="task-brief__confirm-actions">
          <button
            className="btn btn--primary"
            type="button"
            onClick={onApprove}
          >
            确认任务书并生成 SupervisorPlan
          </button>
        </div>
      </div>

      <aside aria-label="任务书右侧检查器" className="task-brief__inspector">
        {inspectorSections.map((section) => (
          <details
            className={cn(
              "task-brief__inspector-section",
              selectedSection === section.id && "section--highlighted"
            )}
            key={section.id}
            open={selectedSection === section.id}
            onClick={() => setSelectedSection(section.id)}
          >
            <summary>
              <div className="inspector-summary-title">
                {section.id === "evidence" && <CheckSquare size={14} />}
                {section.id === "risks" && <ShieldAlert size={14} />}
                {section.id === "formal" && <FileText size={14} />}
                {section.id === "dispatch" && <HelpCircle size={14} />}
                <span>{section.title}</span>
              </div>
            </summary>
            <p>{section.body}</p>
          </details>
        ))}
      </aside>
    </section>
  );
}
