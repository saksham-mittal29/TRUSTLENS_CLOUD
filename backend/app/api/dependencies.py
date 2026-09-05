from fastapi import Header, HTTPException

from app.services.firebase_auth import (
    initialize_firebase,
    verify_firebase_token,
)


def get_current_firebase_user(
    authorization: str | None = Header(default=None)
):
    """
    Extract and verify the Firebase ID token
    from the Authorization header.
    """

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header must use Bearer token"
        )

    id_token = authorization.split(" ", 1)[1].strip()

    if not id_token:
        raise HTTPException(
            status_code=401,
            detail="Firebase ID token is required"
        )

    try:
        initialize_firebase()
        decoded_token = verify_firebase_token(id_token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase ID token"
        )

    return decoded_token
