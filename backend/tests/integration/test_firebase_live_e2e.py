import os
import json
import urllib.parse
import urllib.request
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.firebase_auth import (
    initialize_firebase,
    verify_firebase_token,
)
from app.services.user_repository import get_or_create_user


FIREBASE_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")
TEST_USER_EMAIL = os.getenv("FIREBASE_TEST_USER_EMAIL")
TEST_USER_PASSWORD = os.getenv("FIREBASE_TEST_USER_PASSWORD")

FIREBASE_CONFIGURED = bool(FIREBASE_API_KEY and TEST_USER_EMAIL and TEST_USER_PASSWORD)


@pytest.fixture(scope="module")
def real_firebase_id_token():
    """
    Authenticates against real Google Firebase REST API using environment variables.
    Never uses interactive input().
    """
    if not FIREBASE_CONFIGURED:
        pytest.skip(
            "Real Firebase E2E test skipped: Missing one or more environment variables "
            "(FIREBASE_WEB_API_KEY, FIREBASE_TEST_USER_EMAIL, FIREBASE_TEST_USER_PASSWORD)."
        )

    url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        f"?key={FIREBASE_API_KEY}"
    )

    payload = urllib.parse.urlencode({
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "returnSecureToken": "true",
    }).encode()

    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            return data["idToken"]
    except Exception as exc:
        pytest.fail(f"Real Firebase login failed: {exc}")


@pytest.mark.external
def test_real_firebase_token_verification_and_user_creation(real_firebase_id_token, db_session):

    """
    Tests live token decoding via Firebase Admin SDK and local database user mapping.
    """
    initialize_firebase()
    decoded = verify_firebase_token(real_firebase_id_token)

    assert decoded is not None
    assert "uid" in decoded
    uid = decoded["uid"]

    user = get_or_create_user(db=db_session, firebase_uid=uid)
    assert user is not None
    assert user.id is not None
    assert user.firebase_uid == uid


@pytest.mark.external
def test_real_firebase_authenticated_api_verify_flow(real_firebase_id_token):
    """
    Tests POST /api/verify with a genuine Firebase ID token transmitted via HTTP Bearer header.
    """
    with TestClient(app) as live_client:
        response = live_client.post(
            "/api/verify",
            json={"response": "The Eiffel Tower is located in Paris."},
            headers={"Authorization": f"Bearer {real_firebase_id_token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "verification_id" in data
    assert "trust_score" in data
    assert data["total_claims"] >= 1


@pytest.mark.external
def test_real_firebase_authenticated_history_and_detail(real_firebase_id_token):

    """
    Tests GET /api/verifications and GET /api/verifications/{id} with genuine Firebase auth.
    """
    with TestClient(app) as live_client:
        # 1. Fetch history
        history_res = live_client.get(
            "/api/verifications",
            headers={"Authorization": f"Bearer {real_firebase_id_token}"}
        )
        assert history_res.status_code == 200
        history_data = history_res.json()
        assert "verifications" in history_data

        # 2. If verifications exist, fetch the latest one's details
        if history_data["verifications"]:
            first_id = history_data["verifications"][0]["id"]
            detail_res = live_client.get(
                f"/api/verifications/{first_id}",
                headers={"Authorization": f"Bearer {real_firebase_id_token}"}
            )
            assert detail_res.status_code == 200
            detail_data = detail_res.json()
            assert detail_data["id"] == first_id
            assert "claims" in detail_data
