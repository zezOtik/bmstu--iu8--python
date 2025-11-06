from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator


ARGS = {
    "owner": "bmstu",
    "email": ['wzomzot@hop.ru','1@mail.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 3, 20), # важный атрибут
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
    CREATE TABLE IF NOT EXISTS super_job.employees (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        department VARCHAR(50),
        salary NUMERIC(10, 2),
        invited_date TIMESTAMP
    );
    """

    # Выполняем запрос
    with engine.connect() as conn:
        conn.execute(text(create_table_query))

    print("Таблица 'employees' успешно создана!")


def create_func():
    import pandas as pd
    from sqlalchemy import create_engine, text


    # Подключение к PostgreSQL
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    # SQL-запрос для создания таблицы
    create_func_query = """
    CREATE OR REPLACE FUNCTION super_job.get_avg_salary_by_date(input_date DATE)
    RETURNS NUMERIC(12, 2) AS $$
    DECLARE
        avg_sal NUMERIC(12, 2);
    BEGIN
        SELECT AVG(salary)
        INTO avg_sal
        FROM super_job.employees
        WHERE invited_date = input_date;
    
        RETURN COALESCE(avg_sal, 0.00);  -- возвращает 0.00, если нет данных
    END;
    $$ LANGUAGE plpgsql;
    """

    # Выполняем запрос
    with engine.connect() as conn:
        conn.execute(text(create_func_query))

    print("Функция 'employees' успешно создана!")


def create_schema():
    import pandas as pd
    from sqlalchemy import create_engine, text


    # Подключение к PostgreSQL
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    # SQL-запрос для создания таблицы
    create_schema_query = """
    CREATE SCHEMA IF NOT EXISTS super_job;
    """

    # Выполняем запрос
    with engine.connect() as conn:
        conn.execute(text(create_schema_query))

    print("Схема 'super_job' успешно создана!")


with DAG(dag_id='init_schema', # важный атрибут
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

    t_create_func = PythonOperator(
        task_id='create_func',
        dag=dag,
        python_callable=create_func
    )

    run = t_create_schema >> t_create_table >> t_create_func
