from datetime import datetime, timedelta
import random
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
import math

# Параметры DAG по умолчанию
DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Список аэропортов мира (коды IATA)
AIRPORTS = [
    'SVO', 'JFK', 'LHR', 'CDG', 'FRA', 'NRT', 'PEK', 'SYD', 'DXB', 'SIN',
    'AMS', 'HKG', 'LAX', 'ORD', 'MAD', 'FCO', 'IST', 'GRU', 'YYZ', 'BOM'
]

def generate_transfers_chunk(**context):
    """
    Генерирует порцию данных о рейсах.
    
    Параметры из контекста:
    - chunk_number: номер текущей порции
    - total_flights: общее количество рейсов для генерации
    - min_date/max_date: диапазон дат для генерации
    """
    task_id = context['task_instance'].task_id
    chunk_number = int(task_id.split('_')[-1])
    
    params = context['params']
    total_flights = params['total_flights']
    num_chunks = params['num_chunks']
    min_date_str = context['templates_dict']['min_date']
    max_date_str = context['templates_dict']['max_date']

    # Рассчитываем границы для текущей порции данных
    chunk_size = math.ceil(total_flights / num_chunks)
    start_idx = chunk_number * chunk_size + 1
    end_idx = min((chunk_number + 1) * chunk_size, total_flights)

    # Парсим даты
    min_date = datetime.strptime(min_date_str, '%Y-%m-%d')
    max_date = datetime.strptime(max_date_str, '%Y-%m-%d')
    max_allowed_date = datetime(2025, 12, 31)
    max_date = min(max_date, max_allowed_date)

    # Подключаемся к базе данных
    pg_hook = PostgresHook(postgres_conn_id='airflow_db')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    inserted_count = 0
    # Генерируем рейсы для текущей порции
    for flight_id in range(start_idx, end_idx + 1):
        # Выбираем случайные аэропорты (отправления и назначения)
        origin = random.choice(AIRPORTS)
        destination = random.choice(AIRPORTS)
        # Убеждаемся, что аэропорты отправления и прибытия разные
        while destination == origin:
            destination = random.choice(AIRPORTS)
        
        # Генерируем случайную дату отправления в заданном диапазоне
        days_range = (max_date - min_date).days
        departure_date = min_date + timedelta(days=random.randint(0, days_range))
        
        # Генерируем длительность перелёта (от 1 до 48 часов)
        flight_duration = timedelta(hours=random.randint(1, 48))
        arrival_datetime = departure_date + flight_duration
        arrival_date = arrival_datetime.date()
        
        # Вставляем данные в таблицу
        cursor.execute("""
            INSERT INTO logistic.transfers (id, "from", "to", departure_date, arriving_date)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (flight_id, origin, destination, departure_date, arrival_date))
        
        inserted_count += 1

    # Фиксируем изменения и закрываем соединение
    conn.commit()
    cursor.close()
    conn.close()
    
    # Сохраняем количество вставленных записей для логирования
    context['ti'].xcom_push(key=f'chunk_{chunk_number}_count', value=inserted_count)
    return f"Вставлено {inserted_count} рейсов в порции {chunk_number}"

with DAG(
    dag_id='init_airline_data',
    default_args=DEFAULT_ARGS,
    description='Генерация тестовых данных о рейсах авиакомпании',
    schedule_interval='@once',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['авиакомпания', 'генерация-данных'],
    params={
        'total_flights': 10000,  # Общее количество рейсов для генерации
        'num_chunks': 10          # Количество параллельных задач
    }
) as dag:

    # Очищаем таблицу перед вставкой новых данных
    clear_table = PythonOperator(
        task_id='clear_transfers_table',
        python_callable=lambda: PostgresHook(postgres_conn_id='airflow_db')
            .run("TRUNCATE TABLE logistic.transfers RESTART IDENTITY CASCADE;")
    )

    # Генерируем данные параллельно в нескольких задачах
    with TaskGroup("generate_flight_chunks") as generate_chunks:
        for i in range(dag.params['num_chunks']):
            PythonOperator(
                task_id=f'generate_chunk_{i}',
                python_callable=generate_transfers_chunk,
                templates_dict={
                    'min_date': '{{ macros.datetime(2020, 1, 1).strftime("%Y-%m-%d") }}',
                    'max_date': '{{ ds }}'
                }
            )

    # Определяем порядок выполнения задач
    clear_table >> generate_chunks