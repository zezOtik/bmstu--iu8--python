from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, text

ARGS = {
    "owner": "bmstu",
    "email": ['wzomzot@hop.ru','1@mail.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 3, 20),
    "pool": "default_pool",
    "queue": "default"
}

def calculate_metric(**kwargs):
    execution_date = kwargs['logical_date'].date()
    print(f"Расчет метрики для даты: {execution_date}")
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")
    calc_query = """
    SELECT ed_tech.get_unique_users_by_date(:input_date) AS unique_users;
    """
    with engine.connect() as conn:
        result = conn.execute(text(calc_query), {"input_date": execution_date})
        unique_users = result.scalar()

    print(f"Количество уникальных пользователей за {execution_date}: {unique_users}")
    kwargs['ti'].xcom_push(key='metric_result', value=unique_users)

with DAG(
    dag_id='calculate_metrics_variant5',
    default_args=ARGS,
    schedule_interval='0 8 * * *',
    max_active_runs=1,
    start_date=datetime(2025, 3, 20),
    catchup=True,
    tags=['lab5', 'variant5']
) as dag:

    t_calculate_metric = PythonOperator(
        task_id='calculate_metric',
        python_callable=calculate_metric,
        provide_context=True
    )
