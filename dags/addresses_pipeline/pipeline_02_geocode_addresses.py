"""
Extract Process #2

Use the Census Geocoding API to geocode the addresses in the file that was
extracted in step one. The documentation for the API is available at:

https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf

This process expects the following environment variables to be set:

    * GOOGLE_APPLICATION_CREDENTIALS
      - The full path to your Google application credentials JSON file.
    * PIPELINE_DATA_BUCKET
      - The Google Cloud Storage bucket name where pipeline data is stored.

"""

from dotenv import load_dotenv
load_dotenv()

import datetime as dt
import os
from pipeline_tools import gcs_to_local_file, http_to_gcs

def main(**kwargs):
    bucket_name = os.environ['PIPELINE_DATA_BUCKET']

    local_file_name = gcs_to_local_file(
        gcs_bucket_name=bucket_name,
        gcs_blob_name=f'addresses_{dt.date.today()}.csv'
    )

    with open(local_file_name, 'rb') as opened_file:
        http_to_gcs(
            'post',
            'https://geocoding.geo.census.gov/geocoder/geographies/addressbatch',
            request_data={
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
            },
            request_files={
                'addressFile': ('input.csv', opened_file),
            },
            gcs_bucket_name=bucket_name,
            gcs_blob_name=f'geocoded_address_results_{dt.date.today()}.csv'
        )

if __name__ == '__main__':
    main()
