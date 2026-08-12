import boto3
from botocore.config import Config

def analyze_r2_deep():
    access_key_id = 'da0b24483b393e04e972c8b12f323ca2'
    secret_access_key = '097cf83aca60990c9c7499d6d63a4b75a195ac0416f1691d4e6ac870ae57e0e3'
    endpoint_url = 'https://c924773969fa9cd80ba2bf5bae7cfb00.r2.cloudflarestorage.com'
    bucket_name = 'divine-astrology-data'

    print(f"Deeply Analyzing R2 Bucket: {bucket_name}...")

    try:
        s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name='auto',
            config=Config(connect_timeout=10, read_timeout=10)
        )

        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)

        total_size = 0
        file_count = 0
        tickers = set()

        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    file_count += 1
                    total_size += obj['Size']
                    key = obj['Key']
                    if key.startswith('Stocks/Bars/'):
                        parts = key.split('/')
                        if len(parts) >= 3:
                            tickers.add(parts[2])

        print(f"\n--- Deep Analysis Summary ---")
        print(f"Total Files: {file_count:,}")
        print(f"Total Size: {total_size / 1024 / 1024 / 1024:.2f} GB")
        print(f"Unique Tickers Found ({len(tickers)}):")
        print(f"{', '.join(sorted(list(tickers)))}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_r2_deep()
