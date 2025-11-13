# /dags/collect_data.py
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


def calculate_and_save_metrics(run_date: str):
    from sqlalchemy import create_engine, text

    print(f"Обработка метрик за дату: {run_date}")

    # Подключение к PostgreSQL
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    # SQL-запрос для инкрементального обновления с использованием UPSERT
    upsert_data_query = """
        INSERT INTO logistics.daily_delivered_stats(report_date, delivered_count)
        SELECT :run_date, COUNT(order_id)
        FROM logistics.deliveries
        WHERE status = 'delivered'
        AND update_date = :run_date
        ON CONFLICT (report_date)
        DO UPDATE SET delivered_count = EXCLUDED.delivered_count
    """

    # Выполняем запрос
    with engine.connect() as conn:
        result = conn.execute(text(upsert_data_query), {"run_date": run_date})

    # Получаем количество обработанных записей для логирования
    check_count_query = """
        SELECT delivered_count FROM logistics.daily_delivered_stats
        WHERE report_date = :run_date
    """

    with engine.connect() as conn:
        count_result = conn.execute(text(check_count_query), {"run_date": run_date}).fetchone()
        delivered_count = count_result[0] if count_result else 0

    print(f"Метрики за {run_date} успешно обновлены. Доставлено заказов: {delivered_count}")


with DAG(dag_id='collect_data',  # важный атрибут
         default_args=ARGS,
         schedule_interval='@daily',
         max_active_runs=1,
         start_date=datetime(2025, 3, 20),
         catchup=True,
         tags=['lab5']) as dag:
    t_process_metrics = PythonOperator(
        task_id='collect_data',
        dag=dag,
        python_callable=calculate_and_save_metrics,
        op_kwargs={"run_date": "{{ ds }}"}
    )

    run = t_process_metrics