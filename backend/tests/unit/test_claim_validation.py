from unittest.mock import MagicMock, patch
import pytest
from app.services.claim_verifier import validate_verification, verify_claim


evidence_list = [
    {
        "title": "Source 1",
        "url": "https://example.com/1",
        "snippet": "Example evidence snippet 1",
        "source_reliability": 90
    },
    {
        "title": "Source 2",
        "url": "https://example.com/2",
        "snippet": "Example evidence snippet 2",
        "source_reliability": 70
    }
]


# ==============================================================================
# 1. Verdict Categories Tests
# ==============================================================================

@pytest.mark.unit
def test_validation_verdict_supported():
    data = {"verdict": "SUPPORTED", "confidence": 95, "evidence_quality": 90, "relevant_sources": [1]}
    validated = validate_verification(data, evidence_list)
    assert validated["verdict"] == "SUPPORTED"


@pytest.mark.unit
def test_validation_verdict_contradicted():
    data = {"verdict": "CONTRADICTED", "confidence": 90, "evidence_quality": 85, "relevant_sources": [1]}
    validated = validate_verification(data, evidence_list)
    assert validated["verdict"] == "CONTRADICTED"


@pytest.mark.unit
def test_validation_verdict_uncertain():
    data = {"verdict": "UNCERTAIN", "confidence": 0, "evidence_quality": 0, "relevant_sources": []}
    validated = validate_verification(data, evidence_list)
    assert validated["verdict"] == "UNCERTAIN"


@pytest.mark.unit
def test_validation_invalid_verdicts_fallback_to_uncertain():
    for invalid in ["TRUE", "FALSE", "CONFIRMED", "REFUTED", "UNKNOWN", "PARTIALLY_TRUE", "", None]:
        validated = validate_verification({"verdict": invalid}, evidence_list)
        assert validated["verdict"] == "UNCERTAIN"


# ==============================================================================
# 2. Confidence & Score Range Tests (Clamping & Outside [0, 100])
# ==============================================================================

@pytest.mark.unit
def test_validation_confidence_clamping_above_and_below():
    assert validate_verification({"confidence": 150}, evidence_list)["confidence"] == 100
    assert validate_verification({"confidence": -50}, evidence_list)["confidence"] == 0
    assert validate_verification({"confidence": "85"}, evidence_list)["confidence"] == 85
    assert validate_verification({"confidence": "invalid"}, evidence_list)["confidence"] == 0
    assert validate_verification({"confidence": None}, evidence_list)["confidence"] == 0


@pytest.mark.unit
def test_validation_evidence_quality_and_agreement_clamping():
    validated = validate_verification({
        "evidence_quality": 200,
        "source_agreement": -30
    }, evidence_list)
    assert validated["evidence_quality"] == 100
    assert validated["source_agreement"] == 0


# ==============================================================================
# 3. Missing Fields & Malformed Dict Tests
# ==============================================================================

@pytest.mark.unit
def test_validation_missing_all_fields():
    validated = validate_verification({}, evidence_list)
    assert validated["verdict"] == "UNCERTAIN"
    assert validated["confidence"] == 0
    assert validated["reason"] == ""
    assert validated["evidence_quality"] == 0
    assert validated["source_agreement"] == 0
    assert validated["relevant_sources"] == []


@pytest.mark.unit
def test_validation_non_dict_payload_fallback():
    assert validate_verification(None, evidence_list)["verdict"] == "UNCERTAIN"
    assert validate_verification("not-a-dict", evidence_list)["verdict"] == "UNCERTAIN"
    assert validate_verification([1, 2, 3], evidence_list)["verdict"] == "UNCERTAIN"


# ==============================================================================
# 4. Relevant Sources & Conflicting Evidence Tests
# ==============================================================================

@pytest.mark.unit
def test_validation_conflicting_evidence_low_agreement():
    data = {
        "verdict": "UNCERTAIN",
        "confidence": 40,
        "reason": "Sources 1 and 2 directly disagree on the timeline.",
        "evidence_quality": 60,
        "source_agreement": 10,  # Low agreement signals conflicting sources
        "relevant_sources": [1, 2]
    }
    validated = validate_verification(data, evidence_list)
    assert validated["source_agreement"] == 10
    assert validated["relevant_sources"] == [1, 2]


@pytest.mark.unit
def test_validation_relevant_sources_filtering_and_deduplication():
    data = {
        "relevant_sources": [1, 2, 99, "invalid", 1, -1]
    }
    validated = validate_verification(data, evidence_list)
    # Only 1 and 2 are within 1 <= idx <= len(evidence_list)
    assert validated["relevant_sources"] == [1, 2]


# ==============================================================================
# 5. verify_claim End-to-End Function Tests (Mocked Gemini)
# ==============================================================================

@pytest.mark.unit
def test_verify_claim_zero_evidence_fast_fallback():
    result = verify_claim("Claim text", [])
    assert result["verdict"] == "UNCERTAIN"
    assert result["confidence"] == 0
    assert result["evidence_quality"] == 0
    assert result["relevant_sources"] == []
    assert "No evidence was found" in result["reason"]


@pytest.mark.unit
def test_verify_claim_successful_gemini_integration():
    mock_gemini_response = MagicMock()
    mock_gemini_response.text = """
    ```json
    {
        "verdict": "SUPPORTED",
        "confidence": 95,
        "reason": "Source 1 directly confirms that the Eiffel Tower is in Paris.",
        "evidence_quality": 90,
        "relevant_sources": [1],
        "source_agreement": 85
    }
    ```
    """

    with patch("os.getenv", return_value="fake-api-key"), \
         patch("google.genai.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_gemini_response

        result = verify_claim("The Eiffel Tower is in Paris.", evidence_list)

    assert result["verdict"] == "SUPPORTED"
    assert result["confidence"] == 95
    assert result["evidence_quality"] == 90
    assert result["relevant_sources"] == [1]
    # Source 1 has reliability 90 -> average source_reliability should be 90.0
    assert result["source_reliability"] == 90.0
