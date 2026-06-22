# 章节草案入口

- 状态：`section_scaffolds_ready`
- 来源：`Results/json/paper_revision_round.json`
- 章节数：9
- 正式层写回：关闭

## Agent Team 调用节奏

- call_when: after_section_scaffold_manifest_written
- called_agents: ['ManuscriptAgent']
- recall_when: after_section_draft_files_written
- next_call_when: before_evidence_bound_section_drafting
- boundary: 章节入口已准备；下一步由 ManuscriptAgent 按证据清单扩写草案正文。

## 章节入口

### Abstract

- 文件：`Manuscripts/sections/abstract.md`
- 状态：`section_scaffold_ready`
- 证据项：3
- 工单：`Reviews/agent_packets/manuscriptagent/sections/abstract.md`

### Introduction

- 文件：`Manuscripts/sections/introduction.md`
- 状态：`section_scaffold_ready`
- 证据项：3
- 工单：`Reviews/agent_packets/manuscriptagent/sections/introduction.md`

### Literature and Contribution

- 文件：`Manuscripts/sections/literature-and-contribution.md`
- 状态：`section_scaffold_ready`
- 证据项：3
- 工单：`Reviews/agent_packets/manuscriptagent/sections/literature-and-contribution.md`

### Institutional Background / Theory / Context

- 文件：`Manuscripts/sections/institutional-background-theory-context.md`
- 状态：`section_scaffold_ready`
- 证据项：3
- 工单：`Reviews/agent_packets/manuscriptagent/sections/institutional-background-theory-context.md`

### Conclusion

- 文件：`Manuscripts/sections/conclusion.md`
- 状态：`section_scaffold_ready`
- 证据项：3
- 工单：`Reviews/agent_packets/manuscriptagent/sections/conclusion.md`

### Data and Measurement

- 文件：`Manuscripts/sections/data-and-measurement.md`
- 状态：`section_scaffold_ready`
- 证据项：3
- 工单：`Reviews/agent_packets/manuscriptagent/sections/data-and-measurement.md`

### Empirical Strategy

- 文件：`Manuscripts/sections/empirical-strategy.md`
- 状态：`section_scaffold_ready`
- 证据项：3
- 工单：`Reviews/agent_packets/manuscriptagent/sections/empirical-strategy.md`

### Main Results

- 文件：`Manuscripts/sections/main-results.md`
- 状态：`section_scaffold_ready`
- 证据项：3
- 工单：`Reviews/agent_packets/manuscriptagent/sections/main-results.md`

### Robustness / Mechanisms / Heterogeneity

- 文件：`Manuscripts/sections/robustness-mechanisms-heterogeneity.md`
- 状态：`section_scaffold_ready`
- 证据项：3
- 工单：`Reviews/agent_packets/manuscriptagent/sections/robustness-mechanisms-heterogeneity.md`

## 正式层保护

- changed: `False`
