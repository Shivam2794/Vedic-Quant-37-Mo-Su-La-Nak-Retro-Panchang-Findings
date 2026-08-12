import os

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
transcripts = sorted([f for f in os.listdir(downloads_dir) if "transcript" in f])

for fn in transcripts:
    fp = os.path.join(downloads_dir, fn)
    size = os.path.getsize(fp)
    try:
        with open(fp, "r", encoding="utf-8") as f:
            lines = f.readlines()
            line_count = len(lines)
            first_few = " ".join([l.strip() for l in lines[:3]])[:80]
            last_few = " ".join([l.strip() for l in lines[-3:]])[-80:]
        print(f"{fn:35} | Size: {size:8,} bytes | Lines: {line_count:5} | Start: {first_few}... | End: ...{last_few}")
    except Exception as e:
        print(f"Error reading {fn}: {e}")
