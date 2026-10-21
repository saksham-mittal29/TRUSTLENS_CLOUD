import pytest
from pydantic import ValidationError
from app.schemas.verification import VerificationRequest


@pytest.mark.unit
def test_valid_normal_input():
    req = VerificationRequest(response="The Eiffel Tower is located in Paris.")
    assert req.response == "The Eiffel Tower is located in Paris."


@pytest.mark.unit
def test_empty_string_input_rejected():
    with pytest.raises(ValidationError) as exc_info:
        VerificationRequest(response="")
    assert "response" in str(exc_info.value)


@pytest.mark.unit
def test_missing_input_field_rejected():
    with pytest.raises(ValidationError):
        VerificationRequest()


@pytest.mark.unit
def test_whitespace_only_string_behavior():
    # Schema enforces min_length=1 on raw string; verifies behavior
    req = VerificationRequest(response="   ")
    assert req.response == "   "
    assert len(req.response) == 3


@pytest.mark.unit
def test_maximum_allowed_input_boundary_20000():
    max_text = "A" * 20000
    req = VerificationRequest(response=max_text)
    assert len(req.response) == 20000
    assert req.response == max_text


@pytest.mark.unit
def test_input_above_maximum_20001_rejected():
    oversized_text = "A" * 20001
    with pytest.raises(ValidationError) as exc_info:
        VerificationRequest(response=oversized_text)
    assert "response" in str(exc_info.value)
