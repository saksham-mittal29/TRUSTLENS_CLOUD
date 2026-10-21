from unittest.mock import MagicMock, patch
import pytest
from app.services.claim_extractor import extract_claims


@pytest.mark.unit
def test_claim_extraction_valid_single_claim():
    mock_result = MagicMock()
    mock_result.text = '[{"claim": "The Eiffel Tower is located in Paris."}]'

    with patch("os.getenv", return_value="fake-api-key"), \
         patch("google.genai.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_result

        claims = extract_claims("The Eiffel Tower is located in Paris.")

    assert isinstance(claims, list)
    assert len(claims) == 1
    assert claims[0]["claim"] == "The Eiffel Tower is located in Paris."


@pytest.mark.unit
def test_claim_extraction_valid_multiple_claims():
    mock_result = MagicMock()
    mock_result.text = """
    [
        {"claim": "The Eiffel Tower is in Paris."},
        {"claim": "The Eiffel Tower was completed in 1889."},
        {"claim": "The Eiffel Tower is 330 meters tall."}
    ]
    """

    with patch("os.getenv", return_value="fake-api-key"), \
         patch("google.genai.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_result

        claims = extract_claims("Some text with multiple facts.")

    assert isinstance(claims, list)
    assert len(claims) == 3
    assert claims[0]["claim"] == "The Eiffel Tower is in Paris."
    assert claims[1]["claim"] == "The Eiffel Tower was completed in 1889."
    assert claims[2]["claim"] == "The Eiffel Tower is 330 meters tall."


@pytest.mark.unit
def test_claim_extraction_no_claims_empty_list():
    mock_result = MagicMock()
    mock_result.text = "[]"

    with patch("os.getenv", return_value="fake-api-key"), \
         patch("google.genai.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_result

        claims = extract_claims("Hello world!")

    assert isinstance(claims, list)
    assert len(claims) == 0


@pytest.mark.unit
def test_claim_extraction_malformed_json_raises_value_error():
    mock_result = MagicMock()
    mock_result.text = "Here are the claims: 1. Eiffel tower is in Paris (not json)"

    with patch("os.getenv", return_value="fake-api-key"), \
         patch("google.genai.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_result

        with pytest.raises(ValueError) as exc_info:
            extract_claims("Some text")

    assert "Gemini returned invalid JSON" in str(exc_info.value)


@pytest.mark.unit
def test_claim_extraction_empty_response_raises_value_error():
    mock_result = MagicMock()
    mock_result.text = ""

    with patch("os.getenv", return_value="fake-api-key"), \
         patch("google.genai.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_result

        with pytest.raises(ValueError) as exc_info:
            extract_claims("Some text")

    assert "Gemini returned invalid JSON" in str(exc_info.value)


@pytest.mark.unit
def test_claim_extraction_missing_api_key_raises_error():
    with patch("os.getenv", return_value=None):
        with pytest.raises(ValueError) as exc_info:
            extract_claims("Some text")
    assert "GEMINI_API_KEY environment variable is not set" in str(exc_info.value)
