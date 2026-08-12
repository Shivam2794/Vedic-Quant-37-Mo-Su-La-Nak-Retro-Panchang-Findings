
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def inspect_category(cat_code, cat_name):
    print(f"--- Category {cat_code}: {cat_name} ---")
    cat_rows = [r for r in rows if r['category_code'] == cat_code]
    print(f"Total columns: {len(cat_rows)}")
    for r in cat_rows[:15]:
        print(f"  {r['column_name']} ({r['data_type']}, tv={r['is_time_varying']})")
    if len(cat_rows) > 15:
        print("  ...")
    print("\n")

inspect_category('4', 'Varshaphala')
inspect_category('5', 'Progressions')
inspect_category('6', 'KP System')
inspect_category('7', 'SBC Vedha / Chakras')
inspect_category('8', 'Muhurtha')
inspect_category('9', 'Mundane')
inspect_category('10', 'ML Crosses')
inspect_category('MKT_TECH', 'Market Tech')
inspect_category('MKT_CONTEXT', 'Market Context')
inspect_category('MKT_TARGET', 'Market Target')

# Let's specifically check for Varshaphala planets
vp_planets = [r['column_name'] for r in rows if 'Varshaphala' in r['column_name'] and 'Sign' in r['column_name']]
print(f"Varshaphala Sign columns: {vp_planets}")

# Let's check for Secondary Progressions
sp = [r['column_name'] for r in rows if 'Secondary' in r['column_name']]
print(f"Secondary Progression columns: {sp}")
