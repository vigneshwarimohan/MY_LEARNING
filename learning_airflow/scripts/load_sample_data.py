import csv
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "datasets"
OUTPUT_DIR.mkdir(exist_ok=True)

rows = [
    {"id": i, "name": f"Product {i}", "category": "Learning", "price": 10.0 + i}
    for i in range(1, 11)
]

output_file = OUTPUT_DIR / "learning_sample_data.csv"
with open(output_file, mode="w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["id", "name", "category", "price"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Created sample data with {len(rows)} rows at: {output_file}")
