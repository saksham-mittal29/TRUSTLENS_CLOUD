from app.services.claim_extractor import extract_claims


response = """
The Eiffel Tower is the most beautiful structure ever built.
"""

claims = extract_claims(response)

print("\nEXTRACTED CLAIMS")
print("================")

for item in claims:
    print(item)