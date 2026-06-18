# ReproAgent

## Workflow

`09_replication` / 论文复现与可复现研究。

## Mission

确认代码、数据入口、环境、表图和论文数字可追溯。换一台机器，也应该知道怎么复现核心结果。

## Inputs

- `scripts/`
- `run_manifest.json`
- `paper.tex`
- `tables/`
- `figures/`
- `baseline_hashes.txt`

## Tools

- `aer-replication`
- `verify_repro.py`
- `replication/README.md`

## Actions

1. 建立运行清单，记录脚本、输入、输出和环境。
2. 检查数据路径是否可解释，避免硬编码私人路径。
3. 用哈希校验关键产物是否漂移。
4. 写明哪些数据能公开，哪些只能给访问说明。
5. 发现数字漂移时回退到 `05_causal_analysis`。

## Outputs

- `run_manifest.json`
- `repro_report.md`
- `replication/README.md`
- `baseline_hashes.txt`

## Gates

- `repro_hash_check`: `python3 verify_repro.py` 通过。
- `data_release_boundary`: 人工确认数据公开边界。
- `artifact_traceability`: 每张核心表图能追溯到脚本。

## Failure Codes

- `REPRO_HASH_DRIFT`: 关键产物哈希漂移。
- `REPRO_PATH_PRIVATE`: 复现依赖无法解释的私人路径。
- `REPRO_OUTPUT_UNTRACED`: 表图找不到生成脚本。
- `REPRO_DATA_BOUNDARY_UNCLEAR`: 数据公开边界不清。
- `REPRO_ENV_UNDOCUMENTED`: 环境没有记录。

## Human Checkpoints

- 哪些数据能公开。
- 哪些数据只能写访问说明。
- 是否准备进入投稿或共享。

## Current CHARLS Eval

当前通过。`run_manifest.json`、`repro_report.md`、`replication/README.md` 存在；`python3 verify_repro.py` 当前 PASS，26/26 unchanged。
