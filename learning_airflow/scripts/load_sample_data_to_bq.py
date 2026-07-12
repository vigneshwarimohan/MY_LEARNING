import os
from pathlib import Path

try:
    from google.cloud import bigquery
except ImportError:
    raise RuntimeError(
        "Please install google-cloud-bigquery and google-auth. Example: pip install google-cloud-bigquery google-auth"
    )

from google_auth_utils import load_google_credentials

DATASET = os.getenv("BQ_DATASET", "learning_dataset")
TABLE = os.getenv("BQ_TABLE", "learning_sample_table")
SQL_FILE = Path(__file__).resolve().parents[1] / "sql" / "load_sample_bq_table.sql"

scopes = ["https://www.googleapis.com/auth/bigquery"]
credentials, source, detected_project = load_google_credentials(scopes)
print(f"Using credentials from: {source}")

PROJECT_ID = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT") or detected_project or "your-project-id"

client = bigquery.Client(project=PROJECT_ID, credentials=credentials)


def ensure_dataset_exists(client: bigquery.Client, project_id: str, dataset_id: str, location: str = "US") -> None:
    try:
        client.get_dataset(f"{project_id}.{dataset_id}")
        print(f"Dataset already exists: {project_id}.{dataset_id}")
    except Exception:
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        dataset.location = location
        client.create_dataset(dataset, timeout=30)
        print(f"Created dataset: {project_id}.{dataset_id}")


ensure_dataset_exists(client, PROJECT_ID, DATASET)

with open(SQL_FILE, "r", encoding="utf-8") as handle:
    sql_template = handle.read()

sql = sql_template.replace("{{PROJECT_ID}}", PROJECT_ID).replace("{{DATASET}}", DATASET).replace("{{TABLE}}", TABLE)
print(f"Running SQL to populate BigQuery table: {PROJECT_ID}.{DATASET}.{TABLE}")
job = client.query(sql)
job.result()
print(f"BigQuery table {PROJECT_ID}.{DATASET}.{TABLE} updated.")
