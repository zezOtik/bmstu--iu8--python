from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, text

ARGS = {
    "owner": "bmstu",
    "email": ['wzomzot@hop.ru','1@mail.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 3, 20),
    "pool": "default_pool",
    "queue": "default"
}

def create_schema():
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")
    create_schema_query = """
    CREATE SCHEMA IF NOT EXISTS ed_tech;
    """
    with engine.connect() as conn:
        conn.execute(text(create_schema_query))
    print("Схема 'ed_tech' успешно создана!")

def create_table():
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ed_tech.course_completions
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_query))
    print("Таблица 'course_completions' успешно создана!")

def create_metric_function():
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")
    create_func_query = """
    CREATE OR REPLACE FUNCTION ed_tech.get_unique_users_by_date(input_date DATE)
    """
    with engine.connect() as conn:
        conn.execute(text(create_func_query))
    print("Функция 'get_unique_users_by_date' успешно создана!")

with DAG(
    dag_id='init_schema_variant5',
    default_args=ARGS,
    schedule_interval='@once',
    max_active_runs=1,
    start_date=datetime(2025, 3, 20),
    catchup=False,
    tags=['lab5', 'variant5']
) as dag:

    t_create_schema = PythonOperator(
        task_id='create_schema',
        python_callable=create_schema
    )

    t_create_table = PythonOperator(
        task_id='create_table',
        python_callable=create_table
    )

    t_create_func = PythonOperator(
        task_id='create_metric_function',
        python_callable=create_metric_function
    )

    t_create_schema >> t_create_table >> t_create_func
