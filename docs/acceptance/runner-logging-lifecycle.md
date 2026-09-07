# 验收契约：issue #30 — runner 日志输出断管不得把成功的研究任务误标 FAILED

Status: open          # open | closed。最后一步才改 closed。

分支：`fix/runner-logging-lifecycle`（自 main `452a8954ca4736d98526d5141c1d098186b09e99` 切出）  
对应 issue：yishu-ziyu/empirical-paper-workbench#30

## Change

日志输出通道故障（runner 进程 stdout/stderr 绑在读端已关闭的管道上）不再把本来成功的研究 run 标为 FAILED；真正的业务失败（含业务路径自身的 BrokenPipeError）仍正常报告 FAILED 且错误可诊断。日志降级过程有留痕、可解释，全渠道不可用时的行为在文档中如实说明。

## Not this

- 不在研究节点（spec_run / research_lab / facade / upload pipeline 业务代码）新增任何宽泛 `catch Exception`；不按异常类名吞业务异常。
- 不改统计结果、Claim 门禁（canonical_mismatch / approve / promote）、evidence_revision 语义。
- 不重构任务队列 / claim-lease 机制；不新增观测平台。
- 不改 backend server（uvicorn）侧日志行为——本次只修 runner 进程族（runner 主进程 + supervisor spawn 子进程）。
- 不动用户已在跑的 5173/8000 服务与其 `.local` 数据；隔离验证一律用独立端口、独立 `ECONPAPER_LOCAL_STATE_ROOT`、自启进程，只清理自己拥有的进程。
- 不进入 Phase C，不夹带 DiD / Research Continuity / localized PR #32 范围。

## Evaluator

implementer 子代理实现 + 逐条跑程序留证据；validator 子代理独立复核（只读代码 + 复跑程序 + 对照本契约出 ACCEPT/REJECT）；最终返回用户（外部复核人）裁决。

## 侦察结论（实现前已核实的事实，implementer 直接采信）

- 引爆链：`DEBUG=true` 时 `backend/database.py:25,50` 的 SQLAlchemy `echo=True` 会把每条 SQL/`COMMIT` INFO 日志写 stderr；stderr 为死管道时 `StreamHandler.emit` 抛 `BrokenPipeError`，`Handler.handleError`（`logging.raiseExceptions` 默认 True）再把 "--- Logging error ---" 写回死 stderr 再次抛出，异常穿透日志栈进入业务代码。
- runner 主进程 `backend/runner.py::main()` 无任何 logging 配置；`process_one_run` 的 `except Exception` 会把执行期异常经 `_stable_failure` 落为 run FAILED（`{TypeName}: {kind} execution failed`）——这正是误标路径。
- upload/prewrite 走 `prewrite_supervisor._execute_supervised` 的 **multiprocessing spawn 子进程**：spawn 不继承父进程 logging 配置；子进程 `_child_main` 捕获 `BaseException` 后把 `type(exc).__name__` 作为 error_type 回传（`prewrite_supervisor.py:156-160`），父进程包装为 `RemoteUploadError` → run FAILED。**修复必须同时覆盖 runner 主进程与 spawn 子进程入口。**
- 任务事件持久化已有独立边界：`runner.progress()` 对 event-store 写失败按可观测性处理（`runner.py:204-210`）；`repo.complete` 终态提交失败使 run 保持可重claim（`runner.py:307-314`）。这些语义**不许变**。
- 配置基建现成可用：`config._state_path(env, *parts)`（env 覆盖 → `LOCAL_STATE_ROOT/<parts>`）、`ECONPAPER_LOCAL_STATE_ROOT` 可整体隔离状态目录、`ensure_private_directory` 修权限。
- `config.validate_runtime_secrets()` 在 import 期执行，DEBUG 下的 JWT 提示 `print` 走块缓冲不立即抛——本次不改 config.py，不属于本契约范围。
- 2026-09-06 生产级事故留档：`docs/acceptance/assets/card-browser-journey-audit-2026-09-06/i02-card-boot-failed-brokenpipe.png`（lsof 证实 runner fd1/fd2 指向同一条读端已死的 PIPE）。

## 修复方向（issue #30 给定，implementer 落实）

