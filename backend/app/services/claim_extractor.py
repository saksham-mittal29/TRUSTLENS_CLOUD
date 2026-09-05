import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()


def extract_claims(response: str):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Extract all claims or statements from the following LLM response
that could be evaluated for truth, accuracy, or evidentiary support.

IMPORTANT:
- Include factual claims.
- Include numerical claims.
- Include historical claims.
- Include claims about people, places, events, science, technology, etc.
- Include subjective or comparative claims when they are presented as statements.
- Include ambiguous claims even if they may ultimately be impossible to prove.
- Do NOT discard a claim merely because it is subjective or difficult to verify.
- The verification stage will decide whether a claim is SUPPORTED, CONTRADICTED, or UNCERTAIN.

Return ONLY valid JSON.

The JSON must be an array of objects.
Each object must contain exactly one field called "claim".

Example:

[
  {{"claim": "The Eiffel Tower is located in Paris."}},
  {{"claim": "The Eiffel Tower was completed in 1889."}},
  {{"claim": "The Eiffel Tower is the most beautiful structure ever built."}}
]

Do not include markdown.
Do not include explanations.
Do not add any fields other than "claim".

LLM response:
{response}
"""

    result = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )

    text = result.text.strip()

    try:
        claims = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(
            f"Gemini returned invalid JSON: {text}"
        )

    return claims