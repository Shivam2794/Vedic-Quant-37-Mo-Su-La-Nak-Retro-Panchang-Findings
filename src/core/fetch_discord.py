import requests
import json

token = "NzU4MDExMTI5MDQ4OTg5NzI2.Gicv4-.AQ_l15vFw0J2bTrCocgQewtwNumiibAPJ1edzs"
headers = {
    "Authorization": token
}

# Get user's guilds
r = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers)
if r.status_code == 200:
    guilds = r.json()
    target_guild = None
    for g in guilds:
        if "rick" in g['name'].lower() or "skool" in g['name'].lower():
            target_guild = g
            break
            
    if target_guild:
        print(f"Found guild: {target_guild['name']} ({target_guild['id']})")
        # Get channels
        r = requests.get(f"https://discord.com/api/v9/guilds/{target_guild['id']}/channels", headers=headers)
        if r.status_code == 200:
            channels = r.json()
            target_channel = None
            for c in channels:
                if c.get('name') == 'skool-general':
                    target_channel = c
                    break
                    
            if target_channel:
                print(f"Found channel: {target_channel['name']} ({target_channel['id']})")
                # Get messages
                r = requests.get(f"https://discord.com/api/v9/channels/{target_channel['id']}/messages?limit=100", headers=headers)
                if r.status_code == 200:
                    messages = r.json()
                    
                    with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\discord_skool_general.json', 'w', encoding='utf-8') as f:
                        json.dump(messages, f, indent=2)
                    print(f"Saved {len(messages)} messages to discord_skool_general.json")
                else:
                    print("Failed to get messages:", r.status_code, r.text)
            else:
                print("Could not find skool-general channel.")
        else:
            print("Failed to get channels:", r.status_code, r.text)
    else:
        print("Could not find target guild.")
else:
    print("Failed to get guilds:", r.status_code, r.text)
