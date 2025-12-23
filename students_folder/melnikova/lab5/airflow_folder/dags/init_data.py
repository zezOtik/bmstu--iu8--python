from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import random

default_args = {
    'owner': 'Melnikova_Alisa',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'init_hospital_data',
    default_args=default_args,
    description='Загрузка тестовых данных в таблицу hospital.visits',
    schedule=None,
    catchup=False,
    tags=['hospital', 'data_load']
)

start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

# Очистка существующих данных (опционально)
clear_data = SQLExecuteQueryOperator(
    task_id='clear_existing_data',
    conn_id='postgres_default',
    sql="DELETE FROM hospital.visits;",
    dag=dag
)


# Функция для генерации тестовых данных
def generate_test_data_sql():
    """Генерирует SQL для вставки тестовых данных"""
    sql = "INSERT INTO hospital.visits (visit_id, patient_id, doctor_id, visit_date, diagnosis) VALUES\n"

    values = []
    visit_id = 1

    # Создаем данные для 30 дней
    base_date = datetime(2024, 1, 1).date()

    # Генерация данных с разным количеством визитов в день
    for day_offset in range(30):
        current_date = base_date + timedelta(days=day_offset)

        # Разное количество визитов в разные дни
        if day_offset % 7 == 0:  # Воскресенье - мало визитов
            num_visits = 2
        elif day_offset % 7 == 6:  # Суббота - среднее количество
            num_visits = 4
        else:  # Будни - много визитов
            num_visits = random.randint(3, 10)

        # Создаем специально день с ровно 5 визитами
        if day_offset == 10:  # 11 января будет иметь ровно 5 визитов
            num_visits = 5
        elif day_offset == 20:  # 21 января тоже будет иметь ровно 5 визитов
            num_visits = 5

        for i in range(num_visits):
            patient_id = random.randint(1000, 1100)
            doctor_id = random.randint(1, 10)

            # Список возможных диагнозов
            diagnoses = [
                "Грипп",
                "ОРВИ",
                "Гипертония",
                "Диабет",
                "Астма",
                "Аллергия",
                "Травма",
                "Консультация",
                "Обследование",
                "Вакцинация"
            ]

            diagnosis = random.choice(diagnoses)

            values.append(f"({visit_id}, {patient_id}, {doctor_id}, '{current_date}', '{diagnosis}')")
            visit_id += 1

    sql += ",\n".join(values) + ";"
    return sql


# Динамическая задача для загрузки данных
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


def load_test_data(**context):
    """Загружает тестовые данные в таблицу"""
    hook = PostgresHook(postgres_conn_id='postgres_default')
    sql = generate_test_data_sql()

    # Выполняем SQL
    hook.run(sql)

    # Логируем количество загруженных записей
    count_sql = "SELECT COUNT(*) FROM hospital.visits;"
    count = hook.get_first(count_sql)[0]
    print(f"Загружено {count} записей в таблицу hospital.visits")

    return count


load_data_task = PythonOperator(
    task_id='load_test_data',
    python_callable=load_test_data,
    dag=dag,
)

# Проверка загруженных данных
verify_data = SQLExecuteQueryOperator(
    task_id='verify_data_load',
    conn_id='postgres_default',
    sql="""
    SELECT 
        COUNT(*) as total_visits,
        MIN(visit_date) as first_date,
        MAX(visit_date) as last_date
    FROM hospital.visits;
    """,
    dag=dag
)

# Определение порядка выполнения задач
start >> clear_data >> load_data_task >> verify_data >> end