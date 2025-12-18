from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta

default_args = {
    'owner': 'MelnikovaAlisa',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def init_schema_with_context(**context):
    """
    Инициализация схемы hospital с использованием даты из контекста DAG run

    Параметры из контекста:
    - execution_date: фактическая дата выполнения DAG
    - logical_date: логическая дата (для расписания)
    - dag_run.run_id: уникальный ID запуска DAG
    - ds: дата выполнения в формате YYYY-MM-DD
    """

    # Получаем параметры из контекста DAG run
    execution_date = context['execution_date']
    logical_date = context['logical_date']
    dag_run_id = context['dag_run'].run_id
    ds = context['ds']  # Дата выполнения в формате YYYY-MM-DD

    print("=" * 60)
    print("ИНИЦИАЛИЗАЦИЯ СХЕМЫ HOSPITAL С КОНТЕКСТОМ")
    print("=" * 60)

    print(f" Параметры из контекста DAG run:")
    print(f"   • Execution Date: {execution_date}")
    print(f"   • Logical Date: {logical_date}")
    print(f"   • DAG Run ID: {dag_run_id}")
    print(f"   • DS (дата): {ds}")

    # Используем дату из контекста для именования
    date_suffix = ds.replace('-', '')  # 2024-01-15 -> 20240115

    hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = hook.get_conn()
    conn.autocommit = True
    cursor = conn.cursor()

    # 1. Создаем основную схему hospital
    print(f"\n1. Создаем схему 'hospital'...")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS hospital;")

    # 2. Создаем таблицу visits с дополнительными полями для отслеживания DAG run
    print(f"2. Создаем таблицу 'visits'...")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS hospital.visits (
            visit_id BIGINT PRIMARY KEY,
            patient_id BIGINT NOT NULL,
            doctor_id BIGINT NOT NULL,
            visit_date DATE NOT NULL,
            diagnosis TEXT,
            dag_run_id VARCHAR(100) DEFAULT '{dag_run_id}',
            execution_date TIMESTAMP DEFAULT '{execution_date}',
            logical_date DATE DEFAULT '{logical_date.date()}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 3. Создаем таблицу metrics с привязкой к DAG run
    print(f"3. Создаем таблицу 'metrics'...")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS hospital.metrics (
            metric_id SERIAL PRIMARY KEY,
            metric_name VARCHAR(100) NOT NULL,
            metric_value TEXT,
            calculation_date DATE NOT NULL,
            dag_run_id VARCHAR(100) DEFAULT '{dag_run_id}',
            execution_date TIMESTAMP DEFAULT '{execution_date}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 4. Создаем таблицу для отслеживания инициализаций по дате
    print(f"4. Создаем таблицу 'schema_init_log'...")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS hospital.schema_init_log (
            init_id SERIAL PRIMARY KEY,
            dag_run_id VARCHAR(100) NOT NULL,
            execution_date TIMESTAMP NOT NULL,
            logical_date DATE NOT NULL,
            schema_version VARCHAR(20) DEFAULT '1.0',
            init_date DATE DEFAULT '{logical_date.date()}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_dag_run UNIQUE(dag_run_id)
        );
    """)

    # 5. Записываем лог инициализации
    cursor.execute("""
        INSERT INTO hospital.schema_init_log 
        (dag_run_id, execution_date, logical_date)
        VALUES (%s, %s, %s)
        ON CONFLICT (dag_run_id) 
        DO UPDATE SET 
            execution_date = EXCLUDED.execution_date,
            created_at = CURRENT_TIMESTAMP
    """, (dag_run_id, execution_date, logical_date.date()))

    # 6. Создаем индексы
    print(f"5. Создаем индексы...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_visits_date ON hospital.visits(visit_date);
        CREATE INDEX IF NOT EXISTS idx_visits_patient ON hospital.visits(patient_id);
        CREATE INDEX IF NOT EXISTS idx_visits_doctor ON hospital.visits(doctor_id);
        CREATE INDEX IF NOT EXISTS idx_metrics_date ON hospital.metrics(calculation_date);
        CREATE INDEX IF NOT EXISTS idx_visits_dag_run ON hospital.visits(dag_run_id);
        CREATE INDEX IF NOT EXISTS idx_metrics_dag_run ON hospital.metrics(dag_run_id);
    """)

    # 7. Проверяем созданные таблицы
    cursor.execute("""
        SELECT 
            table_name,
            table_type
        FROM information_schema.tables 
        WHERE table_schema = 'hospital'
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()

    print(f"\n Созданы таблицы в схеме 'hospital':")
    for table_name, table_type in tables:
        print(f"   • {table_name} ({table_type})")

    # 8. Проверяем запись в логе
    cursor.execute("""
        SELECT 
            COUNT(*) as table_count,
            MAX(created_at) as last_init
        FROM hospital.schema_init_log;
    """)

    log_info = cursor.fetchone()

    print(f"\n Статистика инициализации:")
    print(f"   Всего инициализаций: {log_info[0]}")
    print(f"   Последняя инициализация: {log_info[1]}")

    cursor.close()
    conn.close()

    print(f"\n" + "=" * 60)
    print(f" ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА С ИСПОЛЬЗОВАНИЕМ КОНТЕКСТА")
    print("=" * 60)
    print(f"DAG Run ID: {dag_run_id}")
    print(f"Execution Date: {execution_date}")
    print(f"Logical Date: {logical_date}")
    print(f"Init Date: {ds}")

    return {
        'status': 'success',
        'dag_run_id': dag_run_id,
        'execution_date': str(execution_date),
        'logical_date': str(logical_date),
        'tables_created': len(tables),
        'init_timestamp': str(datetime.now())
    }


# Создаем DAG
dag = DAG(
    'init_hospital_schema_context',
    default_args=default_args,
    description='Инициализация схемы с использованием даты из контекста DAG run',
    schedule=None,
    catchup=False,
    tags=['hospital', 'init', 'context']
)

# Определяем задачи
start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

# Единственная задача - PythonOperator, который принимает контекст
init_schema_task = PythonOperator(
    task_id='init_schema_with_context',
    python_callable=init_schema_with_context,
    provide_context=True,  # Ключевой параметр! Передает контекст DAG run
    dag=dag
)

# Определение порядка выполнения задач
start >> init_schema_task >> end