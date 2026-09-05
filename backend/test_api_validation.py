from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

print("=== TRUSTLENS API VALIDATION TEST ===")


# Test 1: Missing response
response = client.post(
    "/api/verify",
    json={}
)

print("\nTest 1: Missing response")
print("Status:", response.status_code)

assert response.status_code == 422

print("Missing response rejected with 422 ✅")


# Test 2: Empty response
response = client.post(
    "/api/verify",
    json={
        "response": ""
    }
)

print("\nTest 2: Empty response")
print("Status:", response.status_code)

assert response.status_code == 422

print("Empty response rejected with 422 ✅")


# Test 3: Oversized response
response = client.post(
    "/api/verify",
    json={
        "response": "A" * 20001
    }
)

print("\nTest 3: Oversized response")
print("Status:", response.status_code)

assert response.status_code == 422

print("Oversized response rejected with 422 ✅")


# Test 4: Invalid field type
response = client.post(
    "/api/verify",
    json={
        "response": 12345
    }
)

print("\nTest 4: Invalid response type")
print("Status:", response.status_code)

assert response.status_code == 422

print("Invalid response type rejected with 422 ✅")


print("\nAll API validation tests passed successfully! 🎉")
