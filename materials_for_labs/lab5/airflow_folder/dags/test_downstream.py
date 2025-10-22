from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from airflow.operators.python import PythonOperator


ARGS = {
    "owner": "bmstu",
    "email": ['wzomzot@hop.ru','1@mail.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 3, 20), # важный атрибут
    "pool": "default_pool",
    "queue": "default"
}

PARAMS = {
    "start_date": "{{ ds }}"
}


with DAG(dag_id='test_downstream', # важный атрибут
         default_args=ARGS,
         schedule_interval='0 7 * * *',
         max_active_runs=1,
         start_date=datetime(2025, 3, 20),
         catchup=False) as dag:

    t_1 = EmptyOperator(task_id='1', dag=dag)

    t_2 = EmptyOperator(task_id='2', dag=dag)

    t5 = BashOperator(
        task_id='my_bash_task',
        bash_command="echo Hello_world {{ ds }}",
        dag=dag
    )

    run = t_1 >> t_2 >> t5