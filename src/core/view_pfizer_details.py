import os

deep_dive_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sop_deep_dive.txt"

with open(deep_dive_path, "r", encoding="utf-8") as f:
    content = f.read()

# Print matches for Pfizer and Genentech Restrictions from Video 6
print("==========================================================================")
print("PFIZER & GENENTECH RESTRICTIONS DETAILED FINDINGS")
print("==========================================================================")

blocks = content.split("FILE:")
for block in blocks:
    if "20251202_124555_transcript" in block:
        # Search for categories inside Video 6
        subblocks = block.split("--- CATEGORY:")
        for sb in subblocks:
            if "Pfizer & Genentech Restrictions" in sb or "Email Auditing & Retention" in sb:
                print(sb.strip())
                print("-" * 50)
