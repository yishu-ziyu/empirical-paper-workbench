# econpaper Agent Instructions

econpaper 是本仓库唯一的产品。开发验证以真实用户路径为准：上传数据 → 研究设定 → 识别与稳健 → 分章评审 → 导出。产品定义见 `docs/product/core-product-contract.md`，全部文档从 `docs/README.md` 进入。

## Commands

```bash
make test         # API 漂移 + agent / backend / frontend 测试
make docs-check   # 文档断链、孤儿文档、超长文档
make verify       # 冒烟检查；需要前后端服务已运行
```

`make verify` 依赖运行中的服务。服务没起来时要明确报告“未运行”，不能拿它顶替本可执行的静态检查或测试。

## Documentation is part of the change

这是硬规则，不是建议。

1. **代码和文档在同一个改动里一起改。** 改功能、接口、领域概念、命令或部署方式时，同一个提交或 PR 必须更新对应文档。代码区域和文档的对应关系见 `docs/conventions.md` 的“代码与文档同步”表。确实不需要改文档时，在 PR 的 “Known gaps” 写明原因。
2. **文档只放 `docs/`。** 根目录只留 `README.md`、`AGENTS.md`、`CLAUDE.md`。新文档放进合适的子文件夹，并在该文件夹的 `README.md` 加一行链接和用途说明。
3. **渐进披露。** 单个文档不超过 400 行。写超了就拆成“概览 + 目录”，分节放进同名子文件夹（做法见 `docs/conventions.md`）。不要为了过检查去调高 `docs/.doc-size-baseline`。
4. **现行文档写现状。** `product/`、`specs/`、`contracts/`、`api/`、`design/`、`dev/`、`deployment/` 描述的是当前行为：过时内容直接改掉，不留“旧版”段落。`acceptance/`、`reviews/`、`plans/`、`notes/`、`cleanup/` 是历史记录，只追加，不改写结论。ADR 只追加。
5. **交付前检查。** 宣布完成前运行 `make docs-check` 和 `python3 scripts/check_docs.py --changed main`，逐条处理“改了代码没改文档”的提示，并在交付说明里报告结果。
6. **读文档从索引开始。** 先读 `docs/README.md` 和相关文件夹的 `README.md`，再按链接打开需要的分节，不要一次读完整个目录。

文档写得和代码不一致时，先用代码和运行结果确认真实行为，再改文档。拿不准哪边是对的，就问用户，不要自己挑一边。

## 长任务状态与 Skill 演进

沿用当前 checkout；只有用户明确要求时才切换或新建分支。

1. 每个新会话规划前先读 `runtime/STATE.md`。用户意图命中活动任务时，再读对应的 `runtime/tasks/<task-id>.md`；恢复任务靠这些文件，不靠聊天记忆。新的长任务按 `runtime/tasks/TEMPLATE.md` 建独立状态文件并登记，不得覆盖其他会话的任务。
2. 每个里程碑结束、上下文压缩、交接或退出前，更新任务文件和索引里的状态、更新时间和下一步。只记恢复所需的事实、改动、失败路径和证据位置。
3. 完整 run 工件以 `runs/`、`backend/runs/` 及对应 session/run ID 为准。任务状态不复制用户数据集、论文正文或大段日志。
4. 重要任务结束后，按 `agent-learning/raw/TEMPLATE.md` 新建去敏运行记录，并把索引状态改为 `complete`。单次任务可以给 `agent-learning/wiki.md` 补证据，但不能据此直接扩写本文件或创建 Skill。
5. Skill 变更单独立项：至少比较 4 份相关运行记录，成功和失败的都要看；一次只改一个 Skill；跑固定验证案例和 `make test`，涉及运行链路时再跑 `make verify` 和真实用户路径。主指标提高、研究可追溯性、人工审批和恢复门槛都没有退化，才接受；否则回滚并记录拒绝原因。
6. 通过验证的 Skill 才放进 `.agents/skills/<skill-name>/SKILL.md`。更换模型、数据类型、计量方法、工具或交互预算后要重新验证。

状态文件和学习记录不得保存凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理，只记去敏事实、ID 和证据位置。
