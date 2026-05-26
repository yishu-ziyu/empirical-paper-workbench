# Auto Research Report

## 研究题目

工业机器人暴露是否影响劳动收入再配置？使用 CFPS 与工业机器人暴露数据

## 能力状态

- local_data: available (local datasets detected)
- statspai: available (statspai module importable)
- cnki: blocked_by_browser_session (Chrome DevTools endpoint not detected; CNKI remains manual-assisted)
- web_search: available (network connectivity check succeeded)
- agentmemory: unavailable (agentmemory executable not found)
- llm_supervisor: unavailable (EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC is not enabled)

## 变量候选

```json
{
  "status": "needs_human_review",
  "evidence_level": "local_file",
  "can_promote": false,
  "dataset": {
    "name": "cfps_robot_reallocation.csv",
    "path": "Data/Final/cfps_robot_reallocation.csv",
    "suffix": ".csv",
    "size": 3729019
  },
  "columns": [
    "pid",
    "provcd",
    "urban",
    "ln_wage",
    "manu_dummy",
    "ISEI_score",
    "part_time",
    "female",
    "age",
    "edu_last",
    "year",
    "year_robot",
    "robot_density",
    "ln_robot",
    "bartik_iv",
    "provcd_num"
  ],
  "roles": {
    "outcome_candidates": [
      "ln_wage"
    ],
    "treatment_candidates": [
      "year_robot",
      "robot_density",
      "ln_robot"
    ],
    "control_candidates": [
      "urban",
      "female",
      "age",
      "edu_last"
    ],
    "instrument_candidates": []
  },
  "rationale": "变量角色为自动候选，必须人工确认后才可进入正式 VariableRoleSet。"
}
```

## 方法候选

- OLS: candidate - 建立探索性基准相关关系，不宣称因果识别。
- DID/IV/RDD/PSM/DML: needs_evidence - 根据题目语义和数据结构选择更强识别策略。

## 缺失证据

- capability_cnki: blocked_by_browser_session Chrome DevTools endpoint not detected; CNKI remains manual-assisted
- capability_agentmemory: unavailable agentmemory executable not found
- capability_llm_supervisor: unavailable EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC is not enabled
- method_identification_upgrade: needs_evidence

## 证据边界

本报告为 exploratory / needs_human_review，不能直接作为正式论文证据。
