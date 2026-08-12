import os

deep_dive_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sop_deep_dive.txt"

with open(deep_dive_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

def print_exact_category(cat_name):
    print(f"\n=== CATEGORY: {cat_name} ===")
    current_file = ""
    in_cat = False
    for line in lines:
        if line.startswith("FILE:"):
            current_file = line.strip()
        elif line.startswith("--- CATEGORY:"):
            if cat_name.lower() in line.lower():
                in_cat = True
                print(f"\n>>> File: {current_file} ({line.strip()})")
            else:
                in_cat = False
        elif in_cat:
            print(line, end="")

# Inspect specific categories one by one
print_exact_category("Pfizer & Genentech Restrictions")
print_exact_category("REMS Blocks & Errors")
print_exact_category("Special exceptions & PR")
print_exact_category("SharePoint & Web=0")
