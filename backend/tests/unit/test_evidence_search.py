from unittest.mock import MagicMock, patch
import pytest
from app.services.evidence_search import search_evidence, calculate_source_reliability


@pytest.mark.unit
def test_search_evidence_normal_results():
    fake_ddgs_results = [
        {
            "title": "Eiffel Tower History",
            "href": "https://www.britannica.com/topic/Eiffel-Tower-Paris-France",
            "body": "The Eiffel Tower is a landmark in Paris completed in 1889."
        },
        {
            "title": "Eiffel Tower Official Site",
            "href": "https://www.toureiffel.paris/en",
            "body": "Official visitor information for the Eiffel Tower."
        }
    ]

    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.__enter__.return_value = mock_ddgs_instance
    mock_ddgs_instance.text.return_value = fake_ddgs_results

    with patch("app.services.evidence_search.DDGS", return_value=mock_ddgs_instance):
        results = search_evidence("Eiffel Tower Paris")

    assert len(results) == 2
    assert results[0]["title"] == "Eiffel Tower History"
    assert results[0]["url"] == "https://www.britannica.com/topic/Eiffel-Tower-Paris-France"
    assert results[0]["snippet"] == "The Eiffel Tower is a landmark in Paris completed in 1889."
    assert results[0]["source_reliability"] == 90  # britannica.com is high reliability
    assert results[1]["source_reliability"] == 50  # toureiffel.paris default


@pytest.mark.unit
def test_search_evidence_zero_results():
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.__enter__.return_value = mock_ddgs_instance
    mock_ddgs_instance.text.return_value = []

    with patch("app.services.evidence_search.DDGS", return_value=mock_ddgs_instance):
        results = search_evidence("Query that returns nothing")

    assert isinstance(results, list)
    assert len(results) == 0


@pytest.mark.unit
def test_search_evidence_search_failure_catches_and_returns_empty():
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.__enter__.return_value = mock_ddgs_instance
    mock_ddgs_instance.text.side_effect = ConnectionError("DuckDuckGo rate limit or network down")

    with patch("app.services.evidence_search.DDGS", return_value=mock_ddgs_instance):
        results = search_evidence("Eiffel Tower")

    assert isinstance(results, list)
    assert len(results) == 0


@pytest.mark.unit
def test_search_evidence_malformed_search_result():
    # Test result items missing href or title or body
    fake_malformed_results = [
        {"only_random_field": "some value"},
        {"href": "https://nature.com/article"},
        {"title": None, "href": "", "body": None}
    ]

    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.__enter__.return_value = mock_ddgs_instance
    mock_ddgs_instance.text.return_value = fake_malformed_results

    with patch("app.services.evidence_search.DDGS", return_value=mock_ddgs_instance):
        results = search_evidence("Query")

    assert len(results) == 3
    assert results[0]["title"] is None
    assert results[0]["url"] == ""
    assert results[0]["source_reliability"] == 50
    assert results[1]["url"] == "https://nature.com/article"
    assert results[1]["source_reliability"] == 90
