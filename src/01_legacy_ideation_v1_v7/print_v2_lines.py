with open(r"C:\Users\Shivam Patel\Downloads\20251027_134548_transcript.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(150, min(260, len(lines))):
    print(f"Line {i+1}: {lines[i].strip()}")
