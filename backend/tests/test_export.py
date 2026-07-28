"""Contract tests for GET /sessions/{id}/export?format=tex (T-02 red stage).

Pins the export contract from spec §12-§14:
- query param format=tex
- response body contains \\title{...}
- Content-Type: application/x-tex (or text/x-tex)

In the red stage the endpoint does not exist, so every test fails on the
status-code assertion (404).
"""


def test_export_tex_returns_title(uploaded_session, client):
    """GET /sessions/{id}/export?format=tex returns a .tex body containing \\title."""
    resp = client.get(
        f"/sessions/{uploaded_session}/export",
        params={"format": "tex"},
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}"
    body = resp.text
    assert "\\title{" in body, f"response body missing \\title{{: {body!r}"


def test_export_tex_content_type(uploaded_session, client):
    """Response Content-Type is application/x-tex or text/x-tex."""
    resp = client.get(
        f"/sessions/{uploaded_session}/export",
        params={"format": "tex"},
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}"
    ctype = resp.headers.get("content-type", "")
    assert "x-tex" in ctype, f"unexpected content-type: {ctype!r}"
