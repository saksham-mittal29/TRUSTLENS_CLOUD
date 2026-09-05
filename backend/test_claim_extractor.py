from app.services.claim_extractor import extract_claims

sample_response = """
The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.
It is named after the engineer Gustave Eiffel, whose company designed and built the tower.
It was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair.
The tower is 330 meters tall, about the same height as an 81-storey building.
"""

print("Testing claim extraction...")
print("\nSample LLM Response:")
print(sample_response.strip())

claims = extract_claims(sample_response)

print("\n" + "-" * 40)
print(f"EXTRACTED CLAIMS ({len(claims)} found)")
print("-" * 40)
for i, item in enumerate(claims, 1):
    print(f"{i}. {item.get('claim')}")
