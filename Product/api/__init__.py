"""Product.api — FastAPI routers for the 5-tab vertical slice.

Each tab (brief / search / variables / design / execute) registers its own
FastAPI router via `app.include_router(...)` in `Product/app.py`.
"""
