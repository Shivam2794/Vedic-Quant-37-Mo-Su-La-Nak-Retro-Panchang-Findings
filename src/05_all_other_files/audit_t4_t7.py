
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

print("--- T4: Natal D1 ---")
check_exists("Natal_Sun_Retrograde")
check_exists("Natal_Sun_Combust")
check_exists("Natal_Sun_Velocity")
check_exists("Natal_Sun_Dig_Bala") # I added this in T4

print("--- T5: Natal Vargas ---")
check_exists("Natal_D9_Sun")
check_exists("Natal_D10_Moon")

print("--- T6: Natal Esoterics ---")
check_exists("Natal_SAV_House")
check_exists("Natal_Sun_Dignity")

print("--- T7: Natal Panchang ---")
check_exists("Natal_Tithi_Completion")
check_exists("Natal_Ishta_Kaal")