1. runner 进程入口（`runner.main()`）配置 logging lifecycle：root logger 显式挂 rotating 文件 handler（默认 `_state_path("ECONPAPER_RUNNER_LOG_FILE", "log", "runner.log")`）+ stderr 控制台 handler（尽力而为）；配置过程幂等（重复进入不叠加 handler）。
2. `logging.raiseExceptions = False` 作为进程级兜底：任何 emit 失败被日志栈自身吸收，绝不穿透业务栈。spawn 子进程入口（`_child_main`）同样生效（子进程可无文件 handler，避免多进程同文件轮转竞争，行为在文档说明）。
3. stderr 通道死亡时：控制台 handler 一次性自禁用，降级原因经文件 handler 留痕一条；文件也不可用时记录被丢弃（诚实说明，不承诺"绝不丢日志"）。
4. 业务异常语义零改动：`_stable_failure`、`repo.fail/complete`、研究节点代码不动。

## Checks

- [ ] C1 **修复前进程级断管复现（回归 A）** — 程序: 仓库内 harness（提交于本分支）以隔离子进程方式跑修复前代码：runner 子进程 fd1+fd2 均指向读端已关闭的管道（复刻事故 lsof 形态），独立 `ECONPAPER_LOCAL_STATE_ROOT` + 独立端口，触发一次真实 `POST /demos/card` upload run — 预期: run 终态 **FAILED**、error 字符串含 BrokenPipeError（与 `_stable_failure` 输出一致）；同时业务已实际提交（DB 中 upload 产物/状态存在）；**实际异常产生位置有 traceback 留档**（harness 可用只读记录器包装 `logging.Handler.handleError` 抓栈写入文件——这只是留档手段，不是 mock  logger 替代进程级复现；复现本身必须是真死管道 + 真业务执行）。证据文件提交到 `docs/acceptance/assets/runner-logging-lifecycle/`，不得只留 /tmp。
- [ ] C2 **修复后两种日志通道下真实任务均成功（回归 B）** — 程序: 同一 harness，修复后：(a) stderr 正常；(b) fd1+fd2 死管道。各触发一次真实 demo card upload run — 预期: 两种条件 run 均 **SUCCEEDED**；验证业务结果与运行记录（upload_readiness=READY、sessions 状态含产物、run 记录含 worker progress 事件），不是只看进程没退出；死管道条件下控制台日志被降级、文件日志仍可用。
- [ ] C3 **业务失败仍 FAILED 且可诊断（回归 C）** — 程序: pytest 级回归（进 `make test`）：注入真实业务错误（stub/触发业务执行器抛错）→ run FAILED、error 为稳定可诊断字符串；其中一例业务路径自身抛 `BrokenPipeError`（模拟 LLM/子进程业务 socket 断管）— 预期: 仍 FAILED，**不因日志修复被吞**；源码核实：研究节点与 `_stable_failure` 无按类名吞 BrokenPipeError 的新逻辑。
- [ ] C4 **降级四不（回归 D）** — 程序: pytest 级回归 + C2 场景断言：(a) 死管道持续写日志无递归风暴（降级留痕仅一条，进程存活完成 run）；(b) 无任务重复执行（run 记录唯一、终态唯一）；(c) 研究结果不重复提交（产物/结果记录唯一，与 C2 断言同源）；(d) logging lifecycle 配置重复调用不叠加 handler（单测断言 handler 数量恒定；含配置函数重复进入与 import 重入两种形态） — 预期: 四项全过。
- [ ] C5 **正常日志可用 + 降级留痕 + 全渠道不可用行为明确（回归 E）** — 程序: C2(a) 断言 stderr 健康时控制台与文件均有日志；死管道场景断言文件中出现一条降级原因记录（含失效通道与剩余通道）；pytest 覆盖"文件与控制台全部不可用"：进程存活、业务完成、记录丢弃不抛错 — 预期: 全过；`docs/local-runner.md` 更新运行说明：修复后不再强依赖重定向（但推荐文件重定向便于排查）、日志文件默认位置与 env 覆盖、降级行为、"所有输出渠道都不可用时日志可能丢弃，业务不受影响"的诚实声明。
- [ ] C6 **红线** — 程序: `git diff main..HEAD` 人工核对 + grep — 预期: 研究节点（services/、facade/、agent/、routers/）无新增宽泛 `except Exception` 吞日志/吞业务异常；统计结果、Claim 门禁、evidence_revision、任务队列结构零改动；改动面限于 runner 进程族 logging lifecycle + 测试 + 文档 + 契约。
- [ ] C7 **全量 gates + CI** — 程序: `cd econpaper && make test`、`cd frontend && npx tsc --noEmit && npm run lint && npm run build`；CI 用推送后最新 HEAD — 预期: 全绿、无新增 skip（`git grep -n '\.skip\|skipIf' -- frontend/src backend/tests` 与 main `452a895` 一致或更少）。
- [ ] C8 **交付物齐全** — 预期: PR 描述含 C1 修复前/后对照、C2 证明、C3 反例、C4 不重复证明、日志正常/降级说明、gates 结果、git status；证据为仓库内可访问文件（PR 可读路径），不留只有本机可见的 /tmp 路径。

