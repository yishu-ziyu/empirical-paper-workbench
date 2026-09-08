# 本地运行前置条件与安全启动（runner / dev 全家桶）

本文记录本地开发时 runner（durable run worker）的启动前置条件与安全启动方式。

背景是首次使用者实弹审计（2026-09-06，J–Q，见
`docs/acceptance/card-canonical-research-experience-validator.md` 追加节）中的
BrokenPipe 事故：**runner 绑定在一个已经退出的 shell 的 PIPE 上时，执行期日志
写 stdout/stderr 会抛 `BrokenPipeError`，worker 把执行异常一律落为 run FAILED，
于是健康的 run 被误标失败。**

> **该事故已修复**（issue #30，验收契约
> `docs/acceptance/runner-logging-lifecycle.md`）：runner 进程族（主进程与
> supervisor spawn 子进程）现在自带 logging lifecycle，日志输出通道故障不会再
> 把本来成功的研究 run 标为 FAILED。下文保留事故机理作为背景与排查参考。

## 事故机理（历史背景）

- `make dev` / `make dev-runner` 启动的 `python -m runner` 会把执行期日志写
  stdout/stderr。
- 如果启动它的终端会话退出（关闭终端、SSH 断开、IDE 内嵌终端回收），而
  runner 进程本身被守护/残留，stdout 管道的读端消失 → 每次写日志都是
  `BrokenPipeError`。
- 修复前的两条引爆路径：
  1. SQLAlchemy `echo` 等 logging 输出写死管道，`emit` 失败；
  2. multiprocessing spawn 在 `process.start()` 里无条件 flush
     `sys.stdout`（`multiprocessing.util._flush_std_streams`），`BrokenPipeError`
     直接穿透进业务执行，被 `runner._stable_failure` 误标为
     `BrokenPipeError: upload_pipeline execution failed` —— 而此时业务 COMMIT
     往往已经发生。

## 修复后的行为（issue #30）

runner 进程族现在通过 `backend/runner_logging.py` 管理输出通道：

- **不再强依赖 stdout/stderr 重定向**：死管道、已退出的终端、`| true` 之类的
  启动方式都不会再把健康的 run 误标 FAILED。
- **文件日志是持久通道**：默认写
  `<ECONPAPER_LOCAL_STATE_ROOT>/log/runner.log`
  （5MB 轮转，保留 3 份备份）。可用环境变量 `ECONPAPER_RUNNER_LOG_FILE`
  整体覆盖该路径。
- **控制台（stderr）是尽力而为通道**：通道死亡时该 handler 一次性自禁用，
  并在文件日志里留痕一条降级原因（含失效通道与剩余通道）。不会出现
  `--- Logging error ---` 风暴。
- **spawn 子进程**（upload/prewrite 的 supervised 执行）：spawn 不继承父进程
  logging 配置，子进程会重新应用进程级兜底（`raiseExceptions=False` + 标准流
  容错），但**不挂文件 handler**——多个子进程并发轮转同一文件会在
  `RotatingFileHandler` 内竞争；子进程的持久痕迹由 run event store
  （`run_events` 表）承担。
- **诚实声明**：如果所有输出通道都不可用（文件不可写且控制台死管道），日志
  记录会被静默丢弃——业务不受影响，但那部分日志就没有了。这是设计取舍：
  可观测性失败不允许演变成业务失败。

文件重定向仍然**推荐**（便于排查 runner 自身问题），只是不再是正确性前提。

## 前置条件

1. Python 3.12 venv 已装好：`make install-backend install-agent`（runner 与
   backend 共用 `backend/.venv`）。
2. `ECONPAPER_LLM=mock`（本地默认）或真实 provider 配置就绪。
3. backend（8000）与 frontend（5173）至少 backend 在跑：`make dev-backend`
   或整套 `make dev`。

## 推荐启动方式

### 方式一：常驻终端里跑整套 dev（最简单）

```bash
cd econpaper
make dev
```

### 方式二：nohup + 日志重定向（推荐给长会话实验）

```bash
cd econpaper
mkdir -p /tmp/econpaper-runner
nohup make dev-runner > /tmp/econpaper-runner/runner.log 2>&1 &
```

- stdout/stderr 全部进 `runner.log`，即使父 shell 退出也不会断管。
- 观察日志：`tail -f /tmp/econpaper-runner/runner.log`。
- 持久文件日志另见 `<ECONPAPER_LOCAL_STATE_ROOT>/log/runner.log`。
- 停止：`pkill -f "python -m runner"`。

### 方式三：直接跑 runner（调试时）

```bash
cd backend && . .venv/bin/activate
DEBUG=true PYTHONPATH="$(cd ..):." nohup python -m runner \
  > /tmp/econpaper-runner/runner.log 2>&1 &
```

（与 Makefile `dev-runner` 同参：`PYTHONPATH=仓库根:仓库根/backend`。）

## 判定记录（契约 C24，2026-09-08 增补 issue #30 结论）

- 仓库自有代码中的 `BrokenPipeError` 只出现在
  `backend/prewrite_supervisor.py`（upload/prewrite 子进程的 liveness /
  cancellation 控制管道收尾），与本研究循环（spec_run / research 节点）
  无关，也不吞执行期异常；`agent/` 下无任何命中。
- J–Q 审计的 stdout 断管复现依赖「runner 绑定已退出 shell 的 PIPE」这一
  环境前提。修复后的进程级对照（FAILED → SUCCEEDED）见
  `docs/acceptance/assets/runner-logging-lifecycle/`
  （harness 与前后证据，契约 `docs/acceptance/runner-logging-lifecycle.md`
  C1/C2）。业务路径自身的 `BrokenPipeError`（如 LLM/子进程 socket 断管）
  仍按原语义落为 FAILED，不被日志修复吞掉。
- 安全结论：按上文方式二启动仍是最优实践；断管不再影响 run 的正确性。
