from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'MelnikovaAlisa',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'collect_hospital_metrics',
    default_args=default_args,
    description='Расчет метрик для медицинской клиники - даты с ровно 5 визитами',
    schedule='0 0 * * *',  # Ежедневно в полночь
    catchup=False,
    tags=['hospital', 'metrics']
)

start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

# Задача для расчета метрики: даты с ровно 5 визитами
calculate_metrics = SQLExecuteQueryOperator(
    task_id='calculate_five_visits_dates',
    conn_id='postgres_default',
    sql="""
    -- Очистка предыдущей метрики за сегодня
    DELETE FROM hospital.metrics 
    WHERE metric_name = 'dates_with_exactly_5_visits' 
    AND calculation_date =  '{{ ds }}'::DATE;

    -- Поиск дат с ровно 5 визитами
    WITH daily_visits AS (
        SELECT 
            visit_date,
            COUNT(*) as visit_count
        FROM hospital.visits
        GROUP BY visit_date
    ),
    five_visits_dates AS (
        SELECT 
            visit_date,
            visit_count
        FROM daily_visits
        WHERE visit_count = 5
    )
    INSERT INTO hospital.metrics (metric_name, metric_value, calculation_date)
    SELECT 
        'dates_with_exactly_5_visits',
        jsonb_build_object(
            'dates', jsonb_agg(
                jsonb_build_object(
                    'date', visit_date::text,
                    'visit_count', visit_count
                )
            ),
            'total_dates', COUNT(*)
        ),
         '{{ ds }}'::DATE
    FROM five_visits_dates;
    """,
    dag=dag
)

# Дополнительная метрика: общая статистика
calculate_statistics = SQLExecuteQueryOperator(
    task_id='calculate_daily_statistics',
    conn_id='postgres_default',
    sql="""
    -- Очистка предыдущей статистики за сегодня
    DELETE FROM hospital.metrics 
    WHERE metric_name = 'daily_visits_statistics' 
    AND calculation_date = CURRENT_DATE;

    -- Общая статистика по визитам
    WITH daily_stats AS (
        SELECT 
            visit_date,
            COUNT(*) as daily_visits,
            COUNT(DISTINCT patient_id) as unique_patients,
            COUNT(DISTINCT doctor_id) as doctors_involved
        FROM hospital.visits
        GROUP BY visit_date
        ORDER BY visit_date DESC
        LIMIT 30  -- Последние 30 дней
    )
    INSERT INTO hospital.metrics (metric_name, metric_value, calculation_date)
    SELECT 
        'daily_visits_statistics',
        jsonb_build_object(
            'statistics', jsonb_agg(
                jsonb_build_object(
                    'date', visit_date::text,
                    'daily_visits', daily_visits,
                    'unique_patients', unique_patients,
                    'doctors_involved', doctors_involved
                )
            ),
            'avg_daily_visits', ROUND(AVG(daily_visits), 2),
            'max_daily_visits', MAX(daily_visits),
            'min_daily_visits', MIN(daily_visits)
        ),
        CURRENT_DATE
    FROM daily_stats;
    """,
    dag=dag
)


# Python задача для вывода результатов
def display_results(**context):
    """Отображает результаты расчета метрик"""
    hook = PostgresHook(postgres_conn_id='postgres_default')

    # Получаем метрики за сегодня
    sql = """
    SELECT 
        metric_name,
        metric_value->>'total_dates' as total_dates,
        metric_value->'dates' as dates_list
    FROM hospital.metrics 
    WHERE metric_name = 'dates_with_exactly_5_visits' 
    AND calculation_date = CURRENT_DATE;
    """

    results = hook.get_records(sql)

    if results:
        for row in results:
            metric_name, total_dates, dates_list = row
            print(f"\n=== Результаты расчета метрик ===")
            print(f"Метрика: {metric_name}")
            print(f"Количество дат с ровно 5 визитами: {total_dates}")

            # Парсим JSON с датами
            if dates_list:
                dates_data = json.loads(dates_list)
                print("Даты с ровно 5 визитами:")
                for date_info in dates_data:
                    print(f"  - {date_info['date']}: {date_info['visit_count']} визитов")

    # Выводим общую статистику
    stats_sql = """
    SELECT metric_value
    FROM hospital.metrics 
    WHERE metric_name = 'daily_visits_statistics' 
    AND calculation_date = CURRENT_DATE;
    """

    stats_result = hook.get_first(stats_sql)
    if stats_result:
        stats = json.loads(stats_result[0])
        print(f"\n=== Общая статистика ===")
        print(f"Среднее количество визитов в день: {stats['avg_daily_visits']}")
        print(f"Максимальное количество визитов в день: {stats['max_daily_visits']}")
        print(f"Минимальное количество визитов в день: {stats['min_daily_visits']}")


display_results_task = PythonOperator(
    task_id='display_metrics_results',
    python_callable=display_results,
    dag=dag,
)

# Создание отчета
create_report = SQLExecuteQueryOperator(
    task_id='create_detailed_report',
    conn_id='postgres_default',
    sql="""
    -- Создание отчета для удобного просмотра
    DROP TABLE IF EXISTS hospital.five_visits_report;

    CREATE TABLE hospital.five_visits_report AS
    WITH daily_counts AS (
        SELECT 
            visit_date,
            COUNT(*) as visit_count,
            COUNT(DISTINCT patient_id) as unique_patients,
            STRING_AGG(DISTINCT diagnosis, ', ') as common_diagnoses
        FROM hospital.visits
        GROUP BY visit_date
    )
    SELECT 
        visit_date,
        visit_count,
        unique_patients,
        common_diagnoses,
        CASE 
            WHEN visit_count = 5 THEN 'Да'
            ELSE 'Нет'
        END as has_exactly_five_visits
    FROM daily_counts
    ORDER BY visit_date DESC;

    -- Добавляем комментарий к таблице
    COMMENT ON TABLE hospital.five_visits_report IS 'Отчет по датам с количеством визитов, включая даты с ровно 5 визитами';
    """,
    dag=dag
)

# Определение порядка выполнения задач
start >> calculate_metrics >> calculate_statistics >> display_results_task >> create_report >> end