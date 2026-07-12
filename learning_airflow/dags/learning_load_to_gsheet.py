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

default_args = get_default_args(owner=TEAM_CONFIG["owner"])

with DAG(
    dag_id=dag_name,
    default_args=default_args,
    description="A learning ETL pipeline that loads 10 rows and pushes to Google Sheet.",
    schedule_interval="@daily",
    catchup=False,
    concurrency=5,
    max_active_runs=1,
    tags=["learning", "etl"],
) as dag:

    start_sensor = create_start_sensor(dag, 7, 0)

    etl_task = PythonOperator(
        task_id="load_sample_data",
        python_callable=run_python_script,
        op_kwargs={"script_name": "load_sample_data.py"},
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    gsheet_task = PythonOperator(
        task_id="export_to_gsheet",
        python_callable=run_python_script,
        op_kwargs={"script_name": "load_to_gsheet.py"},
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    start_sensor >> etl_task >> gsheet_task
