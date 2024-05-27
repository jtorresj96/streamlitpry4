from datetime import datetime, timedelta
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import json
import mlflow
import os
import tempfile
from pathlib import Path
import boto3
import joblib

from botocore.exceptions import NoCredentialsError


mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("My_Model_Experiment")

os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 6),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def load_and_transform_data(**kwargs):
    # Ruta del archivo JSON
    json_file_path = '/opt/airflow/data/data.json'

    # Crear un DataFrame con los datos
    df = pd.read_json(json_file_path)

    # Guardar el DataFrame como una variable en el contexto de Airflow
    kwargs['ti'].xcom_push(key='dataframe', value=df)

def train_model(**kwargs):
    # Preparación del entorno
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='load_and_transform_task', key='dataframe')

    df = df[['house_size', 'bed', 'bath', 'acre_lot', 'price']]
    X = df.drop('price', axis=1)
    y = df['price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    lr = LinearRegression()
    
    mlflow.sklearn.autolog()
    with mlflow.start_run(run_name="LogisticRegression_GridSearch"):
        lr.fit(X_train, y_train)
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/modelpr4"
        mlflow.sklearn.log_model(lr, "modelpr4")
        

# Definir el DAG
dag = DAG(
    'json_to_dataframe_and_train_model',
    default_args=default_args,
    description='DAG to load JSON, transform to DataFrame, and train model',
    schedule_interval=timedelta(days=1),  # Frecuencia de ejecución
)

# Tareas del DAG
start_task = DummyOperator(task_id='start_task', dag=dag)

load_and_transform_task = PythonOperator(
    task_id='load_and_transform_task',
    python_callable=load_and_transform_data,
    provide_context=True,
    dag=dag,
)

train_model_task = PythonOperator(
    task_id='train_model_task',
    python_callable=train_model,
    provide_context=True,
    dag=dag,
)

end_task = DummyOperator(task_id='end_task', dag=dag)

# Definir el orden de las tareas
start_task >> load_and_transform_task >> train_model_task >> end_task