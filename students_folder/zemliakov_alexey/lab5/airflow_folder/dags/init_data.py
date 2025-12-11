from datetime import datetime, timedelta
import random
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


def generate_random_employees(**context):
    num_employees = 10000  # Количество сотрудников для генерации
    batch_size = 1000  # Размер пакета для вставки

    # Списки для генерации случайных данных
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

    start_date = datetime(2018, 1, 1)
    end_date = datetime(2023, 12, 31)

    # Подключение к БД
    pg_hook = PostgresHook(postgres_conn_id='airflow_db')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    # Очистка таблицы перед вставкой
    cursor.execute("TRUNCATE TABLE hr_employees RESTART IDENTITY CASCADE;")

    total_inserted = 0

    # Генерация и вставка данных пакетами
    for batch_start in range(1, num_employees + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, num_employees)
        batch_data = []

        for i in range(batch_start, batch_end + 1):
            # Случайный выбор пола для генерации имени
            is_male = random.choice([True, False])

            if is_male:
                first_name = random.choice(male_first_names)
                last_name = random.choice(last_names_male)
            else:
                first_name = random.choice(female_first_names)
                last_name = random.choice(last_names_female)

            full_name = f"{first_name} {last_name}"
            department = random.choice(departments)

            # Генерация случайной даты приема на работу
            time_between_dates = end_date - start_date
            days_between_dates = time_between_dates.days
            random_number_of_days = random.randrange(days_between_dates)
            hire_date = start_date + timedelta(days=random_number_of_days)

            batch_data.append((i, full_name, department, hire_date))

        # Вставка батчами
        args_str = b','.join(
            cursor.mogrify("(%s,%s,%s,%s)", x) for x in batch_data
        )
        cursor.execute(b"INSERT INTO hr_employees (id, name, department, hire_date) VALUES " + args_str)
        conn.commit()

        total_inserted += len(batch_data)
        print(f"Вставлен пакет записей с {batch_start} по {batch_end} ({len(batch_data)} записей)")

    cursor.close()
    conn.close()

    print(f"Всего вставлено записей: {total_inserted}")
    return f"Успешно сгенерировано и вставлено {total_inserted} записей о сотрудниках"


with DAG(
        'init_data',
        start_date=datetime(2023, 1, 1),
        schedule_interval='@once',
        catchup=False,
        description='Генерация случайных данных о сотрудниках (10 000 записей)',
        tags=['data_generation', 'hr']
) as dag:
    generate_data = PythonOperator(
        task_id='generate_random_employees',
        python_callable=generate_random_employees,
        provide_context=True
    )