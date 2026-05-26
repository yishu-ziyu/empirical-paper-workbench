# Methodology Library Boundary

This directory is the local home for empirical method standards, journal review skills, and method-specific checklists.

It has two layers:

1. `proposals/`
   - Generated or extracted by Auto Mode.
   - May cite external repositories, papers, or user-provided material.
   - Cannot block formal export.
   - Cannot overwrite product state.
   - Must be reviewed before promotion.

2. `canonical/`
   - Reviewed rules owned by this project.
   - Can be used by Method Design, Reviewer, Verifier, and Export gates.
   - Only reviewed canonical rules may set `blocks_formal_export=true`.

Auto Mode may write proposal files here. Auto Mode must not write canonical rules unless a human explicitly reviews and approves the patch.

## Current external skill sources

- AER-Skills: `https://github.com/brycewang-stanford/AER-skills.git`
- Awesome Journal Skills: `https://github.com/brycewang-stanford/awesome-journal-skills.git`
- Awesome Agent Skills for Empirical Research: `https://github.com/brycewang-stanford/Awesome-Agent-Skills-for-Empirical-Research.git`

## First integration target

The first product-facing standard is:

```text
审稿标准：AER-like 顶刊标准
```

It should first enter Task Brief as an optional standard, then Method Design as missing-evidence hints, and finally Review & Export as journal-aware verifier gates after canonical review.
