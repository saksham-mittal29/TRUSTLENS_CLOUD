import sys
from pathlib import Path
import csv
import json
import time

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from app.services.evidence_search import search_evidence


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "dataset.csv"
OUTPUT_FILE = BASE_DIR / "evidence_cache.json"


def create_evidence_cache():
    cache = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=1):
            claim = row["claim"]

            print(f"[{row_number}] Searching evidence: {claim}")

            try:
                evidence = search_evidence(claim)

                cache.append({
                    "id": row["id"],
                    "claim": claim,
                    "ground_truth": row["ground_truth"],
                    "evidence": evidence,
                    "error": "",
                })

                print(
                    f"    Evidence sources: {len(evidence)}"
                )

            except Exception as error:
                print(f"    ERROR: {error}")

                cache.append({
                    "id": row["id"],
                    "claim": claim,
                    "ground_truth": row["ground_truth"],
                    "evidence": [],
                    "error": str(error),
                })

            # Small delay to avoid hammering the search service
            time.sleep(1)

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            cache,
            file,
            indent=2,
            ensure_ascii=False
        )

    successful = sum(
        1 for item in cache
        if not item["error"]
    )

    errors = len(cache) - successful

    print()
    print(f"Cache saved to: {OUTPUT_FILE}")
    print(f"Total claims: {len(cache)}")
    print(f"Successful searches: {successful}")
    print(f"Search errors: {errors}")


if __name__ == "__main__":
    create_evidence_cache()
