import type { SemanticDraft } from "./SemanticGlowCards";

interface TaskBriefDemoProps {
  draft: SemanticDraft;
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
    title: "证据要求",
    body: "题目、数据来源、变量角色、方法前置条件和人工确认记录必须在进入正式层前补齐。",
  },
  {
    title: "风险",
    body: "当前只是设计讨论 Demo；任何推断都不能直接进入论文正文或正式 RunPlan。",
  },
  {
    title: "正式层边界",
    body: "不会改写 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan、Finding 或 Manuscript。",
  },
  {
    title: "派工说明",
    body: "Kimi 可按此结构做前端高保真；Codex 后续负责把按钮接到 TopicSession 和 SupervisorPlan。",
  },
];

export function TaskBriefDemo({ draft }: TaskBriefDemoProps) {
  const decisions = [
    {
      label: "研究题目",
      value: firstLine(draft.message),
      meta: "用户原始输入",
    },
    {
      label: "研究边界",
      value: detectBoundary(draft),
      meta: "草案层判断",
    },
    {
      label: "数据线索",
      value: detectDataClue(draft),
      meta: draft.fileCount || draft.pastedCount ? "本地材料" : "待确认",
    },
    {
      label: "方法倾向",
      value: detectMethodClue(draft.message),
      meta: "候选，不写回",
    },
    {
      label: "下一步",
      value: "生成任务书并进入人工确认",
      meta: draft.mode,
    },
  ];

  return (
    <section aria-label="任务书低保真 Demo" className="task-brief">
      <div className="task-brief__main">
        <div className="task-brief__lead">
          <span className="eyebrow">任务书 Demo</span>
          <h2>先确认研究问题，再展开分析</h2>
          <p>主屏只保留当前必须判断的信号；细节放在右侧 Inspector。</p>
        </div>

        <div className="task-brief__decisions">
          {decisions.map((decision) => (
            <article className="task-brief__decision" key={decision.label}>
              <span>{decision.label}</span>
              <strong>{decision.value}</strong>
              <small>{decision.meta}</small>
            </article>
          ))}
        </div>
      </div>

      <aside aria-label="任务书右侧检查器" className="task-brief__inspector">
        {inspectorSections.map((section) => (
          <details className="task-brief__inspector-section" key={section.title}>
            <summary>{section.title}</summary>
            <p>{section.body}</p>
          </details>
        ))}
      </aside>
    </section>
  );
}
