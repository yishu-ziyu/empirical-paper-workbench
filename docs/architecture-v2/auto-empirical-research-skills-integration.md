# Auto-Empirical Research Skills 接入说明

## 目标

把 `brycewang-stanford/Auto-Empirical-Research-Skills` 接成产品能力源，而不是把外部仓库复制进本项目。

它在本系统中的角色是：

1. 给 Supervisor 提供实证研究 workflow、方法模板、AER-like 检查清单和复现规范。
2. 给 Agent Task Queue 提供可检索的任务拆分依据。
3. 给 Auto Mode 提供 methodology patch proposal 的素材。

## 本地来源

默认读取：

```text
/Users/mahaoxuan/Desktop/经济学论文/Auto-Empirical-Research-Skills
```

也可以用环境变量覆盖：

```text
AERS_SKILLS_PATH=/path/to/Auto-Empirical-Research-Skills
```

系统读取 `catalog/skills.json`，目前会索引 collection 级能力，不逐条展开 1072 个 skill 到主能力列表，避免 UI 和 Supervisor 上下文被噪声淹没。

## 产品边界

AERS 进入系统后分为两类：

| 类型 | 产品状态 | 用途 |
| --- | --- | --- |
| Full empirical pipeline | `template` | 生成研究路线、任务树、执行包骨架 |
| AER / replication / robustness checks | `checklist` | 形成质量门、审稿视角、复现预检 |
| 论文写作 / 文献 / agent 角色 | `advisory` / `role_prompt` | 给写作、审阅和派工提供参考 |

它们不是直接可执行函数。真正执行仍然走本项目已有的执行器，例如 Python、StatsPAI、StataMCP、PDF/DOCX 导出、审计日志和任务队列。

## Canonical 规则边界

Auto Mode 可以：

- 读取 AERS catalog。
- 抽取方法建议。
- 生成 methodology patch proposal。
- 把建议写入 `Program/methodology/proposals/auto-empirical-research-skills/`。

Auto Mode 不可以：

- 静默覆盖 canonical 方法库。
- 静默改变 VariableRoleSet、DesignSpec、RunPlan 的正式层。
- 把外部 skill 文本当成已经人工审阅过的产品规则。

canonical 规则必须人工 review 后合并。

## 许可证

AERS 仓库是 `CC-BY-SA-4.0`。产品侧必须保留：

- 来源 URL
- 许可证
- Attribution / ShareAlike 义务
- 是否改写或抽取为 proposal 的记录

当前 adapter 会把这些信息写入 capability source metadata 和每条外部能力的 `external_source`。

## 当前实现文件

- `Product/backend/auto_empirical_research_skills.py`
- `Product/backend/capability_registry.py`
- `Program/config/capabilities.yml`
- `tests/test_auto_empirical_research_skills_contract.py`

## 当前真实索引结果

在本机执行能力索引后：

- AERS source: available
- collection capabilities: 64
- underlying skill files: 1072
- full empirical pipeline templates: 4
- checklist capabilities: 4

这些结果会写入项目本地：

```text
state/product/capabilities.json
```
