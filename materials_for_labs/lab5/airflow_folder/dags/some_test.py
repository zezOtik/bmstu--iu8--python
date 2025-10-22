from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from airflow.operators.python import PythonOperator


def ty_tyt():
    print("ya tochno tyt")
    pass


def print_text():
    print("ya tyt")
    ty_tyt()
    pass


ARGS = {
    "owner": "bmstu",
    "email": ['wzomzot@hop.ru','1@mail.ru'],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 3, 20), # важный атрибут
    "pool": "default_pool",
    "queue": "default"
}


with DAG(dag_id='dag_for_others', # важный атрибут
         default_args=ARGS,
         schedule_interval='0 7 * * *',
         max_active_runs=1,
         catchup=True) as dag:

    t1 = EmptyOperator(
        task_id='start',
        dag=dag
    )

    t2 = EmptyOperator(
        task_id='start_2',
        dag=dag
    )

    t3 = EmptyOperator(
        task_id='start_3',
        dag=dag
    )

    t4 = EmptyOperator(
        task_id='start_4',
        dag=dag
    )

    t5 = BashOperator(
        task_id='my_bash_task',
        bash_command="echo Hello_world {{ ds }}",
        dag=dag
    )

    t6 = PythonOperator(
        task_id='my_python_operator',
        dag=dag,
        python_callable=print_text
    )

    run = t6 << t5 << t1 << [t2, t3] << t4