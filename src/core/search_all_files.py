import os

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
for root, dirs, files in os.walk(downloads_dir):
    for file in files:
        if "lei" in file.lower() or "sop" in file.lower() or "transcript" in file.lower() or "t-code" in file.lower() or "tcode" in file.lower():
            print(os.path.join(root, file))
