# /dags/collect_data.py
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
        TRUNCATE TABLE logistics.daily_delivered_stats;
    """

    # Выполняем запрос
    with engine.connect() as conn:
        conn.execute(text(truncate_table_query))

    print("Таблица 'daily_delivered_stats' очищена!")

def calculate_and_save_metrics():
    from sqlalchemy import create_engine, text

    # Подключение к PostgreSQL
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    # SQL-запрос для создания таблицы
    insert_data_query = """
        INSERT INTO logistics.daily_delivered_stats(report_date, delivered_count)
        SELECT update_date, COUNT(order_id)
        FROM logistics.deliveries
        WHERE status = 'delivered'
        GROUP BY update_date
    """

    # Выполняем запрос
    with engine.connect() as conn:
        conn.execute(text(insert_data_query))

    print("Таблица 'daily_delivered_stats' успешно обновлена с новыми метриками!")


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

    t_process_metrics = PythonOperator(
        task_id='collect_data',
        dag=dag,
        python_callable=calculate_and_save_metrics()
    )

    run = t_truncate_table >> t_process_metrics