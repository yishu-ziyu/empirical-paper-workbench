# Empirical Research OS v2 Design

Date: 2026-05-28
Status: design-approved-for-planning

## Product Promise

Empirical Research OS is a topic-first empirical research workbench. A user should be able to choose a curated topic or enter a custom topic, connect a model provider, and let Auto Mode advance the project to a Level 3 reviewable paper package: a complete PDF or Word paper, evidence package, literature package, method gate report, reviewer report, revision queue, and manifest.

The system does not mark the result as final automatically. Auto Mode completes the paper package and marks it `needs_human_final_review`; human review decides whether to finalize or send the project back into revision.

## Agreed Product Decisions

- The entry point is `Topic Market + Custom Topic`, not a blank chat box.
- The topic market is small and strong. The first version should contain about 10 to 20 high-quality templates rather than many weak titles.
- A market topic is not just a title. It is a research opportunity with X/Y variables, data sources, method scenarios, literature precedents, risk flags, and a quality target.
- Default mode is Auto Mode. Human-in-the-loop mode remains available, and finalization always requires human review.
- Default quality target is Level 3. Level 2 is supported as a lower course/thesis draft target, and Level 4 is provided as an AER-like or top-journal method gate.
- The first data source is the local dataset motherlode at `/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库`.
- Literature discovery may use networked academic metadata and fulltext discovery sources. Results first enter candidate or project-level caches and are promoted only through citation verification and review states.
- If a literature item is used in the paper, it must enter the project bibliography with metadata, source status, citation purpose, and review state.

## Component Map

### A. Entry And Research Opportunity Assets

1. `Topic Market Layer`
   Curates reviewable research opportunity cards. Each card binds topic, data source, X/Y variables, method path, literature seeds, risk flags, and target quality.

2. `Custom Topic Intake Layer`
   Converts a user-entered topic into a structured research intake: research question, data hints, target quality, output format, and execution mode.

3. `X/Y Research Opportunity Graph`
   Stores known X/Y combinations by dataset, method, literature precedent, and prior empirical usage. This graph is the substrate for the topic market.

4. `Policy Scenario Library`
   Stores DID, RDD, SCM, DDD, cohort DID, Bartik IV, DML, and related policy or identification scenarios as structured templates.

### B. Data And Literature Sources

5. `Data Source Registry`
   Registers local, Git-backed, public, and user-provided data sources. The default local source is the dataset motherlode and is treated as read-only and local-only.

6. `Dataset Motherlode Index`
   Builds a searchable manifest for CGSS, CFPS, CLDS, CMDS, CHARLS, IFR, industrial robot density, listed-company robot penetration, wage policy, provincial, city, and other empirical datasets.

7. `Economics Data Connector`
   Connects macro and meso data sources such as OpenEcon-style services, FRED, World Bank, IMF, OECD, UN Comtrade, and similar public indicators.

8. `Literature Discovery Layer`
   Finds candidate literature from local Zotero, local PDF folders, OpenAlex, Crossref, Semantic Scholar, Unpaywall-style discovery, Chinese literature search queues, and user-provided sources.

9. `Fulltext Acquisition Layer`
   Maximizes available fulltext acquisition from local PDF, Zotero, open fulltext, repository pages, author pages, and user import. It records source URL, access date, file hash, and source status.

10. `Project Bibliography Layer`
    Stores references actually used by a project. Entries track metadata, source status, citation purpose, evidence spans, format status, and review status.

### C. Agent Runtime And Execution

11. `Agent Runtime Core`
    The product's own empirical research agent runtime. It learns from coding-agent orchestration patterns, but the domain logic is empirical research: agent loop, context packer, tool calling, session state, budget, retry, and stop conditions.

12. `Agent Team Layer`
    Defines SupervisorAgent, DataAgent, LiteratureAgent, MethodAgent, ExecutionAgent, ReviewerAgent, ManuscriptAgent, and ExportAgent. Each agent has explicit inputs, outputs, permissions, and acceptance states.

13. `Tool And Capability Registry`
    Registers tools for reading data, reading literature, querying APIs, running Stata/Python/R, generating tables and figures, writing sections, exporting PDF or Word, and packaging artifacts.

14. `Statistical Engine Adapter`
    Adapts Stata, Python, and R execution. A Stata MCP-style bridge belongs here. It must run code, collect logs, read figures, parse regression outputs, and return errors to the agent loop.

15. `Execution Sandbox Layer`
    The CLI-first execution layer. It owns run plans, local execution, logs, error recovery, result files, tables, and figures.

16. `Result Interpreter Layer`
    Reads model outputs, coefficients, significance, robustness failures, runtime errors, and figure diagnostics, then proposes the next model, data, or revision task.

### D. Method, Evidence, And Governance

17. `Method Knowledge Base`
    Converts top-journal method databases, econometric method guides, and policy scenario collections into machine-readable method rules, examples, diagnostics, and evidence requirements.

18. `Method Gate Layer`
    Checks variable definition, identification fit, OLS, ordered models, IV, DID, RDD, PSM, DML, mechanism tests, heterogeneity, reverse causality, omitted-variable risk, and robustness requirements.

19. `Evidence And Provenance Layer`
    Binds every number, table, figure, variable definition, citation, and conclusion to data versions, file hashes, commands, logs, source spans, or review records.

20. `Permission And Human Gate Layer`
    Allows Auto Mode to generate drafts, evidence packages, PDF/Word previews, and promotion proposals. Formal state and finalization move through human review.

### E. Paper Quality, Review, And Delivery

