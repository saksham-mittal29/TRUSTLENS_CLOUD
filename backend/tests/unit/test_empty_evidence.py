import pytest
from app.services.claim_verifier import verify_claim


def test_empty_evidence_fallback():
    claim = "The Eiffel Tower is located on Mars."
    result = verify_claim(claim, [])

    assert result["verdict"] == "UNCERTAIN"
    assert result["confidence"] == 0
    assert result["evidence_quality"] == 0
    assert result["relevant_sources"] == []
    assert "No evidence was found" in result["reason"]
