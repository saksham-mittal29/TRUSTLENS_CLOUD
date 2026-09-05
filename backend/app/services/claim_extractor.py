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
Extract all factual claims from the following LLM response.

Return ONLY valid JSON.

The JSON must be an array of objects.
Each object must contain exactly one field called "claim".

Example:

[
  {{"claim": "The Eiffel Tower is located in Paris."}},
  {{"claim": "The Eiffel Tower was completed in 1889."}}
]

Do not include markdown.
Do not include explanations.

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