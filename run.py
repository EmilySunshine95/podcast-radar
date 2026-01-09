import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

RSS_URL = "https://api.substack.com/feed/podcast/10845.rss"

def fetch(url: str, retries: int = 3, backoff: float = 2.0) -> bytes:
    headers = {
        "User-Agent": "PodcastRadarBot/1.0 (+https://github.com/EmilySunshine95/podcast-radar)"
    }
    last_err = None
    for i in range(retries):
        try:
            print(f"Fetching RSS... attempt {i+1}/{retries}")
            res = requests.get(url, headers=headers, timeout=20)
            res.raise_for_status()
            return res.content
        except Exception as e:
            last_err = e
            time.sleep(backoff * (i + 1))
    raise last_err

xml_bytes = fetch(RSS_URL)

root = ET.fromstring(xml_bytes)
channel = root.find("channel")
items = channel.findall("item")

latest = items[0]
title = latest.find("title").text
link = latest.find("link").text
pub = latest.find("pubDate").text

html = f"""
<html>
<head><meta charset="utf-8"><title>Podcast Radar</title></head>
<body>
<h1>🎙️ Podcast Radar</h1>
<p>Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
<h2>Latest episode</h2>
<p><b>{title}</b></p>
<p><a href="{link}">{link}</a></p>
<p>{pub}</p>
</body>
</html>
"""

# 写入 docs/index.html（Pages 会发布 docs/）

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated docs/index.html")
