import boto3
from botocore.config import Config
import os

def download_db():
    access_key_id = 'da0b24483b393e04e972c8b12f323ca2'
    secret_access_key = '097cf83aca60990c9c7499d6d63a4b75a195ac0416f1691d4e6ac870ae57e0e3'
    endpoint_url = 'https://c924773969fa9cd80ba2bf5bae7cfb00.r2.cloudflarestorage.com'
    bucket_name = 'divine-astrology-data'
    key = 'gujrera.db'
    local_path = 'gujrera.db'

    print(f"Downloading {key} from {bucket_name}...")

    s3 = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name='auto',
        config=Config(connect_timeout=15, read_timeout=60)
    )
    
    if not os.path.exists(local_path):
        s3.download_file(bucket_name, key, local_path)
        print("Download complete.")
    else:
        print("File already exists locally.")

if __name__ == "__main__":
    download_db()
