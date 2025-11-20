from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, text


ARGS = {
    "owner": "Zhukova_Mariya",
    "email": ['test_user_var_2@email.ru','2@email.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 3, 20), # дата первой записи в базе
    "pool": "default_pool",
    "queue": "default"
}


def calculate_and_save_metrics(run_date: str):
    print(f"Обработка метрик за дату: {run_date}")

    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    upsert_data_query = """
        INSERT INTO market.daily_sales_metrics(report_date, total_sales_amount)
        SELECT :run_date, COALESCE(SUM(amount), 0)
        FROM market.sales
        WHERE sale_date = :run_date
        ON CONFLICT (report_date)
        DO UPDATE SET total_sales_amount = EXCLUDED.total_sales_amount
    """

    with engine.connect() as conn:
        conn.execute(text(upsert_data_query), {"run_date": run_date})

    check_amount_query = """
        SELECT total_sales_amount FROM market.daily_sales_metrics
        WHERE report_date = :run_date
    """

    with engine.connect() as conn:
        amount_result = conn.execute(text(check_amount_query), {"run_date": run_date}).fetchone()
        total_amount = amount_result[0] if amount_result else 0

    print(f"Метрики за {run_date} успешно обновлены. Общая сумма продаж: {total_amount}")


def collect_sales_per_day():
    """Обработка всех дат из таблицы sales"""
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")
    
    # Получаем все уникальные даты из sales
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT sale_date 
            FROM market.sales 
            ORDER BY sale_date
        """))
        dates = [row[0] for row in result]
    
    print(f"Найдены даты для обработки: {dates}")
    
    # Обрабатываем каждую дату
    for date in dates:
        calculate_and_save_metrics(str(date))

with DAG(dag_id='collect_data',
         default_args=ARGS,
         schedule_interval='@once', # или daily - если ежедневно
         max_active_runs=1,
         start_date=datetime(2025, 3, 20),
         catchup=True,
         tags=['lab5']) as dag:
    
    t_process_all = PythonOperator(
        task_id='collect_sales_per_day',
        dag=dag,
        python_callable=collect_sales_per_day
    )