import csv
import os
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    raise RuntimeError(
        "Please install gspread and google-auth. Example: pip install gspread google-auth"
    )

from google_auth_utils import load_service_account_info

DATA_DIR = Path(__file__).resolve().parents[1] / "datasets"
input_file = DATA_DIR / "learning_sample_data.csv"

SPREADSHEET_NAME = os.getenv("LEARNING_GSHEET_NAME", "Learning ETL Sheet")

service_account_info, source = load_service_account_info()
print(f"Using credentials from: {source}")

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
client = gspread.authorize(credentials)

with open(input_file, mode="r", encoding="utf-8") as csv_file:
    reader = csv.reader(csv_file)
    rows = list(reader)

spreadsheet = client.open(SPREADSHEET_NAME)
worksheet = spreadsheet.sheet1
worksheet.clear()
worksheet.update(rows)

print(f"Loaded {len(rows)-1} rows into Google Sheet: {SPREADSHEET_NAME}")
