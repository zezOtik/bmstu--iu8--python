from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from airflow.operators.python import PythonOperator


# def req_cbr(**kwargs):
#     print(kwargs)
#
#     # dttm = context.get("logical_date").strftime('%d/%m/%Y')
#     # import requests
#     # url = r"https://cbr.ru/scripts/XML_daily.asp?date_req=" + str(dttm)
#     # answer = requests.get(url=url)
#     # answer = '123456'
#     # print(kwargs)
#     # ti = kwargs["ti"]
#     # ti.xcom_push("xml_req", answer)
#
#     task = kwargs.get("task")
#     render_params = task.render_template(kwargs['params'], kwargs, task.get_template_env())
#     print(render_params)
#
#
# def result(ti):
#     status = ti.xcom_pull(key="xml_req")
#     print(ti)
#     print(status)
#     if status == 0:
#         print("Not ok")


def my_python_function(test_date, greeting="Hello"):
    print(f"{greeting}, {test_date}!")

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


with DAG(dag_id='render_context', # важный атрибут
         default_args=ARGS,
         schedule_interval='0 7 * * *',
         max_active_runs=1,
         catchup=False) as dag:

    t_1 = PythonOperator(
        task_id='render_context',
        dag=dag,
        python_callable=my_python_function,
        op_kwargs={
            "test_date": "{{ logical_date.replace(day=1).strftime('%d/%m/%Y') }}",
            "another_date": "{{ ds }}",
            "pop": "123123"
        }
    )

    run = t_1