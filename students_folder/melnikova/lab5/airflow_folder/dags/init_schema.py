from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import psycopg2

default_args = {
    'owner': 'MelnikovaAlisa',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def init_schema_incremental(**kwargs):
    """
    Инициализация схемы hospital с использованием даты из контекста
    """
    # Получаем дату из контекста
    execution_date = kwargs['logical_date'].date()
    dag_run_id = kwargs['dag_run'].run_id

    print("=" * 60)
    print(f"ИНИЦИАЛИЗАЦИЯ СХЕМЫ HOSPITAL")
    print("=" * 60)
    print(f" Дата из контекста DAG run: {execution_date}")
    print(f" DAG Run ID: {dag_run_id}")

    # Подключаемся к PostgreSQL
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        dbname='airflow',
        user='airflow',
        password='airflow'
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Проверяем, существует ли уже схема для этой даты
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1 FROM information_schema.schemata 
            WHERE schema_name = 'hospital'
        );
    """)
    schema_exists = cursor.fetchone()[0]

    if not schema_exists:
        print("1. Создаем схему 'hospital'...")
        cursor.execute("CREATE SCHEMA hospital;")
    else:
        print("1. Схема 'hospital' уже существует")

    # Создаем таблицу visits с датой из контекста
    print("2. Создаем/проверяем таблицу 'visits'...")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS hospital.visits (
            visit_id BIGINT PRIMARY KEY,
            patient_id BIGINT NOT NULL,
            doctor_id BIGINT NOT NULL,
            visit_date DATE NOT NULL,
            diagnosis TEXT,
            -- Добавляем поля для отслеживания как у коллеги
            dag_run_date DATE DEFAULT '{execution_date}',
            dag_run_id VARCHAR(100) DEFAULT '{dag_run_id}',
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Создаем таблицу metrics с датой из контекста
    print("3. Создаем/проверяем таблицу 'metrics'...")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS hospital.metrics (
            metric_id SERIAL PRIMARY KEY,
            metric_name VARCHAR(100) NOT NULL,
            metric_value TEXT,
            calculation_date DATE NOT NULL DEFAULT '{execution_date}',
            dag_run_date DATE DEFAULT '{execution_date}',
            dag_run_id VARCHAR(100) DEFAULT '{dag_run_id}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Создаем индексы
    print("4. Создаем индексы...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_visits_date ON hospital.visits(visit_date);
        CREATE INDEX IF NOT EXISTS idx_visits_dag_date ON hospital.visits(dag_run_date);
    """)

    # Логируем инициализацию для этой даты
    print("5. Логируем инициализацию...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospital.init_log (
            log_id SERIAL PRIMARY KEY,
            init_date DATE NOT NULL,
            dag_run_id VARCHAR(100) NOT NULL,
            schema_created BOOLEAN DEFAULT TRUE,
            tables_created INTEGER,
            init_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        INSERT INTO hospital.init_log 
        (init_date, dag_run_id, schema_created, tables_created)
        VALUES (%s, %s, %s, %s)
    """, (execution_date, dag_run_id, True, 2))

    # Проверяем результат
    cursor.execute("""
        SELECT COUNT(*) FROM hospital.init_log 
        WHERE init_date = %s
    """, (execution_date,))

    log_count = cursor.fetchone()[0]

    print(f"\n Инициализация завершена для даты: {execution_date}")
    print(f" Статистика:")
    print(f"   • Дата DAG run: {execution_date}")
    print(f"   • DAG Run ID: {dag_run_id}")
    print(f"   • Записей в логе: {log_count}")

    cursor.close()
    conn.close()

    return f"init_completed_for_{execution_date}"


# Создаем DAG
dag = DAG(
    'init_hospital_schema_incremental',
    default_args=default_args,
    description='Инициализация схемы hospital с датой из контекста DAG run',
    schedule_interval='0 0 * * *',  # Ежедневно в полночь
    catchup=True,  # Запускать пропущенные DAG runs
    tags=['hospital', 'init', 'incremental']
)

# Определяем задачи
start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

init_schema_task = PythonOperator(
    task_id='init_schema_incremental',
    python_callable=init_schema_incremental,
    provide_context=True,
    dag=dag
)

# Порядок выполнения
start >> init_schema_task >> end