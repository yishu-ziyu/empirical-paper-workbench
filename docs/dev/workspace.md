# 本地工作区

唯一项目入口是 `/Users/mahaoxuan/Desktop/AI 产品/empirical-paper-workbench/`。
代码、文档、论文材料和验收证据都从这里进入，不使用外部目录或兼容软链接。

```text
empirical-paper-workbench/
├── frontend/、backend/、agent/   产品代码与已有本地环境
├── docs/                       项目文档
├── research/
│   ├── dependencies/StatsPAI/   本地源码依赖；保留其独立 Git 状态
│   ├── materials/              论文、数据与其他研究材料
│   └── .agents/、.claude/       原研究工作区的本地技能配置
└── evidence/                   本机验收证据
```

`research/` 和 `evidence/` 完整保留原内容，但被根 `.gitignore` 和
`.dockerignore` 整体排除。材料、依赖 checkout 和证据不随产品提交或镜像发布。
历史记录中的路径保留当时的原文，不作为当前操作入口。

## 依赖和已有环境

默认依赖根目录是 `research/dependencies/`。来源与固定修订见
[dependencies.md](dependencies.md)。`ECONPAPER_DEPENDENCY_ROOT` 可覆盖默认：
绝对路径直接使用；相对路径仍以产品父目录为基准，与进程当前目录无关。

`backend/.venv`、`agent/.venv` 的 StatsPAI editable 安装都指向
`research/dependencies/StatsPAI/`。该安装直接加载源码；移动依赖时必须同步
两个环境的 `__editable__.statspai-1.22.0.pth` 和
`statspai-1.22.0.dist-info/direct_url.json`，不能只改产品配置。

从项目根目录验证：

```bash
make verify-deps
python3 scripts/check_workspace_layout.py
```

第二条程序按本机 `.local/workspace-merge/manifest.json` 的迁移前清单，
检查材料完整性、独立依赖 Git 状态、现有环境的源码加载与 Card 估计。
它需要本次迁移保留的本机清单，不是克隆仓库后的通用安装步骤。
程序通过不代表网页全流程验收；启动和验证服务见 [local-runner.md](local-runner.md)。
