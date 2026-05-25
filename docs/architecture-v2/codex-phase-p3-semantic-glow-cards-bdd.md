# P3-C Semantic Glow Cards BDD

Status: revised and implemented
Date: 2026-05-25
Scope: `Product/web-react` post-submit analysis workspace only.

## Behavior 1: first screen stays intake-only

Given the user opens the React research entry
When no task has been submitted
Then the first screen shows only the heading and research command input, without semantic cards, stage navigation, agent queue, or audit drawer.

Business rule: the first viewport should behave like a calm starting surface, not a dashboard.

## Behavior 2: submit topic enters analysis workspace

Given the user submits a research topic, pasted content, or local files
When the task is accepted
Then the UI switches to an analysis workspace with the task context, stage navigation, and semantic cards.

Business rule: analysis belongs after user intent is established, so the system does not overload the entry state.

## Behavior 3: cards use grayscale spotlight treatment

Given the user supplied a GlowCard reference
When the React workbench renders semantic cards
Then the card treatment uses pointer-following glow, border light, and low-contrast black/white/gray surfaces, without colored status families.

Business rule: the product should feel technical and alive while staying inside the current black/white/gray design direction.

## Behavior 4: semantic cards stay draft-only

Given the semantic cards are generated from typed text, pasted content, or attached file counts
When the cards display possible research meaning
Then they do not claim formal variable roles, method approval, execution results, findings, or manuscript writeback.

Business rule: semantic analysis can guide the next step, but it must not silently become formal research state.

## Behavior 5: empty state stays quiet

Given the user has not typed or attached anything
When the React entry first loads
Then the semantic analysis rail does not add a large explanatory block; it only appears once there is enough draft material.

Business rule: the first viewport remains calm and does not overload short-term memory before the user starts.
