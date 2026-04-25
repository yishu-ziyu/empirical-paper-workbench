# Multi-Agent Adoption Status

## Current Answer

We have **not** fully matched CoPaper-level multi-agent sophistication yet, but we have now crossed the line from:

- “methodology inspired by Awesome-Agent-Skills-for-Empirical-Research”

to:

- “actual Supervisor + 4-agent orchestration with handoff packets and an independent review loop implemented in code”

## Implemented Now

### Supervisor

- Entry point: `POST /api/projects/{slug}/orchestrate`
- Coordinates a full orchestration run
- Writes a run manifest under `state/orchestration/<run_id>/`

### Four Primary Agents

1. `preparation`
2. `modeling`
3. `visualization`
4. `writing`

### Review Loop

- Independent `reviewer` packet
- Revision requests written as structured artifacts
- Revised markdown draft generated after review

### Handoff Schema

- `Product/backend/orchestration_schema.py`
- `HandoffPacket`
- `ReviewPacket`
- `OrchestrationManifest`

### Verifiable Artifacts

Each orchestration run writes:

- `handoffs/01_preparation.json`
- `handoffs/02_modeling.json`
- `handoffs/03_visualization.json`
- `handoffs/04_writing.json`
- `reviews/01_reviewer.json`
- `outputs/paper_draft_revised.md`
- `run_manifest.json`

## Still Missing Compared with CoPaper-Level Completion

- Dynamic `target_agent` routing by real skill registry
- LLM-backed specialized agent prompts per role
- Iterative multi-round review loops beyond a single reviewer pass
- Persistent cross-project orchestration analytics
- Native literature and citation agent integration in the orchestration chain
- Production-grade UI for inspecting every handoff packet

## Current Practical Meaning

This system can now demonstrate the architectural principle you cared about:

- the writer is no longer the reviewer
- agent responsibilities are separated
- every handoff is inspectable
- the review loop is explicit rather than implied

