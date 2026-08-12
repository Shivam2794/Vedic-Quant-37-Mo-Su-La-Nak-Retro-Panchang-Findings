import os

deep_dive_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sop_deep_dive.txt"

if not os.path.exists(deep_dive_path):
    print("Deep dive file not found!")
    exit(1)

with open(deep_dive_path, "r", encoding="utf-8") as f:
    content = f.read()

# Let's write a function to print all matches for a specific category across all videos
def print_category_matches(category_name):
    print(f"\n==========================================================================================")
    print(f"SEARCHING FOR CATEGORY: {category_name}")
    print(f"==========================================================================================\n")
    
    # We can split by file blocks
    file_blocks = content.split("==================================================")
    
    for i in range(1, len(file_blocks), 2):
        file_header = file_blocks[i].strip()
        file_body = file_blocks[i+1] if i+1 < len(file_blocks) else ""
        
        # Now find the category inside the body
        cat_marker = f"--- CATEGORY: {category_name}"
        if cat_marker in file_body:
            print(f"--- IN FILE: {file_header} ---")
            # Extract just this category block from the body
            parts = file_body.split("--- CATEGORY:")
            for p in parts:
                if p.strip().startswith(category_name):
                    # Print the first few matches or lines
                    lines = p.strip().split("\n")
                    # Let's print the matches
                    print("\n".join(lines[:30]))
                    if len(lines) > 30:
                        print(f"... and {len(lines) - 30} more lines ...")
            print("-" * 50)

# Let's search some crucial categories
print_category_matches("Pfizer & Genentech Restrictions")
print_category_matches("REMS Blocks & Errors")
print_category_matches("Email Auditing & Retention")
print_category_matches("Alteryx & Cartesian Joins")
