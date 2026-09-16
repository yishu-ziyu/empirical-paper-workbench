# First Results review failure

The single real Results generation produced nonempty LLM text but review returned `mock_fallback`, `review_degraded=true`. Root inspection found `pydantic_ai` absent in the built image: the existing `build_review_agent` imports it, while only agent/requirements.txt listed `pydantic-ai-slim[openai]==2.35.3`. Add that same pinned dependency to the backend runtime requirements. Preserve the first degraded result; validate the dependency offline and review the existing text once, without regenerating text or bypassing the independent grounding gate.
