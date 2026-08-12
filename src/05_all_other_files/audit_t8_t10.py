
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

print("--- T8: Transits ---")
check_exists("Kakshya")
check_exists("Transit_Sun_Acceleration")
check_exists("Transit_Jupiter_Stationary")

print("--- T9: Dashas ---")
check_exists("Sandhi")
check_exists("Chidra")
check_exists("Vimshottari_MD_Lord_Natal_Dignity")

print("--- T10: Varshaphala ---")
check_exists("Varshaphala_Mudda_MD_Elapsed")
check_exists("Varshaphala_Jupiter_Retrograde")
check_exists("Varshaphala_Sun_Combust")
check_exists("Distance_Transit_Sun_To_Varshaphala")

