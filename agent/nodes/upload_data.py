from pathlib import Path

import pandas as pd

from ..protocols import UploadDataOutput
from ..state import EconPaperState


def upload_data(state: EconPaperState) -> UploadDataOutput:
    """解析上传的数据集，写入 dataset_meta 到 state.uploaded_datasets。

    契约（T-02 Seam 1）：从 ``state.uploaded_datasets[*].path`` 读取 CSV 路径，
    解析后回写完整 dataset_meta（columns / rows / dtypes / missing_count）。

    若未提供任何数据集（开发 / 测试期），回写一个占位 dataset，保证 graph
    后续节点（clean_data）有载体可写 missing_count。
    """
    datasets = state.get("uploaded_datasets", [])

    if not datasets:
        # 未传数据集：回退占位，保持 graph 流转可用
        session_id = state.get("session_id")
        return {
            "uploaded_datasets": [
                {
                    "session_id": session_id,
                    "name": "placeholder_dataset",
                    "status": "uploaded",
                }
            ]
        }

    result = []
    for ds in datasets:
        path = ds.get("path")
        if not path:
            # 无路径，原样透传
            result.append(ds)
            continue

        p = Path(path)
        df = pd.read_csv(p)

        meta = {
            "name": p.name,
            "path": str(p),
            "format": ds.get("format", "csv"),
            "columns": list(df.columns),
            "rows": len(df),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_count": int(df.isna().sum().sum()),
        }
        result.append(meta)

    return {"uploaded_datasets": result}
