import subprocess, json, os

base = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\quant_rick_channel\The drivers of price and answers to them"

files_to_check = [
    "01_Introduction to the drivers of price.mp4",
    "02_MACD-V_ and some extra ensembling theory.mp4",
]

for fname in files_to_check:
    fpath = os.path.join(base, fname)
    size_mb = os.path.getsize(fpath) / 1_048_576
    res = subprocess.run(
        ["ffprobe", "-v", "error",
         "-show_entries", "format=duration",
         "-show_entries", "stream=codec_name,width,height",
         "-of", "json", fpath],
        capture_output=True, text=True
    )
    if res.returncode == 0:
        d = json.loads(res.stdout)
        duration = float(d.get("format", {}).get("duration", 0))
        mm, ss = int(duration // 60), int(duration % 60)
        streams = d.get("streams", [])
        vid = next((s for s in streams if s.get("codec_name") in ("h264","hevc","vp9")), None)
        res_str = f"{vid['width']}x{vid['height']}" if vid else "audio-only"
        print(f"[OK] {fname}")
        print(f"     Size: {size_mb:.1f} MB | Duration: {mm}m{ss:02d}s | Res: {res_str}")
    else:
        print(f"[FAIL] {fname}")
        print(f"     {res.stderr[-300:]}")

# Also print description content
print("\n--- DESCRIPTIONS ---")
for fname in ["01_Introduction to the drivers of price_description.txt",
              "02_MACD-V_ and some extra ensembling theory_description.txt"]:
    fpath = os.path.join(base, fname)
    if os.path.exists(fpath):
        content = open(fpath, encoding="utf-8").read()
        print(f"\n[{fname}]")
        print(content[:500])