## Evidence

实现分支 `fix/runner-logging-lifecycle`（implementer 填写，validator 复核）。
证据目录：`docs/acceptance/assets/runner-logging-lifecycle/`
（harness：`harness/repro_runner_broken_pipe.py` + `harness/sitecustomize.py`；
证据：`evidence/<case>/`）。复跑命令示例：

```bash
backend/.venv/bin/python \
  docs/acceptance/assets/runner-logging-lifecycle/harness/repro_runner_broken_pipe.py \
  --phase pre --condition dead-pipe \
  --evidence-dir docs/acceptance/assets/runner-logging-lifecycle/evidence/c1-prefix-dead-pipe \
  --port 8002 --timeout 300
# --phase post --condition dead-pipe|healthy-stderr 同理（隔离端口 8002、独立 ECONPAPER_LOCAL_STATE_ROOT、自启进程）
```

- **C1 PASS（修复前复现）** — `evidence/c1-prefix-dead-pipe/`：runner 子进程 fd1+fd2 指向同一条读端已关闭的 PIPE（`runner-lsof.txt`：fd1/fd2 同一 `PIPE 0xae7c…` 设备号），真实 `POST /demos/card` → run 终态 **FAILED**，error=`BrokenPipeError: upload_pipeline execution failed`（summary.json `run_api.status/error`）；业务已实际提交：uploads 目录存在 332282 字节的 `<session>.csv`、DB session state `has_uploaded_datasets=true`（summary.json `uploads_listing`/`db.session_state_excerpt`）。实际异常产生位置 traceback 留档（`runner-logging-evidence.log`，sitecustomize 只读包装 `handleError`/std stream 抓栈，不吞不改）：
  `prewrite_supervisor.py:460 execute_upload_supervised → :321 _execute_supervised → multiprocessing/popen_spawn_posix.py:32 → popen_fork.py:16 → multiprocessing/util.py:438 _flush_std_streams → sys.stdout.flush()` 抛 BrokenPipeError 穿透进业务执行，被 `_stable_failure` 误标。日志 emit 失败本身（`logging.handleError called` ×144）被 CPython 3.12 handleError 吸收，真正的杀手是 spawn 起子进程时的无保护 std 流 flush。
