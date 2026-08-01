# Handoff: F8 - T-11 CHARLS 数据向导

## 目标
实现 CHARLS 数据集向导式导入流程，让用户通过前端交互界面完成变量映射、波次选择和过滤条件配置，无需手动处理 CHARLS 原始变量名。

## 背景
- T-04 已完成 CHARLS 数据检测（`_detect_dataset_type` 和 `_load_charls_config`）
- 后端 `charls.py` 已有 `GET /sessions/{id}/charls/detect` 和 `POST /sessions/{id}/charls/confirm` 端点
- 前端 `CharlsWizard.tsx` 组件已存在（测试文件 `CharlsWizard.test.tsx` 也有）
- 前置依赖 T-04 ✅ 已完成
- CHARLS 配置模板：`agent/dataset_profiles/charls.yaml`

## 具体改动

### 1. 前端 CharlsWizard 组件完善

检查并完善 `frontend/src/components/CharlsWizard.tsx`：
- 调用 `GET /sessions/{session_id}/charls/detect` 检测数据集类型
- 检测到 CHARLS 时自动弹出向导弹窗
- 向导三步流程：
  1. **变量映射**：显示 CHARLS 原始变量名 → 可读名称映射（从 charls.yaml 读取）
  2. **波次选择**：选择要包含的波次（wave 1/2/3/4）
  3. **过滤条件**：可选的应用过滤预设（如年龄范围、城乡分类）
- 确认后调用 `POST /sessions/{session_id}/charls/confirm` 提交配置
- 非 CHARLS 数据集时隐藏向导，不打扰用户

### 2. 前端集成

在 App.tsx 中集成 CHARLS 向导：
- 数据上传完成后自动调用 detect 端点
- 检测到 CHARLS 时弹出 wizard modal
- 向导完成后刷新 Outline 面板显示可读变量名
- 提供跳过/关闭向导的选项

### 3. EdaSidebar 集成

在 `EdaSidebar.tsx` 中添加 CHARLS 检测入口：
- 上传 CSV 后自动检测数据集类型
- 检测结果为 CHARLS 时显示 "CHARLS 数据集已识别" 提示
- 提供 "打开 CHARLS 向导" 按钮供用户手动触发

### 4. 测试
- 前端测试：`cd frontend && npm test`（132 passed）
- 前端新增测试：CharlsWizard 弹窗/变量映射/波次选择/确认提交
- 后端测试：`cd agent && source .venv/bin/activate && python -m pytest tests/ -q`（357 passed）
- 后端新增测试：charls detect/confirm 端点集成测试

### 5. 验证
- 启动后端：`cd backend && uvicorn main:app --reload --port 8001`
- 启动前端：`cd frontend && npm run dev`
- 上传 CHARLS 样本 CSV → 自动弹出向导 → 完成配置 → 进入分析流程

## 依赖
- 前置：T-04 ✅（数据清洗 profiling 已完成）
- 不影响其他任务

## 验收标准
- [ ] 上传 CHARLS 数据集后自动弹出向导弹窗
- [ ] 向导三步（变量映射/波次选择/过滤条件）可交互操作
- [ ] 确认后调用 `/charls/confirm` 端点，配置持久化到 session state
- [ ] 非 CHARLS 数据集不弹出向导
- [ ] 向导可手动关闭/跳过
- [ ] 所有现有测试仍然通过