21. `Manuscript Quality Layer`
    Enforces Level 3 paper quality: complete structure, adequate length, variable table, result tables, figures where needed, literature review, method explanation, mechanism or robustness plan/results, conclusion, reference list, and review checklist.

22. `Review And Revision Loop`
    Produces reviewer reports, revision queues, missing-evidence tasks, literature补强 tasks, model rerun tasks, and revised manuscript drafts.

23. `Paper Package Layer`
    Produces `paper.md`, PDF or Word output, result evidence package, literature review packet, method gate report, reviewer report, revision task queue, reproducibility readme, and manifest.

## Agent Responsibility Chain

For a topic such as `工业机器人对劳动力市场匹配效率的影响`, the expected chain is:

```text
SupervisorAgent
-> Topic Market / X-Y Opportunity Graph
-> DataAgent / Dataset Motherlode Index
-> LiteratureAgent / Literature Discovery
-> MethodAgent / Method Knowledge Base and Method Gate
-> ExecutionAgent / Statistical Engine Adapter and Execution Sandbox
-> Result Interpreter
-> ManuscriptAgent / Manuscript Quality Layer
-> ReviewerAgent / Review and Revision Loop
-> ExportAgent / Paper Package Layer
```

DataAgent should first search the local dataset motherlode and identify likely sources such as IFR industrial robot data, industrial robot density, listed-company robot penetration, CFPS, CLDS, CMDS, city or provincial data, and labor-market segmentation data. If a dataset is not available locally, DataAgent should produce a data requirement and acquisition task rather than inventing evidence.

LiteratureAgent should expand the topic into Chinese and English query sets, discover candidate literature, deduplicate results, verify metadata, locate usable fulltext where available, classify citation purpose, and create project-level citation records. CitationVerifier promotes used sources into Project Bibliography review states.

## Literature State Model

Literature items move through these states:

```text
candidate
metadata_verified
fulltext_located
source_span_extracted
citation_use_proposed
needs_human_review
approved_for_project_bibliography
```

Metadata-only or abstract-only items may support search, comparison, and candidate literature review. If the paper uses a source for a substantive claim, the item must enter Project Bibliography and carry its review state. When source text still needs review, the paper package and reviewer report should mark the item as `needs_fulltext_review` or `needs_human_bibliography_review`.

## Data Source Model

The default source is:

```text
id: primary_local_dataset_motherlode
path: /Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库
status: read_only
scope: local_only
source_type: user_provided_public_dataset_pool
```

The system should generate a dataset manifest containing dataset family, year, file format, file size, hash, candidate unit of analysis, available dictionaries, and field profile status. Project-level DatasetBinding records which source file is used for a specific topic and does not mutate the motherlode.

## Quality Target

Level 3 Auto Mode must produce a complete reviewable paper, not section fragments. The minimum output is:

- Complete PDF or Word document.
- Structured paper source in Markdown.
- Result evidence package.
- Literature review packet and project bibliography state.
- Method gate report.
- Reviewer report.
- Revision task queue.
- Manifest distinguishing executed evidence, draft text, candidate references, and human-review requirements.

The package status is `needs_human_final_review`.

## First Implementation Slices

1. `Dataset Motherlode Index`
   Build a read-only manifest generator for the local empirical dataset motherlode.

2. `Literature Discovery And Bibliography States`
   Build the first LiteratureAgent packet: query planning, source registry, global/project cache schema, and Project Bibliography promotion states.

3. `Level 3 Manuscript Quality Gate`
   Reverse-engineer the accepted paper-quality target into measurable gates for length, sections, tables, methods, references, and review checklist.

4. `Method Knowledge Base Seed`
   Define schema for top-journal method cases, policy scenarios, diagnostics, and method gate requirements.

5. `Statistical Engine Adapter Contract`
   Define the tool contract for Stata/Python/R execution, logs, tables, figures, and result interpretation.

## BDD Seed Behaviors

1. Given a user enters `工业机器人对劳动力市场匹配效率的影响`, When Auto Mode starts, Then DataAgent returns candidate local datasets, matched variables or field profile tasks, and data gaps.

2. Given a topic requires macro or meso indicators, When a connector can satisfy the request, Then the system records query, source, timestamp, indicator definition, and cached data path.

3. Given LiteratureAgent finds candidate sources, When a source is used in manuscript text, Then CitationVerifier creates or updates a Project Bibliography entry with metadata, fulltext state, citation purpose, evidence span state, and review state.

4. Given MethodAgent proposes DID, IV, RDD, SCM, or DML, When Method Gate runs, Then the system checks the matching method knowledge base and returns pass items, gap items, and required follow-up tasks.

5. Given ExecutionAgent runs a model through Stata/Python/R, When execution completes or fails, Then logs, commands, tables, figures, errors, and parsed result summaries are written to the evidence package.

6. Given Auto Mode finishes a Level 3 workflow, When ExportAgent packages the project, Then the system outputs PDF or Word, paper source, evidence package, method gate, reviewer report, revision queue, bibliography state, reproducibility readme, and manifest.

7. Given a package is produced by Auto Mode, When the user views status, Then the system marks it `needs_human_final_review` and shows what must be reviewed before finalization.

## Open Planning Questions

- Which source should seed the first X/Y Research Opportunity Graph: local topic notes, public replication examples, or manually curated economics method databases?
- Should the first statistical adapter target Python first, Stata first, or a contract-only adapter with Python as the reference implementation?
- Should LiteratureAgent's first UI surface be a bibliography review table, a literature map, or an agent activity packet?
