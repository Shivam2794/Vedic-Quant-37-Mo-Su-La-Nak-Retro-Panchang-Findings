import requests
import json
import time
import os

token = "NzU4MDExMTI5MDQ4OTg5NzI2.Gicv4-.AQ_l15vFw0J2bTrCocgQewtwNumiibAPJ1edzs"
headers = {
    "Authorization": token
}
channel_id = "1429032513560379432"
all_messages = []
last_message_id = None

print("Fetching messages...")
while True:
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100"
    if last_message_id:
        url += f"&before={last_message_id}"
    
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        messages = r.json()
        if not messages:
            break
        all_messages.extend(messages)
        last_message_id = messages[-1]['id']
        time.sleep(0.5)
    elif r.status_code == 429:
        retry_after = r.json().get('retry_after', 1)
        print(f"Rate limited, sleeping for {retry_after}")
        time.sleep(retry_after)
    else:
        print(f"Failed to fetch messages: {r.status_code}, response: {r.text}")
        break

print(f"Total messages fetched: {len(all_messages)}")

all_messages.sort(key=lambda x: x['timestamp'])

formatted = []
for m in all_messages:
    author = m['author']['username']
    content = m.get('content', '')
    attachments = [a['url'] for a in m.get('attachments', [])]
    
    msg_str = f"[{m['timestamp']}] {author}: {content}"
    if attachments:
        msg_str += f"\nAttachments: {', '.join(attachments)}"
    formatted.append(msg_str)

file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\skool_general_formatted_v2.txt"
with open(file_path, "w", encoding="utf-8") as f:
    f.write("\n".join(formatted))

print(f"Formatted text saved. Total lines: {len(formatted)}")
