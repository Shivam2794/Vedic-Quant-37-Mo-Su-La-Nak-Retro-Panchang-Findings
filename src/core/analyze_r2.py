import boto3
import sys

def analyze_r2_bucket():
    # Cloudflare R2 Credentials
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
            region_name='auto' # R2 requires region 'auto' or 'us-east-1' sometimes
        )

        # List objects
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)

        total_size = 0
        file_count = 0
        extensions = {}
        
        print(f"\n--- Bucket Contents (Top 20) ---")
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    if file_count < 20:
                        print(f"- {obj['Key']} ({obj['Size'] / 1024 / 1024:.2f} MB) - Last Modified: {obj['LastModified']}")
                    
                    file_count += 1
                    total_size += obj['Size']
                    
                    ext = obj['Key'].split('.')[-1] if '.' in obj['Key'] else 'no_extension'
                    extensions[ext] = extensions.get(ext, 0) + 1

        print(f"\n--- Bucket Summary ---")
        print(f"Total Files: {file_count}")
        print(f"Total Size: {total_size / 1024 / 1024 / 1024:.4f} GB")
        print("File Types:")
        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
            print(f"  .{ext}: {count} files")

    except Exception as e:
        print(f"Error accessing bucket: {e}")

if __name__ == "__main__":
    analyze_r2_bucket()
