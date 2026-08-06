# 试用：Continuous Loop 状态前端

极简静态面板，读仓库内 JSON，展示 best score / 分项条 / history 近 10 条 / PDF / quality reds。

不依赖 React 构建，不影响 quality-loop。

## 打开

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板 && python3 scripts/serve_dashboard.py
```

浏览器打开：

```text
http://127.0.0.1:8765/docs/dashboard/loop_status.html
```

或手动：

```bash
open http://127.0.0.1:8765/docs/dashboard/loop_status.html
```

只起服务、不自动开浏览器：

```bash
python3 scripts/serve_dashboard.py --no-open
```

换端口：

```bash
python3 scripts/serve_dashboard.py --port 8770
```

> 不要用 `file://` 直接双击 HTML：浏览器会拦 `fetch` 本地 JSON。必须从**仓库根**起静态服务。

## 数据源（相对仓库根）

| 文件 | 用途 |
|------|------|
| `state/evolve_archive/best.json` | 历史最高分与分项 |
| `state/evolve_archive/best_pointers.json` | 最佳论文 / PDF 路径 |
| `state/evolve_archive/history.jsonl` | 分数轨迹（面板显示最近 10 条） |
| `Results/json/parent_education_wage_full_pipeline_quality.json` | remaining reds |
| `Results/json/parent_education_wage_continuous_loop_latest.json` | 最近一次 loop 摘要 |
| `docs/loop-status.json` | 产品身份与 CLI |
| `Submissions/parent_education_wage_loop_paper.pdf` | Open PDF |

可选：`.hour-loop/quality_loop_latest.json`（2h 外环实时分；缺了也不影响主面板）。

## 页面文件

- UI：`docs/dashboard/loop_status.html`
- 服务：`scripts/serve_dashboard.py`

页面每 15 秒自动刷新。

## 和主产品的关系

| 路径 | 角色 |
|------|------|
| `PYTHONPATH=. python3 -m Product.cli continuous-loop ...` | 主环（写状态） |
| `python3 scripts/41_quality_loop_2h.py` / quality-loop | 外环迭代（写 archive） |
| 本前端 | **只读** 观察台 |

不会改 loop 逻辑，不会动 `runtime/`。

## 手动验收

1. 起服务后看到总分（best archive）与分项条。
2. History 表有 `history.jsonl` 最近最多 10 行；最佳行可标 ★。
3. **Open PDF** 能打开 `Submissions/parent_education_wage_loop_paper.pdf`。
4. Remaining reds 能列出 quality JSON 中的 section_length / verdict 等。
5. Latest loop 显示 `status`（如 `max_rounds` / `halted_honest` / `completed_green`）。
6. 跑一轮 continuous-loop 或 quality-loop 后，约 15s 内数字更新。
