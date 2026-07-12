import json
import os
from pathlib import Path
from typing import Any, Tuple

import google.auth
from google.oauth2.service_account import Credentials


def _read_json_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _get_default_service_account_file() -> Path:
    return Path(__file__).resolve().parents[1] / "credentials" / "service_account.json"


def load_service_account_info() -> Tuple[dict[str, Any], str]:
    raw_json = os.getenv("SERVICE_ACCOUNT_JSON")
    if raw_json:
        try:
            return json.loads(raw_json), "SERVICE_ACCOUNT_JSON"
        except json.JSONDecodeError as exc:
            raise RuntimeError("SERVICE_ACCOUNT_JSON is not valid JSON.") from exc

    env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        credential_file = Path(env_path).expanduser()
        if credential_file.exists():
            return _read_json_file(credential_file), f"GOOGLE_APPLICATION_CREDENTIALS:{credential_file}"

    default_path = _get_default_service_account_file()
    if default_path.exists():
        return _read_json_file(default_path), f"credentials/service_account.json"

    project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    secret_name = os.getenv("GOOGLE_SECRET_NAME") or os.getenv("SERVICE_ACCOUNT_SECRET_NAME")
    if project_id and secret_name:
        try:
            from google.cloud import secretmanager
        except ImportError as exc:
            raise RuntimeError(
                "google-cloud-secret-manager is not installed. Install it with: pip install google-cloud-secret-manager"
            ) from exc

        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("utf-8")
        return json.loads(payload), f"Secret Manager:{secret_name}"

    raise FileNotFoundError(
        "No service account credentials were found. Provide one of the following:\n"
        "1. SERVICE_ACCOUNT_JSON environment variable with raw JSON\n"
        "2. GOOGLE_APPLICATION_CREDENTIALS pointing to a service account JSON file\n"
        "3. credentials/service_account.json\n"
        "4. GCP_PROJECT_ID and GOOGLE_SECRET_NAME for Secret Manager"
    )


def load_google_credentials(scopes: list[str]) -> tuple[Any, str, str | None]:
    try:
        service_account_info, source = load_service_account_info()
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        project_id = (
            os.getenv("GCP_PROJECT_ID")
            or os.getenv("GOOGLE_CLOUD_PROJECT")
            or service_account_info.get("project_id")
        )
        return credentials, source, project_id
    except FileNotFoundError:
        credentials, detected_project_id = google.auth.default(scopes=scopes)
        project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT") or detected_project_id
        return credentials, "Application Default Credentials", project_id
