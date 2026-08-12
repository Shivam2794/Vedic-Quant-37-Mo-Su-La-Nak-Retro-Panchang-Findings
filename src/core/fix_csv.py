
import csv
import shutil

CSV_FILE = 'master_feature_columns.csv'
BACKUP_FILE = 'master_feature_columns.csv.bak'

# Make a backup first
shutil.copyfile(CSV_FILE, BACKUP_FILE)

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

TYPE_MAP = {'BOOL': 'INTEGER', 'CATEGORY': 'TEXT', 'TIME': 'DATETIME'}

fixed_type = 0
fixed_tv = 0

for r in rows:
    # Task 2: Data Types
    if r['data_type'] in TYPE_MAP:
        r['data_type'] = TYPE_MAP[r['data_type']]
        fixed_type += 1

    # Task 3: is_time_varying fixes
    col_name = r['column_name']
    cat = r['category_code']
    
    if col_name in [
        'Vimshottari_MD_Lord_Natal_House',
        'Vimshottari_MD_Lord_Natal_Exalted',
        'Vimshottari_MD_Lord_Natal_Debilitated',
        'Vimshottari_MD_Lord_Natal_Shadbala'
    ] and r['is_time_varying'] == '0':
        r['is_time_varying'] = '1'
        fixed_tv += 1
        
    if cat == '2A' and r['is_time_varying'] == '0':
        r['is_time_varying'] = '1'
        fixed_tv += 1

with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Fixed {fixed_type} data type entries.")
print(f"Fixed {fixed_tv} is_time_varying entries.")
