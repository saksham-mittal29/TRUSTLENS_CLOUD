from pydantic import ValidationError

from app.schemas.verification import VerificationRequest


print("=== TRUSTLENS INPUT VALIDATION TEST ===")


# Test 1: Valid request
request = VerificationRequest(
    response="The Eiffel Tower is located in Paris."
)

print("\nTest 1: Valid response")
print(request)
assert request.response == "The Eiffel Tower is located in Paris."


# Test 2: Empty response
try:
    VerificationRequest(response="")

    raise AssertionError("Empty response should have been rejected.")

except ValidationError:
    print("Test 2: Empty response rejected ✅")


# Test 3: Missing response
try:
    VerificationRequest()

    raise AssertionError("Missing response should have been rejected.")

except ValidationError:
    print("Test 3: Missing response rejected ✅")


# Test 4: Response exceeding maximum length
try:
    VerificationRequest(
        response="A" * 20001
    )

    raise AssertionError(
        "Response longer than 20000 characters should be rejected."
    )

except ValidationError:
    print("Test 4: Oversized response rejected ✅")


# Test 5: Maximum allowed length
request = VerificationRequest(
    response="A" * 20000
)

print("Test 5: 20000-character response accepted ✅")

assert len(request.response) == 20000


print("\nAll input validation tests passed successfully! 🎉")
