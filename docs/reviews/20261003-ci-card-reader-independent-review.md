# Issue #62 独立评审：ACCEPT

- 公开要求：[GitHub Issue #62](https://github.com/yishu-ziyu/empirical-paper-workbench/issues/62)。
- 基线：`db5f5b62c16099af59d6cf26e23f9f9925626842`。
- 候选：`6627554486127431cf406b17fcfebabd099fcca9`。
- 评审日期：2026-10-02 UTC。
- 结论：**ACCEPT**，限定为 Issue #62 的测试收集与缺数据隔离。

## 隔离与范围

在候选 SHA 的独立 detached worktree 评审；未读取执行者自评、交接、
`runtime/` 状态或任务文件。只查看公开要求、实现差异、相关索引和依赖文档。
未修改实现。评审专用反例在结束前未提供给执行者。
候选没有修改生产估计行为；新增依赖文档的链接结构与描述符合实际 fixture。

## 真实环境证据

主验证解释器：`econpaper-test-env/bin/python`，Python 3.12；真实安装
StatsPAI 1.34.2、numpy 2.1.0、pandas 2.2.3、statsmodels 0.14.6、pyfixest 0.60.0。

| 场景 | 运行结果 | 判定 |
|---|---|---|
| PyPI 安装、无外部 Card CSV，`--collect-only -q` | 10 tests collected | 无模块级 skip，收集正常 |
| 同环境正常执行 reader 文件 | 9 passed, 1 skipped | 只有 `[ivreg]` 因明确缺 CSV skip；4 个非 Card 回归、4 个因果和空结果用例均执行 |
| 有真实公开 Card CSV，正常执行 reader 文件 | 10 passed | IV 真实拟合与结果对照实际执行 |
| 完整依赖环境，StatsPAI 1.22，无 Card | 9 passed, 1 skipped | 固定生产包版本也通过定向测试 |
| 同完整环境，一起执行 reader 与后端 `test_card_claim_ledger.py` | 20 passed, 1 skipped | 后续后端测试实际执行，未被 reader 缺 Card 阻断 |

有 Card 验证通过 GitHub connector 读取 StatsPAI 公共修订
`a98b6743cc797ddd9cc33de1772c3ea3e3f0c394` 的 `papers/data_card1995.csv`。
文件含 3,010 行、35 个 CSV 列（包括 `rownames`）。在评审临时目录建立
fixture 期望的目录层级，仅在独立 pytest 进程中重定向 StatsPAI 的
`__file__`；调用的是安装包真实 `ivreg`，没有伪造 fit 或参考系数。
StatsPAI 1.34.2 的少量 treated units 警告正常报告，不作为失败或 skip。

## 独立反例

反例使用仓库外 pytest 插件，独立进程执行，不改仓库 fixture。

| 反例 | 观察 |
|---|---|
| 把所有 StatsPAI 拟合入口替换为必抛 RuntimeError，再 `--collect-only` | 仍收集 10 个用例；证明收集没有调用拟合 |
| 模拟包规格不存在 | 1 passed, 9 individually skipped；空结果用例仍执行，无模块级 skip |
| 包规格存在，但 import 抛缺失传递依赖 ModuleNotFoundError | 选定回归与空结果得到 1 passed, 1 error；退出码 1，无 skip |
| Card 存在，IV 拟合入口抛 RuntimeError | IV 与空结果得到 1 passed, 1 error；退出码 1，无 skip |
| Card CSV 存在但引号不闭合 | IV 与空结果得到 1 passed, 1 error；ParserError 原样传播，无 skip |

反例说明：只有预期的包缺失和外部文件缺失转换为 fixture 层 skip；
已安装包的导入错误、CSV 读取错误和拟合错误均不会吞掉。

## 检查与边界

- `git diff --check BASE CANDIDATE`：通过。
- `make docs-check`：通过，只有 4 项既存冻结超长记录警告。
- `python3 scripts/check_docs.py --changed main`：通过，code → doc sync 0 提示。
- 全量 agent/backend 的探索运行使用了不完整 PYTHONPATH，途中出现失败并在
  Jupyter 内核测试处有界中断（退出 130）；不据此判断产品失败或宣称全量通过。
  后续定向验证使用 Makefile 标准的 repo 与 repo/backend PYTHONPATH。
- 此评审未验证远程 GitHub CI 全量绿灯；该证据应由后续真实 CI 提供。
- 本结论仅审候选 SHA。评审记录是后续追加文档，不替代候选身份。
