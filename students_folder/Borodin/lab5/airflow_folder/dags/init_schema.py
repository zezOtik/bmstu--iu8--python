from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    'init_schema_airline',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@once',
    catchup=False,
    description='Создание схемы и таблиц для данных о авиаперевозках'
) as dag:

    # Создаём схему и основную таблицу рейсов
    create_transfers_table = PostgresOperator(
        task_id='create_transfers_table',
        postgres_conn_id='airflow_db',
        sql='''
        -- Создаём схему для логистических данных
        CREATE SCHEMA IF NOT EXISTS logistic;
        
        -- Создаём таблицу рейсов
        -- Важно: поле "from" является зарезервированным словом SQL, поэтому берётся в кавычки
        CREATE TABLE IF NOT EXISTS logistic.transfers (
            id BIGINT PRIMARY KEY,
            "from" TEXT NOT NULL,    -- Аэропорт отправления
            "to" TEXT NOT NULL,      -- Аэропорт прибытия
            departure_date DATE NOT NULL,  -- Дата отправления
            arriving_date DATE NOT NULL    -- Дата прибытия
        );
        '''
    )

    # Создаём таблицу для хранения метрик
    create_metrics_table = PostgresOperator(
        task_id='create_metrics_table',
        postgres_conn_id='airflow_db',
        sql='''
        -- Таблица для хранения ежедневной статистики по рейсам
        CREATE TABLE IF NOT EXISTS logistic.daily_flights_count (
            flight_date DATE PRIMARY KEY,  -- Дата рейса
            flight_count INTEGER NOT NULL  -- Количество рейсов
        );
        '''
    )

    # Определяем порядок выполнения задач
    create_transfers_table >> create_metrics_table