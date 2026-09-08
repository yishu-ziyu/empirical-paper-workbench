# 一次真实 Results：API 证据，未通过完整验收

本轮未操作浏览器；API 成功不替代 Card → Results → Evidence 的实际浏览器验收。操作员通过普通账号 API 执行测试批准，不代表真人理解或外部验收。

- session：`b0c198b9-68d2-4ced-9e6b-8d87c74578d0`；复用 API 线唯一真实 Card，12 个 specification runs 为 ok。
- 预期于冻结前写入，保留原结构化 seed criterion（IV < OLS），没有事后改变判断条件。英文编辑未同步中文 seed text，证据保留该差异。
- 审阅 Claim 的关联表述、两项实际来源和 IV 限制后，普通批准接口 200。未选主分析时 prepare-paper 返回 409；显式 promote 已完成的 `iv_region_dummies` 后 prepare 200。无 DB 改研究或强制放行。
- 初次执行在 refresh 401 处停止，`results-execution.json` 中生成次数为 0。保留原件后，普通重新登录继续一次 Results；这不算续期成功。
- 唯一 `generate-chapter` 请求 HTTP 200，15.133 秒。正文非空，`generation_source=llm`，未降级生成。
- **评审不通过本项要求**：`review_source=mock_fallback`、`review_degraded=true`、`grounding_failures=[wording_exceeds_evidence]`。`auto_decision=pass`/score .71 不能覆盖这些失败。没有重试生成，没有批准该章节。现有 `review_chapter.py` 捕获异常降级，未返回异常类别；具体供应商/解析根因待查，不凭连通性探针推断实际评审成功。
- 对文本的人工代码审阅发现：把 IV 大于 OLS 描述为既定偏误解释、把“替代聚类”描述为已验证稳健性，不能仅凭这次主表确定这些结论。正文仅作为失败证据保存，不能对外当作验收通过的统计结果。
- Evidence API 200，`available=true`，source run 为 `c96fd037-efc9-4ac6-a249-95769cbce028`、SUCCEEDED，包含数据 hash、代码路径、events URL。只验证了 API 来源目标，未验证浏览器点击回跳。
- `.tex` 导出 HTTP 200，已重新打开为 UTF-8 文本，4867 bytes，有 document 环境，SHA256 `3ba31629768e3c5b0055a74ab30b927f5fde4f4e5b025cb497ee8f5e410ef4f5`。它包含上述未获批准正文；不声称 PDF/Word 成功。
- chapter 响应未公开实际 provider request ID/token 用量，因此未估算或伪造。

## 可复查命令

脚本 `scripts/private_pilot_results_check.py` 使用外部 0600 账号文件、外部 env 中的 TLS CA 与网关密码；不输出凭据、不注入 Bearer、不覆盖 Cookie 路径、不请求新 Card。先不传 `--approve-inspected-claim` 读取 Claim；审阅后传已检查的 ID 执行一次生成。现有研究已有正文，**不要再次运行生成**。

实跑参数：`--session b0c198b9-68d2-4ced-9e6b-8d87c74578d0 --url https://localhost:18443`；env 为隔离的 `project-ssot-provider.env`，账号为 `api-valid-uuid-run-accounts.json`，二者位于 checkout 外受限目录。输出依次为 results-inspection.json、results-execution.json、results-real-once.json（最后一次实际发出唯一生成请求）。

语法检查：`python3 -m py_compile scripts/private_pilot_results_check.py` 通过。未修改应用、未使用浏览器、未公开部署。

## 封装诊断更新（保留首次结果）

后续隔离镜像诊断记录在 `review-first-failure.md`：镜像没有 `pydantic_ai`，而 `build_review_agent` 首先执行 `from pydantic_ai import Agent`；运行依赖缺少 agent 已固定的 `pydantic-ai-slim[openai]==2.35.3`。这是已定位的封装缺项和必经 import 失败路径。首次响应本身没有保存异常类别；不能把它改写成已记录供应商错误。补包后的 offline import/build 验证由部署实现证据记录。

代码检查也确认当前没有“只评审现有正文”的产品 POST 接口：GET `/review` 只读；POST `/review/decision` 的 reject 会重新生成、accept/force_pass 会放行；直接 content edit 只落盘并清理旧评审。因此不能通过这些端点伪装一次独立重评。本子任务没有追加生成、接受或强制放行操作。
