"""本科论文任务 eval 基线任务库。

每个子目录是一个任务：
- task.json   任务规格（研究问题 / 方法 / 变量 / 数据文件）
- rubric.json 机读评分量规（{id, description, check[, params]} 列表）
- dataset.csv 合成数据（由同目录 gen_dataset.py 固定 seed 生成）

由 agent/eval/run_task.py 加载执行：
    backend/.venv/bin/python agent/eval/run_task.py undergrad_did_01
"""
