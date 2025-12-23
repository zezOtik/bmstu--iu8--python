import csv

from airflow import DAG
from datetime import datetime

from airflow.operators.python import PythonOperator

ARGS = {
    "owner": "bmstu",
    "email": ['wzomzot@hop.ru', '1@mail.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 3, 20),  # важный атрибут
    "pool": "default_pool",
    "queue": "default"
}

CSV_FILE_PATH = '/opt/airflow/dags/deliveries.csv'

def truncate_table():
    from sqlalchemy import create_engine, text

    # Подключение к PostgreSQL
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    # SQL-запрос для создания таблицы
    truncate_table_query = """
        TRUNCATE TABLE logistics.deliveries;
    """

    # Выполняем запрос
    with engine.connect() as conn:
        conn.execute(text(truncate_table_query))

    print("Таблица 'deliveries' очищена!")


def init_deliveries():
    from sqlalchemy import create_engine, text

    # Подключение к PostgreSQL
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    rows_to_insert = []
    with open(CSV_FILE_PATH, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Пропускаем заголовок

        for row in reader:
            status = row[0]
            update_date = row[1]

            rows_to_insert.append({'status': status, 'update_date': update_date})

    # Выполняем запрос
    insert_data_query = """
        INSERT INTO logistics.deliveries (status, update_date) VALUES
        (:status, :update_date)
    """
    with engine.connect() as conn:
        conn.execute(text(insert_data_query), rows_to_insert)


print("Таблица 'deliveries' наполнена заказами!")


with DAG(dag_id='init_data',  # важный атрибут
         default_args=ARGS,
         schedule_interval='@once',
         max_active_runs=1,
         start_date=datetime(2025, 3, 20),
         catchup=False,
         tags=['lab5']) as dag:
    t_truncate_table = PythonOperator(
        task_id='truncate_table',
        dag=dag,
        python_callable=truncate_table
    )

    t_insert_data = PythonOperator(
        task_id='insert_data',
        dag=dag,
        python_callable=init_deliveries
    )

    run = t_truncate_table >> t_insert_data
