from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from . import pipeline_01_download_addresses
from . import pipeline_02_geocode_addresses
from . import pipeline_03_insert_addresses

with DAG(dag_id='addresses_pipeline',
         schedule_interval='@daily',
         start_date=datetime(2021, 10, 22),
         catchup=False) as dag:

    extract_raw_addresses = PythonOperator(
        task_id='extract_raw_addresses',
        python_callable=pipeline_01_download_addresses.main,
    )

    extract_geocoded_addresses = PythonOperator(
        task_id='extract_geocoded_addresses',
        python_callable=pipeline_02_geocode_addresses.main,
    )

    load_address_data = PythonOperator(
        task_id='load_address_data',
        python_callable=pipeline_03_insert_addresses.main,
    )

    extract_raw_addresses >> extract_geocoded_addresses >> load_address_data
