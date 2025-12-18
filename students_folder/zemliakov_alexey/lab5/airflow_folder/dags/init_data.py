from datetime import datetime, timedelta
import random
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import math

# Параметры по умолчанию для DAG
DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def generate_employees_chunk(**context):
    execution_date = context['ds']
    task_id = context['task_instance'].task_id
    task_number = int(task_id.split('_')[-1])

    params = context['params']
    num_employees = params.get('num_employees', 10000)
    num_chunks = params.get('num_chunks', 10)
    min_hire_date_str = context['templates_dict']['min_hire_date']
    max_hire_date_str = context['templates_dict']['max_hire_date']

    chunk_size = math.ceil(num_employees / num_chunks)
    start_idx = task_number * chunk_size + 1
    end_idx = min((task_number + 1) * chunk_size, num_employees)

    print(f"Запуск задачи {task_id} для генерации записей {start_idx} - {end_idx}")
    print(f"Диапазон дат приема на работу: с {min_hire_date_str} по {max_hire_date_str}")

    male_first_names = ['Иван', 'Петр', 'Сидор', 'Алексей', 'Дмитрий', 'Сергей',
                        'Михаил', 'Андрей', 'Николай', 'Василий', 'Александр', 'Максим',
                        'Евгений', 'Владимир', 'Борис', 'Георгий', 'Станислав', 'Роман',
                        'Павел', 'Константин', 'Виктор', 'Игорь', 'Артем', 'Даниил']

    female_first_names = ['Мария', 'Анна', 'Екатерина', 'Ольга', 'Наталья', 'Светлана',
                          'Татьяна', 'Елена', 'Юлия', 'Ирина', 'Анастасия', 'Дарья',
                          'Полина', 'Виктория', 'Ксения', 'Александра', 'Маргарита', 'Валерия',
                          'Алина', 'Зоя', 'Людмила', 'Вера', 'Раиса', 'Марина']

    last_names_male = ['Иванов', 'Петров', 'Сидоров', 'Козлов', 'Смирнов', 'Попов',
                       'Лебедев', 'Новиков', 'Морозов', 'Волков', 'Соколов', 'Белов',
                       'Михайлов', 'Федоров', 'Алексеев', 'Дмитриев', 'Сергеев', 'Егоров',
                       'Степанов', 'Николаев', 'Григорьев', 'Ильин', 'Орлов', 'Титов']

    last_names_female = ['Иванова', 'Петрова', 'Сидорова', 'Козлова', 'Смирнова', 'Попова',
                         'Лебедева', 'Новикова', 'Морозова', 'Волкова', 'Соколова', 'Белова',
                         'Михайлова', 'Федорова', 'Алексеева', 'Дмитриева', 'Сергеева', 'Егорова',
                         'Степанова', 'Николаева', 'Григорьева', 'Ильина', 'Орлова', 'Титова']

    departments = [
        'Engineering', 'Data Science', 'Machine Learning',
        'Marketing', 'Digital Marketing', 'Content Marketing',
        'Sales', 'Enterprise Sales', 'Inside Sales',
        'HR', 'Talent Acquisition', 'Employee Relations',
        'Finance', 'Accounting', 'Financial Planning',
        'Legal', 'Compliance', 'Intellectual Property',
        'Support', 'Customer Success', 'Technical Support',
        'Product', 'Product Management', 'Product Design',
        'Operations', 'Logistics', 'Quality Assurance'
    ]

    min_hire_date = datetime.strptime(min_hire_date_str, '%Y-%m-%d')
    max_hire_date = datetime.strptime(max_hire_date_str, '%Y-%m-%d')

    max_allowed_date = datetime(2025, 12, 31)
    if max_hire_date > max_allowed_date:
        max_hire_date = max_allowed_date

    pg_hook = PostgresHook(postgres_conn_id='airflow_db')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    total_inserted = 0

    for i in range(start_idx, end_idx + 1):
        is_male = random.choice([True, False])

        if is_male:
            first_name = random.choice(male_first_names)
            last_name = random.choice(last_names_male)
        else:
            first_name = random.choice(female_first_names)
            last_name = random.choice(last_names_female)

        full_name = f"{first_name} {last_name}"
        department = random.choice(departments)

        time_between_dates = max_hire_date - min_hire_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates + 1)
        hire_date = min_hire_date + timedelta(days=random_number_of_days)

        cursor.execute("""
            INSERT INTO hr_employees (id, name, department, hire_date)
            VALUES (%s, %s, %s, %s)
        """, (i, full_name, department, hire_date))

        total_inserted += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Задача {task_id} завершена. Вставлено {total_inserted} записей.")
    return f"Задача {task_id} завершена. Вставлено {total_inserted} записей."


with DAG(
        dag_id='init_data_parallel',
        default_args=DEFAULT_ARGS,
        description='Параллельная генерация данных о сотрудниках',
        schedule_interval='@once',
        start_date=days_ago(1),
        catchup=False,
        tags=['data_generation', 'hr', 'parallel'],
        params={
            'num_employees': 10000,
            'num_chunks': 10
        }
) as dag:
    clear_table = PythonOperator(
        task_id='clear_table',
        python_callable=lambda **context: PostgresHook(postgres_conn_id='airflow_db') \
            .get_conn().cursor().execute("TRUNCATE TABLE hr_employees RESTART IDENTITY CASCADE;")
    )

    with TaskGroup("generate_data_chunks") as generate_data_chunks:
        num_chunks = dag.params['num_chunks']

        for i in range(num_chunks):
            PythonOperator(
                task_id=f'generate_chunk_{i}',
                python_callable=generate_employees_chunk,
                op_kwargs={
                    "chunk_number": i,
                    "min_hire_date": "{{ macros.datetime(2018, 1, 1).strftime('%Y-%m-%d') }}",
                    "max_hire_date": "{{ ds }}"
                },
                templates_dict={
                    "min_hire_date": "{{ macros.datetime(2018, 1, 1).strftime('%Y-%m-%d') }}",
                    "max_hire_date": "{{ ds }}"
                }
            )

    check_results = PythonOperator(
        task_id='check_results',
        python_callable=lambda **context: print(
            f"Проверка результатов для {context['params']['num_employees']} записей"),
        trigger_rule='all_success'
    )

    clear_table >> generate_data_chunks >> check_results