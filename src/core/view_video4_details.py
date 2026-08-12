import os

deep_dive_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sop_deep_dive.txt"

with open(deep_dive_path, "r", encoding="utf-8") as f:
    content = f.read()

print("==========================================================================")
print("VIDEO 4: ALTERYX, CARTESIAN JOINS, YY PRIME & ONBOARDING DETAILS")
print("==========================================================================")

blocks = content.split("FILE:")
for block in blocks:
    if "20251111_130036_transcript" in block:
        subblocks = block.split("--- CATEGORY:")
        for sb in subblocks:
            if "Alteryx & Cartesian Joins" in sb or "T-Codes & SAP Systems" in sb or "PDP & Ordering Platforms" in sb:
                print(sb.strip())
                print("-" * 50)
