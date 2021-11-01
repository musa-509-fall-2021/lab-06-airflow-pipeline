from google.cloud import storage
import pandas as pd
import requests
import tempfile


def http_to_gcs(request_method, request_url,
                gcs_bucket_name, gcs_blob_name,
                request_data=None, request_files=None):
    """
    This function makes a request to an HTTP resource and saves the response
    content to a file in Google Cloud Storage.
    """
    # 1. Download data from the specified URL
    print(f'Downloading from {request_url}...')

    response = requests.request(request_method, request_url,
                                data=request_data, files=request_files)

    # 2. Save retrieved data to a local file
    with tempfile.NamedTemporaryFile(delete=False) as local_file:
        local_file_name = local_file.name
        print(f'Saving downloaded content to {local_file_name}...')
        local_file.write(response.content)

    # 3. Upload local file of data to Google Cloud Storage
    print(f'Uploading to GCS file gs://{gcs_bucket_name}/{gcs_blob_name}...')

    storage_robot = storage.Client()
    bucket = storage_robot.bucket(gcs_bucket_name)
    blob = bucket.blob(gcs_blob_name)
    blob.upload_from_filename(local_file_name)


def gcs_to_local_file(gcs_bucket_name, gcs_blob_name, local_file_name=None):
    """
    This function downloads a file from Google Cloud Storage and saves the
    result to a local file. The function returns the name of the saved file.
    """
    print(f'Saving from GCS file gs://{gcs_bucket_name}/{gcs_blob_name} '
          f'to local file {local_file_name}...')

    if local_file_name is None:
        with tempfile.NamedTemporaryFile(delete=False) as local_file:
            local_file_name = local_file.name

    storage_robot = storage.Client()
    bucket = storage_robot.bucket(gcs_bucket_name)
    blob = bucket.blob(gcs_blob_name)
    blob.download_to_filename(local_file_name)

    return local_file_name


def gcs_to_db(gcs_bucket_name, gcs_blob_name, db_conn, table_name, column_names=None):
    """
    This function downloads a file from Google Cloud Storage, reads the file
    contents, and write the contents to a database.
    """
    # 1. Download file from GCS
    local_file_name = gcs_to_local_file(gcs_bucket_name, gcs_blob_name)

    # 2. Read data from downloaded file
    print(f'Reading data from file {local_file_name}...')
    df = pd.read_csv(local_file_name, names=column_names)

    # 3. Write data into database/data warehouse
    print(f'Writing data to table {table_name}...')
    df.to_sql(table_name, db_conn, index=False, if_exists='replace')
