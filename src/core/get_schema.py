from google.cloud import bigquery
import pandas as pd

def check_schema():
    client = bigquery.Client()
    query = """
    SELECT *
    FROM `ml-dev-442817.astral.orion_batch_DJIA_PUBLICATION_enriched`
    LIMIT 1
    """
    df = client.query(query).to_dataframe()
    print("Columns:")
    print(df.columns.tolist())

if __name__ == "__main__":
    check_schema()
