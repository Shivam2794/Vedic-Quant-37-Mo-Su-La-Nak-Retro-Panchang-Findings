
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def check_exists(keyword):
    matches = [r['column_name'] for r in rows if keyword in r['column_name']]
    print(f"Checking '{keyword}': found {len(matches)} matches.")

print("--- Brutal Check #2 (Astrology / Space) ---")
check_exists("Natal_Sun_Declination")
check_exists("Natal_Sun_Kranti")
check_exists("Natal_Sun_Out_Of_Bounds")
check_exists("Natal_D10_Deity")
check_exists("Natal_D60_Deity")
check_exists("Natal_Sun_Dispositor")

print("--- Brutal Check #3 (ML / Geometry) ---")
check_exists("Natal_Sun_Vargottama")
check_exists("Natal_Moon_Vargottama")
check_exists("Natal_Sun_Own_Nakshatra")
check_exists("Natal_Eclipse")
check_exists("Natal_Syzygy")
