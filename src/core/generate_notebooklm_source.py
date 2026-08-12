
import os
import glob

brain_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\35732b90-976f-4cc4-b3fe-7fc24c167fe0"
output_file = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\NotebookLM_Master_Knowledge_Base.md"

markdown_files = glob.glob(os.path.join(brain_dir, "*.md"))

master_header = """# Vedic-Quant ML Architecture: Master Knowledge Base
## Project Overview
This document contains the entire evolutionary history, failures, profound discoveries, and architectural blueprints for building an institutional-grade, 22,781-column Vedic Astrology & Market Data quantitative matrix designed for Deep Learning.

## Core Discoveries & Pivots
1. **The SQLite Limit:** Discovered that SQLite and PostgreSQL cannot handle 22,781 columns. Pivoted to Apache Parquet for ML compatibility.
2. **Ayanamsha Drift:** Realized that calculating transit-to-natal distances using sidereal longitudes across decades introduces a 28 arc-minute precession drift. Pivoted to using purely Tropical mathematical orbs.
3. **Temporal Leakage:** Realized 00:00 UTC captures the sky 14 hours before the market opens. Locked calculations to 16:00 America/New_York (Market Close).
4. **The Node Schism:** Discovered Vimshottari Dasha strictly requires the Mean Node, while physical transit kinematics require True Node. Both must be computed.
5. **Memory Bifurcation:** The dataset is split into 14,508 static Natal columns (computed once) and 8,273 dynamic Transit columns (computed daily).

## Aggregate Project Artifacts
Below are all the brutal audits, implementation plans, and architectural designs generated during the schema phase.

================================================================================
"""

with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write(master_header)
    for md_file in markdown_files:
        filename = os.path.basename(md_file)
        outfile.write(f"\n\n# --- FILE: {filename} ---\n\n")
        try:
            with open(md_file, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
        except Exception as e:
            outfile.write(f"Error reading file: {e}\n")

print(f"Successfully aggregated {len(markdown_files)} artifacts into {output_file}")
