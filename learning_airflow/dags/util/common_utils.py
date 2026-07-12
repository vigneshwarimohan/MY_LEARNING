import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pendulum


def get_local_timezone():
    return pendulum.timezone("Australia/Sydney")


def get_default_args(owner: str = "learner") -> dict:
    tz = get_local_timezone()
    return {
        "owner": owner,
        "depends_on_past": False,
        "start_date": datetime(2026, 1, 1, tzinfo=tz),
        "retries": 0,
        "retry_delay": timedelta(minutes=5),
    }


def create_start_sensor(dag, hour: int = 7, minute: int = 0):
    from airflow.operators.empty import EmptyOperator

    return EmptyOperator(task_id=f"wait_until_{hour:02d}_{minute:02d}", dag=dag)


def run_python_script(script_name: str):
    project_root = Path(__file__).resolve().parents[2]
    script_path = project_root / "scripts" / script_name
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(project_root) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")

    subprocess.run([sys.executable, str(script_path)], check=True, cwd=str(project_root), env=env)
