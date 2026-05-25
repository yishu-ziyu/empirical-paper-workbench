# P3-D Task Brief Demo BDD

Status: draft demo implemented
Date: 2026-05-25

## Behavior 1: topic submission opens a task brief stage page

Given the user starts from the clean React intake page
When the user submits a research topic
Then the app opens an analysis workspace whose first page is the task brief
And the task brief main screen shows only the research question, boundaries, data clues, method direction, and next action.

Business rule: after the first input, the user should land in one focused decision page, not a full dashboard.

## Behavior 2: task brief details live in a right inspector

Given the task brief page is visible
When the user needs more detail
Then evidence requirements, risks, draft/final boundaries, and dispatch notes are shown in a right inspector
And those details are not expanded into the main workspace by default.

Business rule: high-noise audit details must be available without overwhelming the primary decision surface.

## Behavior 3: semantic cards are no longer the default first analysis page

Given the app already has semantic analysis cards
When the user submits a topic
Then those cards may remain as secondary demo material
But the first visible analysis module is the task brief page.

Business rule: cards are useful later, but the first analysis stop must clarify the research task.

## Behavior 4: the demo is explicitly low-fidelity and draft-only

Given this is a design discussion demo
When the user reviews the page
Then the UI must label outputs as draft/demo state through structure and copy
And it must not create or overwrite formal ResearchQuestion, VariableRoleSet, DesignSpec, RunPlan, Finding, or Manuscript state.

Business rule: the demo supports UI decisions; it is not yet a formal product writeback.

