"""
Extract Process #1

This process retrieves data from a URL, downloads that data, and then uploads
the data to a Google Cloud Storage bucket. The process expects the following
environment variables to be set:

    * GOOGLE_APPLICATION_CREDENTIALS
      - The full path to your Google application credentials JSON file.
    * PIPELINE_DATA_BUCKET
      - The Google Cloud Storage bucket name where pipeline data is stored.

"""

from dotenv import load_dotenv
load_dotenv()

import datetime as dt
import os
from pipeline_tools import http_to_gcs

def main(**kwargs):
    bucket_name = os.environ['PIPELINE_DATA_BUCKET']  # <-- retrieve the bucket name from the environment

    http_to_gcs(
        request_method='get',
        request_url='https://storage.googleapis.com/mjumbewu_musa_509/lab04_pipelines_and_web_services/get_latest_addresses',
        gcs_bucket_name=bucket_name,
        gcs_blob_name=f'addresses_{dt.date.today()}.csv',
    )

if __name__ == '__main__':
    main()
