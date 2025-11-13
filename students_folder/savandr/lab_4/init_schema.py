from airflow import DAG
from datetime import datetime

from airflow.providers.standard.operators.python import PythonOperator

ARGS = {
    "owner": "bmstu",
    "email": ['wzomzot@hop.ru', '1@mail.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 3, 20),  # важный атрибут
    "pool": "default_pool",
    "queue": "default"
}


def create_table():
    import pandas as pd
    from sqlalchemy import create_engine, text

    # Подключение к PostgreSQL
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    # SQL-запрос для создания таблицы
    create_table_query = """
    CREATE TABLE IF NOT EXISTS logistics.deliveries (
        event_id SERIAL PRIMARY KEY,
        order_id BIGINT NOT NULL,
        status TEXT NOT NULL,
        update_date DATE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS logistics.daily_delivered_stats (
        report_date DATE PRIMARY KEY,
        delivered_count INT NOT NULL
    );
    """

    # Выполняем запрос
    with engine.connect() as conn:
        conn.execute(text(create_table_query))

    print("Таблица 'deliveries' успешно создана!")

def create_schema():
    import pandas as pd
    from sqlalchemy import create_engine, text

    # Подключение к PostgreSQL
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    # SQL-запрос для создания таблицы
    create_schema_query = """
    CREATE SCHEMA IF NOT EXISTS logistics;
    """

    # Выполняем запрос
    with engine.connect() as conn:
        conn.execute(text(create_schema_query))

    print("Схема 'logistics' успешно создана!")


with DAG(dag_id='init_schema',  # важный атрибут
         default_args=ARGS,
         schedule_interval='@once',
         max_active_runs=1,
         start_date=datetime(2025, 3, 20),
         catchup=False,
         tags=['lab5']) as dag:
    t_create_schema = PythonOperator(
        task_id='create_schema',
        dag=dag,
        python_callable=create_schema
    )

    t_create_table = PythonOperator(
        task_id='create_table',
        dag=dag,
        python_callable=create_table
    )

    run = t_create_schema >> t_create_table
