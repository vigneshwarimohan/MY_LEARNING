from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from util.common_utils import get_default_args, run_python_script

TEAM_CONFIG = {
    "owner": "learner",
    "email": ["learner@example.com"],
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

default_args = get_default_args(owner=TEAM_CONFIG["owner"])

with DAG(
    dag_id="monday",
    default_args=default_args,
    description="Runs SQL load to BigQuery first, then loads the data to Google Sheets.",
    schedule_interval="0 7 * * 1",
    catchup=False,
    concurrency=5,
    max_active_runs=1,
    tags=["learning", "bq", "gsheet", "monday"],
) as dag:

    run_sql_first = PythonOperator(
        task_id="run_sql_first",
        python_callable=run_python_script,
        op_kwargs={"script_name": "load_sample_data_to_bq.py"},
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    load_sheet_second = PythonOperator(
        task_id="load_sheet_second",
        python_callable=run_python_script,
        op_kwargs={"script_name": "load_bq_to_gsheet.py"},
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    run_sql_first >> load_sheet_second
