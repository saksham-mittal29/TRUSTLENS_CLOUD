import os
import sys
from pathlib import Path

# Ensure working directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.api.dependencies import get_current_firebase_user
from app.main import app


@pytest.fixture
def mock_firebase_user():
    return {
        "uid": "test-user-uid-12345",
        "email": "testuser@trustlens.ai",
        "name": "Test User",
        "auth_time": 1700000000,
        "iss": "https://securetoken.google.com/trustlens",
    }


@pytest.fixture
def auth_headers():
    return {
        "Authorization": "Bearer mock-valid-firebase-id-token"
    }


@pytest.fixture
def authenticated_client(mock_firebase_user):
    """
    TestClient with Firebase authentication mocked via dependency override.
    """
    app.dependency_overrides[get_current_firebase_user] = lambda: mock_firebase_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def client(authenticated_client):
    """
    Default client fixture defaulting to authenticated state for standard API tests.
    """
    return authenticated_client


@pytest.fixture
def unauthenticated_client():
    """
    TestClient with NO auth dependency overrides to test 401 Unauthorized rejection.
    """
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """
    Provides a real database session from app.database.SessionLocal
    and cleans up any test entities.
    """
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_claims():
    return [
        {"claim": "The Eiffel Tower is in Paris."},
        {"claim": "The Eiffel Tower was completed in 1889."}
    ]


@pytest.fixture
def sample_evidence():
    return [
        {
            "title": "Eiffel Tower - Wikipedia",
            "url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
            "snippet": "The Eiffel Tower is a landmark located in Paris, completed in 1889.",
            "source_reliability": 75
        }
    ]


@pytest.fixture
def sample_verification_result():
    return {
        "verdict": "SUPPORTED",
        "confidence": 95,
        "reason": "Evidence directly confirms the claim.",
        "evidence_quality": 90,
        "source_agreement": 85,
        "relevant_sources": [1]
    }
