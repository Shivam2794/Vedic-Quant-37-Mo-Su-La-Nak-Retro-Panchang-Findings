import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
transcripts = sorted([f for f in os.listdir(downloads_dir) if f.endswith("_transcript.txt")])

keywords = [
    r"t-?code",
    r"sap",
    r"exclusion",
    r"inclusion",
    r"alteryx",
    r"cartesian",
    r"kotg",
    r"pdp",
    r"gpo",
    r"y_[a-za-z0-9_]+",
    r"z_[a-za-z0-9_]+",
    r"override",
    r"howell",
    r"peneer",
    r"brugamand",
    r"single-?listing",
    r"class of trade",
    r"\bcot\b",
    r"hosp",
    r"hoso",
    r"yy\s*prime",
    r"kinray",
    r"audit",
    r"ruster",
    r"roster",
    r"web\s*equals"
]

compiled_keywords = [re.compile(kw, re.IGNORECASE) for kw in keywords]

output_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\search_results_utf8.txt"

with open(output_path, "w", encoding="utf-8") as out:
    out.write(f"Searching across {len(transcripts)} transcripts...\n")

    for transcript in transcripts:
        path = os.path.join(downloads_dir, transcript)
        matches = []
        with open(path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                matched_kws = []
                for kw, pattern in zip(keywords, compiled_keywords):
                    if pattern.search(line):
                        matched_kws.append(kw)
                if matched_kws:
                    matches.append((idx + 1, line.strip(), matched_kws))
                    
        if matches:
            out.write(f"\n==================================================\n")
            out.write(f"FILE: {transcript} ({len(matches)} matches)\n")
            out.write(f"==================================================\n")
            for line_num, line_text, kws in matches: # Write ALL matches to file!
                out.write(f"L{line_num} [{', '.join(kws)}]: {line_text}\n")
                
print("Search script successfully updated to write UTF-8 directly!")
