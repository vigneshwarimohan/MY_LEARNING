from datetime import timedelta
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
import os

from util.common_utils import get_default_args, create_start_sensor, run_python_script

local_tz = "Australia/Sydney"
dag_name = os.path.basename(__file__).split(".")[0]

TEAM_CONFIG = {
    "owner": "learner",
    "email": ["learner@example.com"],
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

def _script_path(script_name: str) -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", script_name)


def _bq_sql_path(sql_name: str) -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "sql", sql_name)


default_args = get_default_args(owner=TEAM_CONFIG["owner"])

with DAG(
    dag_id=dag_name,
    default_args=default_args,
    description="A learning DAG that loads data to BigQuery and exports it to Google Sheets.",
    schedule_interval="@daily",
    catchup=False,
    concurrency=5,
    max_active_runs=1,
    tags=["learning", "bq", "gsheet"],
) as dag:

    start_sensor = create_start_sensor(dag, 7, 0)

    load_bq_table = PythonOperator(
        task_id="load_bq_table",
        python_callable=run_python_script,
        op_kwargs={"script_name": "load_sample_data_to_bq.py"},
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    export_bq_to_sheet = PythonOperator(
        task_id="export_bq_to_sheet",
        python_callable=run_python_script,
        op_kwargs={"script_name": "load_bq_to_gsheet.py"},
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    start_sensor >> load_bq_table >> export_bq_to_sheet
