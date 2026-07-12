import os
import csv
from pathlib import Path

try:
    import gspread
    from gspread.exceptions import SpreadsheetNotFound
    from google.oauth2.service_account import Credentials
    from google.cloud import bigquery
except ImportError:
    raise RuntimeError(
        "Please install gspread, google-auth, google-cloud-bigquery, and google-cloud-secret-manager. "
        "Example: pip install gspread google-auth google-cloud-bigquery google-cloud-secret-manager"
    )

from google_auth_utils import load_service_account_info

DATASET = os.getenv("BQ_DATASET", "learning_dataset")
TABLE = os.getenv("BQ_TABLE", "learning_sample_table")
SPREADSHEET_NAME = os.getenv("LEARNING_GSHEET_NAME", "Learning ETL Sheet")
OUTPUT_CSV = Path(__file__).resolve().parents[1] / "datasets" / "learning_bq_data.csv"

service_account_info, source = load_service_account_info()
print(f"Using credentials from: {source}")

PROJECT_ID = (
    os.getenv("GCP_PROJECT_ID")
    or os.getenv("GOOGLE_CLOUD_PROJECT")
    or service_account_info.get("project_id")
    or "your-project-id"
)

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)

bq_client = bigquery.Client(project=PROJECT_ID, credentials=credentials)
query = f"SELECT * FROM `{PROJECT_ID}.{DATASET}.{TABLE}` LIMIT 100"
print(f"Querying BigQuery table: {PROJECT_ID}.{DATASET}.{TABLE}")

job = bq_client.query(query)
rows = job.result()

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_CSV, mode="w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([field.name for field in rows.schema])
    for row in rows:
        writer.writerow([row[field.name] for field in rows.schema])

print(f"Wrote {OUTPUT_CSV}")

client = gspread.authorize(credentials)
try:
    spreadsheet = client.open(SPREADSHEET_NAME)
except SpreadsheetNotFound:
    spreadsheet = client.create(SPREADSHEET_NAME)

worksheet = spreadsheet.sheet1
worksheet.clear()

with open(OUTPUT_CSV, mode="r", encoding="utf-8") as file:
    reader = csv.reader(file)
    rows = list(reader)
    worksheet.update(rows)

print(f"Loaded {len(rows)-1} rows into Google Sheet: {SPREADSHEET_NAME}")
