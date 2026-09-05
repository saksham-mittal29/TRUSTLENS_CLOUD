from fastapi import HTTPException

from app.api.dependencies import get_current_firebase_user


try:
    get_current_firebase_user("Basic abc123")
except HTTPException as exc:
    print("STATUS:", exc.status_code)
    print("DETAIL:", exc.detail)