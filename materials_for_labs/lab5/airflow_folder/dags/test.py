from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime


with DAG(dag_id='dag_demo', # важный атрибут
         schedule_interval='0 7 * * *',
         max_active_runs=1,
         start_date=datetime(2025, 3, 20), # важный атрибут
         catchup=True) as dag:

    task_1 = EmptyOperator(task_id='dummy_task_1')

    task_2 = EmptyOperator(task_id='dummy_task_2')

    task_3 = EmptyOperator(task_id='dummy_task_3')

    task_4 = EmptyOperator(task_id='dummy_task_4')

    task_5 = EmptyOperator(task_id='dummy_task_5')

    task_dummy = EmptyOperator(task_id='task_dummy')

    run = task_1 >> [ task_2, task_3 ] >> task_dummy >> [ task_4, task_5]