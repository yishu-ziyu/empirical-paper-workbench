# CGSS 审稿式修订任务队列

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- schema：`p6.cgss_revision_task_queue.v1`
- 状态：`needs_human_revision_queue_approval`
- 草案层：是
- 写入正式论文：否
- 写入 state/product/agent_task_queue.json：否
- 写入 DesignSpec / RunPlan：否

## 当前需要处理
- `revision_queue_needs_human_approval`

## Agent 队列

### LiteratureAgent
- `literature.verify_open_seed_sources`：核验未批准文献与 CGSS 官方来源 -> `Reviews/agent_packets/literatureagent/cgss_source_verification.md`
- `literature.revise_review_blocks`：审阅文献综述段落块 -> `Reviews/agent_packets/literatureagent/cgss_literature_revision_brief.md`

### MethodAgent
- `method.decide_primary_ordered_outcome_model`：审阅 OLS 与 Ordered Logit 的主模型角色 -> `Reviews/agent_packets/methodagent/cgss_primary_model_decision.md`
- `method.review_blocked_causal_methods`：复核暂不进入的因果方法族 -> `Reviews/agent_packets/methodagent/cgss_blocked_method_review.md`

### WriterAgent
- `writer.prepare_section_revision_briefs`：生成章节级修订简报 -> `Reviews/agent_packets/writeragent/cgss_section_revision_briefs.md`
- `writer.prepare_claim_wording_guardrails`：生成论断措辞边界 -> `Reviews/agent_packets/writeragent/cgss_claim_wording_guardrails.md`

### ReviewerAgent
- `reviewer.audit_revision_queue`：审计四类 Agent 修订队列 -> `Reviews/agent_packets/revieweragent/cgss_revision_queue_audit.md`
- `reviewer.prepare_human_approval_checklist`：生成人工批准检查清单 -> `Reviews/agent_packets/revieweragent/cgss_human_approval_checklist.md`

## 人工批准后才可进入
- `agent_draft_review_packets`
- `human_reviewer_round`
- `draft_section_revision_briefs`

