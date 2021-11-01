"""
Load Process

Take the files that we've created and load them both into the database. You
should end up with two tables: addresses and geocoded_address_results.

This process expects the following environment variables to be set:

    * GOOGLE_APPLICATION_CREDENTIALS
      - The full path to your Google application credentials JSON file.
    * PIPELINE_DATA_BUCKET
      - The Google Cloud Storage bucket name where pipeline data is stored.
    * PIPELINE_PROJECT
      - The Google Cloud Platform project
    * PIPELINE_DATASET
      - The BigQuery dataset

"""

from dotenv import load_dotenv
load_dotenv()

import datetime as dt
import os
import sqlalchemy as sqa
from pipeline_tools import gcs_to_db

def main(**kwargs):
    bucket_name = os.environ['PIPELINE_DATA_BUCKET']
    project_name = os.environ['PIPELINE_PROJECT']
    dataset_name = os.environ['PIPELINE_DATASET']

    db = sqa.create_engine(f'bigquery://{project_name}/{dataset_name}')

    addresses_column_names = [
        'address_id',
        'street_address',
        'city',
        'state',
        'zip',
    ]
    gcs_to_db(
        gcs_bucket_name=bucket_name, gcs_blob_name=f'addresses_{dt.date.today()}.csv',
        db_conn=db, table_name='addresses', column_names=addresses_column_names
    )

    geocoded_column_names = [
        'address_id',
        'input_address',
        'match_status',
        'match_type',
        'matched_address',
        'lon_lat',
        'tiger_line_id',
        'tiger_line_side',
    ]
    gcs_to_db(
        gcs_bucket_name=bucket_name, gcs_blob_name=f'geocoded_address_results_{dt.date.today()}.csv',
        db_conn=db, table_name='geocoded_address_results', column_names=geocoded_column_names
    )

if __name__ == '__main__':
    main()
