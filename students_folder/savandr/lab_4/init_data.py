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

    # SQL-запрос для создания таблицы
    insert_data_query = """
        INSERT INTO logistics.deliveries (order_id, status, update_date) VALUES
        (101, 'processing', '2025-10-20'),
        (102, 'processing', '2025-10-20'),
        (101, 'in_transit', '2025-10-21'),
        (103, 'processing', '2025-10-22'),
        (102, 'delivered', '2025-10-22'), 
        (101, 'delivered', '2025-10-22'), 
        (104, 'processing', '2025-10-23'),
        (103, 'in_transit', '2025-10-23'),
        (104, 'delivered', '2025-10-23'), 
        (105, 'cancelled', '2025-10-23'), 
        (103, 'delivered', '2025-10-24'); 
    """

    # Выполняем запрос
    with engine.connect() as conn:
        conn.execute(text(insert_data_query))

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
        python_callable=truncate_table()
    )

    t_insert_data = PythonOperator(
        task_id='insert_data',
        dag=dag,
        python_callable=init_deliveries
    )

    run = t_truncate_table >> t_insert_data
