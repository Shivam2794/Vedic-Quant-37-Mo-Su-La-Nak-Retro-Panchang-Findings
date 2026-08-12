import subprocess
import sys
import os

def run(cmd):
    print(f'Running: {cmd}')
    subprocess.run(cmd, shell=True, check=True)

try:
    import pillow_heif
except ImportError:
    run(f'"{sys.executable}" -m pip install pillow-heif Pillow')

import pillow_heif
from PIL import Image

files = [
    r'C:\Users\Shivam Patel\Downloads\20260520_161140.heic',
    r'C:\Users\Shivam Patel\Downloads\20260520_155140.heic',
    r'C:\Users\Shivam Patel\Downloads\20260520_155124.heic',
    r'C:\Users\Shivam Patel\Downloads\20260520_155237.heic',
    r'C:\Users\Shivam Patel\Downloads\20260520_161345.heic'
]

for f in files:
    if os.path.exists(f):
        heif_file = pillow_heif.read_heif(f)
        image = Image.frombytes(
            heif_file.mode, 
            heif_file.size, 
            heif_file.data,
            'raw',
        )
        out_path = f.replace('.heic', '.jpg')
        image.save(out_path, format='jpeg')
        print(f'Saved: {out_path}')
    else:
        print(f'Not found: {f}')
