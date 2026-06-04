"""/api/variables endpoint.

L3-variables lane: 数据变量识别 (Variables) tab 后端入口。

约定：
- POST /api/variables 接受 VariablesRequest（topic_slug, brief_path, dataset_name, custom_dataset_path）
- 调用 Product.backend.wrapper.variables_service.run_variables
- 落盘 Tasks/{topic_slug}/variables.yaml
- verdict_passed 表示变量数 >= 3 且 role 都合法
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from Product.api._paths import DATA_ROOT, TASKS_ROOT
from Product.backend.wrapper.variables_service import run_variables
from Product.types.research import VariablesRequest, VariablesResponse

router = APIRouter()


@router.post("/api/variables", response_model=VariablesResponse)
def post_variables(req: VariablesRequest) -> VariablesResponse:
    """调 wrapper service 完成端到端变量识别。"""
    try:
        return run_variables(
            req,
            data_root=DATA_ROOT,
            tasks_root=TASKS_ROOT,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"variables failed: {exc}") from exc
