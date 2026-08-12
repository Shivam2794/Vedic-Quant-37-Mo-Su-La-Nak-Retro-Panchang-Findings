import requests
import sys

token = "NzU4MDExMTI5MDQ4OTg5NzI2.Gicv4-.AQ_l15vFw0J2bTrCocgQewtwNumiibAPJ1edzs"
headers = {
    "Authorization": token
}

with open("channels.txt", "w", encoding="utf-8") as f:
    f.write("Fetching guilds...\n")
    r = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers)
    if r.status_code == 200:
        guilds = r.json()
        for g in guilds:
            f.write(f"Guild: {g['name']} (ID: {g['id']})\n")
            
            # fetch channels for this guild
            cr = requests.get(f"https://discord.com/api/v9/guilds/{g['id']}/channels", headers=headers)
            if cr.status_code == 200:
                channels = cr.json()
                for c in channels:
                    if 'name' in c and c['name'] is not None:
                        if 'skool' in c['name'].lower() or 'general' in c['name'].lower() or 'chat' in c['name'].lower() or 'rick' in c['name'].lower():
                            f.write(f"  - Channel: {c['name']} (ID: {c['id']})\n")
    else:
        f.write(f"Failed to fetch guilds: {r.status_code} {r.text}\n")