## 队列 JSON
```json
{
  "schema_version": "p6.cgss_revision_task_queue.v1",
  "generated_at": "2026-05-27T11:00:58.614666+00:00",
  "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
  "draft_layer_only": true,
  "formal_writeback_allowed": false,
  "source_artifacts": {
    "literature_seed_package": {
      "path": "Results/json/cgss_social_capital_happiness_literature_seed_package.json",
      "schema_version": "p6.cgss_literature_seed_package.v1",
      "status": "needs_human_literature_review"
    },
    "literature_review_draft_packet": {
      "path": "Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json",
      "schema_version": "p6.cgss_literature_review_draft_packet.v1",
      "status": "needs_human_literature_review_draft_approval"
    },
    "method_structure_gate_packet": {
      "path": "Results/json/cgss_social_capital_happiness_method_structure_gate_packet.json",
      "schema_version": "p6.cgss_method_structure_gate_packet.v1",
      "status": "needs_human_method_structure_approval"
    }
  },
  "boundary_flags": {
    "wrote_formal_manuscript": false,
    "wrote_state_product": false,
    "modified_design_spec": false,
    "modified_run_plan": false,
    "wrote_agent_task_queue_json": false
  },
  "status": "needs_human_revision_queue_approval",
  "blocking_reasons": [
    "revision_queue_needs_human_approval"
  ],
  "agent_packets": [
    {
      "agent": "LiteratureAgent",
      "input_summary": {
        "seed_source_count": 10,
        "coverage": [
          "social_capital_theory",
          "subjective_wellbeing_measurement",
          "cgss_empirical_context",
          "ordinal_outcome_method",
          "chinese_literature_queue"
        ],
        "open_source_ids": [
          "S01",
          "S02",
          "S05"
        ],
        "paragraph_block_ids": [
          "theory_foundation",
          "measurement_foundation",
          "cgss_empirical_context",
          "method_transition"
        ]
      },
      "tasks": [
        {
          "task_id": "literature.verify_open_seed_sources",
          "agent": "LiteratureAgent",
          "title": "核验未批准文献与 CGSS 官方来源",
          "objective": "逐条处理 open dependency，补齐访问日期、DOI/Zotero 元数据和中文文献人工核验结论。",
          "evidence_inputs": [
            "literature_seed_package.seed_sources",
            "literature_review_draft_packet.open_dependencies"
          ],
          "output_target": "Reviews/agent_packets/literatureagent/cgss_source_verification.md",
          "status": "queued_for_human_approved_revision",
          "draft_layer_only": true,
          "formal_writeback_allowed": false
        },
        {
          "task_id": "literature.revise_review_blocks",
          "agent": "LiteratureAgent",
          "title": "审阅文献综述段落块",
          "objective": "检查理论、测量、中国经验和方法衔接四类段落是否仍停留在候选层，并提出草案层修订建议。",
          "evidence_inputs": [
            "literature_review_draft_packet.paragraph_blocks",
            "literature_seed_package.coverage"
          ],
          "output_target": "Reviews/agent_packets/literatureagent/cgss_literature_revision_brief.md",
          "status": "queued_for_human_approved_revision",
          "draft_layer_only": true,
          "formal_writeback_allowed": false
        }
      ],
      "acceptance_checks": [
        "source_verification_recorded",
        "paragraph_blocks_reviewed",
        "no_formal_bibliography_write"
      ],
      "write_boundary": {
        "draft_layer_only": true,
        "formal_writeback_allowed": false,
        "must_not_write": [
          "Manuscripts/sections",
          "Data/literature/processed/verified_bibliography.csv",
          "state/product"
        ]
      }
    },
    {
      "agent": "MethodAgent",
      "input_summary": {
        "claim_boundary": "positive_conditional_association",
        "supported_claim_types": [
          "conditional_association",
          "ordered_outcome_robustness"
        ],
        "blocked_method_families": [
          "DID",
          "IV",
          "RDD",
          "PSM",
          "DML"
        ],
        "human_decisions": [
          "OLS 作为主模型还是 Ordered Logit 作为主模型",
          "是否把社会资本指数拆成信任、交往、参与三个分维度",
          "是否补充跨年份 CGSS 或其他稳健性数据"
        ]
      },
      "tasks": [
        {
          "task_id": "method.decide_primary_ordered_outcome_model",
          "agent": "MethodAgent",
          "title": "审阅 OLS 与 Ordered Logit 的主模型角色",
          "objective": "基于当前主结果门禁，给出 OLS/Ordered Logit 在正文和稳健性中的推荐排布。",
          "evidence_inputs": [
            "method_structure_gate_packet.method_claim_gates.main_result_gate"
          ],
          "output_target": "Reviews/agent_packets/methodagent/cgss_primary_model_decision.md",
          "status": "queued_for_human_approved_revision",
          "draft_layer_only": true,
          "formal_writeback_allowed": false
        },
        {
          "task_id": "method.review_blocked_causal_methods",
          "agent": "MethodAgent",
          "title": "复核暂不进入的因果方法族",
          "objective": "检查 DID、IV、RDD、PSM、DML 等方法族的阻断理由，避免在正文中写入未获支持的因果设计。",
          "evidence_inputs": [
            "method_structure_gate_packet.method_claim_gates.blocked_method_families"
          ],
          "output_target": "Reviews/agent_packets/methodagent/cgss_blocked_method_review.md",
          "status": "queued_for_human_approved_revision",
          "draft_layer_only": true,
          "formal_writeback_allowed": false
        }
      ],
      "acceptance_checks": [
        "claim_boundary_confirmed",
        "blocked_methods_remain_out_of_formal_design",
        "human_model_decision_recorded"
      ],
      "write_boundary": {
        "draft_layer_only": true,
        "formal_writeback_allowed": false,
        "must_not_write": [
          "DesignSpec",
          "RunPlan",
          "state/product"
        ]
      }
    },
    {
      "agent": "WriterAgent",
      "input_summary": {
        "paragraph_block_count": 4,
        "target_sections": [
          "Abstract",
          "Introduction",
          "Literature and Contribution",
          "Institutional Background / Theory / Context",
          "Data and Measurement",
          "Empirical Strategy",
          "Main Results",
          "Robustness / Mechanisms / Heterogeneity",
          "Conclusion",
          "References"
        ]
      },
      "tasks": [
        {
          "task_id": "writer.prepare_section_revision_briefs",
          "agent": "WriterAgent",
          "title": "生成章节级修订简报",
          "objective": "把文献段落、方法门禁和章节证据要求转成草案层写作工单，不直接写正式论文正文。",
          "evidence_inputs": [
            "literature_review_draft_packet.paragraph_blocks",
            "method_structure_gate_packet.section_standards"
          ],
          "output_target": "Reviews/agent_packets/writeragent/cgss_section_revision_briefs.md",
          "status": "queued_for_human_approved_revision",
          "draft_layer_only": true,
          "formal_writeback_allowed": false
        },
        {
          "task_id": "writer.prepare_claim_wording_guardrails",
          "agent": "WriterAgent",
          "title": "生成论断措辞边界",
          "objective": "把 positive conditional association、有序模型稳健性和禁止因果措辞写成草案层写作约束。",
          "evidence_inputs": [
            "method_structure_gate_packet.method_claim_gates.supported_claims"
          ],
          "output_target": "Reviews/agent_packets/writeragent/cgss_claim_wording_guardrails.md",
          "status": "queued_for_human_approved_revision",
          "draft_layer_only": true,
          "formal_writeback_allowed": false
        }
      ],
      "acceptance_checks": [
        "section_briefs_ready",
        "claim_wording_guardrails_ready",
        "formal_manuscript_not_written"
      ],
      "write_boundary": {
        "draft_layer_only": true,
        "formal_writeback_allowed": false,
        "must_not_write": [
          "Manuscripts/sections",
          "Manuscripts/generated",
          "state/product"
        ]
      }
    },
    {
      "agent": "ReviewerAgent",
      "input_summary": {
        "input_statuses": {
          "literature_seed_package": "needs_human_literature_review",
          "literature_review_draft_packet": "needs_human_literature_review_draft_approval",
          "method_structure_gate_packet": "needs_human_method_structure_approval"
        }
      },
      "tasks": [
        {
          "task_id": "reviewer.audit_revision_queue",
          "agent": "ReviewerAgent",
          "title": "审计四类 Agent 修订队列",
          "objective": "复核每条任务是否有输入、输出、人工批准条件和正式层保护边界。",
          "evidence_inputs": [
            "revision_task_queue.agent_packets"
          ],
          "output_target": "Reviews/agent_packets/revieweragent/cgss_revision_queue_audit.md",
          "status": "queued_for_human_approved_revision",
          "draft_layer_only": true,
          "formal_writeback_allowed": false
        },
        {
          "task_id": "reviewer.prepare_human_approval_checklist",
          "agent": "ReviewerAgent",
          "title": "生成人工批准检查清单",
          "objective": "把文献、方法和写作任务压缩成人工审阅前必须确认的清单。",
          "evidence_inputs": [
            "literature_seed_package.status",
            "literature_review_draft_packet.status",
            "method_structure_gate_packet.status"
          ],
          "output_target": "Reviews/agent_packets/revieweragent/cgss_human_approval_checklist.md",
          "status": "queued_for_human_approved_revision",
          "draft_layer_only": true,
          "formal_writeback_allowed": false
        }
      ],
      "acceptance_checks": [
        "human_approval_required",
        "draft_layer_only",
        "no_agent_task_queue_json_written"
      ],
      "write_boundary": {
        "draft_layer_only": true,
        "formal_writeback_allowed": false,
        "must_not_write": [
          "state/product/agent_task_queue.json",
          "DesignSpec",
          "RunPlan",
          "formal manuscript"
        ]
      }
    }
  ],
  "agent_task_queue": [
    {
      "task_id": "literature.verify_open_seed_sources",
      "agent": "LiteratureAgent",
      "title": "核验未批准文献与 CGSS 官方来源",
      "objective": "逐条处理 open dependency，补齐访问日期、DOI/Zotero 元数据和中文文献人工核验结论。",
      "evidence_inputs": [
        "literature_seed_package.seed_sources",
        "literature_review_draft_packet.open_dependencies"
      ],
      "output_target": "Reviews/agent_packets/literatureagent/cgss_source_verification.md",
      "status": "queued_for_human_approved_revision",
      "draft_layer_only": true,
      "formal_writeback_allowed": false
    },
    {
      "task_id": "literature.revise_review_blocks",
      "agent": "LiteratureAgent",
      "title": "审阅文献综述段落块",
      "objective": "检查理论、测量、中国经验和方法衔接四类段落是否仍停留在候选层，并提出草案层修订建议。",
      "evidence_inputs": [
        "literature_review_draft_packet.paragraph_blocks",
        "literature_seed_package.coverage"
      ],
      "output_target": "Reviews/agent_packets/literatureagent/cgss_literature_revision_brief.md",
      "status": "queued_for_human_approved_revision",
      "draft_layer_only": true,
      "formal_writeback_allowed": false
    },
    {
      "task_id": "method.decide_primary_ordered_outcome_model",
      "agent": "MethodAgent",
      "title": "审阅 OLS 与 Ordered Logit 的主模型角色",
      "objective": "基于当前主结果门禁，给出 OLS/Ordered Logit 在正文和稳健性中的推荐排布。",
      "evidence_inputs": [
        "method_structure_gate_packet.method_claim_gates.main_result_gate"
      ],
      "output_target": "Reviews/agent_packets/methodagent/cgss_primary_model_decision.md",
      "status": "queued_for_human_approved_revision",
      "draft_layer_only": true,
      "formal_writeback_allowed": false
    },
    {
      "task_id": "method.review_blocked_causal_methods",
      "agent": "MethodAgent",
      "title": "复核暂不进入的因果方法族",
      "objective": "检查 DID、IV、RDD、PSM、DML 等方法族的阻断理由，避免在正文中写入未获支持的因果设计。",
      "evidence_inputs": [
        "method_structure_gate_packet.method_claim_gates.blocked_method_families"
      ],
      "output_target": "Reviews/agent_packets/methodagent/cgss_blocked_method_review.md",
      "status": "queued_for_human_approved_revision",
      "draft_layer_only": true,
      "formal_writeback_allowed": false
    },
    {
      "task_id": "writer.prepare_section_revision_briefs",
      "agent": "WriterAgent",
      "title": "生成章节级修订简报",
      "objective": "把文献段落、方法门禁和章节证据要求转成草案层写作工单，不直接写正式论文正文。",
      "evidence_inputs": [
        "literature_review_draft_packet.paragraph_blocks",
        "method_structure_gate_packet.section_standards"
      ],
      "output_target": "Reviews/agent_packets/writeragent/cgss_section_revision_briefs.md",
      "status": "queued_for_human_approved_revision",
      "draft_layer_only": true,
      "formal_writeback_allowed": false
    },
    {
      "task_id": "writer.prepare_claim_wording_guardrails",
      "agent": "WriterAgent",
      "title": "生成论断措辞边界",
      "objective": "把 positive conditional association、有序模型稳健性和禁止因果措辞写成草案层写作约束。",
      "evidence_inputs": [
        "method_structure_gate_packet.method_claim_gates.supported_claims"
      ],
      "output_target": "Reviews/agent_packets/writeragent/cgss_claim_wording_guardrails.md",
      "status": "queued_for_human_approved_revision",
      "draft_layer_only": true,
      "formal_writeback_allowed": false
    },
    {
      "task_id": "reviewer.audit_revision_queue",
      "agent": "ReviewerAgent",
      "title": "审计四类 Agent 修订队列",
      "objective": "复核每条任务是否有输入、输出、人工批准条件和正式层保护边界。",
      "evidence_inputs": [
        "revision_task_queue.agent_packets"
      ],
      "output_target": "Reviews/agent_packets/revieweragent/cgss_revision_queue_audit.md",
      "status": "queued_for_human_approved_revision",
      "draft_layer_only": true,
      "formal_writeback_allowed": false
    },
    {
      "task_id": "reviewer.prepare_human_approval_checklist",
      "agent": "ReviewerAgent",
      "title": "生成人工批准检查清单",
      "objective": "把文献、方法和写作任务压缩成人工审阅前必须确认的清单。",
      "evidence_inputs": [
        "literature_seed_package.status",
        "literature_review_draft_packet.status",
        "method_structure_gate_packet.status"
      ],
      "output_target": "Reviews/agent_packets/revieweragent/cgss_human_approval_checklist.md",
      "status": "queued_for_human_approved_revision",
      "draft_layer_only": true,
      "formal_writeback_allowed": false
    }
  ],
  "promotion": {
    "allowed": false,
    "required_decision": "human_approve_cgss_revision_task_queue",
    "would_enable": [
      "agent_draft_review_packets",
      "human_reviewer_round",
      "draft_section_revision_briefs"
    ]
  }
}
```
