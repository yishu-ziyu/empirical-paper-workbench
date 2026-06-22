# Problem: 全自动论文机产品化

> 日期：2026-06-22
> 项目：实证论文项目模板 + StatspAI_跑通一次_CHARLS_DID
> 阶段：Design Phase 0

## User

**主用户**：实证经济学研究者（PhD 候选人、junior faculty、研究机构）。

特征：
- 2-5 篇论文压力，时间紧迫
- 熟悉 Stata/R/Python，但不熟悉全链路自动化
- 需要从 idea + 数据 → 可提交论文的端到端能力
- 愿意为省时间付费（$50-200/篇 或 $20-50/月订阅）

**当前使用方式**：
- 用 `实证论文项目模板` 作为产品开发仓库
- 用 `StatspAI_跑通一次_CHARLS_DID` 作为 proof case 和 runtime 来源
- 用 `论文核心素材库` 作为数据母库

## Task

用户正在构建一个**全自动实证论文生产流水线**，目标：

> 用户输入题目和数据 → 系统自动完成研究设计 → 跑统计 → 生成论文初稿 → 审阅修订 → 交付 PDF/DOCX + 证据包 + 复现说明

具体来说，用户需要：
1. 一个可复用的 Agent 编排 runtime，能把 10 步 workflow 串成可执行 pipeline
2. 一个产品界面（FastAPI + React），让用户能看到进度、签收节点、查看证据
3. 一个证据审计系统，确保每个 claim 都有真实数据/表格/运行支持
4. 跨题目可复用——不是只跑通一个 CHARLS，而是任何题目 + 数据都能套

## Obstacle

### 核心障碍

| 障碍 | 当前状态 | 影响 |
|------|----------|------|
| **两层 runtime 不统一** | CHARLS 有 `runtime/pipeline.py`（简洁可执行），主仓库有 `auto_mode_*` 系列脚本（30+ 个，复杂但已跑通） | 两套 runtime 不能互换，跨题验证时不知道用哪套 |
| **工作台缺失** | CHARLS 有 workbench（被用户评为 1/100 分），主仓库有 React 产品壳 | 没有一个高质量的可视化状态面板 |
| **数据集切换成本高** | 当前 demo 线（父母教育→子女工资）卡在字段缺失，CGSS 线刚启动审阅 | 换题需要手动改配置、检查变量、构造样本 |
| **StatsPAI 集成不深** | 主仓库有 StatsPAI runner，但只接 OLS，DID/IV/RDD 未接入 | 统计方法受限，不能覆盖主流实证方法 |
| **证据链断裂** | P0-P18 建立了完善的证据审计系统，但只在一个 demo 线上验证 | 跨题时证据审计是否还能工作未知 |

### 根本原因

项目已经花了 2 个月建立了**完善的 spec 和部分实现**，但：
1. Layer 2（Agent runtime）有两套不兼容的实现
2. Layer 3（产品界面）有 React 壳但没有高质量工作台
3. 没有完成过**跨题验证**——只在一个 demo 上跑通

## Evidence

已有证据：
- ✅ CHARLS DID 端到端跑通（Layer 1 proof case）
- ✅ 10 步 workflow registry 完整（`workflows/registry.json`）
- ✅ P0-P18 完整任务链在一个 demo 上跑通
- ✅ 1214 项测试通过
- ✅ StatsPAI OLS adapter 可用
- ✅ React + FastAPI 产品壳可用
- ✅ 证据审计系统（claim register, integrity audit, finding card）

缺少证据：
- ❌ 跨题验证——第二个题目跑通 10 步
- ❌ Layer 2 runtime 统一——两套实现需要合并
- ❌ 高质量工作台——CHARLS 版被用户评为 1/100 分
- ❌ DID/IV/RDD 方法接入 StatsPAI
