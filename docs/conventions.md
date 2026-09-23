# 文档约定

适用于 `docs/` 下所有文档。`make docs-check` 会机械检查其中能查的部分，其余靠提交者和周期巡检。

## 位置

- 项目文档只放 `docs/`。仓库根目录只留 `README.md`（总目录）、`AGENTS.md`（Agent 规则）和 `CLAUDE.md`（指向 AGENTS.md）。
- 组件目录可以有自己的 `README.md`，但只讲“这个目录怎么用”；产品行为、接口、决策一律写进 `docs/`。
- `runtime/` 与 `agent-learning/` 是 Agent 运行状态和学习记录，不算文档，也不做索引。

## 渐进披露

- 每个文件夹有一个 `README.md`：一句话说明文件夹放什么，然后逐个链接其中的文档，每条附一句用途。
- 单个文档不超过 **400 行**。超过就拆：原文件保留为概览（标题、背景段落、目录），每个二级标题成为同名子文件夹里的 `NN-slug.md`；单节仍超长时，再按三级标题拆一层。分节文件顶部写一行“上级”回链。
- 链接用相对路径，指向具体文件。新文档必须挂进所在文件夹的 `README.md`，否则 `docs-check` 会报孤儿文档。

## 现行文档与历史记录

| 类型 | 目录 | 维护方式 |
|---|---|---|
| 现行 | `product/`、`specs/`、`contracts/`、`api/`、`design/`、`dev/`、`deployment/` | 描述当前真实行为。代码变了就在同一改动里更新；过时内容直接删改，不留“旧版”段落。 |
| 决策 | `adr/` | 只追加。推翻旧决策时写新 ADR，并在旧 ADR 顶部标注“已被 ADR-NNNN 取代”。 |
| 记录 | `acceptance/`、`reviews/`、`plans/`、`notes/`、`cleanup/` | 事后不改写结论；只允许修链接、补索引。超长记录不强制拆分，但已计入 `docs/.doc-size-baseline`，不得再变长。 |

## 代码与文档同步

改动命中下表左列时，同一个提交或 PR 里必须改右列文档；确实无需改文档时，在 PR 的 “Known gaps” 写明原因。

| 代码 | 文档 |
|---|---|
| `backend/routers/`、`backend/schemas/`、`backend/main.py` | `api/`（端点说明）+ `make gen-api` 重新生成 `api/openapi.json` |
| `frontend/src/components/`、`frontend/src/App.tsx` | `specs/frontend-interaction-current.md`，涉及产品流程时还有 `product/core-flow-map.md` |
| `agent/nodes/`、`agent/engine/`、`backend/services/` | 对应的 `contracts/` 或 `specs/`；新增或改名领域概念时改 `product/glossary.md` |
| `agent/llm/` | `adr/0008-multi-llm-routing.md` 与 `deployment/` 的配置表 |
| `Makefile`、`docker-compose.yml`、`deploy/`、`.env.docker` | 根目录 `README.md` 命令表、`dev/local-runner.md`、`deployment/` |
| 新的架构取舍 | 新 ADR，并加进 `adr/README.md` |

这张表在 `scripts/check_docs.py` 的 `DOC_MAP` 里有一份可执行副本，两边一起改。

## 检查

```bash
make docs-check                                  # 断链、孤儿文档、超长文档
python3 scripts/check_docs.py --changed main     # 另外列出“改了代码没改文档”的区域
```

规则写得再清楚，也还是会有遗漏，所以要定期巡检：每个里程碑结束时跑一次 `--changed main`，逐条确认或补文档；再按 [文档目录](README.md) 抽读现行文档，核对它和代码行为是否一致。
