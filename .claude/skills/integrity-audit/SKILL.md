---
name: integrity-audit
description: 手动审计论文 section 完整性 / 反捏造。Use when user types /integrity-audit or says "审计 / 跑 audit / 全量查 / 改前先查",或写 §5 / §6 草稿前主动调用。
---

# Integrity Audit

`evidence/integrity_audit.py` 的手动触发入口。

**这不是 PostToolUse hook**(那个在 `Product/scripts/post_tool_audit.py`,每次 Edit/Write/MultiEdit 写 `Manuscripts/sections/*.md` 自动跑);这是给"主动全量审计 / 写前 dry-run / 跨 section 对比"用的。

## 6 维度审计(只读 + 可修)

每次 audit 跑 6 个维度:Required Files / Section Completeness / Number Anchoring / Forbidden Patterns / Source-of-Truth Drift / Gap Honesty。完整定义见 `evidence/integrity_audit.py`。

## 3 个使用模式

```bash
# 1) 写完后,自动修复可修项
python3 evidence/integrity_audit.py --section <name> --write

# 2) 投递前,全量扫 9 section(只读)
python3 evidence/integrity_audit.py --all

# 3) 改前 dry-run,只看不写
python3 evidence/integrity_audit.py --section <name>
```

`<name>` ∈ {`abstract`, `introduction`, `literature-and-contribution`, `institutional-background-theory-context`, `data-and-measurement`, `empirical-strategy`, `main-results`, `robustness-mechanisms-heterogeneity`, `conclusion`}。

## 退出码

- `0` = CLEAN / READY,可投递
- `1` = BLOCKED,有捏造或缺失,必修
- `2` = 工具错误,audit 脚本本身炸了(不是 section 问题)

## 和 post_tool_audit hook 的分工

| 场景 | 用谁 |
|---|---|
| Edit/Write/MultiEdit 任意 `Manuscripts/sections/*.md` | hook 自动跑(不需要调 skill) |
| 写完整篇,投递前 | `/integrity-audit` + `--all` 全量扫 |
| 改 §5 草稿前,看现状 | `/integrity-audit` + `--section main-results` |
| 改完非 section 文件想审计 | hook 不覆盖,需 `/integrity-audit` + `--section` 指向具体 section |
