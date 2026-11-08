from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "tanusha",
    "retries": 1,
}

with DAG(
    dag_id="expense_tracker_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 10, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    generate_data = BashOperator(
        task_id="generate_data",
        bash_command="python /opt/airflow/dags/generate_data.py",
    )

    load_to_postgres = BashOperator(
        task_id="load_to_postgres",
        bash_command="python /opt/airflow/dags/load_to_postgres.py",
    )

    clean_data = BashOperator(
        task_id="clean_data",
        bash_command="python /opt/airflow/dags/clean_data.py",
    )

    generate_data >> load_to_postgres >> clean_data