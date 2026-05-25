import { useEffect, useMemo, useRef, type ReactNode } from "react";
import { cn } from "../lib/cn";

export interface SemanticDraft {
  message: string;
  mode: string;
  fileCount: number;
  pastedCount: number;
  hasMaterial: boolean;
}

interface SemanticItem {
  label: string;
  title: string;
  body: string;
  signal: string;
}

function includesAny(source: string, terms: string[]): boolean {
  return terms.some((term) => source.includes(term.toLowerCase()));
}

function detectTopic(message: string): string {
  const trimmed = message.trim();
  if (!trimmed) return "等待研究题目";
  const firstLine = trimmed.split(/\n+/)[0] || trimmed;
  return firstLine.length > 36 ? `${firstLine.slice(0, 36)}...` : firstLine;
}

function detectDataSignal(draft: SemanticDraft, normalized: string): string {
  if (draft.fileCount > 0) return `已附 ${draft.fileCount} 个本地文件，优先建立数据画像。`;
  if (draft.pastedCount > 0) return `已附 ${draft.pastedCount} 段长文本，先抽取变量和样本边界。`;
  if (includesAny(normalized, ["cfps", "chns", "clds", "cgss", "数据库", "数据"])) {
    return "题目中已有数据线索，下一步匹配本地数据候选池。";
  }
  return "尚未看到明确数据来源，需要递归搜索或绑定本地数据。";
}

function detectMethodSignal(normalized: string): string {
  if (includesAny(normalized, ["did", "双重差分", "政策", "试点", "事件研究"])) {
    return "优先检查处理组、对照组、政策时点和平行趋势。";
  }
  if (includesAny(normalized, ["iv", "工具变量", "内生"])) {
    return "优先检查工具变量相关性、排除限制和第一阶段强度。";
  }
  if (includesAny(normalized, ["rdd", "断点", "阈值"])) {
    return "优先检查 running variable、带宽和断点附近样本。";
  }
  if (includesAny(normalized, ["psm", "匹配"])) {
    return "优先检查共同支撑、协变量平衡和匹配后样本。";
  }
  if (includesAny(normalized, ["dml", "机器学习", "因果森林"])) {
    return "先确认处理变量、结果变量和交叉拟合策略。";
  }
  return "先从描述统计、变量角色确认和基准模型开始。";
}

function detectEvidenceGap(draft: SemanticDraft, normalized: string): string {
  if (draft.fileCount === 0 && draft.pastedCount === 0 && !includesAny(normalized, ["数据", "cfps", "chns", "cgss"])) {
    return "缺数据来源；不能进入实证执行。";
  }
  if (!includesAny(normalized, ["变量", "因变量", "自变量", "处理变量", "控制变量"])) {
    return "缺变量角色；需要先生成并审阅 VariableRoleSet。";
  }
  if (!includesAny(normalized, ["识别", "因果", "did", "iv", "rdd", "psm", "dml", "固定效应"])) {
    return "缺识别设计；结果只能保持探索性。";
  }
  return "已有初步边界；仍需人工确认后才能进入正式层。";
}

function nextTask(draft: SemanticDraft, normalized: string): string {
  if (draft.mode === "human-review") return "生成任务书后等待人工审阅。";
  if (includesAny(normalized, ["文献", "机制", "理论"])) return "先做递归研究搜索，再回填变量与方法要求。";
  if (draft.fileCount > 0 || includesAny(normalized, ["cfps", "chns", "cgss", "数据"])) {
    return "启动字段画像，生成变量角色候选。";
  }
  return "补充数据线索或让 Supervisor 搜索可用数据。";
}

export function useSemanticAnalysis(draft: SemanticDraft): SemanticItem[] {
  return useMemo(() => {
    const normalized = draft.message.toLowerCase();
    return [
      {
        label: "研究对象",
        title: detectTopic(draft.message),
        body: "将用户输入压缩为本轮研究对象，只用于草案层判断。",
        signal: draft.message.trim() ? "topic_detected" : "empty",
      },
      {
        label: "数据线索",
        title: "可用数据边界",
        body: detectDataSignal(draft, normalized),
        signal: draft.fileCount || draft.pastedCount ? "local_material" : "needs_source",
      },
      {
        label: "方法线索",
        title: "候选识别路径",
        body: detectMethodSignal(normalized),
        signal: "exploratory_method",
      },
      {
        label: "证据缺口",
        title: "进入执行前必须补齐",
        body: detectEvidenceGap(draft, normalized),
        signal: "needs_human_review",
      },
      {
        label: "下一步任务",
        title: "Supervisor 草案动作",
        body: nextTask(draft, normalized),
        signal: draft.mode,
      },
    ];
  }, [draft]);
}

function GlowCard({ children, className }: { children: ReactNode; className?: string }) {
  const cardRef = useRef<HTMLElement>(null);

  useEffect(() => {
    function syncPointer(event: PointerEvent) {
      const card = cardRef.current;
      if (!card) return;
      const rect = card.getBoundingClientRect();
      card.style.setProperty("--glow-x", `${event.clientX - rect.left}px`);
      card.style.setProperty("--glow-y", `${event.clientY - rect.top}px`);
    }

    document.addEventListener("pointermove", syncPointer);
    return () => document.removeEventListener("pointermove", syncPointer);
  }, []);

  return (
    <article className={cn("semantic-glow-card", className)} data-glow-card ref={cardRef}>
      {children}
    </article>
  );
}

export function SemanticGlowCards({ draft }: { draft: SemanticDraft }) {
  const items = useSemanticAnalysis(draft);
  if (!draft.hasMaterial) return null;

  return (
    <section aria-label="实时语义分析" className="semantic-analysis-grid">
      {items.map((item) => (
        <GlowCard key={item.label}>
          <span>{item.label}</span>
          <strong>{item.title}</strong>
          <p>{item.body}</p>
          <small>{item.signal}</small>
        </GlowCard>
      ))}
    </section>
  );
}
