from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, text
import csv
import os

ARGS = {
    "owner": "bmstu",
    "email": ['wzomzot@hop.ru','1@mail.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 3, 20),
    "pool": "default_pool",
    "queue": "default"
}

def load_data_incremental(**kwargs):
    execution_date = kwargs['logical_date'].date()
    print(f"Загрузка данных для даты: {execution_date}")

    csv_file_path = "/opt/airflow/dags/input_data/input_data.csv"
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV файл не найден: {csv_file_path}")
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")
    filtered_records = []
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Пропуск заголовка
        for row in reader:
            if len(row) < 3:
                continue
            user_id, course_name, completion_date_str = row[0], row[1], row[2]
            try:
                completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
            except ValueError:
                continue  # Пропуск некорректных дат

            if completion_date == execution_date:
                filtered_records.append((user_id, course_name, completion_date))

    if not filtered_records:
        print(f"Нет записей в CSV с completion_date = {execution_date}")
        return

    data = [
        {
            "user_id": int(r[0]),
            "course_name": r[1],
            "completion_date": r[2]
        }
        for r in filtered_records
    ]

    with engine.connect() as conn:
        stmt = text("""
            INSERT INTO ed_tech.course_completions (user_id, course_name, completion_date)
            VALUES (:user_id, :course_name, :completion_date)
        """)
        conn.execute(stmt, data)
    print(f"Успешно вставлено {len(data)} записей с completion_date = {execution_date}")

with DAG(
    dag_id='load_data_variant5',
    default_args=ARGS,
    schedule_interval='0 7 * * *',
    max_active_runs=1,
    start_date=datetime(2025, 3, 20),
    catchup=True,
    tags=['lab5', 'variant5']
) as dag:

    t_load_data = PythonOperator(
        task_id='load_data_incremental',
        python_callable=load_data_incremental,
        provide_context=True
    )
