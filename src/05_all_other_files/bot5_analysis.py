import json
import glob
import os
import re

logs = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\brain\*\.system_generated\logs\transcript.jsonl")

# target directories:
# astrology_ml, astro_ml_research, kp_astrology

# Or just find files mentioned in transcripts where "Astro" or "Advance" is present.
output_file = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\bot5_analysis.py"