- **C2 PASS（修复后两条件均 SUCCEEDED）** — `evidence/c2-postfix-dead-pipe/` 与 `evidence/c2-postfix-healthy-stderr/`（与提交代码一致的最终复跑）：两条件 run 终态均 **SUCCEEDED**、`error=None`、`upload_readiness=READY`、`run_events` 7 条（含 4 条 `run.progress` worker 事件）、attempts 产物（`03_outliers_0.csv`/`clean.do` 等）落盘、run 记录唯一终态唯一（summary.json）。死管道条件下：控制台 handler 降级（`runner-file.log` 首部恰好 1 条 `WARNING runner log channel stderr is unavailable (BrokenPipeError…) ; remaining channels: file(…/runner.log)`），文件日志 242 行持续可用；健康条件下：`runner-console.log` 与 `runner-file.log` 均有 SQL/INFO 记录、降级记录 0 条。
- **C3 PASS（业务失败仍 FAILED 且可诊断）** — `backend/tests/test_runner_logging_lifecycle.py::test_business_failures_still_fail_the_run_with_stable_error`（spawn 子进程内业务执行器真实抛 `BrokenPipeError` → FAILED，error=`BrokenPipeError: upload_pipeline executor failed`，稳定且含异常类型；`RuntimeError` 业务错误同样 FAILED 且不泄敏感文本）；`test_stable_failure_classification_is_unchanged` 钉死 `_stable_failure` 分类。源码核实：`git diff main..HEAD -- backend/` 仅 `runner.py(+5)`、`prewrite_supervisor.py(+7)`、`runner_logging.py(新增)`；services/、facade/、agent/、routers/ 零改动，无任何按类名吞 BrokenPipeError 的新逻辑。
- **C4 PASS（降级四不）** — (a) `test_dead_console_degrades_once_and_file_survives`：死控制台连续 300 条日志，恰 1 条降级留痕、进程存活、文件通道继续收 `record 299`；`test_multiprocessing_spawn_flush_cannot_escape` 直接钉死 spawn flush 逃逸路径已闭合；(b) `test_successful_upload_run_leaves_single_records_and_result`：run 记录唯一、attempt=1、`run.claimed`/`run.succeeded` 各 1 条；C2 两场景 summary.json 同源核实；(c) 同测试断言产物唯一（`cleaned*.csv` 仅 1 个）；(d) `test_configure_is_idempotent_across_reentry_and_reload`：重复调用 + `importlib.reload` 重入后 handler 数量恒定（marker 属性而非 isinstance，重导入下不失效），`test_child_configuration_installs_no_file_handler` 覆盖 child 形态。
- **C5 PASS（正常可用 + 降级留痕 + 全渠道不可用）** — 正常：`test_healthy_channels_log_to_file_and_console` + C2 健康场景证据（控制台与文件均有记录）；降级留痕：C2 死管道 `runner-file.log` 恰 1 条（含失效通道 stderr 与剩余通道 file 路径）；全渠道不可用：`test_all_channels_unavailable_process_and_business_survive`（文件路径不可创建 + 控制台死流：进程存活、业务函数完成、记录丢弃不抛错）。`docs/local-runner.md` 已更新：不再强依赖重定向（仍推荐）、默认位置 `<ECONPAPER_LOCAL_STATE_ROOT>/log/runner.log` 与 `ECONPAPER_RUNNER_LOG_FILE` 覆盖、降级行为、spawn 子进程取舍、"所有输出渠道都不可用时日志可能丢弃，业务不受影响"。
- **C6 PASS（红线）** — `git diff main..HEAD --stat -- backend/` = 上述 3 个文件；研究节点/统计/Claim 门禁/evidence_revision/任务队列零改动；契约文件除 Evidence 节外未改动，Status 保持 open。
- **C7 PASS（全量 gates）** — `make test`（agent+backend+frontend 三套）全绿；backend 单独复跑 `467 passed, 8 skipped, 0 failed`；`frontend npx tsc --noEmit` exit 0、`npm run lint` 0 errors（6 条既有 warning）、`npm run build` 成功；`git grep -n '\.skip\|skipIf' -- frontend/src backend/tests` 与 main `452a895` 基线一致（5 处：test_outline×2、test_postgres_upload_recovery、test_prewrite_supervisor、test_s3），无新增 skip。注意：backend `test_prewrite_supervisor` 的两个取消延迟断言（<1.0s 预算）在与其他 gate 并行抢 CPU 时会翻flaky（本机实测），静默串行运行稳定全绿——复核时请勿并行压测。
- **C8（交付物）** — 证据均为仓库内路径（`docs/acceptance/assets/runner-logging-lifecycle/`），无 /tmp-only 依赖；PR 由 orchestrator 开出，描述请引用本节与上述证据目录。

实施备注（给 validator）：修复形态为 `backend/runner_logging.py`（`raiseExceptions=False` 兜底 + root logger 挂 RotatingFileHandler（默认 `_state_path("ECONPAPER_RUNNER_LOG_FILE","log","runner.log")`，目录创建失败降级为仅控制台不炸启动）+ 自禁用 stderr 控制台 handler + 进程级一次性降级留痕 + `sys.stdout/stderr` 容错包装（关闭 spawn flush 逃逸路径，业务 socket/pipes 不经过该包装））；接入点仅 `runner.main()` 开头与 `prewrite_supervisor._child_main`（ready 握手之后，保 spawn 启动延迟与 main 持平；子进程不挂文件 handler，避免多进程同文件轮转竞争）。复现 harness 是只读留证（sitecustomize 包装 handleError/std 流仅记录后原样重抛），未改动任何业务代码。

## Named relaxations

无。
