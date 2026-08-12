import json
with open(r'C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\transcripts\video_12.json', encoding='utf-8') as f:
    d = json.load(f)
with open('video_12_text.txt', 'w', encoding='utf-8') as f:
    for s in d['segments']:
        f.write(f"[{s['start']:.1f} - {s['end']:.1f}] {s['text']}\n")
