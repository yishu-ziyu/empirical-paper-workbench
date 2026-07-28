"""agent/tests conftest — sys.path setup 已上移至根 conftest.py（ADR-0003 Stage C）。

本文件保留为占位，确保 agent/tests/ 作为 pytest 测试目录被发现。
所有公共 fixture（make_state / mock_llm_for / six_chapter_outline 等）
由根目录 conftest.py 提供。
"""
