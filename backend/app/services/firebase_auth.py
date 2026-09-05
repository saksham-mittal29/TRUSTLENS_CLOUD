import os

import firebase_admin
from firebase_admin import auth, credentials

from dotenv import load_dotenv

load_dotenv()


def initialize_firebase():
    """
    Initialize Firebase Admin SDK once for the backend.
    """

    if firebase_admin._apps:
        return firebase_admin.get_app()

    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    if not credentials_path:
        raise ValueError(
            "FIREBASE_CREDENTIALS_PATH environment variable is not set"
        )

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"Firebase credentials file not found: {credentials_path}"
        )

    cred = credentials.Certificate(credentials_path)

    return firebase_admin.initialize_app(cred)


def verify_firebase_token(id_token: str):
    """
    Verify a Firebase ID token and return the decoded token.
    """

    if not id_token:
        raise ValueError("Firebase ID token is required")

    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token

    except Exception as exc:
        raise ValueError(
            f"Invalid Firebase ID token: {str(exc)}"
        )
