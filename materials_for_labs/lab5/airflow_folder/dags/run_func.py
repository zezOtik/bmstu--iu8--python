from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator


ARGS = {
    "owner": "bmstu",
    "email": ['wzomzot@hop.ru','1@mail.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "pool": "default_pool",
    "queue": "default"
}


def run_func(run_date: str):
    import os
    import csv
    from sqlalchemy import create_engine, text

    csv_file_path = "/opt/airflow/dags/input_data/input_data.csv"

    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV файл не найден: {csv_file_path}")

    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    filtered_records = []
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            if len(row) < 4:
                continue
            name, department, salary, invited_date = row[0], row[1], row[2], row[3]

            if invited_date == run_date:
                filtered_records.append((name, department, salary, invited_date))

    if not filtered_records:
        print(f"Нет записей в CSV с invited_date = {run_date}")
        return

    data = [
        {
            "name": r[0],
            "department": r[1],
            "salary": r[2],
            "invited_date": r[3]
        }
        for r in filtered_records
    ]

    # Вставка в БД
    with engine.connect() as conn:
        stmt = text("""
            INSERT INTO super_job.employees (name, department, salary, invited_date)
            VALUES (:name, :department, :salary, :invited_date)
        """)
        conn.execute(stmt, data)

    print(f"Успешно вставлено {len(data)} записей с invited_date = {run_date}")

with DAG(dag_id='insert_data_dag',
         default_args=ARGS,
         schedule_interval='0 7 * * *',
         max_active_runs=1,
         start_date=datetime(2025, 1, 1),
         catchup=True,
         tags=['lab5']) as dag:

    t_run_func = PythonOperator(
        task_id='insert_data',
        dag=dag,
        python_callable=run_func,
        op_kwargs={"run_date": "{{ ds }}"}
    )

    run = t_run_func
