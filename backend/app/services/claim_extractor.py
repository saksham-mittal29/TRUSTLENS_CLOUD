import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def extract_claims(response: str):
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please add GEMINI_API_KEY=your_key to backend/.env")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Extract all factual claims from the following LLM response.

Return only the claims as a numbered list.
Do not explain anything.

LLM response:
{response}
"""

    model_name = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    result = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    return result.text
