# Context

Shared product language for **empirical-paper-workbench**.  
Glossary only. Product narrative SSOT: `docs/PRODUCT.md`.

## Terms

### empirical-paper-workbench

Local-first **full-auto** empirical paper workbench.  
Repo: this directory / https://github.com/yishu-ziyu/empirical-paper-workbench.git  
Not the whole `/Users/mahaoxuan/Desktop/经济学论文` tree. Not upstream StatsPAI/AERS.

### Continuous Empirical Loop

Core product loop:

```text
propose (design) → run (data + estimate) → evaluate (gate/claim/repro) → learn (revise/rerun) → package
```

Inspired by continuous experimental automation (e.g. Discovery Loop spirit), applied to empirical papers.

### paper package

User-facing outcome: openable draft (md/docx/pdf) + Results tables/figures + claim↔evidence + replication script/report.

### harness

Production agent stack: context + tools + constraints + verification + correction.  
`Agent = Model + Harness`, not bare chat.

### internal brake

Integrity audit, quality gate, citation honesty, REPRO, tool whitelist, path sandbox.  
Brakes live **inside** the loop; they are not the product slogan or a human signoff station per phase.

### course paper green

Draft is usable as a course/undergrad empirical paper baseline: structure, real estimates, honest limits, claims bound to evidence, repro path.  
PDF-on-disk alone is not green.

### proof case

A real paper project used as quality reference (e.g. CHARLS DID). Not the product identity.

### pilot case

A concrete topic used to verify the loop (e.g. parent education wage, CGSS).

### headless state

UI-independent run/package state for any surface (CLI, API, future UI). Optional; CLI full-pipeline is first-class.

## Retired language (do not revive)

- product-control P0–P18 as product phases  
- 「半成品 + 红标」as brand promise  
- draft-first-as-excuse for stopping at half work  
- human signoff every gate as default UX  
