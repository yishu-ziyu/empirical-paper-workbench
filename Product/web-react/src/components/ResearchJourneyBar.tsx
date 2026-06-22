type Stage = "brief" | "search" | "variables" | "design" | "execution" | "identification-audit";

const JOURNEY_STAGES = [
  { id: "design", label: "研究设计", stageIds: ["brief"] as Stage[] },
  { id: "data", label: "数据", stageIds: ["search"] as Stage[] },
  { id: "model", label: "模型", stageIds: ["design"] as Stage[] },
  { id: "draft", label: "正文", stageIds: ["execution"] as Stage[] },
  { id: "export", label: "复现导出", stageIds: ["identification-audit"] as Stage[] },
] as const;

type JourneyStatus = "done" | "running" | "pending";

interface ResearchJourneyBarProps {
  activeStage: Stage;
  completedStages: Stage[];
  onStageSelect: (stage: Stage) => void;
}

export function ResearchJourneyBar({
  activeStage,
  completedStages,
  onStageSelect,
}: ResearchJourneyBarProps) {
  const completedSet = new Set(completedStages);

  function getStageStatus(stageIds: readonly Stage[]): JourneyStatus {
    const allDone = stageIds.every((id) => completedSet.has(id));
    if (allDone) return "done";
    if (stageIds.includes(activeStage)) return "running";
    return "pending";
  }

  function handleClick(stageIds: readonly Stage[]) {
    onStageSelect(stageIds[0]);
  }

  return (
    <div className="journey-bar">
      <div className="journey-track">
        {JOURNEY_STAGES.map((stage, index) => {
          const status = getStageStatus(stage.stageIds);
          const isActive = stage.stageIds.includes(activeStage);
          const cls = isActive
            ? "active"
            : status === "done"
              ? "done"
              : status === "running"
                ? "running"
                : "";

          const title =
            status === "done"
              ? "已完成"
              : status === "running"
                ? "进行中"
                : "待处理";

          const nextStatus =
            index < JOURNEY_STAGES.length - 1
              ? getStageStatus(JOURNEY_STAGES[index + 1].stageIds)
              : null;
          const connectorCls =
            index < JOURNEY_STAGES.length - 1 &&
            status === "done" &&
            nextStatus === "done"
              ? "done"
              : "";

          return (
            <div key={stage.id} className="journey-stage-group">
              <div
                className={`journey-stage ${cls}`}
                onClick={() => handleClick(stage.stageIds)}
                title={title}
                role="button"
                tabIndex={0}
              >
                <span className="journey-dot" />
                <span>{stage.label}</span>
              </div>
              {index < JOURNEY_STAGES.length - 1 && (
                <div className={`journey-connector ${connectorCls}`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
