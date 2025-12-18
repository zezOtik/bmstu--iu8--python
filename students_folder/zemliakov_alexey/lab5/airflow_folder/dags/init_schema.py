from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    'init_schema',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@once',
    catchup=False,
    description='Создание схемы и таблиц в метабазе Airflow'
) as dag:

    create_employees_table = PostgresOperator(
        task_id='create_employees_table',
        postgres_conn_id='airflow_db',
        sql='''
        CREATE TABLE IF NOT EXISTS hr_employees (
            id BIGINT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            hire_date DATE
        );
        '''
    )

    create_metrics_table = PostgresOperator(
        task_id='create_metrics_table',
        postgres_conn_id='airflow_db',
        sql='''
        CREATE TABLE IF NOT EXISTS hr_monthly_hires (
            month TEXT PRIMARY KEY,
            count INTEGER NOT NULL
        );
        '''
    )

    create_employees_table >> create_metrics_table