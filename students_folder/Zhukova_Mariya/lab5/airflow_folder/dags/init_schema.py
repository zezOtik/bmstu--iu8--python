from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, text


ARGS = {
    "owner": "Zhukova_Mariya",
    "email": ['test_user_var_2@email.ru','2@email.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 11, 20),
    "pool": "default_pool",
    "queue": "default"
}


def create_schema():
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    create_schema_query = """
    CREATE SCHEMA IF NOT EXISTS market;
    """

    with engine.connect() as conn:
        conn.execute(text(create_schema_query))

    print("Схема 'market' успешно создана!")


def create_table():
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS market.sales (
        id BIGINT PRIMARY KEY,
        product_name TEXT NOT NULL,
        sale_date DATE NOT NULL,
        amount DECIMAL(10,2) NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS market.daily_sales_metrics (
        report_date DATE PRIMARY KEY,
        total_sales_amount DECIMAL(15,2) NOT NULL
    );
    """

    with engine.connect() as conn:
        conn.execute(text(create_table_query))

    print("Таблицы 'sales' и 'daily_sales_metrics' успешно созданы!")


with DAG(dag_id='init_schema',
         default_args=ARGS,
         schedule_interval='@once',
         max_active_runs=1,
         start_date=datetime(2025, 3, 20),
         catchup=True,
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