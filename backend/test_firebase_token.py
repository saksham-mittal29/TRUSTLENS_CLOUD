import json
import urllib.parse
import urllib.request
from getpass import getpass

from app.database import SessionLocal
from app.services.firebase_auth import (
    initialize_firebase,
    verify_firebase_token,
)
from app.services.user_repository import get_or_create_user


import os

api_key = os.getenv("FIREBASE_WEB_API_KEY")
email = os.getenv("FIREBASE_TEST_USER_EMAIL")
password = os.getenv("FIREBASE_TEST_USER_PASSWORD")

if not (api_key and email and password):
    print("⚠️ Skipping test_firebase_token.py: Missing environment variables.")
    print("   Set FIREBASE_WEB_API_KEY, FIREBASE_TEST_USER_EMAIL, FIREBASE_TEST_USER_PASSWORD to run.")
    raise SystemExit(0)



url = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    f"?key={api_key}"
)

payload = urllib.parse.urlencode({
    "email": email,
    "password": password,
    "returnSecureToken": "true",
}).encode()

request = urllib.request.Request(
    url,
    data=payload,
    headers={
        "Content-Type": "application/x-www-form-urlencoded"
    },
    method="POST",
)

try:
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode())

except Exception as exc:
    print("Firebase login failed:", exc)
    raise SystemExit(1)


id_token = data["idToken"]

print("\nFirebase login successful.")

initialize_firebase()

decoded_token = verify_firebase_token(id_token)

print("Firebase token verified successfully.")
print("Firebase UID:", decoded_token["uid"])

db = SessionLocal()

try:
    user = get_or_create_user(
        db=db,
        firebase_uid=decoded_token["uid"]
    )

    print("Local User ID:", user.id)
    print("User Firebase UID:", user.firebase_uid)

finally:
    db.close()
