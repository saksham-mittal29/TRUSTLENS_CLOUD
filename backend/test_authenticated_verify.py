import json
import urllib.parse
import urllib.request
from getpass import getpass


api_key = input("Firebase Web API Key: ").strip()
email = input("Firebase test user email: ").strip()
password = getpass("Firebase test user password: ")


# Firebase login
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

print("Firebase login successful.")


# Authenticated TrustLens verification
verification_request = urllib.request.Request(
    "http://127.0.0.1:8000/api/verify",
    data=json.dumps({
        "response": "The Eiffel Tower is in Paris."
    }).encode(),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(verification_request) as response:
        result = json.loads(response.read().decode())
except urllib.error.HTTPError as exc:
    print("TrustLens API failed.")
    print("Status:", exc.code)
    print("Response:", exc.read().decode())
    raise SystemExit(1)

print("Authenticated verification successful.")
print(json.dumps(result, indent=2, default=str))
