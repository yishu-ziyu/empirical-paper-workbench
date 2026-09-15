"""OpenAlex works search: mock HTTP, no live network."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from agent.nodes.literature_sources.openalex import OPENALEX, openalex_search


def _make_mock_urlopen(payload: dict):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(payload).encode("utf-8")
    mock_resp.__enter__ = lambda self: self
    mock_resp.__exit__ = lambda *args: None
    return mock_resp


def test_openalex_maps_works():
    payload = {
        "results": [
            {
                "id": "https://openalex.org/W1",
                "doi": "https://doi.org/10.1162/003355303322552856",
                "display_name": "Minimum Wages and Employment",
                "publication_year": 2000,
                "authorships": [
                    {"author": {"display_name": "David Card"}},
                    {"author": {"display_name": "Alan Krueger"}},
                ],
                "primary_location": {
                    "landing_page_url": "https://example.edu/card-krueger"
                },
            }
        ]
    }
    with patch(
        "agent.nodes.literature_sources.openalex.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(payload)
        result = openalex_search("minimum wage employment")

    assert len(result) == 1
    assert result[0]["title"] == "Minimum Wages and Employment"
    assert result[0]["authors"] == ["David Card", "Alan Krueger"]
    assert result[0]["year"] == 2000
    assert result[0]["doi"] == "https://doi.org/10.1162/003355303322552856"
    assert result[0]["url"] == "https://example.edu/card-krueger"
    assert result[0]["source"] == "openalex"
    req = mock_urlopen.call_args[0][0]
    assert req.full_url.startswith(OPENALEX)
    ua = ""
    for key, value in req.header_items():
        if key.lower() == "user-agent":
            ua = value
    assert "mailto:" in ua


def test_openalex_empty_query():
    assert openalex_search("  ") == []


def test_openalex_error_raises():
    with patch(
        "agent.nodes.literature_sources.openalex.urllib.request.urlopen",
        side_effect=OSError("down"),
    ):
        try:
            openalex_search("minimum wage")
        except RuntimeError as exc:
            assert "OpenAlex" in str(exc)
        else:
            raise AssertionError("expected RuntimeError")
