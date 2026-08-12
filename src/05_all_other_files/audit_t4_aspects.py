
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def check_exists(keyword):
    matches = [r['column_name'] for r in rows if keyword in r['column_name']]
    print(f"Checking '{keyword}': found {len(matches)} matches.")
    if len(matches) > 0 and len(matches) <= 10:
        print(f"  Examples: {matches}")
    elif len(matches) > 10:
        print(f"  Examples: {matches[:5]} ... {matches[-5:]}")

print("--- T4 check ---")
check_exists("Natal_Sun_Aspect")
check_exists("Natal_Sun_Distance")
check_exists("Natal_Sun_Orb")
