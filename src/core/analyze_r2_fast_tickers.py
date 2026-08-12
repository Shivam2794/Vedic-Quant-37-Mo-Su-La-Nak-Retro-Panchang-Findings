import boto3
from botocore.config import Config

def extract_tickers_fast():
    access_key_id = 'da0b24483b393e04e972c8b12f323ca2'
    secret_access_key = '097cf83aca60990c9c7499d6d63a4b75a195ac0416f1691d4e6ac870ae57e0e3'
    endpoint_url = 'https://c924773969fa9cd80ba2bf5bae7cfb00.r2.cloudflarestorage.com'
    bucket_name = 'divine-astrology-data'

    print(f"Executing High-Speed Ticker Extraction on: {bucket_name}...")

    try:
        s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name='auto',
            config=Config(connect_timeout=10, read_timeout=10)
        )

        # Using Delimiter to instantly get all sub-folders (tickers) without scanning millions of files
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix='Stocks/Bars/', Delimiter='/')
        
        tickers = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                # prefix will be like 'Stocks/Bars/AAL/'
                ticker = prefix['Prefix'].split('/')[2]
                tickers.append(ticker)
                
        print(f"\n--- Discovered Tickers ({len(tickers)}) ---")
        print(', '.join(sorted(tickers)))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_tickers_fast()
