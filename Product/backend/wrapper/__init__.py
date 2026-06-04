"""Wrapper services for 5-tab vertical slice.

每个 tab (brief / search / variables / design / execute) 一个 service:
`*_service.py` 暴露 build/write/verify 函数，包装现有 40+ backend services
和 `llm_client.chat_completion`。
"""
