# 端点一览

> 上级：[econpaper API 文档](../README.md)


| Router | 端点 | 方法 | 说明 |
|--------|------|------|------|
| sessions | `/upload` | POST | 上传 CSV 文件，创建 session，运行 graph pipeline |
| sessions | `/sessions` | POST | 创建空 session（不上传文件） |
| sessions | `/sessions/{id}` | GET | 查询 session 状态（用于 localStorage 恢复校验） |
| sessions | `/sessions/{id}/export` | GET | 导出论文源码（format=tex 当前仅支持 LaTeX） |
| outline | `/sessions/{id}/direction` | POST | 设置研究方向；识别通过后写 Table 1 + 方程并停下 |
| outline | `/sessions/{id}/prewrite/confirm` | POST | 确认方向预览后继续 estimate → outline |
| outline | `/sessions/{id}/resume` | POST | 用户调整大纲后重跑 generate_outline |
| chapter | `/sessions/{id}/generate-chapter` | POST | 生成指定章节（写入 current_chapter → 跑节点 → 返回章节） |
| chapter | `/sessions/{id}/approve-chapter` | POST | 审批章节，标记 status="approved" |
| chapter | `/sessions/{id}/rollback` | POST | 回滚到指定版本 |
| chapter | `/sessions/{id}/regenerate` | POST | 重新生成当前章 |
| chapter | `/sessions/{id}/chapters/{index}/versions` | GET | 获取指定章节的所有版本历史 |
| eda | `/sessions/{id}/eda` | POST | 探索性数据分析（describe / corr / missing / plot / scatter / regression） |
| sample | `/sessions/{id}/transform` | POST | 变量重编码与构造（sub-step 5） |
| sample | `/sessions/{id}/filter` | POST | 样本筛选（sub-step 6） |
| sample | `/sessions/{id}/balance` | POST | 面板平衡性检查（sub-step 7） |
| charls | `/sessions/{id}/charls/detect` | GET | CHARLS 数据集检测 |
| charls | `/sessions/{id}/charls/confirm` | POST | 确认 CHARLS 向导配置 |
| code_export | `/sessions/{id}/replication-package` | GET | 复现包 zip：实际运行的代码 + 研究时的数据 + README |
| code_export | `/sessions/{id}/replication-script` | GET | 复现脚本 `replication.py`：设定运行实际执行的调用 |
| code_export | `/sessions/{id}/code-export` | GET | 导出翻译版代码（py / do / R / m），数值未核对 |
| doc_export | `/sessions/{id}/doc-export` | GET | 导出文档（tex / pdf / docx） |
| progress | `/sessions/{id}/progress` | GET | 查询论文完成进度 |
| review | `/sessions/{id}/review` | GET | 获取当前章的评审信息 |
| review | `/sessions/{id}/review/decision` | POST | 提交 HITL 评审决策（accept / reject / force_pass） |
| ws | `/sessions/{id}/stream` | WS | WebSocket 实时流推送 |
| — | `/` | GET | 服务根路径（返回服务信息） |
| — | `/health` | GET | 健康检查 |
