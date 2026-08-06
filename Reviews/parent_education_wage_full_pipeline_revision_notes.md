# 修订笔记 · continuous_loop_parent_education_wage_20260807_001958_r1

## 质量门

- path: `Results/json/parent_education_wage_full_pipeline_quality.json`
- verdict: ['too_thin', 'section_length_gate_required', 'needs_review_loop']
- status: None
- learn_signal: `Results/json/parent_education_wage_full_pipeline_learn_signal.json`

## 强制红线

1. 文献 verified_count=0 → 不得写正式引用列表冒充已核验。
2. OLS ≠ 因果。
3. 所有数字必须回链 table/json。

## recommended_next_tasks（机器可读，供 L8 消费）

```json
[
  {
    "id": "expand_working_paper_sections",
    "agent": "ManuscriptAgent",
    "reason": "正文结构或篇幅还没有达到 working paper 初稿区间。",
    "inputs": []
  },
  {
    "id": "expand_underdeveloped_sections",
    "agent": "ManuscriptAgent",
    "reason": "核心章节已存在，但篇幅没有达到 working paper 可审阅的最低厚度。",
    "inputs": [
      {
        "section": "Introduction",
        "status": "too_short",
        "english_word_count": 4,
        "chinese_char_count": 689,
        "target_english_words": "1800-3000",
        "target_chinese_chars": "2800-5000"
      },
      {
        "section": "Literature and Contribution",
        "status": "too_short",
        "english_word_count": 36,
        "chinese_char_count": 1368,
        "target_english_words": "1000-1800",
        "target_chinese_chars": "1500-3000"
      },
      {
        "section": "Institutional Background / Theory / Context",
        "status": "too_short",
        "english_word_count": 1,
        "chinese_char_count": 536,
        "target_english_words": "800-1500",
        "target_chinese_chars": "1200-2500"
      },
      {
        "section": "Data and Measurement",
        "status": "too_short",
        "english_word_count": 1,
        "chinese_char_count": 475,
        "target_english_words": "800-1500",
        "target_chinese_chars": "1200-2500"
      },
      {
        "section": "Empirical Strategy",
        "status": "too_short",
        "english_word_count": 6,
        "chinese_char_count": 263,
        "target_english_words": "1200-2000",
        "target_chinese_chars": "1800-3500"
      },
      {
        "section": "Main Results",
        "status": "too_short",
        "english_word_count": 6,
        "chinese_char_count": 457,
        "target_english_words": "2000-3500",
        "target_chinese_chars": "3000-6000"
      },
      {
        "section": "Robustness / Mechanisms / Heterogeneity",
        "status": "too_short",
        "english_word_count": 0,
        "chinese_char_count": 415,
        "target_english_words": "1500-3000",
        "target_chinese_chars": "2200-5000"
      },
      {
        "section": "Conclusion",
        "status": "too_short",
        "english_word_count": 7,
        "chinese_char_count": 285,
        "target_english_words": "500-800",
        "target_chinese_chars": "800-1300"
      }
    ],
    "section_expansion_packet": {
      "source": "section_length_checks",
      "source_quality_report": "Results/json/paper_quality_report.json",
      "owner_agent": "ManuscriptAgent",
      "draft_layer_only": true,
      "formal_writeback_allowed": false,
      "sections": [
        {
          "section": "Introduction",
          "status": "too_short",
          "current_units": {
            "english_word_count": 4,
            "chinese_char_count": 689
          },
          "target_units": {
            "english_words": "1800-3000",
            "chinese_chars": "2800-5000"
          },
          "required_evidence": [
            "research_question",
            "contribution_matrix.md",
            "approved_findings"
          ],
          "writing_instruction": "补齐本节论证链、证据来源和与全文主问题的连接。",
          "output_path": "Manuscripts/sections/introduction.md"
        },
        {
          "section": "Literature and Contribution",
          "status": "too_short",
          "current_units": {
            "english_word_count": 36,
            "chinese_char_count": 1368
          },
          "target_units": {
            "english_words": "1000-1800",
            "chinese_chars": "1500-3000"
          },
          "required_evidence": [
            "verified_bibliography.csv",
            "contribution_matrix.md",
            "closest_papers"
          ],
          "writing_instruction": "先按相邻问题、识别方法和本文增量组织文献，再把每一类贡献绑定到已核验来源。",
          "output_path": "Manuscripts/sections/literature-and-contribution.md"
        },
        {
          "section": "Institutional Background / Theory / Context",
          "status": "too_short",
          "current_units": {
            "english_word_count": 1,
            "chinese_char_count": 536
          },
          "target_units": {
            "english_words": "800-1500",
            "chinese_chars": "1200-2500"
          },
          "required_evidence": [
            "domain_notes",
            "mechanism_hypotheses",
            "literature_context"
          ],
          "writing_instruction": "补齐本节论证链、证据来源和与全文主问题的连接。",
          "output_path": "Manuscripts/sections/institutional-background-theory-context.md"
        },
        {
          "section": "Data and Measurement",
          "status": "too_short",
          "current_units": {
            "english_word_count": 1,
            "chinese_char_count": 475
          },
          "target_units": {
            "english_words": "800-1500",
            "chinese_chars": "1200-2500"
          },
          "required_evidence": [
            "dataset_profile",
            "variable_dictionary",
            "sample_construction_log"
          ],
          "writing_instruction": "补齐数据来源、样本筛选、变量定义、缺失处理和描述统计，不把未校验字段写成正式事实。",
          "output_path": "Manuscripts/sections/data-and-measurement.md"
        },
        {
          "section": "Empirical Strategy",
          "status": "too_short",
          "current_units": {
            "english_word_count": 6,
            "chinese_char_count": 263
          },
          "target_units": {
            "english_words": "1200-2000",
            "chinese_chars": "1800-3500"
          },
          "required_evidence": [
            "design_spec",
            "run_plan",
            "method_gate_report"
          ],
          "writing_instruction": "写清估计方程、识别假设、标准误、方法门状态和仍需人工判断的边界。",
          "output_path": "Manuscripts/sections/empirical-strategy.md"
        },
        {
          "section": "Main Results",
          "status": "too_short",
          "current_units": {
            "english_word_count": 6,
            "chinese_char_count": 457
          },
          "target_units": {
            "english_words": "2000-3500",
            "chinese_chars": "3000-6000"
          },
          "required_evidence": [
            "main_regression_table",
            "approved_findings",
            "coefficient_interpretation"
          ],
          "writing_instruction": "围绕主表和主图解释系数方向、量级、显著性、经济含义和与研究问题的关系。",
          "output_path": "Manuscripts/sections/main-results.md"
        },
        {
          "section": "Robustness / Mechanisms / Heterogeneity",
          "status": "too_short",
          "current_units": {
            "english_word_count": 0,
            "chinese_char_count": 415
          },
          "target_units": {
            "english_words": "1500-3000",
            "chinese_chars": "2200-5000"
          },
          "required_evidence": [
            "robustness_matrix",
            "mechanism_or_heterogeneity_results",
            "method_gate_report"
          ],
          "writing_instruction": "把稳健性、机制、异质性和敏感性结果按证据强度分层组织。",
          "output_path": "Manuscripts/sections/robustness-mechanisms-heterogeneity.md"
        },
        {
          "section": "Conclusion",
          "status": "too_short",
          "current_units": {
            "english_word_count": 7,
            "chinese_char_count": 285
          },
          "target_units": {
            "english_words": "500-800",
            "chinese_chars": "800-1300"
          },
          "required_evidence": [
            "approved_findings",
            "limitations_register",
            "reviewer_scorecard_report"
          ],
          "writing_instruction": "补齐本节论证链、证据来源和与全文主问题的连接。",
          "output_path": "Manuscripts/sections/conclusion.md"
        }
      ],
      "verification": {
        "required_before_completion": [
          "section_length_checks.status=passed",
          "updated_section_drafts",
          "human_review_before_formal_writeback",
          "no_state_product_writeback"
        ]
      }
    },
    "verification": {
      "required_before_completion": [
        "section_length_checks.status=passed",
        "updated_section_drafts"
      ]
    }
  },
  {
    "id": "run_reviewer_revision_loop",
    "agent": "ReviewerAgent",
    "reason": "形成审稿意见、修订记录和再次生成路径。",
    "inputs": [
      "paper_draft",
      "paper_quality_report"
    ]
  }
]
```
