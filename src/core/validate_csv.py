
import csv

CSV_FILE = 'master_feature_columns.csv'

def validate_csv(path):
    with open(path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    
    # 1. Zero duplicates
    names = [r['column_name'] for r in rows]
    duplicates = [name for name in set(names) if names.count(name) > 1]
    if duplicates:
        print(f"DUPLICATES FOUND: {duplicates}")
    else:
        print("1. Zero duplicates: PASSED")
    
    # 2. All data types valid
    valid = {'TEXT','INTEGER','REAL','FLOAT','DATETIME','DATE'}
    bad = [r for r in rows if r['data_type'] not in valid]
    if bad:
        print(f"2. Invalid types found: {[r['column_name'] + ' (' + r['data_type'] + ')' for r in bad[:10]]}")
    else:
        print("2. All data types valid: PASSED")
    
    # 3. is_time_varying only 0 or 1
    bad_tv = [r for r in rows if r['is_time_varying'] not in ('0','1')]
    if bad_tv:
        print(f"3. Invalid is_time_varying found: {[r['column_name'] for r in bad_tv[:10]]}")
    else:
        print("3. is_time_varying only 0 or 1: PASSED")
    
    # 4. No blank descriptions
    blank_desc = [r for r in rows if not r['description'].strip()]
    if blank_desc:
        print(f"4. Blank descriptions found: {[r['column_name'] for r in blank_desc[:10]]}")
    else:
        print("4. No blank descriptions: PASSED")
    
    # 5. All _Flag columns are INTEGER
    flag_cols = [r for r in rows if r['column_name'].endswith('_Flag')]
    wrong_type = [r for r in flag_cols if r['data_type'] != 'INTEGER']
    if wrong_type:
        print(f"5. Flag columns not INTEGER: {[r['column_name'] for r in wrong_type[:10]]}")
    else:
        print("5. All _Flag columns are INTEGER: PASSED")

    print(f"\nFinal column count: {len(rows)}")
    
validate_csv(CSV_FILE)
