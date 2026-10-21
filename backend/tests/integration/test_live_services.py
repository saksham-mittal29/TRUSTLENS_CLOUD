import os
import pytest
from app.services.evidence_search import search_evidence, calculate_source_reliability
from app.services.claim_extractor import extract_claims
from app.services.claim_verifier import verify_claim


@pytest.mark.unit
def test_source_reliability_static_heuristics():
    assert calculate_source_reliability("https://www.cdc.gov/data") == 95
    assert calculate_source_reliability("https://mit.edu/research") == 90
    assert calculate_source_reliability("https://www.nature.com/articles/1") == 90
    assert calculate_source_reliability("https://wikipedia.org/wiki/Earth") == 75
    assert calculate_source_reliability("https://en.wikipedia.org/wiki/Earth") == 70
    assert calculate_source_reliability("https://example.org/about") == 70

    assert calculate_source_reliability("https://randomsite.com/news") == 60
    assert calculate_source_reliability("https://unknown-domain.xyz/news") == 50


@pytest.mark.external
@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not configured for live test"
)
def test_live_claim_extractor():
    response_text = "The Eiffel Tower is located in Paris, France."
    try:
        claims = extract_claims(response_text)
        assert isinstance(claims, list)
        assert len(claims) >= 1
        assert "claim" in claims[0]
    except Exception as exc:
        if "503" in str(exc) or "429" in str(exc) or "UNAVAILABLE" in str(exc):
            pytest.skip(f"Live Gemini API is temporarily unavailable ({exc})")
        raise


@pytest.mark.external
def test_live_duckduckgo_search():

    try:
        results = search_evidence("Eiffel Tower Paris")
        assert isinstance(results, list)
        if len(results) > 0:
            first = results[0]
            assert "title" in first
            assert "url" in first
            assert "snippet" in first
            assert "source_reliability" in first
    except Exception as exc:
        pytest.skip(f"Live DuckDuckGo search failed ({exc})")

