import json

user_urls = [
    "https://stream.video.skool.com/oGWBkfLV01Qmn73FCNCB02OzvSRb1k01U02GLj36OP7pwDs.m3u8",
    "https://stream.video.skool.com/uvI63rhTCp9m2Q4gkTcqzPLOANOFj2ILLWs2keFxx01w.m3u8",
    "https://stream.video.skool.com/7lhbH017Ba6X6NUOW6rgMpRf3yrylq011RMLakRGujCn00.m3u8",
    "https://stream.video.skool.com/A4lL16rZBt9S400d36NFB1JNnhhGLeN00ebgOO9IJ34xs.m3u8",
    "https://stream.video.skool.com/ff4SEbR1d34Em7ccoiQPvW700wWxxqp9VGAu4z00YN01zY.m3u8",
    "https://stream.video.skool.com/FlicVtrVSf02xog00qxUvqJY00wXAPCLeS66Wan6RBOPf8.m3u8",
    "https://stream.video.skool.com/ZEQQTjbXrXXRr327lbXJ7DRMhy00sd7DH3IpX7f7F634.m3u8",
    "https://stream.video.skool.com/Qsr1aStzP2xooDimgw9NsNFDu3y9qwNQYyzFInSkKwg.m3u8",
    "https://stream.video.skool.com/u968oS4BSoIVOd2YQEs3SwxFuFm01EWdmD02xxkgeSCpo.m3u8",
    "https://stream.video.skool.com/4XciyFJkaO9tX13jXhyWyFzXqX18cRpHdL8sFKrY100U.m3u8",
    "https://stream.video.skool.com/KjRPe1kiEW602qlQrOmz026gBqDXFg013JsDovn3VVK8og.m3u8",
    "https://stream.video.skool.com/4iv5DvMFC3bS01nItAQ2OMlt6x702XzZ957a100n3zhhfA.m3u8",
    "https://stream.video.skool.com/WfNVpDLLgm5rbiUdFZ006DkK9exd007EAKjb2F6Ig00nr00.m3u8"
]

with open("urls.txt", "r", encoding="utf-8") as f:
    existing_urls = [line.strip().split("?")[0] for line in f if line.strip()]

results = []
for i, url in enumerate(user_urls):
    base_url = url.split("?")[0]
    if base_url in existing_urls:
        idx = existing_urls.index(base_url)
        if idx < 11:
            status = f"Completed (skool_video_{idx:02d}.mp4)" if idx > 0 else "Completed (skool_video.mp4)"
        else:
            status = "Failed Download (.part file)"
    else:
        status = "Not in urls.txt (Missing entirely)"
    
    results.append(f"User URL #{i+1}: {status}")

for r in results:
    print(r)
