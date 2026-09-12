import json
import csv
import random
from pathlib import Path


INPUT_FILE = Path("evaluation/shared_task_dev.jsonl")
OUTPUT_FILE = Path("evaluation/dataset.csv")

TARGET_PER_LABEL = 20

LABEL_MAP = {
    "SUPPORTS": "SUPPORTED",
    "REFUTES": "CONTRADICTED",
    "NOT ENOUGH INFO": "UNCERTAIN",
}


selected = {
    "SUPPORTS": [],
    "REFUTES": [],
    "NOT ENOUGH INFO": [],
}


with INPUT_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        if all(
            len(selected[label]) >= TARGET_PER_LABEL
            for label in selected
        ):
            break

        item = json.loads(line)

        label = item.get("label")

        if label not in selected:
            continue

        if len(selected[label]) >= TARGET_PER_LABEL:
            continue

        claim = item.get("claim", "").strip()

        if not claim:
            continue

        selected[label].append(
            {
                "claim": claim,
                "ground_truth": LABEL_MAP[label],
            }
        )


rows = []
row_id = 1

for label in ["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"]:
    for item in selected[label]:
        rows.append(
            {
                "id": row_id,
                "claim": item["claim"],
                "ground_truth": item["ground_truth"],
            }
        )
        row_id += 1

random.seed(42)
random.shuffle(rows)


with OUTPUT_FILE.open(
    "w",
    newline="",
    encoding="utf-8",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["id", "claim", "ground_truth"],
    )

    writer.writeheader()
    writer.writerows(rows)


print(f"Created: {OUTPUT_FILE}")
print(f"Total claims: {len(rows)}")

for label in ["SUPPORTED", "CONTRADICTED", "UNCERTAIN"]:
    count = sum(
        1 for row in rows
        if row["ground_truth"] == label
    )
    print(f"{label}: {count}")
