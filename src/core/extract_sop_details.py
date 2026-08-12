import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
transcripts = sorted([f for f in os.listdir(downloads_dir) if f.endswith("_transcript.txt")])

keywords_map = {
    "T-Codes & SAP Systems": [r"t-?code", r"kotg", r"gcu[1-9]", r"gcul", r"se[0-9]+", r"vk[0-9]+", r"va[0-9]+", r"mm[0-9]+", r"t\s*code"],
    "Exclusion Owners & Codes": [r"howell", r"peneer", r"brugamand", r"hartman", r"ec\s*[0-9]+", r"exclusion\s*code"],
    "REMS Blocks & Errors": [r"rems", r"brems", r"check\s*failed", r"brems\s*struct"],
    "Pfizer & Genentech Restrictions": [r"pfizer", r"genentech", r"benlysta", r"xolair", r"solar", r"actemra", r"camera", r"the\s*max"],
    "Alteryx & Cartesian Joins": [r"alteryx", r"cartesian", r"join", r"prime", r"yy\s*prime", r"bu\s*code", r"buying\s*group", r"hosp", r"hoso"],
    "PDP & Ordering Platforms": [r"pdp", r"platform", r"run\s*team", r"visibility", r"replicate"],
    "Email Auditing & Retention": [r"retention", r"retention\s*compliance", r"outlook", r"deleted", r"audit", r"save\s*email", r"email\s*approval"],
    "Special exceptions & PR": [r"puerto", r"rico", r"pr\s*ndc", r"bypass", r"prison", r"sequestered", r"alternate", r"alternative"],
    "SharePoint & Web=0": [r"sharepoint", r"web\s*=\s*0", r"web=0", r"mapping\s*file", r"path"]
}

output_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sop_deep_dive.txt"

with open(output_path, "w", encoding="utf-8") as out:
    out.write("LE&I TRANSCRIPTS DEEP-DIVE KEYWORDS EXTRACTION\n")
    out.write("==================================================\n\n")
    
    for transcript in transcripts:
        path = os.path.join(downloads_dir, transcript)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        out.write(f"\n\n==================================================\n")
        out.write(f"FILE: {transcript} ({len(lines)} lines)\n")
        out.write(f"==================================================\n")
        
        # Track which lines match which categories to avoid duplicate printouts
        matched_lines = set()
        
        for cat_name, patterns in keywords_map.items():
            compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
            cat_matches = []
            
            for idx, line in enumerate(lines):
                # Search for keyword matches
                matches_found = []
                for p_idx, pat in enumerate(compiled):
                    m = pat.search(line)
                    if m:
                        matches_found.append(patterns[p_idx])
                
                if matches_found:
                    # Capture context: 1 line before, matching line, 1 line after
                    start = max(0, idx - 1)
                    end = min(len(lines) - 1, idx + 1)
                    context_snippet = []
                    for c_idx in range(start, end + 1):
                        prefix = ">>> " if c_idx == idx else "    "
                        context_snippet.append(f"{prefix}L{c_idx+1}: {lines[c_idx].strip()}")
                    
                    cat_matches.append((idx + 1, matches_found, "\n".join(context_snippet)))
            
            if cat_matches:
                out.write(f"\n--- CATEGORY: {cat_name} ({len(cat_matches)} matches) ---\n")
                for l_num, m_kws, snippet in cat_matches:
                    out.write(f"Line {l_num} (Matched: {', '.join(m_kws)}):\n{snippet}\n\n")

print("Deep-dive extractor script written to scratch directory.")
