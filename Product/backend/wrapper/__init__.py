"""Wrapper services for 5-tab vertical slice.

Each tab (brief / search / variables / design / execution) has its own
`*_service.py` module exposing build/write/verify functions that wrap the
existing 40+ backend services and `llm_client.chat_completion`.
"""
