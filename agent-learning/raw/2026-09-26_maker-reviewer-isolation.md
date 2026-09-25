# econpaper Codex Run Record

- Date: 2026-09-26
- Task ID / state file: RETRO-REVIEW-9E830281（`runtime/tasks/20260925-retro-review-9e830281.md`）、REFRESH-LOCK-AND-P3-1（`runtime/tasks/20260925-refresh-lock-and-p3.md`）
- Commit / Git context: 补审 `e1c06a88..9e830281`；修复候选 `66712a63`，本地合并到 main，未 push
- Model and tool environment: Claude Code 协调者；执行者和评审都是独立子 agent；mock 模型；网络只允许回环地址
- Dataset class / research method（不含原始数据）: 合成 CSV，OLS
- Task: 按执行与评审隔离规则补审第 3 轮，并修复补审发现的问题
- Result: pass
- Session / run ID: 见证据目录
- Verification commands: `make test`、`make verify`、`make docs-check`、`git diff --check`、SSE 断开负载脚本、真实浏览器估计运行中刷新
- Output evidence locations: `../empirical-paper-workbench-evidence/retro-review-9e830281/`、`../empirical-paper-workbench-evidence/review-66712a63/`

## 成功动作

- 评审读不到执行者的收尾报告和自评，并被要求自己设计新反例。补审就是这样找出了旧流程一直漏掉的 P1。
- 给评审的规则是“先在基线上复现出问题，再判候选”。原脚本在新基线上复现不出来时，评审加重负载，而不是直接判闭合。

## 失败动作与根因

- 执行者用 `pkill -f` 宽匹配清端口，误杀了无关项目的 dev server。根因：prompt 里没有写进程安全规则。
- 执行者没能复现 P1，只写了一个机制层面的测试。当时这一点只能由评审用真实负载来补。

## 可复现条件

SQLite；运行中的 run 预先有约 3000 条事件；每轮开 4 条 SSE 流并随机断开，同时发 12 个读请求和写入。基线在约 70–150 轮内出现 500。

## 候选模式

- 派 agent 时写死：只能停止自己记录了 PID 的进程；端口冲突就换端口。
- 评审 prompt 里写明禁止读取的路径（执行者的任务文件、证据目录），再加上“基线先复现”的要求。
