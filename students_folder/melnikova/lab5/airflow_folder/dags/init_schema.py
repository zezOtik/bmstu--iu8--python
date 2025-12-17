from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

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
    'init_hospital_schema',
    default_args=default_args,
    description='Инициализация схемы для медицинской клиники',
    schedule=None,
    catchup=False,
    tags=['hospital', 'init']
)

start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

# Создание схемы hospital
create_schema = SQLExecuteQueryOperator(
    task_id='create_hospital_schema',
    conn_id='postgres_default',
    sql="""
    CREATE SCHEMA IF NOT EXISTS hospital;
    """,
    dag=dag
)

# Создание таблицы visits
create_visits_table = SQLExecuteQueryOperator(
    task_id='create_visits_table',
    conn_id='postgres_default',
    sql="""
    CREATE TABLE IF NOT EXISTS hospital.visits (
        visit_id BIGINT PRIMARY KEY,
        patient_id BIGINT NOT NULL,
        doctor_id BIGINT NOT NULL,
        visit_date DATE NOT NULL,
        diagnosis TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    dag=dag
)

# Создание таблицы для метрик
create_metrics_table = SQLExecuteQueryOperator(
    task_id='create_metrics_table',
    conn_id='postgres_default',
    sql="""
    CREATE TABLE IF NOT EXISTS hospital.metrics (
        metric_id SERIAL PRIMARY KEY,
        metric_name VARCHAR(100) NOT NULL,
        metric_value JSONB,
        calculation_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    dag=dag
)

# Создание индексов для производительности
create_indexes = SQLExecuteQueryOperator(
    task_id='create_indexes',
    conn_id='postgres_default',
    sql="""
    CREATE INDEX IF NOT EXISTS idx_visits_date ON hospital.visits(visit_date);
    CREATE INDEX IF NOT EXISTS idx_visits_patient ON hospital.visits(patient_id);
    CREATE INDEX IF NOT EXISTS idx_visits_doctor ON hospital.visits(doctor_id);
    CREATE INDEX IF NOT EXISTS idx_metrics_date ON hospital.metrics(calculation_date);
    """,
    dag=dag
)

# Определение порядка выполнения задач
start >> create_schema >> create_visits_table >> create_metrics_table >> create_indexes >> end