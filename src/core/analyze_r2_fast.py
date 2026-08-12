import boto3
from botocore.config import Config
import sys

def analyze_r2_bucket():
    access_key_id = 'da0b24483b393e04e972c8b12f323ca2'
    secret_access_key = '097cf83aca60990c9c7499d6d63a4b75a195ac0416f1691d4e6ac870ae57e0e3'
    endpoint_url = 'https://c924773969fa9cd80ba2bf5bae7cfb00.r2.cloudflarestorage.com'
    bucket_name = 'divine-astrology-data'

    print(f"Connecting to R2 Bucket: {bucket_name}...")

    try:
        s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name='auto',
            config=Config(connect_timeout=5, read_timeout=5, retries={'max_attempts': 0})
        )

        response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=50)
        
        if 'Contents' not in response:
            print("Bucket is empty or not accessible.")
            return
            
        print("\n--- Bucket Contents ---")
        for obj in response['Contents']:
            print(f"- {obj['Key']} ({obj['Size']} bytes)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_r2_bucket()
