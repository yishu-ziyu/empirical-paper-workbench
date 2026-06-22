# 全量产品清理审核

日期：2026-06-19

## 判断

当前项目的问题不是功能少，而是历史证明链路、旧 demo 线、P 阶段命名、静态前端和真实产品入口混在一起。清理标准只有一个：用户进入产品后看到的是论文生产流水线，而不是工程历史、作品集 demo 或内部阶段编号。

## 当前产品入口

- 唯一用户产品壳：`Product/web-react/src/App.tsx`。
- 唯一服务入口：`Product/app.py`。
- 当前主推进线：CGSS 论文生产链的浏览器内审阅报告、用户可读修订清单、headless state 回读。
- `Product/web` 已删除，不再作为源码、回退入口或验收入口。
- `/legacy` 只重定向到 `/`。

## 已清理

- 删除旧静态前端源码：`Product/web/index.html`、`Product/web/assets/app.js`、旧 CSS。
- FastAPI 不再挂载旧 `/assets` 静态目录。
- React 主入口不再挂 `ProductControlP0Panel`。
- 清理本地运行垃圾：`__pycache__`、`.DS_Store`、本地运行日志、空旧入口目录。
- 默认 pytest 收集已忽略直接读取 `Product/web` 的旧静态前端测试、退役 P3/P6 视觉实验测试和旧论文快照测试；这些测试不是当前 CGSS 论文生产链验收面。
- `Product/api/design.py` 暴露 `_TASKS_ROOT` 兼容 wrapper wire-in 测试，避免任务根目录 patch 失效。
- LLM Supervisor / service preflight 的无配置测试已清理完整 provider 环境变量，避免本机真实密钥污染“无配置”场景。
- runtime 插件包验证不再硬编码不存在的本机 `plugin-creator` validator；外部 validator 存在则跑，不存在则记录 skip，包内 validator 和临时项目安装验证仍必须通过。

## 验证结果

- `python3 -m pytest -q -p no:cacheprovider`：1214 passed, 3 skipped, 5 warnings, 51 subtests passed。
- `python3 scripts/25_agent_runtime_preflight.py`：PASS。
- `python3 scripts/33_validate_plugin_package.py`：PASS。
- `python3 -m py_compile Product/app.py Product/api/design.py Product/backend/llm_client.py scripts/25_agent_runtime_preflight.py scripts/33_validate_plugin_package.py tests/conftest.py tests/test_full_product_cleanup_audit.py tests/test_llm_supervisor_provider_status.py tests/test_service_preflight_contract.py`：PASS。
- `npm run build` in `Product/web-react`：PASS；Vite 仍提示主 JS chunk 大于 500 kB。
- `git diff --check`：PASS。

## 暂不删除但降级为历史证据

这些东西不再定义产品，但现在仍有测试或历史证据价值，不能在一次清理里盲删：

- `Product/web-react/src/components/ProductControlP0Panel.tsx`：历史 P 阶段聚合面板。当前主入口不能 import 或 render 它。
- `Product/backend/product_control_p*.py`：父母教育工资长链路的后端证明材料。它们只能作为 capability evidence，不能作为用户产品语言。
- `Tasks/parent-education-wage-*`、`Reviews/parent_education_wage_*`、`docs/product-control/workflow-dashboard.*`：历史推进和验收记录。保留为证据，不作为当前主线。
- `artifacts/ui-checks/*.png`：历史 UI 验收截图。保留为证据，不作为当前运行依赖。

## 必须继续清的硬问题

1. 删除或归档 `ProductControlP0Panel.tsx` 和 `Product/backend/product_control_p*.py`，或迁入明确的 legacy/capability namespace。
2. 把 `Product/app.py` 中大量 `/product-control/pN-*` 路由从当前产品语义中抽离，至少迁入 legacy 或 capability namespace。
3. 把 `Tasks/current-stage.md` 下方旧阶段流水账折叠成历史快照，避免后续代理从旧 P 阶段恢复。
4. 把 `docs/product-control/` 里“作品集 demo / P12-P18 / 父母教育工资”文档明确标为历史能力证据。
5. 给 CGSS 论文生产链补齐浏览器内审阅报告、修订清单、headless 回读三件事，作为新的验收主线。

## 以后不允许

- 不允许新增平行 demo 来绕开当前 CGSS 主线。
- 不允许把 P0-P18 写成用户产品阶段。
- 不允许把 PDF ready 写成论文完成。
- 不允许把 mock、workflow 合同、Agent 日志当研究证据。
- 不允许恢复 `Product/web` 作为产品入口。
