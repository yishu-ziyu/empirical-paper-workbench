# econpaper 本地目录整合

- Task ID: WORKSPACE-DIRECTORY-MERGE-1
- Status: complete
- Git context: main@db5f5b62；原有 5 个本地提交和临时页面保持
- Goal: 唯一管理入口 empirical-paper-workbench；配套工作区进入 research，证据进入 evidence
- Hard bar: 文件内容完整、依赖仍能运行；材料与证据不进入 Git/Docker；不提交、不推送
- Current review / approval gate: 独立 validator ACCEPT，主代理完成客观验收
- Verified facts: 主环境无运行服务；迁移前 make verify-deps、文档检查通过
- Changed files: 默认依赖路径、Card 依赖回退、4 份本机 editable 元数据、Git/Docker 忽略规则、现行路径文档与验收程序
- Data / output evidence locations: .local/workspace-merge/（本机、gitignored）
- Test evidence: docs/acceptance/workspace-directory-merge.md
- Pending external state: 无
- Next action: 已交付唯一入口；材料和证据保留在 research/evidence，不入 Git；未提交、未推送
- Updated at: 2026-10-06
