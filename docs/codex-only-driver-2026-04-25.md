# Codex-Only Driver

## Decision

This product lane is designed to be driven by **Codex itself**.

That means:

- no extra model gateway is required for the product concept
- no separate external LLM backend is treated as necessary architecture
- the multi-agent system is framed as a Codex-driven orchestration layer

## Why

The core goal is not “model switching”, but:

- stronger research workflow orchestration
- clearer role separation
- inspectable handoffs
- a real review loop
- publication-oriented outputs

Those are system-design problems before they are model-vendor problems.

## Practical Implication

The current product shell should assume:

- `Supervisor`
- `preparation`
- `modeling`
- `visualization`
- `writing`
- `reviewer`

are logical Codex-driven roles inside the product architecture.

## What This Does Not Mean

It does **not** mean the current local prototype already embeds Codex as a runtime API product.

It means:

- the architecture is being shaped around a Codex-native orchestration philosophy
- we are not designing around the assumption that another external model must be added later

