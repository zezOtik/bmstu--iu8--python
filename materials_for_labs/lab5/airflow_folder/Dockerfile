FROM apache/airflow:2.10.5

# Become root to install requirements
USER root

ADD requirements.txt requirements.txt

# Switch back to airflow user
USER airflow

RUN pip install --user --no-cache-dir -r requirements.txt

# Set project name argument
# Example: PROJECT=mymod
#!!!!! Use only lowercase letters
ARG PROJECT=bmstutest

COPY --chown=airflow:root dags /opt/airflow/dags/${PROJECT}