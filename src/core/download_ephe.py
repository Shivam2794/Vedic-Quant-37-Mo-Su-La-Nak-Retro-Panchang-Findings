
import os
import urllib.request

EPHE_DIR = r"C:\ephemeris"
os.makedirs(EPHE_DIR, exist_ok=True)

BASE_URL = "https://www.astro.com/ftp/swisseph/ephe/"
FILES_TO_DOWNLOAD = [
    "sepl_18.se1",
    "semo_18.se1",
    "seas_18.se1"
]

for file in FILES_TO_DOWNLOAD:
    url = BASE_URL + file
    dest = os.path.join(EPHE_DIR, file)
    if not os.path.exists(dest):
        print(f"Downloading {file}...")
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"Successfully downloaded {file}")
        except Exception as e:
            print(f"Failed to download {file}: {e}")
    else:
        print(f"{file} already exists.")

print("Ephemeris download process complete.")
