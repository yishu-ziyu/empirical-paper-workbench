# 验收契约：复现脚本（实际运行的代码）

日期：2026-09-24。设计依据：[创作台方案 · 现状差距](../design/paper-workspace/gaps.md)。

## 目标

用户能从产品里下载一份 Python 脚本。脚本里的调用，就是研究台账中每次设定运行实际执行的调用；用分析时的同一份数据运行它，能得到与证据里记录相同的数字。

## 背景事实

- 设定运行（`backend/services/spec_run.py`）读 `pd.read_csv(csv_path)` 后直接调用 `statspai.feols` / `statspai.ivreg`；IV 另跑 `statspai.effective_f_test`。缺少 StatsPAI 时 OLS 退回 `statsmodels`。
- 现有“导出代码”里的 Python 版由 `translate_code` 重新生成（pandas + statsmodels），不是实际运行的代码，界面上也没有说明。

## 必须成立（Hard bar）

1. `GET /sessions/{id}/replication-script` 返回 `replication.py`（附件下载）。脚本按运行顺序，为每条设定运行写出与实际执行相同的调用：同一估计器、同一公式、同一关键字参数。
2. 脚本开头用 sha256 校验分析数据文件；与记录不符时停止运行，并说明原因。
2a. `GET /sessions/{id}/replication-package` 返回 zip：`replication.py`、`analysis_data.csv`（研究时实际读取的那份文件，字节相同）和 `README.md`。解压后直接运行 `python replication.py` 就能复现。只有会话所有者能下载。
3. 在真实 Card 会话里执行设定运行后，用分析数据运行下载的脚本：每条运行的系数与标准误和记录值一致（四位小数），样本量一致，有效 F 与第一阶段 F 一致（两位小数）。由自动测试执行脚本来验证，不能只断言字符串。
4. 生成器不认识的估计器不能被改写成别的调用：脚本里写明“这次计算未纳入脚本”及原因，不输出伪造的代码。
5. 没有设定运行的会话返回 404；别人的会话走现有的会话归属检查。
6. 导出对话框的第一项是“复现脚本 · 实际运行的代码”；原有四种格式标明“翻译版 · 数值未核对”。前端测试覆盖请求路径。
7. 文档同步：API 端点说明、`openapi.json`、前端交互基线、创作台差距清单。

## 不接受的替代

- 用 `translate_code` 的输出冒充复现脚本。
- 只校验脚本文本长什么样，不实际运行。
- 为了让数字对上，在脚本里改公式或参数。

## 验证方式

- 后端：新测试跑真实 Card 流程（`/demos/card` → 冻结 → 设定运行），下载复现包，解压到临时目录执行脚本，逐条比对；另有 404、未知估计器、哈希不符三个反例。
- 前端：`CodeExportDialog` 的 vitest。
- 全量：`make test`、`make docs-check`。
- 真实路径：开发服务器上对 Card 会话下载脚本并在命令行运行。

## 范围外（本轮不做）

- 画布式 Notebook 界面、`used_by` 反查（依赖 Document / Ref）。
- Stata / R 翻译版的数值核对。
- 正式估计链路（`agent/nodes/estimate.py` 主流程、prewrite）的计算记录；本轮只覆盖研究台账的设定运行。

## 结果（2026-09-24）：通过

| 条目 | 证据 |
|---|---|
| 1 实际调用 | `test_script_endpoint_is_the_actual_calls`：每条 ok 运行的公式原样出现，估计器调用一致，不含翻译产物 |
| 2 / 2a 哈希与复现包 | `test_package_reproduces_every_recorded_number`（打包数据与记录 sha256 相同）；`test_script_stops_on_wrong_data`（改一个字节即 `SystemExit`）；`test_changed_data_is_refused`（409 路径） |
| 3 数字一致 | 同上测试：真实 Card 流程执行设定运行后，解压复现包并运行脚本，逐条比对系数、标准误（四位小数）和 F_eff / 第一阶段 F（两位小数） |
| 4 不伪造 | `test_unknown_estimator_is_listed_not_rewritten`、`test_failed_run_is_kept_as_comment` |
| 5 404 / 归属 | `test_no_runs_is_404`；端点复用 `require_session_ownership` |
| 6 界面 | `CodeExportDialog.test.tsx` 新增 4 项：复现包是第一项、只下载脚本不走 code-export、404 显示原因、翻译版单独成栏 |
| 7 文档 | API 端点表与详情、`openapi.json`、前端交互基线、创作台差距清单均已更新 |

全量：`make test` 通过（agent 1072、backend 727、frontend 558，API 漂移检查通过）；`make docs-check` 与 `--changed origin/main` 通过。

未做：开发服务器上的人工下载。测试已在进程内走真实 HTTP 路由、真实 runner 和真实数据，并实际执行脚本；登录后的界面点击没有在浏览器里走一遍。

过程中发现并修复：原型放在 `frontend/src/prototypes/` 时触发了 `cardCanonicalLiterals` 守卫（产品源码不得写死 Card 系数），已移到 `frontend/prototypes/`，没有放宽测试。
