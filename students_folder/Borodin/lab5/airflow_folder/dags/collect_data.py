from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    'calculate_daily_flights',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    description='Расчёт ежедневного количества отправленных рейсов'
) as dag:

    # Очищаем таблицу с метриками перед новым расчётом
    truncate_metrics = PostgresOperator(
        task_id='truncate_metrics',
        postgres_conn_id='airflow_db',
        sql='TRUNCATE TABLE logistic.daily_flights_count;'
    )

    # Выполняем расчёт количества рейсов по дням
    calculate_metrics = PostgresOperator(
        task_id='calculate_daily_counts',
        postgres_conn_id='airflow_db',
        sql='''
        -- Заполняем таблицу метрик количеством рейсов по дням
        INSERT INTO logistic.daily_flights_count (flight_date, flight_count)
        SELECT 
            departure_date AS flight_date,  -- Дата отправления как ключ метрики
            COUNT(*) AS flight_count        -- Количество рейсов в этот день
        FROM logistic.transfers
        GROUP BY departure_date             -- Группируем по дате отправления
        ORDER BY flight_date;               -- Сортируем по дате
        '''
    )

    # Определяем порядок выполнения задач
    truncate_metrics >> calculate_metrics