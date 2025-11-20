import csv
from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, text


ARGS = {
    "owner": "Zhukova_Mariya",
    "email": ['test_user_var_2@email.ru','2@email.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 11, 20),
    "pool": "default_pool",
    "queue": "default"
}

CSV_FILE_PATH = '/opt/airflow/dags/sales_data.csv'

def truncate_table():
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    truncate_table_query = "TRUNCATE TABLE market.sales;"

    with engine.connect() as conn:
        conn.execute(text(truncate_table_query))

    print("Таблица 'sales' очищена!")


def init_sales():
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")

    rows_to_insert = []
    with open(CSV_FILE_PATH, 'r') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            id = int(row[0])
            product_name = row[1]
            sale_date = row[2]
            amount = float(row[3])

            rows_to_insert.append({
                'id': id, 
                'product_name': product_name, 
                'sale_date': sale_date, 
                'amount': amount
            })

    insert_data_query = """
        INSERT INTO market.sales (id, product_name, sale_date, amount) 
        VALUES (:id, :product_name, :sale_date, :amount)
    """
    
    with engine.connect() as conn:
        conn.execute(text(insert_data_query), rows_to_insert)

    print(f"Таблица 'sales' наполнена {len(rows_to_insert)} записями!")


with DAG(dag_id='init_data',
         default_args=ARGS,
         schedule_interval='@once',
         max_active_runs=1,
         start_date=datetime(2025, 3, 20),
         catchup=True,
         tags=['lab5']) as dag:

    t_truncate_table = PythonOperator(
        task_id='truncate_table',
        dag=dag,
        python_callable=truncate_table
    )

    t_insert_data = PythonOperator(
        task_id='insert_data',
        dag=dag,
        python_callable=init_sales
    )

    run = t_truncate_table >> t_insert_data