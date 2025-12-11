from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    'collect_data',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    description='Расчет ежемесячной метрики новых сотрудников'
) as dag:

    truncate_metrics = PostgresOperator(
        task_id='truncate_metrics_table',
        postgres_conn_id='airflow_db',
        sql='TRUNCATE TABLE hr_monthly_hires;'
    )

    calculate_metrics = PostgresOperator(
        task_id='calculate_monthly_hires',
        postgres_conn_id='airflow_db',
        sql='''
        INSERT INTO hr_monthly_hires (month, count)
        SELECT 
            TO_CHAR(hire_date, 'YYYY-MM') AS month,
            COUNT(*) AS count
        FROM hr_employees
        GROUP BY month
        ORDER BY month;
        '''
    )

    truncate_metrics >> calculate_metrics