import requests
import json
import sys

token = "NzU4MDExMTI5MDQ4OTg5NzI2.Gicv4-.AQ_l15vFw0J2bTrCocgQewtwNumiibAPJ1edzs"
channel_id = "1429032513560379432" # skool-general

headers = {
    "Authorization": token
}

print(f"Fetching messages from channel {channel_id}...")
r = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100", headers=headers)

if r.status_code == 200:
    messages = r.json()
    with open("discord_messages.txt", "w", encoding="utf-8") as f:
        for msg in reversed(messages):  # chronological order
            author = msg.get('author', {}).get('username', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            f.write(f"[{timestamp}] {author}: {content}\n")
            
            # also dump attachments
            for attach in msg.get('attachments', []):
                f.write(f"  [Attachment: {attach.get('filename')} - {attach.get('url')}]\n")
    print("Messages saved to discord_messages.txt")
else:
    print(f"Failed to fetch messages: {r.status_code} {r.text}")
