
import csv
from collections import Counter, defaultdict

with open('master_feature_columns.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows: {len(rows)}")
print(f"CSV columns: {list(rows[0].keys())}")
print()

cats = defaultdict(list)
for r in rows:
    cats[r['category_code']].append(r)

print("=== CATEGORY BREAKDOWN ===")
for code in sorted(cats.keys()):
    group = cats[code]
    name = group[0]['category_name']
    types = Counter(r['data_type'] for r in group)
    tv = sum(1 for r in group if r['is_time_varying'] == '1')
    samples = [r['column_name'] for r in group[:6]]
    print(f"[{code}] {name}")
    print(f"  Count: {len(group)} | Time-varying: {tv} | Static: {len(group)-tv}")
    print(f"  Types: {dict(types)}")
    print(f"  Samples: {samples}")
    print()

print()
print("=== DETAILED SCANS ===")

# Check for nulls / blanks in key fields
null_col   = [r for r in rows if not r['column_name'].strip()]
null_cat   = [r for r in rows if not r['category_code'].strip()]
null_desc  = [r for r in rows if not r['description'].strip()]
null_type  = [r for r in rows if not r['data_type'].strip()]
null_tv    = [r for r in rows if r['is_time_varying'] not in ('0','1')]

print(f"Blank column_name: {len(null_col)}")
print(f"Blank category_code: {len(null_cat)}")
print(f"Blank description: {len(null_desc)}")
print(f"Blank data_type: {len(null_type)}")
print(f"Invalid is_time_varying (not 0 or 1): {len(null_tv)}")
if null_tv:
    for r in null_tv[:10]:
        print(f"  -> {r['column_name']} is_time_varying='{r['is_time_varying']}'")

print()

# Check for duplicate column names
name_counts = Counter(r['column_name'] for r in rows)
dups = {k: v for k, v in name_counts.items() if v > 1}
print(f"Duplicate column names: {len(dups)}")
for k, v in sorted(dups.items(), key=lambda x: -x[1])[:20]:
    print(f"  '{k}' appears {v} times")

print()

# Check valid data types
valid_types = {'TEXT','INTEGER','REAL','FLOAT','BOOLEAN','DATE','DATETIME','INT','NUMERIC','BIT'}
bad_types = [r for r in rows if r['data_type'].strip().upper() not in valid_types]
print(f"Non-standard data_type values: {len(bad_types)}")
bad_type_vals = Counter(r['data_type'] for r in bad_types)
for t, c in bad_type_vals.most_common(20):
    print(f"  '{t}': {c} rows")

print()

# Check time-varying correctness: static categories should have is_time_varying=0
STATIC_CATS = {'1A','1B','1C','2A','2B','2C','2D','2E','2F','2G','2H'}
tv_wrong = [r for r in rows if r['category_code'] in STATIC_CATS and r['is_time_varying'] == '1']
print(f"Static-cat rows wrongly marked time-varying: {len(tv_wrong)}")
for r in tv_wrong[:10]:
    print(f"  [{r['category_code']}] {r['column_name']} is_time_varying=1")

print()

# Check dynamic categories that should be time_varying=1
DYNAMIC_CATS = {'3A','3B','3C','3D','4A','4B','4C','5A','5B','5C','5D','6A','6B','6C',
                '7A','7B','7C','7D','7E','7F','8A','8B','8C','8D','9A','9B','10A','10B','10C'}
tv_static_wrong = [r for r in rows if r['category_code'] in DYNAMIC_CATS and r['is_time_varying'] == '0']
print(f"Dynamic-cat rows wrongly marked static: {len(tv_static_wrong)}")
for r in tv_static_wrong[:10]:
    print(f"  [{r['category_code']}] {r['column_name']} is_time_varying=0")

print()

# Per-category deep scan - show all column names for small cats, samples for large
for code in sorted(cats.keys()):
    group = cats[code]
    print(f"--- [{code}] {group[0]['category_name']} ({len(group)} cols) ---")
    col_names = [r['column_name'] for r in group]
    
    # Check naming conventions
    has_lower  = [c for c in col_names if c != c.lower()]
    has_spaces = [c for c in col_names if ' ' in c]
    has_dash   = [c for c in col_names if '-' in c]
    
    print(f"  Mixed case names: {len(has_lower)} | Spaces: {len(has_spaces)} | Dashes: {len(has_dash)}")
    if has_lower[:5]:
        print(f"  Mixed case examples: {has_lower[:5]}")
    if has_spaces[:5]:
        print(f"  Space examples: {has_spaces[:5]}")
    if has_dash[:5]:
        print(f"  Dash examples: {has_dash[:5]}")
    
    # Check descriptions for suspicious words
    suspicious = ['TODO','TBD','FIXME','placeholder','unknown','N/A']
    sus_rows = [r for r in group if any(s.lower() in r['description'].lower() for s in suspicious)]
    if sus_rows:
        print(f"  Suspicious descriptions ({len(sus_rows)}):")
        for r in sus_rows[:5]:
            print(f"    {r['column_name']}: {r['description'][:80]}")
    
    print()
