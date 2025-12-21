FROM apache/airflow:2.10.5

# Установка системных зависимостей (только если они необходимы для компиляции)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Возврат к пользователю airflow
USER airflow

# Копирование и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r requirements.txt