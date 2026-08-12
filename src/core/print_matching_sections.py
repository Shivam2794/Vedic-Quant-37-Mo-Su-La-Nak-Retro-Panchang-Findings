import os

deep_dive_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sop_deep_dive.txt"

if not os.path.exists(deep_dive_path):
    print("Deep dive file not found!")
    exit(1)

with open(deep_dive_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

def search_category_details(target_category):
    print(f"\n==========================================================================================")
    print(f"DISPLAYING MATCHES FOR: {target_category}")
    print(f"==========================================================================================\n")
    
    current_file = "Unknown"
    in_target_category = False
    block_lines = []
    
    for line in lines:
        if line.startswith("FILE:"):
            current_file = line.strip()
        elif line.startswith("--- CATEGORY:"):
            if target_category.lower() in line.lower():
                in_target_category = True
                print(f"\n>>> IN FILE: {current_file} ({line.strip()}) <<<\n")
            else:
                in_target_category = False
        elif in_target_category:
            block_lines.append(line)
            
    # Now we print the block lines. Let's print them but clean up spacing
    output = "".join(block_lines)
    # Print the first 5000 characters to keep it readable, and we can read more if needed
    if len(output) > 6000:
        print(output[:6000])
        print(f"\n... [TRUNCATED - {len(output)-6000} chars remaining] ...")
    else:
        print(output)

# Let's run it for key categories
search_category_details("Pfizer & Genentech Restrictions")
search_category_details("REMS Blocks & Errors")
search_category_details("Email Auditing & Retention")
search_category_details("Alteryx & Cartesian Joins")
