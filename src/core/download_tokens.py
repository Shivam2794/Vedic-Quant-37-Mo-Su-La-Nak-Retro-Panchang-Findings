import urllib.request, json
url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
print("Downloading...")
req = urllib.request.urlopen(url)
data = json.loads(req.read())
print("Parsing...")
token_map = {}
for item in data:
    if item['exch_seg'] == 'NSE':
        token_map[item['symbol']] = item['token']

with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\angel_token_map.json", "w") as f:
    json.dump(token_map, f)
print(f"Saved {len(token_map)} tokens.")
