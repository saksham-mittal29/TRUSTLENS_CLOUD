import pytest
from fastapi import HTTPException
from app.api.dependencies import get_current_firebase_user


def test_missing_authorization_header():
    with pytest.raises(HTTPException) as exc_info:
        get_current_firebase_user(authorization=None)
    assert exc_info.value.status_code == 401
    assert "Authorization header is required" in exc_info.value.detail


def test_non_bearer_authorization_header():
    with pytest.raises(HTTPException) as exc_info:
        get_current_firebase_user(authorization="Basic dXNlcjpwYXNz")
    assert exc_info.value.status_code == 401
    assert "must use Bearer token" in exc_info.value.detail


def test_empty_bearer_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_firebase_user(authorization="Bearer ")
    assert exc_info.value.status_code == 401
    assert "Firebase ID token is required" in exc_info.value.detail
