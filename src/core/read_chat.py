import csv
import sys
import os

csv.field_size_limit(sys.maxsize)

base_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\bulk_export_csv"
out_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"

files_to_process = {
    "skool-general": r"rick's skool - skool - skool-general [1429032513560379432].csv"
}

for name, filename in files_to_process.items():
    file_input_csv = os.path.join(base_dir, filename)
    output_txt = os.path.join(out_dir, f"{name}_output.txt")
    
    with open(file_input_csv, 'r', encoding='utf-8') as f, open(output_txt, 'w', encoding='utf-8') as out:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = row.get("Date", "")
            author = row.get("Author", "")
            content = row.get("Content", "")
            attachments = row.get("Attachments", "")
            
            out.write(f"[{timestamp}] {author}: {content}\n")
            if attachments:
                out.write(f"  ATTACHMENTS: {attachments}\n")
            out.write("-" * 40 + "\n")
print("Done")
