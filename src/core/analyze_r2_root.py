import boto3
from botocore.config import Config

def check_root_directories():
    access_key_id = 'da0b24483b393e04e972c8b12f323ca2'
    secret_access_key = '097cf83aca60990c9c7499d6d63a4b75a195ac0416f1691d4e6ac870ae57e0e3'
    endpoint_url = 'https://c924773969fa9cd80ba2bf5bae7cfb00.r2.cloudflarestorage.com'
    bucket_name = 'divine-astrology-data'

    try:
        s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name='auto',
            config=Config(connect_timeout=10, read_timeout=10)
        )

        print("Querying root directories of the bucket...")
        # Empty prefix, delimiter='/' means it will only return top-level folders
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix='', Delimiter='/')
        
        folders = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                folders.append(prefix['Prefix'])
                
        print(f"\nTop-Level Folders Found ({len(folders)}):")
        for f in folders:
            print(f"  - {f}")
            
        print("\nAlso checking if there are any files directly in the root:")
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("  (No root-level files found)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_root_directories()
