import os
import re

files = [
    r"C:\Users\Shivam Patel\Downloads\Institutionalizing Vedic Feature Engineering.md",
    r"C:\Users\Shivam Patel\Downloads\Institutionalizing Vedic Feature Engineering 2.md",
    r"C:\Users\Shivam Patel\Downloads\Troubleshooting Autonomous System Startup.md",
    r"C:\Users\Shivam Patel\Downloads\Troubleshooting Autonomous System Startup indian vedic quant.md"
]

out_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\timeline_extraction.txt"

with open(out_path, "w", encoding="utf-8") as out:
    for fpath in files:
        if not os.path.exists(fpath):
            out.write(f"FILE NOT FOUND: {fpath}\n\n")
            continue
            
        out.write(f"========== FILE: {os.path.basename(fpath)} ==========\n")
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Extract User Input sections and Planner Response summaries
        # We look for "### User Input" and "### Planner Response" or "User:"
        
        sections = re.split(r'(### User Input|### Planner Response)', content)
        for i in range(1, len(sections), 2):
            header = sections[i]
            body = sections[i+1].strip() if i+1 < len(sections) else ""
            
            # If body is too long, we extract first 1000 chars
            if len(body) > 1000:
                body = body[:1000] + "\n... [TRUNCATED]"
                
            out.write(f"\n{header}\n{body}\n")
        out.write("\n" + "="*50 + "\n\n")

print("Timeline extracted.")
