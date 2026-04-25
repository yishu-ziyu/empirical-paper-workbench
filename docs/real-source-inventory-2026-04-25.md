# Real Source Inventory

## 1. Dataset Motherlode

- Registered path: `/Users/mahaoxuan/Desktop/实证数据库`
- Nature: mixed raw empirical-data pool, not a single-paper clean package
- Quick inventory:
  - total files: 492
  - `.dta`: 172
  - `.pdf`: 128
  - `.sav`: 25
  - `.do`: 21
  - `.xlsx`: 19
- Current judgment:
  - This should be treated as an external `Data/Raw` source pool.
  - We should not copy all of it into the current thesis repo.
  - Once the topic is narrowed, we should promote only a selected subset into the project workspace.

### Visible strong clusters

- `A001CFPS中国家庭追踪调查`
- `A005CLDS中国劳动力动态调查数据`
- `A019-中国流动人口动态监测CMDS数据2011-2018年`
- `外部源数据/IFR工业机器人数据（1993-2023年）`
- `外部源数据/工业机器人安装密度(2006-2023年)`

This is enough to support a serious topic search in labor market, automation, matching efficiency, migration, and panel household data.

## 2. Literature Source A: Zotero

- Registered path: `/Users/mahaoxuan/Zotero`
- Nature: actual Zotero data directory
- Strong evidence:
  - `zotero.sqlite`
  - `zotero-mcp-vectors.sqlite`
  - `storage/` attachment tree
- Quick inventory:
  - total files: 876
  - `.js`: 746
  - `.pdf`: 52
  - `.sqlite`: 2
  - `.bib`: 2

### Judgment

- Zotero should be treated as the canonical bibliographic source.
- Its metadata layer is stronger than the plain PDF folder.
- We should prefer Zotero when we later need:
  - bibliographic identities
  - titles
  - citation export
  - attachment-to-reference linkage

## 3. Literature Source B: PDF Folder

- Registered path: `/Users/mahaoxuan/Desktop/论文核心素材库/1_文献/PDF原文`
- Nature: curated reading pool, mostly full-text files
- Current visible pattern:
  - highly relevant to robots, labor markets, matching, automation, wage effects
  - mixed naming quality: some very clean names, some code-like names such as `w20939.pdf`
  - at least one project hint file is visible:
    - `工业机器人应用对就业市场匹配效率的影响研究【这个是我研究的课....pdf`

### Judgment

- This folder is likely closer to the papers you are actively reading.
- It is not a good canonical bibliography source by itself.
- It is a strong fast-access full-text pool.

## 4. Overlap Judgment

- Exact filename overlap between Zotero PDFs and the PDF folder: `0`
- This does **not** mean there is no semantic overlap.
- It only means the two sources use different naming conventions.

### Practical implication

We should not deduplicate by filename alone.

The safe order is:

1. keep both sources untouched
2. use Zotero as citation truth
3. use the PDF folder as reading pool
4. only if needed later, compute deeper overlap by title / DOI / hash

## 5. Recommended Next Step

Given the current materials, the thesis topic should be discovered by intersecting:

- robot / automation related literature
- labor market matching / matching efficiency literature
- feasible data families inside `实证数据库`

That means the next real step is not “write the title first”, but:

1. shortlist feasible data families
2. shortlist literature clusters
3. identify variables and units of analysis
4. then converge on a final topic

