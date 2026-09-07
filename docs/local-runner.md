# 本地运行前置条件与安全启动（runner / dev 全家桶）

本文记录本地开发时 runner（durable run worker）的启动前置条件与安全启动方式。
背景是首次使用者实弹审计（2026-09-06，J–Q，见
`docs/acceptance/card-canonical-research-experience-validator.md` 追加节）中的
BrokenPipe 事故：**runner 绑定在一个已经退出的 shell 的 PIPE 上时，执行期日志
写 stdout/stderr 会抛 `BrokenPipeError`，worker 把执行异常一律落为 run FAILED，
于是健康的 run 被误标失败。**

## 事故机理（为什么必须重定向）

- `make dev` / `make dev-runner` 启动的 `python -m runner` 会把执行期日志写
  stdout/stderr。
- 如果启动它的终端会话退出（关闭终端、SSH 断开、IDE 内嵌终端回收），而
  runner 进程本身被守护/残留，stdout 管道的读端消失 → 每次写日志都是
  `BrokenPipeError`。
- runner 的异常边界（`runner.process_one_run`）会把执行期异常标记为 run
  FAILED。日志管道死亡 ≠ 研究失败，但当前实现无法区分这两者（已知问题，
  独立后续处理，不在研究循环内吞掉异常）。

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

保持该终端开启；不要在会退出的 shell（一次性容器 exec、CI step、
`command &` 后父 shell 立即退出的场景）里启动。

### 方式二：nohup + 日志重定向（推荐给长会话实验）

```bash
cd econpaper
mkdir -p /tmp/econpaper-runner
nohup make dev-runner > /tmp/econpaper-runner/runner.log 2>&1 &
```

- stdout/stderr 全部进 `runner.log`，即使父 shell 退出也不会断管。
- 观察日志：`tail -f /tmp/econpaper-runner/runner.log`。
- 停止：`pkill -f "python -m runner"`。

### 方式三：直接跑 runner（调试时）

```bash
cd backend && . .venv/bin/activate
DEBUG=true PYTHONPATH="$(cd ..):." nohup python -m runner \
  > /tmp/econpaper-runner/runner.log 2>&1 &
```

（与 Makefile `dev-runner` 同参：`PYTHONPATH=仓库根:仓库根/backend`。）

## 判定记录（契约 C24）

- 仓库自有代码中的 `BrokenPipeError` 只出现在
  `backend/prewrite_supervisor.py`（upload/prewrite 子进程的 liveness /
  cancellation 控制管道收尾），与本研究循环（spec_run / research 节点）
  无关，也不吞执行期异常；`agent/` 下无任何命中。
- J–Q 审计的 stdout 断管复现依赖「runner 绑定已退出 shell 的 PIPE」这一
  环境前提；修 runner 的 logging lifecycle 属独立后续，不在研究循环内
  吞 BrokenPipe。
- 安全结论：按上文方式二启动即可规避；runner 自身的 FAILED 误标修复
  留给独立的 runner PR。
